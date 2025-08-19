#!/usr/bin/env python
# search/services.py

from rest_framework import serializers

from metadata.models import Participant

class FamilyDetailInputSerializer(serializers.Serializer):
    participant_id = serializers.CharField()

    def validate_participant_id(self, value):
        if not Participant.objects.filter(pk=value).exists():
            raise serializers.ValidationError("AnotherModel with this ID does not exist.")

        return value
