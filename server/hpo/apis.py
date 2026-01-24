#!/usr/bin/env python
# hpo/apis.py

import json
import time
from django.db.models import F, Q, Value, Case, When, FloatField
from django.db.models.functions import Greatest, Coalesce
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.contrib.postgres.search import TrigramSimilarity
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from hpo.models import HPOTerm
from hpo.selectors import get_hpo_term_by_id
from hpo.services import (
    phenotype_extraction,
    PhenotypeExtractRequestSerializer,
    PhenotypeExtractResponseSerializer,
    refresh_from_obo,
    build_vectors_from_csv,
    attach_vectors_to_release,
)


class HPOLookupIDView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="reverse_lookup",
        tags=["HPO"],
        manual_parameters=[
            openapi.Parameter(
                "hpo_ids",
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    description="HPO term ID (e.g. HP:0001251)",
                    default="HP:0001251",
                    type=openapi.TYPE_STRING
                )
            )
        ],
        responses={200: "Term found", 404: "Not found"},
    )
    def get(self, request):
        hpo_ids = request.GET.get("hpo_ids").split(',')
        if not hpo_ids:
            return Response({"error": "Missing hpo_id parameter"}, status=400)

        data = get_hpo_term_by_id(hpo_ids)
        if "error" in data:
            return Response(data, status=404)
        return Response(data, status=200)


class HPOAutocompleteView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="hpo_autocomplete",
        tags=["HPO"],
        manual_parameters=[
            openapi.Parameter("q", openapi.IN_QUERY, description="Query prefix or substring", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("limit", openapi.IN_QUERY, description="Max results (<=50)", type=openapi.TYPE_INTEGER, default=10),
            openapi.Parameter("include_deprecated", openapi.IN_QUERY, description="Include deprecated terms (0/1)", type=openapi.TYPE_STRING, enum=["0","1"], default="0"),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "query": openapi.Schema(type=openapi.TYPE_STRING),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(          # <— use Schema here, not Items
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "hpo_id":     openapi.Schema(type=openapi.TYPE_STRING),
                                "label":      openapi.Schema(type=openapi.TYPE_STRING),
                                "snippet":    openapi.Schema(type=openapi.TYPE_STRING),
                                "deprecated": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "score":      openapi.Schema(type=openapi.TYPE_NUMBER, format="float"),
                            },
                            required=["hpo_id", "label"]
                        ),
                    ),
                },
                required=["query", "results"]
            )
        }
    )

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        if not q:
            return Response({"query": q, "results": []})
        limit = min(int(request.GET.get("limit", 10)), 50)
        include_deprecated = request.GET.get("include_deprecated") == "1"

        q_norm = q.lower()

        qs = HPOTerm.objects.all()
        if not include_deprecated:
            qs = qs.filter(deprecated=False)

        # Row-level prefix flag (1.0 only when the normalized label starts with the query)
        prefix_expr = Case(
            When(label_normalized__startswith=q_norm, then=Value(1.0)),
            default=Value(0.0),
            output_field=FloatField(),
        )

        # Trigram similarity on normalized label
        qs = qs.annotate(
            trig=TrigramSimilarity("label_normalized", q_norm),
            prefix=prefix_expr,
        ).annotate(
            # Final score favors prefix hits, then trigram
            score=Greatest(F("prefix"), F("trig"))
        )

        # Filters:
        # - For short queries (<=2), require a prefix match to reduce noise
        # - Otherwise, allow either prefix match or a reasonable trigram floor
        short = len(q_norm) <= 2
        if short:
            qs = qs.filter(label_normalized__startswith=q_norm)
        else:
            qs = qs.filter(
                Q(label_normalized__startswith=q_norm) |
                Q(trig__gt=0.25) |                      # tighten similarity floor
                Q(synonyms_concat__icontains=q_norm)    # catch simple synonym hits
            )

        # Order: prefix first, then trigram, then label for stability
        qs = qs.order_by(F("prefix").desc(), F("trig").desc(), "label")[:limit]

        rows = [
            {
                "hpo_id": t.hpo_id,
                "label": t.label,
                "snippet": t.label,   # swap to a richer snippet if you want
                "deprecated": t.deprecated,
                "score": float(getattr(t, "score", 0.0)),
            }
            for t in qs
        ]
        return Response({"query": q, "results": rows})


class HPOSearchView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="hpo_search",
        tags=["HPO"],
        manual_parameters=[
            openapi.Parameter("q", openapi.IN_QUERY, description="Free-text query", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("limit", openapi.IN_QUERY, description="Max results (<=100)", type=openapi.TYPE_INTEGER, default=20),
            openapi.Parameter("include_deprecated", openapi.IN_QUERY, description="Include deprecated terms (0/1)", type=openapi.TYPE_STRING, enum=["0","1"], default="0"),
            openapi.Parameter("semantic", openapi.IN_QUERY, description="Use FAISS semantic fallback (0/1)", type=openapi.TYPE_STRING, enum=["0","1"], default="0"),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "query": openapi.Schema(type=openapi.TYPE_STRING),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(          # <— use Schema here, not Items
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "hpo_id":     openapi.Schema(type=openapi.TYPE_STRING),
                                "label":      openapi.Schema(type=openapi.TYPE_STRING),
                                "snippet":    openapi.Schema(type=openapi.TYPE_STRING),
                                "deprecated": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "score":      openapi.Schema(type=openapi.TYPE_NUMBER, format="float"),
                                "source":     openapi.Schema(type=openapi.TYPE_STRING),
                            },
                            required=["hpo_id", "label"]
                        ),
                    ),
                },
                required=["query", "results"]
            )
        }
    )

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        if not q:
            return Response({"query": q, "results": []})

        limit = min(int(request.GET.get("limit", 20)), 100)
        include_deprecated = request.GET.get("include_deprecated") == "1"
        use_semantic = request.GET.get("semantic") == "1"

        base = HPOTerm.objects.all()
        if not include_deprecated:
            base = base.filter(deprecated=False)

        vector = (
            SearchVector("label", weight="A") +
            SearchVector("synonyms_concat", weight="B") +
            SearchVector("definition", weight="C")
        )
        query = SearchQuery(q, search_type="plain")

        qs = (
            base
            .annotate(rank=SearchRank(vector, query))
            .annotate(trig=TrigramSimilarity("label_normalized", q.lower()))
            .annotate(score=Greatest(Coalesce(F("rank"), Value(0.0)), Coalesce(F("trig"), Value(0.0))))
            .filter(Q(rank__gt=0.0) | Q(trig__gt=0.15))
            .order_by("-score", "label")[:limit]
        )

        results = [
            {
                "hpo_id": t.hpo_id,
                "label": t.label,
                "snippet": t.label,
                "deprecated": t.deprecated,
                "score": float(getattr(t, "score", 0.0)),
                "source": "text",
            }
            for t in qs
        ]

        # Semantic fallback via FAISS
        if use_semantic and len(results) < limit:
            try:
                k = max(limit, 20)
                sem_lists = search_hpo_batch([q], k=k)
                sem = sem_lists[0] if sem_lists else []
                if not include_deprecated:
                    # quick filter (DB hit per candidate; optimize if needed)
                    sem = [c for c in sem if not HPOTerm.objects.filter(hpo_id=c["hpo_id"], deprecated=True).exists()]
                seen = {r["hpo_id"] for r in results}
                for c in sem:
                    if c["hpo_id"] in seen:
                        continue
                    results.append({
                        "hpo_id": c["hpo_id"],
                        "label": c["label"],
                        "snippet": c["label"],
                        "deprecated": False,
                        "score": float(c["score"]),
                        "source": "semantic",
                    })
                    seen.add(c["hpo_id"])
                    if len(results) >= limit:
                        break
                results.sort(key=lambda r: r["score"], reverse=True)
            except Exception:
                pass

        return Response({"query": q, "results": results[:limit]})


