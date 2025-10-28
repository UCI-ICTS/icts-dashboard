#!/usr/bin/env python
# hpo/apis.py

import json
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
    PhenotypeExtractResponseSerializer
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

        raw_text = ser.validated_data["raw_text"]
        try:
            result = phenotype_extraction(raw_text)   # returns dict with phrases / matches / meta
            return Response(result, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
