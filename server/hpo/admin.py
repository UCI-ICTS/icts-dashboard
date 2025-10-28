#!/usr/bin/env python
# hpo/admin.py

"""HPO Admin Pannel
"""

# hpo/admin.py
from __future__ import annotations

from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .models import HPOTerm, HPOEdge, HPOArtifact


# ---------------------------
# Inlines to browse the graph
# ---------------------------

class ChildEdgeInline(admin.TabularInline):
    """
    Shows children of a term (this term is the parent).
    """
    model = HPOEdge
    fk_name = "parent"
    extra = 0
    verbose_name = "Child edge"
    verbose_name_plural = "Children"
    raw_id_fields = ("child",)
    fields = ("child", "child_label", "child_deprecated")
    readonly_fields = ("child_label", "child_deprecated")

    def child_label(self, obj):
        return getattr(obj.child, "label", "")
    child_label.short_description = "Child label"

    def child_deprecated(self, obj):
        return getattr(obj.child, "deprecated", False)
    child_deprecated.boolean = True
    child_deprecated.short_description = "Child deprecated"


class ParentEdgeInline(admin.TabularInline):
    """
    Shows parents of a term (this term is the child).
    """
    model = HPOEdge
    fk_name = "child"
    extra = 0
    verbose_name = "Parent edge"
    verbose_name_plural = "Parents"
    raw_id_fields = ("parent",)
    fields = ("parent", "parent_label", "parent_deprecated")
    readonly_fields = ("parent_label", "parent_deprecated")

    def parent_label(self, obj):
        return getattr(obj.parent, "label", "")
    parent_label.short_description = "Parent label"

    def parent_deprecated(self, obj):
        return getattr(obj.parent, "deprecated", False)
    parent_deprecated.boolean = True
    parent_deprecated.short_description = "Parent deprecated"


# ---------------------------
# HPOTerm admin
# ---------------------------

@admin.register(HPOTerm)
class HPOTermAdmin(admin.ModelAdmin):
    """
    Browse Human Phenotype Ontology terms with handy columns and graph inlines.
    """
    list_display = (
        "hpo_id",
        "label",
        "release",
        "deprecated",
        "num_parents",
        "num_children",
        "synonyms_count",
    )
    list_filter = (
        "deprecated",
        "release",
    )
    search_fields = (
        "hpo_id",
        "label",
        "label_normalized",
        "synonyms_concat",
        "definition",
    )
    ordering = ("hpo_id",)

    # useful read-only helpers on the form
    readonly_fields = (
        "hpo_id",
        "label_normalized",
        "synonyms_preview",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("Identity", {
            "fields": ("hpo_id", "label", "deprecated", "release"),
        }),
        ("Text", {
            "fields": ("definition",),
        }),
        ("Synonyms", {
            "fields": ("synonyms", "synonyms_preview", "synonyms_concat"),
            "description": "Raw JSON list in <b>synonyms</b>; joined string in <b>synonyms_concat</b>.",
        }),
        ("Search helpers", {
            "fields": ("label_normalized", "search_tsv"),
            "classes": ("collapse",),
            "description": "Materialized fields used by autocomplete/search.",
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    inlines = (ParentEdgeInline, ChildEdgeInline)
    save_on_top = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # annotate parent/child counts for list_display
        return qs.annotate(
            _num_parents=Count("parents", distinct=True),
            _num_children=Count("children", distinct=True),
        )

    def num_parents(self, obj):
        return getattr(obj, "_num_parents", 0)
    num_parents.short_description = "# parents"
    num_parents.admin_order_field = "_num_parents"

    def num_children(self, obj):
        return getattr(obj, "_num_children", 0)
    num_children.short_description = "# children"
    num_children.admin_order_field = "_num_children"

    def synonyms_count(self, obj):
        try:
            return len(obj.synonyms or [])
        except Exception:
            return 0
    synonyms_count.short_description = "# syns"

    def synonyms_preview(self, obj):
        """
        Pretty, short preview of first few synonyms.
        """
        syns = (obj.synonyms or [])[:8]
        if not syns:
            return "-"
        return format_html_join(mark_safe("<br/>"), "• {}", ((s,) for s in syns))
    synonyms_preview.short_description = "First synonyms"


# ---------------------------
# HPOEdge admin
# ---------------------------

@admin.register(HPOEdge)
class HPOEdgeAdmin(admin.ModelAdmin):
    """
    Raw view of edges (is_a relationships). Usually you’ll browse via the HPOTerm inlines.
    """
    list_display = ("parent", "parent_label", "child", "child_label")
    search_fields = ("parent__hpo_id", "parent__label", "child__hpo_id", "child__label")
    raw_id_fields = ("parent", "child")
    ordering = ("parent__hpo_id", "child__hpo_id")

    def parent_label(self, obj):
        return getattr(obj.parent, "label", "")
    parent_label.short_description = "Parent label"

    def child_label(self, obj):
        return getattr(obj.child, "label", "")
    child_label.short_description = "Child label"


# ---------------------------
# HPOArtifact admin
# ---------------------------

@admin.action(description="Mark selected artifact as ACTIVE (and deactivate others)")
def make_active(modeladmin, request, queryset):
    """
    Only the most recently selected artifact will be kept active.
    """
    # choose the newest selected row to be active
    target = queryset.order_by("-built_at").first()
    if target:
        HPOArtifact.objects.exclude(pk=target.pk).update(active=False)
        target.active = True
        target.save()

@admin.register(HPOArtifact)
class HPOArtifactAdmin(admin.ModelAdmin):
    """
    Tracks HPO release + file paths for CSV/FAISS/NPZ. Use the action to flip active.
    """
    list_display = (
        "release",
        "active",
        "embed_model",
        "short_csv",
        "short_faiss",
        "short_npz",
        "built_at",
    )
    list_filter = ("active", "release", "embed_model")
    search_fields = ("release", "csv_path", "faiss_path", "npz_path", "embed_model")
    readonly_fields = ("csv_sha256", "built_at")
    actions = (make_active,)
    ordering = ("-built_at",)

    def _short_path(self, path: str, width: int = 48) -> str:
        if not path:
            return "-"
        return (path if len(path) <= width else f"…{path[-width:]}")

    def short_csv(self, obj):
        return self._short_path(obj.csv_path)
    short_csv.short_description = "csv_path"

    def short_faiss(self, obj):
        return self._short_path(obj.faiss_path)
    short_faiss.short_description = "faiss_path"

    def short_npz(self, obj):
        return self._short_path(obj.npz_path)
    short_npz.short_description = "npz_path"
