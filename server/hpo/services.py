#!/usr/bin/env python
# hpo/services.py

"""
RAG-HPO services
================

What this module does
---------------------
1) Ingest HPO
   - download hp.obo (or use an existing CSV)
   - parse terms + synonyms + definitions + is_a edges
   - upsert into Postgres (HPOTerm / HPOEdge)
   - materialize helpers:
     * label_normalized (ASCII, lowercased)
     * synonyms_concat (semicolon-joined)
     * search_tsv (tsvector over label + synonyms_concat + definition)
   - record an HPOArtifact row (paths & metadata)

2) Build vectors (optional but recommended)
   - read the CSV (label + synonyms + definition)
   - build text per term: "<label>  <synonyms…>  <definition>"
   - compute embeddings (OpenAI or local ST), L2-normalize
   - write FAISS index + NPZ (ids/labels/vecs)
   - attach to the active HPOArtifact

3) Runtime search & mapping
   - autocomplete/search endpoints use Postgres trigram + full-text over
     label, synonyms, and definition (no LLM, very fast)
   - semantic retrieval (FAISS) returns top-k HPO candidates per phrase
   - LLM selector chooses exactly one HPO ID from each candidate list
     (batch prompts; strict JSON out; null allowed)

Key functions
-------------
refresh_from_obo(...)                 # end-to-end: download → parse → import → index → artifact
build_vectors_from_csv(...)           # compute embeddings & write FAISS/NPZ
attach_vectors_to_release(...)        # attach FAISS/NPZ to an HPO release (and mark active)
search_hpo_batch([...], k=20, ...)    # FAISS retrieval for many phrases at once
phenotype_extraction(note)            # extract → validate → retrieve → LLM select (returns structured result)

Synonyms handling
-----------------
- Parsed from OBO 'synonym' stanzas (quoted text extracted).
- Stored as JSON array in HPOTerm.synonyms (use psycopg2.extras.Json on upsert).
- Flattened into synonyms_concat for trigram/FTS.
- Included in embedding text so FAISS captures synonymy.

Operational notes
-----------------
- Requires Postgres extensions: 'pg_trgm' + 'fuzzystrmatch' (enabled via migrations).
- GIN/trigram indexes must exist (see models.py).
- The active HPOArtifact determines which FAISS/NPZ gets loaded at runtime.
- OPENAI_API_KEY read from environment when provider='openai'.

"""

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
from rest_framework import serializers
from typing import Iterable, List, Optional, Tuple, Dict
from psycopg2.extras import Json, execute_values
from hpo.models import HPOTerm, HPOEdge, HPOArtifact

# ---------- Serializers ----------
class HPOTermLiteSerializer(serializers.Serializer):
    hpo_id     = serializers.CharField()
    label      = serializers.CharField()
    snippet    = serializers.CharField()   # short text (label/syn/def mashup)
    deprecated = serializers.BooleanField()
    score      = serializers.FloatField()

class PhenotypeExtractRequestSerializer(serializers.Serializer):
    raw_text = serializers.CharField(
        help_text="Text to decode for HPO terms",
        default="gait instability with ataxia and seizures since childhood."
    )

class PhenotypeChoiceSerializer(serializers.Serializer):
    id     = serializers.CharField()
    hpo_id = serializers.CharField(allow_null=True)
    label  = serializers.CharField(allow_null=True, required=False)
    rank   = serializers.IntegerField(allow_null=True, required=False)
    score  = serializers.FloatField(allow_null=True, required=False)
    source = serializers.CharField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True)

class PhenotypePhraseSerializer(serializers.Serializer):
    id         = serializers.CharField()
    phrase     = serializers.CharField()
    sentence   = serializers.CharField(required=False, allow_blank=True)
    verdict    = serializers.CharField(required=False, allow_blank=True)
    reason     = serializers.CharField(required=False, allow_blank=True)
    candidates = serializers.ListField(child=serializers.DictField(), required=False)
    choice     = PhenotypeChoiceSerializer(required=False)

class PhenotypeExtractResponseSerializer(serializers.Serializer):
    phrases = PhenotypePhraseSerializer(many=True)
    matches = PhenotypeChoiceSerializer(many=True, required=False)
    meta    = serializers.DictField()

class HPOLookupIDSerializer(serializers.Serializer):
    hpo_id     = serializers.CharField()
    label      = serializers.CharField(allow_null=True, required=False)
    definition = serializers.CharField(allow_null=True, required=False)
    synonyms   = serializers.ListField(child=serializers.CharField(), required=False)
    release    = serializers.CharField(allow_null=True, required=False)
    deprecated = serializers.BooleanField(required=False)
    error      = serializers.CharField(required=False)  # present only if not found

