#!/usr/bin/env python
# hpo/services.py

from __future__ import annotations
import csv
import datetime as dt
import faiss
import hashlib
import json
import numpy as np
import obonet
import os
import re
import requests
import unicodedata
from django.conf import settings
from django.db import connection, transaction
from io import StringIO
from openai import OpenAI
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Dict

from .models import HPOTerm, HPOEdge, HPOArtifact

"""Utilities to fetch, parse, import, and index HPO data.
Usage:

A) One-shot: fetch + import + index (no vectors yet)
from hpo.services import refresh_from_obo, verify_term_count
csv_path, terms, edges = refresh_from_obo()   # downloads from hp.obo, imports terms/edges, builds search_tsv, records artifact
verify_term_count()

B) Build vectors and attach to the active release

OpenAI embeddings

from hpo.services import get_active_artifact, build_vectors_from_csv, attach_vectors_to_release
art = get_active_artifact()
faiss_p, npz_p, used_model = build_vectors_from_csv(Path(art.csv_path), provider="openai")
attach_vectors_to_release(art.release, faiss_p, npz_p, used_model, set_active=True)


Local embeddings (no API)

faiss_p, npz_p, used_model = build_vectors_from_csv(Path(art.csv_path), provider="local", local_model="sentence-transformers/all-MiniLM-L6-v2")
attach_vectors_to_release(art.release, faiss_p, npz_p, used_model, set_active=True)

C) Only import from an existing CSV (skip download/parse)
from hpo.services import upsert_terms, backfill_search_tsv, record_artifact
import csv, json
rows = []
with open("data/hpo/hpo_texts_2025-10-01.csv", newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append({
            "hpo_id": row["hpo_id"],
            "label": row["label"],
            "definition": row.get("definition",""),
            "synonyms": json.loads(row.get("synonyms_json","[]")),
            "deprecated": False,
        })
upsert_terms(rows, release="2025-10-01")
backfill_search_tsv()
record_artifact("2025-10-01", "local-csv", Path("data/hpo/hpo_texts_2025-10-01.csv"), active=True)

Notes & guardrails

Extensions: make sure you previously enabled pg_trgm (migration with RunSQL), and created your GIN indexes.

Transactions: refresh_from_obo wraps upserts + tsv backfill + artifact record in a single transaction.

Upserts: uses INSERT … ON CONFLICT DO UPDATE; requires hpo_id as PK (you already have it).

Search freshness: re-run backfill_search_tsv() at the end of any import; or add a DB trigger later if you want it automatic.

Vectors: FAISS/NPZ are files on disk—only paths live in Postgres via HPOArtifact.
"""


# ---------- Config helpers ----------
_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.DOTALL)

# ensure OpenAI-compatible environment variable
if getattr(settings, "EMBED_API_KEY", None):
    os.environ["OPENAI_API_KEY"] = settings.EMBED_API_KEY
if getattr(settings, "EMBED_BASE_URL", None):
    os.environ["OPENAI_BASE_URL"] = settings.EMBED_BASE_URL

def data_dir() -> Path:
    return Path(os.getenv("HPO_DATA_DIR", getattr(settings, "HPO_DATA_DIR", "utilities/hpo_artifacts"))).resolve()

def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# ======================= Prompt Loading =======================
def load_prompts(file_path="utilities/hpo_artifacts/system_prompts.json"):
    if not os.path.exists(file_path):
        return (f"Error: Prompt file '{file_path}' not found.")
    with open(file_path, "r") as f:
        return json.load(f)

prompts = load_prompts()
system_message_I = prompts.get("system_message_I", "")
system_message_II = prompts.get("system_message_II", "")

# ---------- Download & parse ----------

def download_obo(url: str, dest: Optional[Path] = None) -> Path:
    """
    Download hp.obo (or any OBO) and save to disk.
    """
    dest = dest or (data_dir() / "hp.obo")
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest

