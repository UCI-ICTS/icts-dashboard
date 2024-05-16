"""Metadata Admin Pannel
"""

from django.contrib import admin
from metadata.models import Participant, InternalProjectId, Family, PmidId

class ParticipantAdmin(admin.ModelAdmin):
    list_display =["participant_id"]
    
class InternalProjectIdAdmin(admin.ModelAdmin):
    list_display=["internal_project_id"]

class FamilyAdmin(admin.ModelAdmin):
    list_display=["family_id"]

class PmidIdAdmin(admin.ModelAdmin):
    list_display=["pmid_id"]

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(InternalProjectId, InternalProjectIdAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(PmidId, PmidIdAdmin)