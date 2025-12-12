#!/usr/bin/env python
# hpo/models.py

"""
"""
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

class HPOTerm(models.Model):
    hpo_id = models.CharField(primary_key=True, max_length=16)  # e.g., "HP:0001251"
    label = models.TextField()
    definition = models.TextField(blank=True, null=True)
    synonyms = models.JSONField(default=list, blank=True)  # list[str]
    release = models.CharField(max_length=32)              # e.g., "2025-09-01"
    deprecated = models.BooleanField(default=False)

    # Search helpers (materialized for fast LIKE/fuzzy/tsvector)
    label_normalized = models.TextField(db_index=True)     # lowercased/ASCII’d version of label
    synonyms_concat = models.TextField(blank=True)         # synonyms joined into one string
    search_tsv = SearchVectorField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # Full-text search index over the materialized SearchVectorField
            GinIndex(
                fields=["search_tsv"],
                name="hpo_term_tsv_gin"
            ),
            GinIndex(
                fields=["label_normalized"],
                opclasses=["gin_trgm_ops"],
                name="hpo_term_trgm_label"
            ),
            GinIndex(
                fields=["synonyms_concat"],
                opclasses=["gin_trgm_ops"],
                name="hpo_term_trgm_syn"
            )
        ]

    def __str__(self):
        return f"{self.hpo_id} · {self.label}"


class HPOEdge(models.Model):
    parent = models.ForeignKey(HPOTerm, on_delete=models.CASCADE, related_name="children")
    child = models.ForeignKey(HPOTerm, on_delete=models.CASCADE, related_name="parents")

    class Meta:
        unique_together = (("parent", "child"),)
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["child"]),
        ]


class HPOArtifact(models.Model):
    # Provenance + pointers to your on-disk artifacts
    release = models.CharField(max_length=32)         # e.g., "2025-09-01"
    source_url = models.TextField()                   # OBO/JSON source you parsed
    csv_path = models.TextField()                     # path or object URL to hpo_texts.csv
    faiss_path = models.TextField()                   # path to hpo_store.faiss
    npz_path = models.TextField()                     # path to hpo_store.npz
    embed_model = models.CharField(max_length=128)    # e.g., "text-embedding-3-large"
    csv_sha256 = models.CharField(max_length=128)     # for reproducibility
    built_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)        # which artifact to load at startup

    class Meta:
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["release"]),
        ]