def parse_obo_to_rows(obo_path: Path) -> Tuple[List[Dict], List[Tuple[str, str]]]:
    """
    Return:
      - term rows: [{hpo_id, label, definition, synonyms (list), deprecated(bool)}]
      - edges: [(parent_id, child_id)] for is_a relations
    """
    g = obonet.read_obo(obo_path.as_posix())
    term_rows: List[Dict] = []
    edges: List[Tuple[str, str]] = []

    for node, data in g.nodes(data=True):
        if not str(node).startswith("HP:"):
            continue
        label = data.get("name", "") or ""
        definition = data.get("def", "") or ""
        if isinstance(definition, list):
            definition = " ".join(definition)

        syns = data.get("synonym", []) or []
        if not isinstance(syns, list):
            syns = [str(syns)]
        # strip quotes like "Ataxia" EXACT [] etc.
        clean_syns = []
        for s in syns:
            s = str(s)
            # the OBO synonym line often looks like: "Ataxia" EXACT [] ()
            # keep text inside the first pair of quotes, if present
            if s.startswith('"'):
                try:
                    clean_syns.append(s.split('"')[1])
                except Exception:
                    clean_syns.append(s.strip('"'))
            else:
                clean_syns.append(s)
        deprecated = bool(data.get("is_obsolete", False))
        term_rows.append({
            "hpo_id": node,
            "label": label,
            "definition": definition,
            "synonyms": clean_syns,
            "deprecated": deprecated,
        })

        # is_a edges: parent HP -> child HP (current node is child; is_a points to parents)
        for parent in data.get("is_a", []) or []:
            if str(parent).startswith("HP:"):
                edges.append((parent, node))

    return term_rows, edges

def write_hpo_csv(term_rows: List[Dict], out_csv: Path) -> Path:
    """
    Write a flat CSV for provenance / optional rebuilds.
    Columns: hpo_id,label,definition,synonyms_json,deprecated
    """
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["hpo_id", "label", "definition", "synonyms_json", "deprecated"])
        for r in term_rows:
            w.writerow([r["hpo_id"], r["label"], r["definition"], json.dumps(r["synonyms"]), int(r["deprecated"])])
    return out_csv

# ---------- Normalization & search helpers ----------

def _normalize_ascii_lower(s: str) -> str:
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii").lower()

def _concat_synonyms(syns: List[str]) -> str:
    return "; ".join(s for s in syns if s)

def backfill_search_tsv():
    """
    Compute search_tsv = to_tsvector('english', label || ' ' || synonyms_concat || ' ' || coalesce(definition,''))
    Run after bulk upsert or inside your import command.
    """
    with connection.cursor() as cur:
        cur.execute("""
            UPDATE hpo_hpoterm
            SET search_tsv = to_tsvector(
              'english',
              coalesce(label,'') || ' ' ||
              coalesce(synonyms_concat,'') || ' ' ||
              coalesce(definition,'')
            );
        """)

# ---------- Import / Upsert (terms & edges) ----------

def upsert_terms(term_rows: List[Dict], release: str, batch: int = 2000):
    """
    Efficient Postgres upsert (INSERT ... ON CONFLICT DO UPDATE) in chunks.
    Requires HPOTerm(hpo_id PK).
    """
    sql = """
    INSERT INTO hpo_hpoterm
        (hpo_id, label, definition, synonyms, release, deprecated,
         label_normalized, synonyms_concat, search_tsv, created_at, updated_at)
    VALUES
        %s
    ON CONFLICT (hpo_id) DO UPDATE SET
        label = EXCLUDED.label,
        definition = EXCLUDED.definition,
        synonyms = EXCLUDED.synonyms,
        release = EXCLUDED.release,
        deprecated = EXCLUDED.deprecated,
        label_normalized = EXCLUDED.label_normalized,
        synonyms_concat = EXCLUDED.synonyms_concat,
        updated_at = NOW();
    """
    def row_tuple(r: Dict):
        ln = _normalize_ascii_lower(r["label"])
        syn_concat = _concat_synonyms(r["synonyms"])
        return (
            r["hpo_id"], r["label"], r["definition"], json.dumps(r["synonyms"]),
            release, r["deprecated"],
            ln, syn_concat, None,  # search_tsv backfilled later
            dt.datetime.utcnow(), dt.datetime.utcnow()
        )

    from psycopg2.extras import execute_values
    with connection.cursor() as cur:
        buf: List[tuple] = []
        for r in term_rows:
            buf.append(row_tuple(r))
            if len(buf) >= batch:
                execute_values(cur, sql, buf, page_size=batch)
                buf = []
        if buf:
            execute_values(cur, sql, buf, page_size=batch)