class HPOExtractPhenotypesView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="extract_phenotypes",
        tags=["HPO"],
        request_body=PhenotypeExtractRequestSerializer,
        responses={
            200: PhenotypeExtractResponseSerializer,
            400: "Bad request",
        },
    )
    def post(self, request):
        ser = PhenotypeExtractRequestSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        userText = ser.validated_data["userText"]
        # print("sleeping")
        # time.sleep(10)
        # print("wake up")
        try:
            result = phenotype_extraction(userText)   # returns dict with phrases / matches / meta
            # return Response(TEST_RETURN, status=200)
            return Response(result, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class HPOSetupArtifacts(APIView):
    permission_class = [AllowAny]

    @swagger_auto_schema(
        operation_id="setup_artifacts",
        tags=["HPO"],
        request_body="",
        responses={
            200: "Artifacts set up",
            400: "Error setting up artifacts"
        },
    )
    def post(self, request):
        try:
            release, csv_path = refresh_from_obo()
            faiss_path, npz_path, embed_model = build_vectors_from_csv(csv_path)
            art = attach_vectors_to_release(release, faiss_path, npz_path, embed_model, True)
            return Response({"Release": release}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


TEST_RETURN = [
  {
    "phrase": "severe pain and discharge from his left eye",
    "category": "Abnormal",
    "id": "p0",
    "verdict": "keep",
    "reason": "Describes severe pain and discharge, indicating an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.5353209376335144,
        "hpo_id": "HP:0034427",
        "label": "Purulent eye discharge"
      },
      {
        "rank": 2,
        "score": 0.4816495478153229,
        "hpo_id": "HP:0200026",
        "label": "Ocular pain"
      },
      {
        "rank": 3,
        "score": 0.4653787314891815,
        "hpo_id": "HP:0034808",
        "label": "Eyelid pain"
      },
      {
        "rank": 4,
        "score": 0.4604657292366028,
        "hpo_id": "HP:0030857",
        "label": "Eye movement-induced pain"
      },
      {
        "rank": 5,
        "score": 0.425251305103302,
        "hpo_id": "HP:0011885",
        "label": "Hemorrhage of the eye"
      },
      {
        "rank": 6,
        "score": 0.41673654317855835,
        "hpo_id": "HP:6000420",
        "label": "Burning eye sensation"
      },
      {
        "rank": 7,
        "score": 0.40803125500679016,
        "hpo_id": "HP:0100533",
        "label": "Inflammatory abnormality of the eye"
      },
      {
        "rank": 8,
        "score": 0.4046233892440796,
        "hpo_id": "HP:0010607",
        "label": "Hordeolum externum"
      },
      {
        "rank": 9,
        "score": 0.3949189782142639,
        "hpo_id": "HP:0032776",
        "label": "Focal aware autonomic seizure with lacrimation"
      },
      {
        "rank": 10,
        "score": 0.39458543062210083,
        "hpo_id": "HP:0031881",
        "label": "Decreased tear drainage"
      },
      {
        "rank": 11,
        "score": 0.39413294196128845,
        "hpo_id": "HP:0007717",
        "label": "Chronic irritative conjunctivitis"
      },
      {
        "rank": 12,
        "score": 0.39333993196487427,
        "hpo_id": "HP:0034803",
        "label": "Hemolacria"
      },
      {
        "rank": 13,
        "score": 0.3927156925201416,
        "hpo_id": "HP:0000557",
        "label": "Buphthalmos"
      },
      {
        "rank": 14,
        "score": 0.38941073417663574,
        "hpo_id": "HP:0009926",
        "label": "Epiphora"
      },
      {
        "rank": 15,
        "score": 0.38371556997299194,
        "hpo_id": "HP:0000559",
        "label": "Corneal scarring"
      },
      {
        "rank": 16,
        "score": 0.38336867094039917,
        "hpo_id": "HP:0031621",
        "label": "Anterior chamber flare grade 4+"
      },
      {
        "rank": 17,
        "score": 0.3831248879432678,
        "hpo_id": "HP:6000058",
        "label": "Exacerbation of eyelid lesion by crying"
      },
      {
        "rank": 18,
        "score": 0.3828388452529907,
        "hpo_id": "HP:0031615",
        "label": "Hypopyon"
      },
      {
        "rank": 19,
        "score": 0.37941935658454895,
        "hpo_id": "HP:0010606",
        "label": "Hordeolum"
      },
      {
        "rank": 20,
        "score": 0.3792000412940979,
        "hpo_id": "HP:0012375",
        "label": "Chemosis"
      }
    ],
    "choice": {
      "id": "p0",
      "hpo_id": "HP:0034427",
      "label": "Purulent eye discharge",
      "rank": 1,
      "score": 0.5353209376335144,
      "source": "llm-select",
      "reason": "Severe pain and discharge from the eye aligns with purulent eye discharge."
    }
  },
  {
    "phrase": "progressively increasing hard swelling in his left lower lid",
    "category": "Abnormal",
    "id": "p1",
    "verdict": "keep",
    "reason": "Describes progressively increasing hard swelling, indicating an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.5209861993789673,
        "hpo_id": "HP:0012568",
        "label": "Lower eyelid edema"
      },
      {
        "rank": 2,
        "score": 0.5084909200668335,
        "hpo_id": "HP:0012724",
        "label": "Upper eyelid edema"
      },
      {
        "rank": 3,
        "score": 0.5043079257011414,
        "hpo_id": "HP:0007838",
        "label": "Progressive ptosis"
      },
      {
        "rank": 4,
        "score": 0.49588948488235474,
        "hpo_id": "HP:6000058",
        "label": "Exacerbation of eyelid lesion by crying"
      },
      {
        "rank": 5,
        "score": 0.4937295913696289,
        "hpo_id": "HP:0010732",
        "label": "Nodular changes affecting the eyelids"
      },
      {
        "rank": 6,
        "score": 0.4855293035507202,
        "hpo_id": "HP:0007655",
        "label": "Eversion of lateral third of lower eyelids"
      },
      {
        "rank": 7,
        "score": 0.482362300157547,
        "hpo_id": "HP:0030939",
        "label": "Palpebral thickening"
      },
      {
        "rank": 8,
        "score": 0.4785095751285553,
        "hpo_id": "HP:0040151",
        "label": "Epiblepharon of lower lid"
      },
      {
        "rank": 9,
        "score": 0.47366267442703247,
        "hpo_id": "HP:0100540",
        "label": "Palpebral edema"
      },
      {
        "rank": 10,
        "score": 0.4734167754650116,
        "hpo_id": "HP:6000059",
        "label": "Localized to upper eyelid"
      },
      {
        "rank": 11,
        "score": 0.4705628454685211,
        "hpo_id": "HP:6000840",
        "label": "Localized soft-tissue swelling on extremity"
      },
      {
        "rank": 12,
        "score": 0.46438297629356384,
        "hpo_id": "HP:6001266",
        "label": "Localized to eyelid"
      },
      {
        "rank": 13,
        "score": 0.46386635303497314,
        "hpo_id": "HP:6001265",
        "label": "Localized to the lower eyelid"
      },
      {
        "rank": 14,
        "score": 0.462835431098938,
        "hpo_id": "HP:0010605",
        "label": "Chalazion"
      },
      {
        "rank": 15,
        "score": 0.4598076641559601,
        "hpo_id": "HP:0000629",
        "label": "Periorbital fullness"
      },
      {
        "rank": 16,
        "score": 0.4538257122039795,
        "hpo_id": "HP:0500091",
        "label": "Lymphangioma of the orbit"
      },
      {
        "rank": 17,
        "score": 0.4430523216724396,
        "hpo_id": "HP:0010749",
        "label": "Blepharochalasis"
      },
      {
        "rank": 18,
        "score": 0.43843573331832886,
        "hpo_id": "HP:0010604",
        "label": "Cyst of the eyelid"
      },
      {
        "rank": 19,
        "score": 0.43569672107696533,
        "hpo_id": "HP:0040150",
        "label": "Epiblepharon of upper lid"
      },
      {
        "rank": 20,
        "score": 0.4350321590900421,
        "hpo_id": "HP:0030793",
        "label": "Jaw swelling"
      }
    ],
    "choice": {
      "id": "p1",
      "hpo_id": "HP:0012568",
      "label": "Lower eyelid edema",
      "rank": 1,
      "score": 0.5209861993789673,
      "source": "llm-select",
      "reason": "Progressively increasing hard swelling in the lower lid corresponds to lower eyelid edema."
    }
  },
  {
    "phrase": "proptosis",
    "category": "Abnormal",
    "id": "p2",
    "verdict": "keep",
    "reason": "Proptosis is an abnormal physical sign.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.7044878005981445,
        "hpo_id": "HP:0000520",
        "label": "Proptosis"
      },
      {
        "rank": 2,
        "score": 0.4794730246067047,
        "hpo_id": "HP:0007655",
        "label": "Eversion of lateral third of lower eyelids"
      },
      {
        "rank": 3,
        "score": 0.473020076751709,
        "hpo_id": "HP:0000497",
        "label": "Globe retraction and deviation on abduction"
      },
      {
        "rank": 4,
        "score": 0.46512866020202637,
        "hpo_id": "HP:0000577",
        "label": "Exotropia"
      },
      {
        "rank": 5,
        "score": 0.4543362557888031,
        "hpo_id": "HP:0000508",
        "label": "Ptosis"
      },
      {
        "rank": 6,
        "score": 0.45411285758018494,
        "hpo_id": "HP:0007650",
        "label": "Progressive ophthalmoplegia"
      },
      {
        "rank": 7,
        "score": 0.44668400287628174,
        "hpo_id": "HP:0100886",
        "label": "Abnormality of globe location"
      },
      {
        "rank": 8,
        "score": 0.44473597407341003,
        "hpo_id": "HP:0500044",
        "label": "Upper eyelid retraction"
      },
      {
        "rank": 9,
        "score": 0.4411480724811554,
        "hpo_id": "HP:0000656",
        "label": "Ectropion"
      },
      {
        "rank": 10,
        "score": 0.4404057264328003,
        "hpo_id": "HP:0031623",
        "label": "Brow ptosis"
      },
      {
        "rank": 11,
        "score": 0.4396588206291199,
        "hpo_id": "HP:0007715",
        "label": "Weak extraocular muscles"
      },
      {
        "rank": 12,
        "score": 0.4386458992958069,
        "hpo_id": "HP:0008507",
        "label": "Static ophthalmoparesis"
      },
      {
        "rank": 13,
        "score": 0.43541088700294495,
        "hpo_id": "HP:0500043",
        "label": "Eyelid retraction"
      },
      {
        "rank": 14,
        "score": 0.4324886202812195,
        "hpo_id": "HP:0031727",
        "label": "Excyclotropia"
      },
      {
        "rank": 15,
        "score": 0.43215590715408325,
        "hpo_id": "HP:0007651",
        "label": "Ectropion of lower eyelids"
      },
      {
        "rank": 16,
        "score": 0.42802953720092773,
        "hpo_id": "HP:0032039",
        "label": "Abnormality of the ocular adnexa"
      },
      {
        "rank": 17,
        "score": 0.4277222454547882,
        "hpo_id": "HP:0007838",
        "label": "Progressive ptosis"
      },
      {
        "rank": 18,
        "score": 0.4265873432159424,
        "hpo_id": "HP:0025313",
        "label": "Exophoria"
      },
      {
        "rank": 19,
        "score": 0.4259081780910492,
        "hpo_id": "HP:0007800",
        "label": "Increased axial length of the globe"
      },
      {
        "rank": 20,
        "score": 0.42248672246932983,
        "hpo_id": "HP:0011347",
        "label": "Abnormality of ocular abduction"
      }
    ],
    "choice": {
      "id": "p2",
      "hpo_id": "HP:0000520",
      "label": "Proptosis",
      "rank": 1,
      "score": 0.7044878005981445,
      "source": "llm-select",
      "reason": "Proptosis directly matches the HPO term for proptosis."
    }
  },
  {
    "phrase": "irregular, hard lesion of 4×5 cm in the left inferior orbital region",
    "category": "Abnormal",
    "id": "p3",
    "verdict": "keep",
    "reason": "Describes an irregular, hard lesion, indicating an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.5391949415206909,
        "hpo_id": "HP:0030670",
        "label": "Hamartoma of the orbital region"
      },
      {
        "rank": 2,
        "score": 0.49454665184020996,
        "hpo_id": "HP:0500091",
        "label": "Lymphangioma of the orbit"
      },
      {
        "rank": 3,
        "score": 0.4848953187465668,
        "hpo_id": "HP:0025604",
        "label": "Orbital schwannoma"
      },
      {
        "rank": 4,
        "score": 0.47137022018432617,
        "hpo_id": "HP:0000606",
        "label": "Abnormality of the periorbital region"
      },
      {
        "rank": 5,
        "score": 0.46969932317733765,
        "hpo_id": "HP:0000315",
        "label": "Abnormality of the orbital region"
      },
      {
        "rank": 6,
        "score": 0.4683396518230438,
        "hpo_id": "HP:6000614",
        "label": "Orbital inflammation"
      },
      {
        "rank": 7,
        "score": 0.467799574136734,
        "hpo_id": "HP:0500070",
        "label": "Conjunctival dermolipoma"
      },
      {
        "rank": 8,
        "score": 0.4673795700073242,
        "hpo_id": "HP:3000030",
        "label": "Abnormal morphology of bony orbit of skull"
      },
      {
        "rank": 9,
        "score": 0.46644723415374756,
        "hpo_id": "HP:0001144",
        "label": "Orbital cyst"
      },
      {
        "rank": 10,
        "score": 0.46459081768989563,
        "hpo_id": "HP:3000061",
        "label": "Abnormality of infra-orbital nerve"
      },
      {
        "rank": 11,
        "score": 0.45941704511642456,
        "hpo_id": "HP:0031581",
        "label": "Tessier number 9 facial cleft"
      },
      {
        "rank": 12,
        "score": 0.455337256193161,
        "hpo_id": "HP:0031577",
        "label": "Tessier number 5 facial cleft"
      },
      {
        "rank": 13,
        "score": 0.45398566126823425,
        "hpo_id": "HP:0010732",
        "label": "Nodular changes affecting the eyelids"
      },
      {
        "rank": 14,
        "score": 0.4507750868797302,
        "hpo_id": "HP:0005472",
        "label": "Orbital craniosynostosis"
      },
      {
        "rank": 15,
        "score": 0.4472009539604187,
        "hpo_id": "HP:0500040",
        "label": "Dermolipoma of the conjunctiva"
      },
      {
        "rank": 16,
        "score": 0.4463813006877899,
        "hpo_id": "HP:0031445",
        "label": "Oral mucosa nodule"
      },
      {
        "rank": 17,
        "score": 0.4399736225605011,
        "hpo_id": "HP:3000072",
        "label": "Abnormal levator palpebrae superioris morphology"
      },
      {
        "rank": 18,
        "score": 0.43904152512550354,
        "hpo_id": "HP:0004407",
        "label": "Bony paranasal bossing"
      },
      {
        "rank": 19,
        "score": 0.43586379289627075,
        "hpo_id": "HP:0100011",
        "label": "Scleral schwannoma"
      },
      {
        "rank": 20,
        "score": 0.43462932109832764,
        "hpo_id": "HP:0500092",
        "label": "Orbital rhabdomyosarcoma"
      }
    ],
    "choice": {
      "id": "p3",
      "hpo_id": "HP:0030670",
      "label": "Hamartoma of the orbital region",
      "rank": 1,
      "score": 0.5391949415206909,
      "source": "llm-select",
      "reason": "Irregular, hard lesion in the orbital region is best described as a hamartoma of the orbital region."
    }
  },
  {
    "phrase": "cystic swelling of 6×7 cm in the left high parietal region",
    "category": "Abnormal",
    "id": "p4",
    "verdict": "keep",
    "reason": "Cystic swelling is an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.5020380020141602,
        "hpo_id": "HP:0032327",
        "label": "Interhemispheric cyst"
      },
      {
        "rank": 2,
        "score": 0.48848646879196167,
        "hpo_id": "HP:0006951",
        "label": "Retrocerebellar cyst"
      },
      {
        "rank": 3,
        "score": 0.48613637685775757,
        "hpo_id": "HP:0010723",
        "label": "Cystic lesions of the pinnae"
      },
      {
        "rank": 4,
        "score": 0.48215287923812866,
        "hpo_id": "HP:6000461",
        "label": "Cerebral subcortical cyst"
      },
      {
        "rank": 5,
        "score": 0.4807890057563782,
        "hpo_id": "HP:0000933",
        "label": "Posterior fossa cyst at the fourth ventricle"
      },
      {
        "rank": 6,
        "score": 0.4713834822177887,
        "hpo_id": "HP:0010879",
        "label": "Postnatal cystic hygroma"
      },
      {
        "rank": 7,
        "score": 0.4704537093639374,
        "hpo_id": "HP:0002416",
        "label": "Subependymal cysts"
      },
      {
        "rank": 8,
        "score": 0.4665932357311249,
        "hpo_id": "HP:0000476",
        "label": "Cystic hygroma"
      },
      {
        "rank": 9,
        "score": 0.46014806628227234,
        "hpo_id": "HP:0006706",
        "label": "Cystic liver disease"
      },
      {
        "rank": 10,
        "score": 0.459689736366272,
        "hpo_id": "HP:0007291",
        "label": "Posterior fossa cyst"
      },
      {
        "rank": 11,
        "score": 0.4583864212036133,
        "hpo_id": "HP:0033140",
        "label": "Blake's pouch cyst"
      },
      {
        "rank": 12,
        "score": 0.4554864764213562,
        "hpo_id": "HP:0010576",
        "label": "Intracranial cystic lesion"
      },
      {
        "rank": 13,
        "score": 0.455330491065979,
        "hpo_id": "HP:0025246",
        "label": "Trichilemmal cyst"
      },
      {
        "rank": 14,
        "score": 0.45470112562179565,
        "hpo_id": "HP:0012489",
        "label": "Suprasellar arachnoid cyst"
      },
      {
        "rank": 15,
        "score": 0.45416972041130066,
        "hpo_id": "HP:0012487",
        "label": "Cerebellopontine angle arachnoid cyst"
      },
      {
        "rank": 16,
        "score": 0.45088014006614685,
        "hpo_id": "HP:0006799",
        "label": "Basal ganglia cysts"
      },
      {
        "rank": 17,
        "score": 0.44657760858535767,
        "hpo_id": "HP:0011816",
        "label": "Parietal encephalocele"
      },
      {
        "rank": 18,
        "score": 0.44651615619659424,
        "hpo_id": "HP:0001407",
        "label": "Hepatic cysts"
      },
      {
        "rank": 19,
        "score": 0.4457842707633972,
        "hpo_id": "HP:0030423",
        "label": "Splenic cyst"
      },
      {
        "rank": 20,
        "score": 0.442754864692688,
        "hpo_id": "HP:0030730",
        "label": "Parietal meningocele"
      }
    ],
    "choice": {
      "id": "p4",
      "hpo_id": "HP:0032327",
      "label": "Interhemispheric cyst",
      "rank": 1,
      "score": 0.5020380020141602,
      "source": "llm-select",
      "reason": "Cystic swelling in the parietal region fits the description of an interhemispheric cyst."
    }
  },
  {
    "phrase": "another similar one of 3×4 cm in the lower lumbar region",
    "category": "Abnormal",
    "id": "p5",
    "verdict": "keep",
    "reason": "Describes another similar lesion, indicating an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.49653318524360657,
        "hpo_id": "HP:0004589",
        "label": "Dysplasia of second lumbar vertebra"
      },
      {
        "rank": 2,
        "score": 0.48848021030426025,
        "hpo_id": "HP:0008416",
        "label": "Six lumbar vertebrae"
      },
      {
        "rank": 3,
        "score": 0.48513370752334595,
        "hpo_id": "HP:0008421",
        "label": "Tall lumbar vertebral bodies"
      },
      {
        "rank": 4,
        "score": 0.4810936152935028,
        "hpo_id": "HP:0008464",
        "label": "Absent spinous processes of lower thoracic and lumbar vertebrae"
      },
      {
        "rank": 5,
        "score": 0.47051572799682617,
        "hpo_id": "HP:0008425",
        "label": "Cuboid-shaped thoracolumbar vertebral bodies"
      },
      {
        "rank": 6,
        "score": 0.46610748767852783,
        "hpo_id": "HP:0410275",
        "label": "Lumbosacral hemangioma"
      },
      {
        "rank": 7,
        "score": 0.4568644165992737,
        "hpo_id": "HP:0200133",
        "label": "Lumbosacral meningocele"
      },
      {
        "rank": 8,
        "score": 0.45340704917907715,
        "hpo_id": "HP:0004626",
        "label": "Lumbar scoliosis"
      },
      {
        "rank": 9,
        "score": 0.45332100987434387,
        "hpo_id": "HP:0008424",
        "label": "Hypoplastic 5th lumbar vertebrae"
      },
      {
        "rank": 10,
        "score": 0.4384872317314148,
        "hpo_id": "HP:0005638",
        "label": "Decreased anterioposterior diameter of lumbar vertebral bodies"
      },
      {
        "rank": 11,
        "score": 0.43783318996429443,
        "hpo_id": "HP:0008439",
        "label": "Lumbar hemivertebrae"
      },
      {
        "rank": 12,
        "score": 0.4376797080039978,
        "hpo_id": "HP:0004619",
        "label": "Lumbar kyphoscoliosis"
      },
      {
        "rank": 13,
        "score": 0.4361090362071991,
        "hpo_id": "HP:0012033",
        "label": "Sacral lipoma"
      },
      {
        "rank": 14,
        "score": 0.4353175163269043,
        "hpo_id": "HP:0003423",
        "label": "Thoracolumbar kyphoscoliosis"
      },
      {
        "rank": 15,
        "score": 0.43175235390663147,
        "hpo_id": "HP:0008430",
        "label": "Anterior beaking of lumbar vertebrae"
      },
      {
        "rank": 16,
        "score": 0.431493878364563,
        "hpo_id": "HP:0003440",
        "label": "Horizontal sacrum"
      },
      {
        "rank": 17,
        "score": 0.4204891324043274,
        "hpo_id": "HP:0003309",
        "label": "Ovoid thoracolumbar vertebrae"
      },
      {
        "rank": 18,
        "score": 0.41612547636032104,
        "hpo_id": "HP:0008470",
        "label": "Lower thoracic interpediculate narrowness"
      },
      {
        "rank": 19,
        "score": 0.41472262144088745,
        "hpo_id": "HP:0004601",
        "label": "Spina bifida occulta at L5"
      },
      {
        "rank": 20,
        "score": 0.4126328229904175,
        "hpo_id": "HP:0002766",
        "label": "Relatively short spine"
      }
    ],
    "choice": {
      "id": "p5",
      "hpo_id": None,
      "label": None,
      "rank": None,
      "score": None,
      "source": "llm-null",
      "reason": "No clear match for a cystic lesion in the lumbar region among the candidates."
    }
  },
  {
    "phrase": "two firm swellings of 1×1 cm in the right paraorbital region",
    "category": "Abnormal",
    "id": "p6",
    "verdict": "keep",
    "reason": "Describes firm swellings, indicating an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.4754800796508789,
        "hpo_id": "HP:0500091",
        "label": "Lymphangioma of the orbit"
      },
      {
        "rank": 2,
        "score": 0.4709663689136505,
        "hpo_id": "HP:0030670",
        "label": "Hamartoma of the orbital region"
      },
      {
        "rank": 3,
        "score": 0.4702571928501129,
        "hpo_id": "HP:0000629",
        "label": "Periorbital fullness"
      },
      {
        "rank": 4,
        "score": 0.46642863750457764,
        "hpo_id": "HP:0025604",
        "label": "Orbital schwannoma"
      },
      {
        "rank": 5,
        "score": 0.4573745131492615,
        "hpo_id": "HP:0100539",
        "label": "Periorbital edema"
      },
      {
        "rank": 6,
        "score": 0.45325830578804016,
        "hpo_id": "HP:0000606",
        "label": "Abnormality of the periorbital region"
      },
      {
        "rank": 7,
        "score": 0.44365933537483215,
        "hpo_id": "HP:0500070",
        "label": "Conjunctival dermolipoma"
      },
      {
        "rank": 8,
        "score": 0.44176816940307617,
        "hpo_id": "HP:0001144",
        "label": "Orbital cyst"
      },
      {
        "rank": 9,
        "score": 0.4370443820953369,
        "hpo_id": "HP:0000315",
        "label": "Abnormality of the orbital region"
      },
      {
        "rank": 10,
        "score": 0.43507444858551025,
        "hpo_id": "HP:6000614",
        "label": "Orbital inflammation"
      },
      {
        "rank": 11,
        "score": 0.4339723587036133,
        "hpo_id": "HP:0030793",
        "label": "Jaw swelling"
      },
      {
        "rank": 12,
        "score": 0.4306985139846802,
        "hpo_id": "HP:0500040",
        "label": "Dermolipoma of the conjunctiva"
      },
      {
        "rank": 13,
        "score": 0.43030256032943726,
        "hpo_id": "HP:0025246",
        "label": "Trichilemmal cyst"
      },
      {
        "rank": 14,
        "score": 0.42846113443374634,
        "hpo_id": "HP:0030668",
        "label": "Periorbital dermoid cyst"
      },
      {
        "rank": 15,
        "score": 0.4280499815940857,
        "hpo_id": "HP:0010732",
        "label": "Nodular changes affecting the eyelids"
      },
      {
        "rank": 16,
        "score": 0.42694973945617676,
        "hpo_id": "HP:0012549",
        "label": "Conjunctival lipoma"
      },
      {
        "rank": 17,
        "score": 0.41735416650772095,
        "hpo_id": "HP:6000059",
        "label": "Localized to upper eyelid"
      },
      {
        "rank": 18,
        "score": 0.4173505902290344,
        "hpo_id": "HP:0100011",
        "label": "Scleral schwannoma"
      },
      {
        "rank": 19,
        "score": 0.41730108857154846,
        "hpo_id": "HP:0012724",
        "label": "Upper eyelid edema"
      },
      {
        "rank": 20,
        "score": 0.4171793460845947,
        "hpo_id": "HP:0012507",
        "label": "Weakness of orbicularis oculi muscle"
      }
    ],
    "choice": {
      "id": "p6",
      "hpo_id": "HP:0500091",
      "label": "Lymphangioma of the orbit",
      "rank": 1,
      "score": 0.4754800796508789,
      "source": "llm-select",
      "reason": "Firm swellings in the paraorbital region are consistent with lymphangioma of the orbit."
    }
  },
  {
    "phrase": "a 2×2 cm in the right forearm",
    "category": "Abnormal",
    "id": "p7",
    "verdict": "keep",
    "reason": "Describes a lesion in the forearm, indicating an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.512457013130188,
        "hpo_id": "HP:0006368",
        "label": "Forearm reduction defects"
      },
      {
        "rank": 2,
        "score": 0.4690304398536682,
        "hpo_id": "HP:0003957",
        "label": "Cortical thickening of the forearm bones"
      },
      {
        "rank": 3,
        "score": 0.4665285050868988,
        "hpo_id": "HP:0003966",
        "label": "Sclerotic foci in forearm bones"
      },
      {
        "rank": 4,
        "score": 0.4406922161579132,
        "hpo_id": "HP:0003964",
        "label": "Osteoporotic forearm bones"
      },
      {
        "rank": 5,
        "score": 0.43504491448402405,
        "hpo_id": "HP:0005632",
        "label": "Absent forearm"
      },
      {
        "rank": 6,
        "score": 0.4335823059082031,
        "hpo_id": "HP:0002973",
        "label": "Abnormal forearm morphology"
      },
      {
        "rank": 7,
        "score": 0.4332548975944519,
        "hpo_id": "HP:0003960",
        "label": "Exostoses of the forearm bones"
      },
      {
        "rank": 8,
        "score": 0.4290481209754944,
        "hpo_id": "HP:0003958",
        "label": "Cross-fusion of the forearm bones"
      },
      {
        "rank": 9,
        "score": 0.4254063367843628,
        "hpo_id": "HP:0003977",
        "label": "Deformed radius"
      },
      {
        "rank": 10,
        "score": 0.4174576997756958,
        "hpo_id": "HP:0003965",
        "label": "Pseudarthrosis of the forearm bones"
      },
      {
        "rank": 11,
        "score": 0.41483068466186523,
        "hpo_id": "HP:0001454",
        "label": "Abnormality of the upper arm"
      },
      {
        "rank": 12,
        "score": 0.41245222091674805,
        "hpo_id": "HP:0003959",
        "label": "Deformed forearm bones"
      },
      {
        "rank": 13,
        "score": 0.41231828927993774,
        "hpo_id": "HP:0009821",
        "label": "Forearm undergrowth"
      },
      {
        "rank": 14,
        "score": 0.4122098982334137,
        "hpo_id": "HP:0040072",
        "label": "Abnormal forearm bone morphology"
      },
      {
        "rank": 15,
        "score": 0.410617470741272,
        "hpo_id": "HP:0007398",
        "label": "Asymmetric, linear skin defects"
      },
      {
        "rank": 16,
        "score": 0.409446120262146,
        "hpo_id": "HP:0003954",
        "label": "Angulated forearm bones"
      },
      {
        "rank": 17,
        "score": 0.4061989188194275,
        "hpo_id": "HP:0009822",
        "label": "Aplasia involving forearm bones"
      },
      {
        "rank": 18,
        "score": 0.399966835975647,
        "hpo_id": "HP:0003978",
        "label": "Fractured radius"
      },
      {
        "rank": 19,
        "score": 0.39994215965270996,
        "hpo_id": "HP:6000299",
        "label": "Forearm pain"
      },
      {
        "rank": 20,
        "score": 0.39885658025741577,
        "hpo_id": "HP:0003970",
        "label": "Undermodelled forearm bones"
      }
    ],
    "choice": {
      "id": "p7",
      "hpo_id": None,
      "label": None,
      "rank": None,
      "score": None,
      "source": "llm-null",
      "reason": "No specific match for a lesion in the forearm among the candidates."
    }
  },
  {
    "phrase": "corneal opacity",
    "category": "Abnormal",
    "id": "p8",
    "verdict": "keep",
    "reason": "Corneal opacity is an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.730503499507904,
        "hpo_id": "HP:0008039",
        "label": "Subepithelial corneal opacities"
      },
      {
        "rank": 2,
        "score": 0.7000812292098999,
        "hpo_id": "HP:0007957",
        "label": "Corneal opacity"
      },
      {
        "rank": 3,
        "score": 0.6826867461204529,
        "hpo_id": "HP:0000559",
        "label": "Corneal scarring"
      },
      {
        "rank": 4,
        "score": 0.674140453338623,
        "hpo_id": "HP:0008011",
        "label": "Peripheral opacification of the cornea"
      },
      {
        "rank": 5,
        "score": 0.6671620011329651,
        "hpo_id": "HP:0007727",
        "label": "Opacification of the corneal epithelium"
      },
      {
        "rank": 6,
        "score": 0.6633697152137756,
        "hpo_id": "HP:0008511",
        "label": "Central posterior corneal opacity"
      },
      {
        "rank": 7,
        "score": 0.6624817848205566,
        "hpo_id": "HP:0007705",
        "label": "Corneal degeneration"
      },
      {
        "rank": 8,
        "score": 0.6564143896102905,
        "hpo_id": "HP:0011493",
        "label": "Central opacification of the cornea"
      },
      {
        "rank": 9,
        "score": 0.6520181894302368,
        "hpo_id": "HP:0007759",
        "label": "Opacification of the corneal stroma"
      },
      {
        "rank": 10,
        "score": 0.6197114586830139,
        "hpo_id": "HP:0011494",
        "label": "Generalized opacification of the cornea"
      },
      {
        "rank": 11,
        "score": 0.6041465997695923,
        "hpo_id": "HP:0007881",
        "label": "Central corneal dystrophy"
      },
      {
        "rank": 12,
        "score": 0.5900938510894775,
        "hpo_id": "HP:0007856",
        "label": "Punctate opacification of the cornea"
      },
      {
        "rank": 13,
        "score": 0.5699194669723511,
        "hpo_id": "HP:0007710",
        "label": "Peripheral vitreous opacities"
      },
      {
        "rank": 14,
        "score": 0.5598993301391602,
        "hpo_id": "HP:0040004",
        "label": "Abnormality of corneal shape"
      },
      {
        "rank": 15,
        "score": 0.5499297380447388,
        "hpo_id": "HP:6001289",
        "label": "Corneal keloid"
      },
      {
        "rank": 16,
        "score": 0.5490127801895142,
        "hpo_id": "HP:0007760",
        "label": "Crystalline corneal dystrophy"
      },
      {
        "rank": 17,
        "score": 0.543466329574585,
        "hpo_id": "HP:0007880",
        "label": "Marginal corneal dystrophy"
      },
      {
        "rank": 18,
        "score": 0.5414246320724487,
        "hpo_id": "HP:0200066",
        "label": "Ribbonlike corneal degeneration"
      },
      {
        "rank": 19,
        "score": 0.5401961803436279,
        "hpo_id": "HP:0007827",
        "label": "Nodular corneal dystrophy"
      },
      {
        "rank": 20,
        "score": 0.5381405353546143,
        "hpo_id": "HP:0007836",
        "label": "Mosaic corneal dystrophy"
      }
    ],
    "choice": {
      "id": "p8",
      "hpo_id": "HP:0007957",
      "label": "Corneal opacity",
      "rank": 2,
      "score": 0.7000812292098999,
      "source": "llm-select",
      "reason": "Corneal opacity directly corresponds to the HPO term for corneal opacity."
    }
  },
  {
    "phrase": "parapapillary atrophy",
    "category": "Abnormal",
    "id": "p9",
    "verdict": "keep",
    "reason": "Parapapillary atrophy is an abnormal finding.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.7513628602027893,
        "hpo_id": "HP:0500087",
        "label": "Peripapillary atrophy"
      },
      {
        "rank": 2,
        "score": 0.7119870781898499,
        "hpo_id": "HP:0007950",
        "label": "Peripapillary chorioretinal atrophy"
      },
      {
        "rank": 3,
        "score": 0.6368687152862549,
        "hpo_id": "HP:0031609",
        "label": "Geographic atrophy"
      },
      {
        "rank": 4,
        "score": 0.5963383913040161,
        "hpo_id": "HP:0007903",
        "label": "Paravenous chorioretinal atrophy"
      },
      {
        "rank": 5,
        "score": 0.5932677984237671,
        "hpo_id": "HP:0007685",
        "label": "Peripheral retinal avascularization"
      },
      {
        "rank": 6,
        "score": 0.5894292593002319,
        "hpo_id": "HP:0001105",
        "label": "Retinal atrophy"
      },
      {
        "rank": 7,
        "score": 0.5785308480262756,
        "hpo_id": "HP:0007722",
        "label": "Retinal pigment epithelial atrophy"
      },
      {
        "rank": 8,
        "score": 0.576321542263031,
        "hpo_id": "HP:0030491",
        "label": "Choriocapillaris atrophy"
      },
      {
        "rank": 9,
        "score": 0.572959303855896,
        "hpo_id": "HP:0001099",
        "label": "Fundus atrophy"
      },
      {
        "rank": 10,
        "score": 0.5724788904190063,
        "hpo_id": "HP:0200070",
        "label": "Peripheral retinal atrophy"
      },
      {
        "rank": 11,
        "score": 0.565703272819519,
        "hpo_id": "HP:0007401",
        "label": "Macular atrophy"
      },
      {
        "rank": 12,
        "score": 0.5589342713356018,
        "hpo_id": "HP:0007791",
        "label": "Patchy atrophy of the retinal pigment epithelium"
      },
      {
        "rank": 13,
        "score": 0.5480326414108276,
        "hpo_id": "HP:0025010",
        "label": "Foveal atrophy"
      },
      {
        "rank": 14,
        "score": 0.5446546673774719,
        "hpo_id": "HP:6000771",
        "label": "Abnormal peripapillary microvascular network"
      },
      {
        "rank": 15,
        "score": 0.543478786945343,
        "hpo_id": "HP:0030616",
        "label": "Foveal retinal pigment epithelial loss on macular OCT"
      },
      {
        "rank": 16,
        "score": 0.5404672622680664,
        "hpo_id": "HP:0000533",
        "label": "Chorioretinal atrophy"
      },
      {
        "rank": 17,
        "score": 0.5359269380569458,
        "hpo_id": "HP:0007769",
        "label": "Peripheral retinal degeneration"
      },
      {
        "rank": 18,
        "score": 0.5262974500656128,
        "hpo_id": "HP:0030611",
        "label": "Retinal pigment epithelial loss on macular OCT"
      },
      {
        "rank": 19,
        "score": 0.5120017528533936,
        "hpo_id": "HP:0007980",
        "label": "Absent retinal pigment epithelium"
      },
      {
        "rank": 20,
        "score": 0.5114139914512634,
        "hpo_id": "HP:0007964",
        "label": "Degenerative vitreoretinopathy"
      }
    ],
    "choice": {
      "id": "p9",
      "hpo_id": "HP:0500087",
      "label": "Peripapillary atrophy",
      "rank": 1,
      "score": 0.7513628602027893,
      "source": "llm-select",
      "reason": "Parapapillary atrophy aligns with peripapillary atrophy."
    }
  },
  {
    "phrase": "history of his father's death due to some unknown abdominal condition",
    "category": "Family History",
    "id": "p10",
    "verdict": "keep",
    "reason": "Not a phenotypic finding; relates to family history.",
    "candidates": [
      {
        "rank": 1,
        "score": 0.48010653257369995,
        "hpo_id": "HP:6000311",
        "label": "History of abdominal surgery"
      },
      {
        "rank": 2,
        "score": 0.39989227056503296,
        "hpo_id": "HP:0032318",
        "label": "Family history of heart disease"
      },
      {
        "rank": 3,
        "score": 0.3961125612258911,
        "hpo_id": "HP:0032317",
        "label": "Family history of cancer"
      },
      {
        "rank": 4,
        "score": 0.380184531211853,
        "hpo_id": "HP:0005243",
        "label": "Partial abdominal muscle agenesis"
      },
      {
        "rank": 5,
        "score": 0.3669315576553345,
        "hpo_id": "HP:0002686",
        "label": "Pregnancy history"
      },
      {
        "rank": 6,
        "score": 0.3644937574863434,
        "hpo_id": "HP:0003745",
        "label": "Sporadic"
      },
      {
        "rank": 7,
        "score": 0.3634646534919739,
        "hpo_id": "HP:0004392",
        "label": "Prune belly"
      },
      {
        "rank": 8,
        "score": 0.3616026043891907,
        "hpo_id": "HP:4000173",
        "label": "History of previous pregnancy with hydrops fetalis"
      },
      {
        "rank": 9,
        "score": 0.34399014711380005,
        "hpo_id": "HP:0011458",
        "label": "Abdominal symptom"
      },
      {
        "rank": 10,
        "score": 0.3429962992668152,
        "hpo_id": "HP:0005247",
        "label": "Hypoplasia of the abdominal wall musculature"
      },
      {
        "rank": 11,
        "score": 0.34193992614746094,
        "hpo_id": "HP:6000194",
        "label": "History of adrenalectomy"
      },
      {
        "rank": 12,
        "score": 0.3418276309967041,
        "hpo_id": "HP:0032322",
        "label": "Healthy"
      },
      {
        "rank": 13,
        "score": 0.340587854385376,
        "hpo_id": "HP:0030733",
        "label": "Vesicoallantoic abdominal wall defect"
      },
      {
        "rank": 14,
        "score": 0.34055429697036743,
        "hpo_id": "HP:0001438",
        "label": "Abnormal abdomen morphology"
      },
      {
        "rank": 15,
        "score": 0.34042835235595703,
        "hpo_id": "HP:0004298",
        "label": "Abnormality of the abdominal wall"
      },
      {
        "rank": 16,
        "score": 0.33835965394973755,
        "hpo_id": "HP:0040410",
        "label": "History of vasectomy"
      },
      {
        "rank": 17,
        "score": 0.33672505617141724,
        "hpo_id": "HP:0002012",
        "label": "Abnormality of the abdominal organs"
      },
      {
        "rank": 18,
        "score": 0.3354794681072235,
        "hpo_id": "HP:0034856",
        "label": "Maternal amniocentesis"
      },
      {
        "rank": 19,
        "score": 0.3352504372596741,
        "hpo_id": "HP:0006583",
        "label": "Fatal liver failure in infancy"
      },
      {
        "rank": 20,
        "score": 0.33491647243499756,
        "hpo_id": "HP:0034896",
        "label": "History of recent anticoagulant ingestion"
      }
    ],
    "choice": {
      "id": "p10",
      "hpo_id": None,
      "label": None,
      "rank": None,
      "score": None,
      "source": "llm-null",
      "reason": "No relevant HPO term for a family history of an unknown abdominal condition."
    }
  }
]