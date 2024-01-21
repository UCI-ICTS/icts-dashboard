"""Metadata Admin Pannel
"""

from django.contrib import admin
from metadata.models import Participant

class ParticipantAdmin(admin.ModelAdmin):
    list_display =["participant_id"]
    
admin.site.register(Participant, ParticipantAdmin)