def import_edges(edges: List[Tuple[str, str]], batch: int = 5000):
    """
    Bulk insert edges; ignore duplicates (unique_together on parent, child).
    """
    sql = """
    INSERT INTO hpo_hpoedge (parent_id, child_id)
    VALUES %s
    ON CONFLICT DO NOTHING;
    """
    from psycopg2.extras import execute_values
    with connection.cursor() as cur:
        buf = []
        for p, c in edges:
            buf.append((p, c))
            if len(buf) >= batch:
                execute_values(cur, sql, buf, page_size=batch)
                buf = []
        if buf:
            execute_values(cur, sql, buf, page_size=batch)

# ---------- Artifact records ----------

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def record_artifact(
    release: str,
    source_url: str,
    csv_path: Path,
    faiss_path: Optional[Path] = None,
    npz_path: Optional[Path] = None,
    embed_model: Optional[str] = None,
    active: bool = True,
) -> HPOArtifact:
    """
    Create (or update) an HPOArtifact row that points to CSV/FAISS/NPZ on disk.
    """
    csv_sha = sha256_file(csv_path)
    art, _ = HPOArtifact.objects.update_or_create(
        release=release,
        defaults=dict(
            source_url=source_url,
            csv_path=str(csv_path),
            faiss_path=str(faiss_path) if faiss_path else "",
            npz_path=str(npz_path) if npz_path else "",
            embed_model=embed_model or "",
            csv_sha256=csv_sha,
            active=active,
        ),
    )
    if active:
        # Deactivate others
        HPOArtifact.objects.exclude(id=art.id).update(active=False)
    return art

def get_active_artifact() -> Optional[HPOArtifact]:
    return HPOArtifact.objects.filter(active=True).order_by("-built_at").first()

# ---------- End-to-end convenience flows ----------

def refresh_from_obo(
    source_url: str = "https://purl.obolibrary.org/obo/hp.obo",
    release: Optional[str] = None,
    write_csv: bool = True,
    import_edges_flag: bool = True,
) -> Tuple[Path, List[Dict], List[Tuple[str, str]]]:
    """
    Download OBO, parse, optionally write CSV, upsert terms + edges, and backfill tsv.
    Returns (csv_path, terms, edges).
    """
    obo_path = download_obo(source_url)
    terms, edges = parse_obo_to_rows(obo_path)

    # Discover release version if not supplied (fallback to current date)
    release = release or dt.datetime.utcnow().date().isoformat()

    csv_path = data_dir() / f"hpo_texts_{release}.csv"
    if write_csv:
        write_hpo_csv(terms, csv_path)
    else:
        # Still produce a small CSV for provenance if caller expects a file path
        write_hpo_csv(terms, csv_path)

    with transaction.atomic():
        upsert_terms(terms, release=release)
        if import_edges_flag and edges:
            import_edges(edges)
        backfill_search_tsv()
        record_artifact(
            release=release,
            source_url=source_url,
            csv_path=csv_path,
            embed_model="",  # set when you build vectors
            active=True,
        )
    return csv_path, terms, edges

# ---------- Vector build (choose OpenAI or local ST) ----------

def build_vectors_from_csv(
    csv_path: Path,
    out_dir: Optional[Path] = None,
    provider: str = "openai",               # "openai" or "local"
    openai_api_key: Optional[str] = None,
    openai_base_url: str = "https://api.openai.com/v1",
    embed_model: str = "text-embedding-3-large",
    local_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch: int = 256,
) -> Tuple[Path, Path, str]:
    """
    Read CSV (hpo_id,label,definition,synonyms_json,deprecated), compute embeddings, write FAISS + NPZ.
    Returns (faiss_path, npz_path, embed_model_used).
    """
    out = out_dir or data_dir()
    out.mkdir(parents=True, exist_ok=True)
    faiss_path = out / "hpo_store.faiss"
    npz_path = out / "hpo_store.npz"

    ids: List[str] = []
    labels: List[str] = []
    texts: List[str] = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ids.append(row["hpo_id"])
            labels.append(row["label"])
            definition = row.get("definition", "") or ""
            syns = row.get("synonyms_json", "[]")
            try:
                syn_list = json.loads(syns)
            except Exception:
                syn_list = []
            text = " ".join([row["label"], _concat_synonyms(syn_list), definition]).strip()
            texts.append(text)

    if provider == "openai":
        client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"), base_url=openai_base_url)
        vecs: List[List[float]] = []
        for i in range(0, len(texts), batch):
            chunk = texts[i:i+batch]
            resp = client.embeddings.create(model=embed_model, input=chunk)
            vecs.extend([d.embedding for d in resp.data])
        X = np.asarray(vecs, dtype="float32")
        faiss.normalize_L2(X)
        index = faiss.IndexFlatIP(X.shape[1])
        index.add(X)

    else:  # local
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(local_model, device="cpu")
        V = model.encode(texts, normalize_embeddings=True, batch_size=batch)
        X = np.asarray(V, dtype="float32")
        index = faiss.IndexFlatIP(X.shape[1])
        index.add(X)
        embed_model = local_model  # record for artifact

    np.savez(npz_path, ids=np.array(ids, dtype=object), labels=np.array(labels, dtype=object), vecs=X)
    faiss.write_index(index, faiss_path)
    return faiss_path, npz_path, embed_model

