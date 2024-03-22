"""Metadata Admin Pannel
"""

from django.contrib import admin
from metadata.models import Participant, InternalProjectId

class ParticipantAdmin(admin.ModelAdmin):
    list_display =["participant_id"]
    
class InternalProjectIdAdmin(admin.ModelAdmin):
    list_display=["internal_project_id"]

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(InternalProjectId, InternalProjectIdAdmin)