"""Submodels Admin Pannel
"""

from django.contrib import admin

from submodels.models import ReportedRace, InternalProjectId, PmidId

class ReportedRaceAdmin(admin.ModelAdmin):
    list_display = ["name"]

# class InternalProjectIdAdmin(admin.ModelAdmin):
#     list_display = ["internal_project_id"]


# class PmidIdAdmin(admin.ModelAdmin):
#     list_display = ["pmid_id"]

# admin.site.register(InternalProjectId, InternalProjectIdAdmin)
# admin.site.register(PmidId, PmidIdAdmin)
admin.site.register(ReportedRace, ReportedRaceAdmin)