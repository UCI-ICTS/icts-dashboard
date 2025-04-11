"""Metadata Admin Pannel
"""

from django.contrib import admin
from metadata.models import (
    Participant,
    InternalProjectId,
    Family,
    PmidId,
    Phenotype,
    GeneticFindings,
    Analyte,
    Biobank
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

class BiobankAdmin(admin.ModelAdmin):
    list_display = ["biobank_id"]


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(InternalProjectId, InternalProjectIdAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(PmidId, PmidIdAdmin)
admin.site.register(Phenotype, PhenotypeAdmin)
admin.site.register(GeneticFindings, GeneticFindingsAdmin)
admin.site.register(Analyte, AnalyteAdmin)
admin.site.register(Biobank, BiobankAdmin)
