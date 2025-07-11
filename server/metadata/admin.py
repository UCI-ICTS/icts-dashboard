"""Metadata Admin Panel"""

from django.contrib import admin
from metadata.models import (
    Participant,
    InternalProjectId,
    Family,
    PmidId,
    Phenotype,
    GeneticFindings,
    Analyte,
    Biobank,
)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["participant_id"]


class InternalProjectIdAdmin(admin.ModelAdmin):
    list_display = ["internal_project_id"]


class FamilyAdmin(admin.ModelAdmin):
    list_display = ["family_id"]


class PmidIdAdmin(admin.ModelAdmin):
    list_display = ["pmid_id"]


class PhenotypeAdmin(admin.ModelAdmin):
    list_display = ["phenotype_id"]


class GeneticFindingsAdmin(admin.ModelAdmin):
    list_display = ["genetic_findings_id"]


class AnalyteAdmin(admin.ModelAdmin):
    list_display = ["analyte_id"]


@admin.register(Biobank)
class BiobankAdmin(admin.ModelAdmin):
    list_display = [
        "biobank_id",
        "participant_id",
        "display_analytes",
        "display_experiments",
        "status",
        "collection_date",
        "completed",
    ]
    search_fields = ["biobank_id", "participant__participant_id", "tube_barcode"]
    list_filter = ["status", "completed", "collection_date"]
    ordering = ["-collection_date"]

    def display_analytes(self, obj):
        return ", ".join(a.analyte_id for a in obj.child_analytes.all())

    display_analytes.short_description = "Analytes"

    def display_experiments(self, obj):
        return ", ".join(e.experiment_id for e in obj.experiments.all())

    display_experiments.short_description = "Experiments"


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(InternalProjectId, InternalProjectIdAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(PmidId, PmidIdAdmin)
admin.site.register(Phenotype, PhenotypeAdmin)
admin.site.register(GeneticFindings, GeneticFindingsAdmin)
admin.site.register(Analyte, AnalyteAdmin)