class HPOLookupIDResponseSerializer(serializers.Serializer):
    results = HPOLookupIDSerializer(many=True)

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
            r["hpo_id"],
            r["label"],
            r["definition"],
            Json(r["synonyms"]),   # <— instead of json.dumps(...)
            release,
            r["deprecated"],
            ln,
            syn_concat,
            None,                  # search_tsv backfilled later
            dt.datetime.utcnow(),
            dt.datetime.utcnow(),
        )

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

    # 1) Load FAISS + metadata
    index, ids, labels, _ = _load_faiss_once()
    
    # 2) Embed all phrases at once => (Q, D)
    Q = len(query_text)
    query_vec = embed_texts(query_text, **embed_kwargs)
    faiss.normalize_L2(query_vec)

    # 3) Search all queries in one call
    scores, idxs = index.search(query_vec, k)
    
    # 4) Build a per-query result list
    results_per_query = []
    for qi in range(Q):
        row = []
        for rank, (score, idx) in enumerate(zip(scores[qi], idxs[qi]), start=1):
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


def _mk_items_with_ids(extracted: List[Dict]) -> List[Dict]:
    """Normalize extracted list -> [{'id','phrase','sentence'}...]"""
    items = []
    for i, it in enumerate(extracted):
        phrase = (it.get("phrase") or "").strip()
        if not phrase:
            continue
        items.append({
            "id": f"p{i}",
            "phrase": phrase,
            "sentence": (it.get("sentence") or "").strip()
        })
    return items


def extract_phrases(
    note: str,
    prompt: str, 
    openai_api_key: Optional[str] = None,
    openai_base_url: str = "https://api.openai.com/v1"
) -> list:
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


def _slim_candidates(cands: List[Dict], topn: int = 10) -> List[Dict]:
    """Trim and shorten keys for token efficiency."""
    out = []
    for c in cands[:topn]:
        out.append({
            "id": c["hpo_id"],
            "l":  c["label"],
            "s":  round(float(c["score"]), 3),
            "r":  int(c["rank"]),
            # optionally include a one-sentence definition: "d": c.get("definition","")[:180]
        })
    return out


