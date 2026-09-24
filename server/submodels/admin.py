"""Submodels Admin Pannel
"""

from django.contrib import admin

from submodels.models import ReportedRace, InternalProjectId, PmidId
from experiments.models import PrepTargetsDetail

class ReportedRaceAdmin(admin.ModelAdmin):
    list_display = ["name"]

class InternalProjectIdAdmin(admin.ModelAdmin):
    list_display = ["internal_project_id"]

class PmidIdAdmin(admin.ModelAdmin):
    list_display = ["pmid_id"]

class PrepTargetsDetailsAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin.site.register(ReportedRace, ReportedRaceAdmin)
admin.site.register(InternalProjectId, InternalProjectIdAdmin)
admin.site.register(PmidId, PmidIdAdmin)
admin.site.register(PrepTargetsDetail, PrepTargetsDetailsAdmin)