def attach_vectors_to_release(release: str, faiss_path: Path, npz_path: Path, embed_model: str, set_active: bool = True):
    """
    Update/Create the HPOArtifact row for this release with the FAISS/NPZ pointers.
    """
    art = HPOArtifact.objects.filter(release=release).order_by("-built_at").first()
    if not art:
        # If terms were loaded by another path, create artifact row now
        art = HPOArtifact(release=release, source_url="", csv_path="", embed_model=embed_model, active=set_active)
    art.faiss_path = str(faiss_path)
    art.npz_path = str(npz_path)
    art.embed_model = embed_model
    if set_active:
        art.active = True
        HPOArtifact.objects.exclude(id=art.id).update(active=False)
    art.save()
    return art

# ---------- Sanity checks ----------

def verify_term_count(min_expected: int = 18000) -> int:
    """
    Quick guard to ensure the ontology loaded sensibly.
    """
    n = HPOTerm.objects.count()
    if n < min_expected:
        raise RuntimeError(f"Only {n} HPO terms found; expected >= {min_expected}.")
    return n

# ---------- Semantic search (FAISS inference) ----------

_FAISS_CACHE = None  # singleton cache to avoid reloading for every query


def _load_faiss_once() -> Tuple[faiss.Index, np.ndarray, np.ndarray, np.ndarray]:
    """
    Lazy-load FAISS + NPZ into memory.
    Returns: (index, ids, labels, vecs)
    """
    global _FAISS_CACHE
    if _FAISS_CACHE:
        return _FAISS_CACHE

    art = get_active_artifact()
    if not art or not art.faiss_path or not art.npz_path:
        raise RuntimeError("No active HPOArtifact with FAISS/NPZ found.")

    index = faiss.read_index(str(art.faiss_path))
    data = np.load(art.npz_path, allow_pickle=True)
    ids = data["ids"]
    labels = data["labels"]
    vecs = data["vecs"]
    _FAISS_CACHE = (index, ids, labels, vecs)
    return _FAISS_CACHE


def embed_texts(
    texts: List[str],
    openai_api_key: Optional[str] = None,
    openai_base_url: str = "https://api.openai.com/v1",
    embed_model: str = "text-embedding-3-large",
    batch_size: int = 128
) -> np.ndarray:
    """
    Compute embeddings for a list of texts using OpenAI model.
    Returns a 2D numpy array (n_texts x dim).
    """
    if not texts:
        return np.zeros((0,0), dtype="float32")
    
    client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"), base_url=openai_base_url)
    all_vectors: list[list[float]] =[]
    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i + batch_size]
        response = client.embeddings.create(model=embed_model, input=chunk)
        all_vectors.extend(d.embedding for d in response.data)
    return np.asarray(all_vectors, dtype="float32")


def search_hpo(
    query_text: list,
    k: int = 20,
    **embed_kwargs,
) -> List[dict]:
    """
    Perform a semantic search over the FAISS index.
    Returns: list of {rank, score, hpo_id, label}.

    Input:  phrases -> List[str]   length Q
    Output: List[List[dict]]       length Q, each inner list has k dicts
    """

    index, ids, labels, _ = _load_faiss_once()
    Q = len(query_text)
    query_vec = embed_texts(query_text, **embed_kwargs)
    faiss.normalize_L2(query_vec)
    scores, idxs = index.search(query_vec, k)
    results_per_query = []
    for qi in range(Q):
        row = []
        for rank, (score, idx) in enumerate(zip(scores[0], idxs[0]), start=1):
            row.append({
                "rank": rank,
                "score": float(score),
                "hpo_id": str(ids[idx]),
                "label": str(labels[idx]),
            })
        results_per_query.append(row)
    return results_per_query