def best_match(
    validated_phrases: List[Dict],
    prompt: str,
    *,
    openai_api_key: Optional[str] = None,
    openai_base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    max_output_tokens: int = 512,
    chunk_size: int = 24,          # #items per request (keep small for latency)
    topn_for_llm: int = 10,        # send fewer than FAISS k to save tokens
    accept_null: bool = True,      # allow {"hpo_id": null} rather than forcing fallback
) -> Dict:
    """
    Ask the LLM to pick exactly one HPO ID from the provided candidate list.
    
    validated_phrases: 
        [{id, phrase, candidates:[{hpo_id,label,rank,score,...}], sentence?}, ...]
    returns: 
        [{id, hpo_id, source, reason, label, rank, score}, ...]
    
    (falls back to cosine top-1 if anything goes wrong)
    """
    # 0) Guard: empty candidates → no-op
    if not validated_phrases:
        return []

    # 1) Build client and initialize results
    results: List[Dict] = []
    client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
                    base_url=openai_base_url)
    
    
    # 2) Prepare payload
    for start in range(0, len(validated_phrases), chunk_size):
        batch = validated_phrases[start:start+chunk_size]
        # Build compact payload + per-item id→candidate-set for validation
        id_to_candset: Dict[str, set] = {}
        id_to_fullcands: Dict[str, List[Dict]] = {}
        payload_items = []

        for it in batch:
            pid   = it["id"]
            phrase = it["phrase"]
            slim  = _slim_candidates(it["candidates"], topn=topn_for_llm)
            id_to_candset[pid] = {c["id"] for c in slim}
            id_to_fullcands[pid] = it["candidates"]  # full list (with rank/score/label)

            payload_items.append({
                "id": pid,
                "p": phrase,
                "ctx": it.get("sentence", "") or "",
                "cands": slim,
            })

        # System-only rules; user is pure JSON
        # keep system text SHORT for speed
        sys_msg = (
            "You map phenotype phrases to HPO IDs.\n"
            "For each object in 'items', choose exactly one HPO from its 'cands' list.\n\n"
            "Input JSON shape:\n"
            '{"items":[{"id":"p0","p":"<phrase>","ctx":"<optional context>",'
            '"cands":[{"id":"HP:#######","l":"<label>","s":0.000,"r":1}, ...]}]}\n\n'
            "Return ONLY JSON (no markdown):\n"
            '[{"id":"p0","hpo_id":"HP:#######" | null, "reason":"<short rationale>"}]\n\n'
            "Rules:\n"
            "- Choose only from the provided candidate IDs.\n"
            "- Use context (ctx) for nuance if available.\n"
            "- If none fits clearly, set hpo_id to null.\n"
            "- Be concise and consistent.\n"
        )

        system_text = prompt or sys_msg

        user_json = {"items": payload_items}

        resp = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_text},
                {"role": "user",   "content": json.dumps(user_json, ensure_ascii=False)},
            ],
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        text = getattr(resp, "output_text", None) or resp.output[0].content[0].text
        arr = _coerce_json(text)

        # Some models may wrap the array in an object {items:[...]}
        if isinstance(arr, dict):
            arr = arr.get("items") or arr.get("results") or []

        # Build per-item choice with validation + optional fallback
        for row in arr or []:
            pid   = row.get("id")
            hpo_id = (row.get("hpo_id") or None)
            reason = (row.get("reason") or "")

            if pid not in id_to_candset:
                continue  # unknown id, skip

            candset = id_to_candset[pid]
            fullcands = id_to_fullcands[pid]

            if hpo_id is None and accept_null:
                results.append({
                    "id": pid, "hpo_id": None, "label": None, "rank": None, "score": None,
                    "source": "llm-null", "reason": reason
                })
                continue

            if hpo_id in candset:
                chosen = next(c for c in fullcands if c["hpo_id"] == hpo_id)
                results.append({
                    "id": pid,
                    "hpo_id": hpo_id,
                    "label": chosen["label"],
                    "rank": chosen["rank"],
                    "score": float(chosen["score"]),
                    "source": "llm-select",
                    "reason": reason,
                })
            else:
                # fallback policy
                top = fullcands[0]
                results.append({
                    "id": pid,
                    "hpo_id": top["hpo_id"],
                    "label": top["label"],
                    "rank": top["rank"],
                    "score": float(top["score"]),
                    "source": "fallback-top1" if not accept_null else "fallback-unknown-id",
                    "reason": f"Unknown id {hpo_id!r}; used top-1." if hpo_id else reason,
                })

        # Also handle any items missing from arr at all (defensive)
        present = {r["id"] for r in results[-len(batch):]}
        for it in batch:
            if it["id"] in present:
                continue
            # No response for this id; choose policy:
            if accept_null:
                results.append({
                    "id": it["id"], "hpo_id": None, "label": None, "rank": None, "score": None,
                    "source": "llm-missing", "reason": "No entry returned for this id."
                })
            else:
                top = it["candidates"][0]
                results.append({
                    "id": it["id"],
                    "hpo_id": top["hpo_id"], "label": top["label"],
                    "rank": top["rank"], "score": float(top["score"]),
                    "source": "fallback-missing", "reason": "No entry; used top-1."
                })

    # Keep original order if helpful: sort by numeric suffix of 'p#'
    try:
        results.sort(key=lambda r: int(str(r["id"]).lstrip("p")))
    except Exception:
        pass
    return results


