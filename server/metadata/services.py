#!/usr/bin/env python3
# metadata/servces.py

from django.db import transaction, IntegrityError
from rest_framework import serializers
from metadata.models import (
    Analyte,
    Participant,
    Family,
    Phenotype,
    InternalProjectId,
    PmidId,
    TwinId,
)
from metadata.selectors import get_participant


class AnalyteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analyte
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Analyte instance using the validated data"""

        # participant_instance = validated_data["participant_id"]
        # if "age_at_collection" in validated_data:
        #     try:
        #         participant_instance.age_at_enrollment == validated_data["age_at_collection"]
        #     except:
        #         raise ValueError
        # import pdb; pdb.set_trace()
        analyte_instance = Analyte.objects.create(**validated_data)
        return analyte_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class PhenotypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phenotype
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Phenotype instance using the validated data"""
        phenotype = Phenotype.objects.create(**validated_data)
        return phenotype

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = "__all__"

    def create(self, validated_data):
        family_id = validated_data.get("family_id")
        family, created = Family.objects.get_or_create(
            family_id=family_id, defaults=validated_data
        )
        return family

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ParticipantSerializer(serializers.ModelSerializer):
    prior_testing = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of prior testing entries",
        required=False,
    )

    internal_project_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="An identifier used by GREGoR research centers to identify a set of participants for their internal tracking",
    )

    pmid_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Case specific PubMed IDs if applicable",
    )

    twin_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Participant IDs for twins, triplets, etc.",
    )

    class Meta:
        model = Participant
        fields = "__all__"

    def create(self, validated_data):
        internal_project_ids = validated_data.pop("internal_project_ids", [])
        pmid_ids = validated_data.pop("pmid_ids", [])
        twin_ids = validated_data.pop("twin_ids", [])

        try:
            with transaction.atomic():
                participant = Participant.objects.create(**validated_data)
                if internal_project_ids:
                    self._set_relationship(
                        participant,
                        InternalProjectId,
                        internal_project_ids,
                        "internal_project_ids",
                    )
                if pmid_ids:
                    self._set_relationship(participant, PmidId, pmid_ids, "pmid_ids")
                if twin_ids:
                    self._set_relationship(participant, TwinId, twin_ids, "twin_ids")
                participant.save()
        except IntegrityError as error:
            raise serializers.ValidationError(error)

        return participant

    def update(self, instance, validated_data):
        internal_project_ids = validated_data.pop("internal_project_ids", [])
        pmid_ids = validated_data.pop("pmid_ids", [])
        twin_ids = validated_data.pop("twin_ids", [])

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            self._set_relationship(instance, InternalProjectId, internal_project_ids)
            self._set_relationship(instance, PmidId, pmid_ids)
            self._set_relationship(instance, TwinId, twin_ids)

        return instance

    def _set_relationship(self, instance, model, ids, related_name):
        # Setting ManyToMany relations
        manager = getattr(instance, related_name)
        manager.set(model.objects.filter(pk__in=ids))


def get_or_create_sub_models(datum):
    # Define how to handle creation of related objects
    mapping = {
        "family_id": (Family, "family_id"),
        "internal_project_id": (InternalProjectId, "internal_project_id"),
        "pmid_id": (PmidId, "pmid_id"),
        "twin_id": (TwinId, "twin_id"),
    }

    for key, (model, field_name) in mapping.items():
        if isinstance(datum.get(key), list):  # Handles list fields differently
            objects = []
            for item in datum[key]:
                obj, created = model.objects.get_or_create(**{field_name: item})
                objects.append(obj.pk)
            datum[key] = objects
        else:
            if datum.get(key):
                obj, created = model.objects.get_or_create(**{field_name: datum[key]})
                datum[key] = obj.pk

    return datum
