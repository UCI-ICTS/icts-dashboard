#!/usr/bin/env python3
# metadata/servces.py

import os
import jsonref
import jsonschema
from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from metadata.models import Participant, Family, InternalProjectId, PmidId, TwinId

class ParticipantSerializer(serializers.ModelSerializer):
    prior_testing = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of prior testing entries",
        required=False  # Set to True if it's a required field
    )

    class Meta:
        model = Participant
        fields = '__all__'  # Or specify fields including 'pmid_ids'
        extra_kwargs = {
            'participant': {'example': 'BCM_Subject_1'},
            'internal_project_id': {'default': 'Project_XYZ'},
            'gregor_center': {'default': 'BCM'},
            'consent_code': {'default': 'GRU'},
            'recontactable': {'default': 'Yes'},
        }

def get_or_create_sub_models(datum):
    # Mapping of datum keys to model and field names

    mapping = {
        "family_id": (Family, "family_id"),
        "internal_project_id": (InternalProjectId, "internal_project_id"),
        "pmid_id": (PmidId, "pmid_id"),
        "twin_id": (TwinId, "twin_id")
    }

    for key, (model, field_name) in mapping.items():
        if key == "family_id":
            obj, created = model.objects.get_or_create(**{field_name: datum[key]})
            datum[key] = obj.pk
        else:
            objects = []
            for item in datum[key]:
                obj, created = model.objects.get_or_create(**{field_name: datum[key]})
                objects.append(obj.pk)
            datum[key] = objects
    return datum