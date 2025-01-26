#!/usr/bin/env python3
# metadata/servces.py

from django.db import transaction, IntegrityError
from rest_framework import serializers
from metadata.models import (
    Analyte,
    GeneticFindings,
    Participant,
    Family,
    Phenotype,
    InternalProjectId,
    PmidId,
    TwinId,
)

from submodels.models import ReportedRace


class GeneticFindingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneticFindings
        fields = "__all__"

    def create(self, validated_data):
        """Create a new GeneticFindings instance using the validated data"""
        genetic_findings_instance = GeneticFindings.objects.create(**validated_data)
        return genetic_findings_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


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
        """Create an new instance of the model with validated data"""
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


class ParticipantOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = "__all__"


class ParticipantInputSerializer(serializers.ModelSerializer):
    prior_testing = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of prior testing entries"
    )

    internal_project_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="An identifier used by GREGoR research centers to identify a set of participants for their internal tracking",
    )

    pmid_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Case specific PubMed IDs if applicable",
    )

    twin_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Participant IDs for twins, triplets, etc.",
    )

    reported_race = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Participant IDs for twins, triplets, etc.",
    )

    class Meta:
        model = Participant
        fields = "__all__"

    def create(self, validated_data):
        internal_project_id = validated_data.pop("internal_project_id", [])
        pmid_id = validated_data.pop("pmid_id", [])
        twin_id = validated_data.pop("twin_id", [])
        reported_race = validated_data.pop("reported_race", [])

        try:
            with transaction.atomic():
                participant = Participant.objects.create(**validated_data)
                if internal_project_id:
                    self._set_relationship(
                        participant,
                        InternalProjectId,
                        internal_project_id,
                        "internal_project_id",
                    )
                if pmid_id:
                    self._set_relationship(participant, PmidId, pmid_id, "pmid_id")
                if twin_id:
                    self._set_relationship(participant, TwinId, twin_id, "twin_id")
                if reported_race:
                    self._set_relationship(participant, ReportedRace, reported_race, "reported_race")
                participant.save()
        except IntegrityError as error:
            raise serializers.ValidationError(error)

        return participant

    def update(self, instance, validated_data):
        internal_project_id = validated_data.pop("internal_project_id", [])
        pmid_id = validated_data.pop("pmid_id", [])
        twin_id = validated_data.pop("twin_id", [])
        reported_race = validated_data.pop("reported_race", [])

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            self._set_relationship(instance, InternalProjectId, internal_project_id, "internal_project_id")
            self._set_relationship(instance, PmidId, pmid_id, "pmid_id")
            self._set_relationship(instance, TwinId, twin_id, "twin_id")
            self._set_relationship(instance, ReportedRace, reported_race, "reported_race")

        return instance

    def _set_relationship(self, instance, model, ids, related_name):
        # Setting ManyToMany relations
        print(instance, model, ids, related_name)  # Debugging
        try:
            manager = getattr(instance, related_name)
            if model == ReportedRace:  # Special handling for ReportedRace
                manager.set(model.objects.filter(description__in=ids))
            else:
                manager.set(model.objects.filter(pk__in=ids))
        except Exception as e:
            print(f"Error setting relationship: {e}")
            raise


def get_or_create_sub_models(datum: dict) -> dict:
    """
    Create or retrieve related model instances based on the provided data.

    This function processes the `datum` dictionary to handle the creation or retrieval
    of related model instances. It updates the `datum` dictionary with the primary keys
    of the related instances.

    Args:
        datum (dict): A dictionary containing the data for the main model and its related models.

    Returns:
        dict: The updated `datum` dictionary with primary keys of the related instances.
    """
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
