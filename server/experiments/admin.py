"""Metadata Admin Pannel
"""

from django.contrib import admin
from experiments.models import (
    Experiment,
    Aligned,
    ExperimentDNAShortRead,
    AlignedDNAShortRead,
)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ["experiment_id"]


class AlignedAdmin(admin.ModelAdmin):
    list_display = ["aligned_id"]


class ExperimentDNAShortReadAdmin(admin.ModelAdmin):
    list_display = ["experiment_dna_short_read_id"]


class AlignedDNAShortReadAdmin(admin.ModelAdmin):
    list_display = ["aligned_dna_short_read_id"]


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Aligned, AlignedAdmin)
admin.site.register(ExperimentDNAShortRead, ExperimentDNAShortReadAdmin)
admin.site.register(AlignedDNAShortRead, AlignedDNAShortReadAdmin)