def validate_phrases_bulk(
    extracted: List[Dict],
    system_message_double_check: str,
    *,
    openai_api_key: Optional[str] = None,
    openai_base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    max_output_tokens: int = 512,
    chunk_size: int = 50,   # safety for very long lists
) -> Dict[str, Dict]:
    """
    Input  : extracted -> [{'phrase':..., 'sentence':...}, ...]  (or your extractor’s dicts)
    Output : verdict_map -> { id: {'id':..,'verdict':'keep|drop','reason':'...'}, ... }
    """
    client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
                    base_url=openai_base_url)

    items = _mk_items_with_ids(extracted)  # [{'id','phrase','sentence'}...]
    verdict_map: Dict[str, Dict] = {}

    for start in range(0, len(items), chunk_size):
        chunk = items[start:start+chunk_size]

        # Keep user content compact to save tokens
        user_payload = {
            "items": chunk,
            "rules": "Return only a JSON array of {id, verdict, reason}. No markdown."
        }

        resp = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_message_double_check},
                {"role": "user",   "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        text = getattr(resp, "output_text", None) or resp.output[0].content[0].text
        arr = _coerce_json(text)  # expect a JSON array
        if isinstance(arr, dict):  # if model returns object, try to unwrap a common pattern
            arr = arr.get("items") or arr.get("results") or []

        for row in arr or []:
            rid = row.get("id")
            if not rid:
                continue
            verdict = (row.get("verdict") or "").strip().lower()
            reason  = (row.get("reason")  or "").strip()
            if verdict not in {"keep", "drop"}:
                # default to 'keep' if uncertain; adjust policy as you like
                verdict = "keep"
            verdict_map[rid] = {"id": rid, "verdict": verdict, "reason": reason}

    return verdict_map


def phenotype_extraction(note: str) -> list:
    """
    extract -> bulk validate -> batch retrieve candidates
    returns a structured dict to the API
    """

    prompts = load_prompts()
    sys_I = prompts['system_message_I']
    sys_II = prompts['system_message_II']
    sys_dc = prompts['system_message_double_check']

    # 1) extract => list[dict]
    phrases = extract_phrases(note, sys_I)
    if isinstance(phrases, dict): 
        phrases = phrases.get("phenotypes",[])
    
    # ensure each item has a stable ID for mapping, same order as 
    for index, phrase in enumerate(phrases):
        phrase["id"] = f"p{index}"
    
    # 2) bulk validate
    verdicts = validate_phrases_bulk(phrases, sys_dc)
    # phrases = [
    #     {'phrase': 'residual left-sided hemiplegia', 'category': 'Abnormal', 'id': 'p0'}, 
    #     {'phrase': 'right ear pain', 'category': 'Abnormal', 'id': 'p1'}, 
    #     {'phrase': 'purulent discharge', 'category': 'Abnormal', 'id': 'p2'}, 
    #     {'phrase': 'bilateral decrease in hearing', 'category': 'Abnormal', 'id': 'p3'}, 
    #     {'phrase': 'right ear soft granular tissue mass', 'category': 'Abnormal', 'id': 'p4'}, 
    #     {'phrase': 'bleeding on touch', 'category': 'Abnormal', 'id': 'p5'}, 
    #     {'phrase': 'otalgia', 'category': 'Abnormal', 'id': 'p6'}, 
    #     {'phrase': 'oedematous canal', 'category': 'Abnormal', 'id': 'p7'}, 
    #     {'phrase': 'non-visible tympanic membrane', 'category': 'Abnormal', 'id': 'p8'}
    # ]
    # verdicts = {
    #     'p0': {'id': 'p0', 'verdict': 'keep', 'reason': 'describes an abnormal physical sign (hemiplegia)'}, 
    #     'p1': {'id': 'p1', 'verdict': 'keep', 'reason': 'describes an abnormal symptom (ear pain)'},
    #     'p2': {'id': 'p2', 'verdict': 'keep', 'reason': 'describes an abnormal finding (purulent discharge)'},
    #     'p3': {'id': 'p3', 'verdict': 'keep', 'reason': 'describes an abnormal finding (decrease in hearing)'},
    #     'p4': {'id': 'p4', 'verdict': 'keep', 'reason': 'describes an abnormal finding (soft granular tissue mass)'},
    #     'p5': {'id': 'p5', 'verdict': 'keep', 'reason': 'describes an abnormal finding (bleeding on touch)'},
    #     'p6': {'id': 'p6', 'verdict': 'keep', 'reason': 'describes an abnormal symptom (otalgia)'},
    #     'p7': {'id': 'p7', 'verdict': 'keep', 'reason': 'describes an abnormal finding (oedematous canal)'},
    #     'p8': {'id': 'p8', 'verdict': 'keep', 'reason': 'describes an abnormal finding (non-visible tympanic membrane)'}
    # }
    
    # 3) Build validated list with no deleting
    validated_phrases: List[Dict] = []
    for phrase in phrases:
        verdict = verdicts.get(phrase["id"])
        if not verdict:
            continue
        if verdict['verdict'] == "keep":
            validated_phrases.append(phrase | verdict)
    
    if not validated_phrases:
        return {"phrases": [], "candidates": [], "meta": {"k": 20, "count": 0}}

    # 4) Batch retrieval (or top-l per phrase)
    hpo_candidates = search_hpo([p["phrase"] for p in validated_phrases])
    for phrase, candidate in zip(validated_phrases, hpo_candidates):
        phrase["candidates"] = candidate
    
    choices = best_match(
        validated_phrases=validated_phrases,
        prompt=None,
        topn_for_llm=10,
        accept_null=True
    )
    # attach back by id
    choice_by_id = {c["id"]: c for c in choices}
    for it in validated_phrases:
        it["choice"] = choice_by_id.get(it["id"])

    return validated_phrases
