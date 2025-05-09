"""Metadata Admin Pannel
"""

from django.contrib import admin
from experiments.models import (
    Aligned,
    Experiment,
    AlignedDNAShortRead,
    ExperimentDNAShortRead,
    AlignedPacBio,
    ExperimentPacBio,
    AlignedNanopore,
    ExperimentNanopore,
    AlignedRNAShortRead,
    ExperimentRNAShortRead,
    ExperimentType,
    LibraryPrepType,
)


class AlignedAdmin(admin.ModelAdmin):
    list_display = ["aligned_id"]


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ["experiment_id"]


class AlignedDNAShortReadAdmin(admin.ModelAdmin):
    list_display = ["aligned_dna_short_read_id"]


class ExperimentDNAShortReadAdmin(admin.ModelAdmin):
    list_display = ["experiment_dna_short_read_id"]


class AlignedPacBioAdmin(admin.ModelAdmin):
    list_display = ["aligned_pac_bio_id"]


class ExperimentPacBioAdmin(admin.ModelAdmin):
    list_display = ["experiment_pac_bio_id"]


class AlignedNanoporeAdmin(admin.ModelAdmin):
    list_display = ["aligned_nanopore_id"]


class ExperimentNanoporeAdmin(admin.ModelAdmin):
    list_display = ["experiment_nanopore_id"]


class AlignedRNAShortReadAdmin(admin.ModelAdmin):
    list_display = ["aligned_rna_short_read_id"]


class ExperimentRNAShortReadAdmin(admin.ModelAdmin):
    list_display = ["experiment_rna_short_read_id"]


admin.site.register(LibraryPrepType)
admin.site.register(ExperimentType)
admin.site.register(Aligned, AlignedAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(AlignedDNAShortRead, AlignedDNAShortReadAdmin)
admin.site.register(ExperimentDNAShortRead, ExperimentDNAShortReadAdmin)
admin.site.register(AlignedPacBio, AlignedPacBioAdmin)
admin.site.register(ExperimentPacBio, ExperimentPacBioAdmin)
admin.site.register(AlignedNanopore, AlignedNanoporeAdmin)
admin.site.register(ExperimentNanopore, ExperimentNanoporeAdmin)
admin.site.register(AlignedRNAShortRead, AlignedRNAShortReadAdmin)
admin.site.register(ExperimentRNAShortRead, ExperimentRNAShortReadAdmin)