def _coerce_json(txt: str) -> dict:
    s = txt.strip()
    if s.startswith("```"):
        s = _FENCE_RE.sub("", s).strip()
    return json.loads(s)


def extract_phrases(
    note: str,
    prompt: str, 
    openai_api_key: Optional[str] = None,
    openai_base_url: str = "https://api.openai.com/v1") -> list:
    """"""

    client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
    response = client.responses.create(
        model="gpt-4o-mini", 
        input=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": note},
        ],
    )
    response_text = getattr(response, "output_text", None)
    data = _coerce_json(response_text)
    return data


def best_match(
    phrase: str,
    candidates: List[Dict],
    prompt: str,
    *,
    sentence_context: Optional[str] = None,     # if your extractor provides it
    openai_api_key: Optional[str] = None,
    openai_base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    max_output_tokens: int = 128,
) -> Dict:
    """
    Ask the LLM to pick exactly one HPO ID from the provided candidate list.
    Returns: {'hpo_id','label','rank','score','source','rationale'}
             (falls back to cosine top-1 if anything goes wrong)
    """
    # 0) Guard: empty candidates → no-op
    if not candidates:
        return {"hpo_id": None, "label": None, "rank": None, "score": None,
                "source": "fallback-empty", "rationale": "No candidates provided."}

    # 1) Prepare payload
    cand_ids = {c["hpo_id"] for c in candidates}
    user_payload = {
        "phrase": phrase,
        "context": sentence_context or "",
        "candidates": candidates
    }

    # 2) Build client
    client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
                    base_url=openai_base_url)

    # 3) Call LLM (SDK 2.6.0: no response_format, ask for raw JSON explicitly)
    #    Keep the user content short: one compact JSON blob + an instruction line
    user_content = (
        "Given the JSON below, choose the single best HPO candidate.\n"
        "Return ONLY a JSON object like: {\"hpo_id\":\"HP:0000000\", \"reason\":\"...\"} (no markdown).\n\n"
        + json.dumps(user_payload, ensure_ascii=False)
    )

    try:
        resp = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": user_content},
            ],
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        text = getattr(resp, "output_text", None) or resp.output[0].content[0].text
        parsed = _coerce_json(text)  # {'hpo_id': 'HP:...', 'reason': '...'}
        hpo_id = (parsed.get("hpo_id") or "").strip()

        # 4) Validate chosen ID is in the candidate set
        if hpo_id in cand_ids:
            # find matching candidate to bring back rank/score/label
            chosen = next(c for c in candidates if c["hpo_id"] == hpo_id)
            return {
                "hpo_id": hpo_id,
                "label": chosen["label"],
                "rank": chosen["rank"],
                "score": chosen["score"],
                "source": "llm-select",
                "rationale": parsed.get("reason", ""),
            }

        # 5) If the model returned an unknown ID, fall back to cosine top-1
        top = candidates[0]
        return {
            "hpo_id": top["hpo_id"],
            "label": top["label"],
            "rank": top["rank"],
            "score": float(top["score"]),
            "source": "fallback-top1",
            "rationale": f"Model returned unknown id ({hpo_id}); fell back to cosine top-1.",
        }

    except Exception as e:
        # 6) Robust fallback on any error
        top = candidates[0]
        return {
            "hpo_id": top["hpo_id"],
            "label": top["label"],
            "rank": top["rank"],
            "score": float(top["score"]),
            "source": f"fallback-error:{type(e).__name__}",
            "rationale": str(e),
        }


def phenotype_extraction(note: str) -> list:
    """"""

    prompts = load_prompts()
    sys_I = prompts['system_message_I']
    sys_II = prompts['system_message_II']
    sys_dc = prompts['system_message_double_check']

    phrases = extract_phrases(note, sys_I)
    if isinstance(phrases, dict): 
        phrases = phrases.get("phenotypes",[])

    evaluated_phrases = extract_phrases(str(phrases), sys_dc)
    validated_phrases = []
    for index, phrase in enumerate(evaluated_phrases):
        if phrase['verdict'] == "keep":
            validated_phrases.append(phrases[index]|phrase)

    hpo_candidates = search_hpo([p["phrase"] for p in validated_phrases])
    
    for index, candidate in enumerate(hpo_candidates):
        phrases[index].update(
            best_match(
                phrase=phrases[index]["phrase"],
                candidates=candidate,
                prompt=sys_II
            )
        )   

    return phrases
