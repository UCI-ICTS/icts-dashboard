#!/usr/bin/env python3
# experiments/servces.py

from django.db import transaction
from rest_framework import serializers
from experiments.models import (
    Aligned,
    AlignedDNAShortRead,
    AlignedPacBio,
    Experiment,
    ExperimentDNAShortRead,
    ExperimentPacBio,
)


class ExperimentPacBioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentPacBio
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentPacBio instance using the validated data"""
        print("pacbio create")
        experiment_pac_bio_id = validated_data.get("experiment_pac_bio_id")
        experiment_pac_bio, created = ExperimentPacBio.objects.get_or_create(
            experiment_pac_bio_id=experiment_pac_bio_id, defaults=validated_data
        )
        return experiment_pac_bio

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        print("pacbio updated")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class ExperimentShortReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentDNAShortRead
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentDNAShortRead instance using the validated data"""

        experiment_dna_short_read_id = validated_data.get(
            "experiment_dna_short_read_id"
        )
        experiment_dna_short_read, created = (
            ExperimentDNAShortRead.objects.get_or_create(
                experiment_dna_short_read_id=experiment_dna_short_read_id,
                defaults=validated_data,
            )
        )
        return experiment_dna_short_read

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Experiment instance using the validated data"""

        experiment_id = validated_data.get("experiment_id")
        experiment, created = Experiment.objects.get_or_create(
            experiment_id=experiment_id, defaults=validated_data
        )
        return experiment

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class ExperimentService:
    """
    Service class that provides static methods to create, update, and validate experiments.

    This class encapsulates the logic for handling experiments by interfacing with
    the Experiment model and related serializers to ensure data integrity and compliance
    with business rules before persisting in the database.

    Methods:
        create_or_update_experiment(data): Creates a new experiment or updates an existing one
        based on the provided data dictionary.
        validate_experiment(data, validator): Validates experiment data against a specified
        JSON schema using a validator instance.
    """

    @staticmethod
    def create_or_update_experiment(data):
        identifier = data["experiment_id"]
        existing_experiment = Experiment.objects.filter(
            experiment_id=identifier
        ).first()

        # Determine if it's a creation or update
        if existing_experiment:
            serializer = ExperimentSerializer(existing_experiment, data=data)
        else:
            serializer = ExperimentSerializer(data=data)

        if serializer.is_valid():
            experiment_instance = serializer.save()
            return serializer
        else:
            return serializer

    @staticmethod
    def validate_experiment(data, validator):
        validator.validate_json(json_object=data, table_name="experiment")
        return validator.get_validation_results()


class AlignedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aligned
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Experiment instance using the validated data"""

        aligned_id = validated_data.get("aligned_id")
        aligned, created = Aligned.objects.get_or_create(
            aligned_id=aligned_id, defaults=validated_data
        )
        return aligned

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class AlignedDNAShortReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlignedDNAShortRead
        fields = "__all__"

    # TODO: determine if this is needed.
    # def validate(self, data):
    #     instance = AlignedDNAShortRead(**data)
    #     if (
    #         not instance.aligned_dna_short_read_set.exists()
    #         and not instance.called_variants_dna_short_read.exists()
    #     ):
    #         raise serializers.ValidationError(
    #             "Either aligned_dna_short_read_set or called_variants_dna_short_read is required."
    #         )
    #     return data


class AlignedService:
    """
    Service class that provides static methods to create, update, and validate Alignments.

    This class encapsulates the logic for handling alignments by interfacing with
    the Aligned model and related serializers to ensure data integrity and compliance
    with business rules before persisting in the database.

    Methods:
        create_or_update_aligned(data): Creates a new alignement or updates an existing one
        based on the provided data dictionary.
        validate_aligned(data, validator): Validates experiment data against a specified
        JSON schema using a validator instance.
    """

    @staticmethod
    def create_or_update_aligned(data):
        """Create or Update Aligned

        Creates a new alignement or updates an existing one
        based on the provided data dictionary."""

        identifier = data["aligned_id"]
        existing_aligned = Aligned.objects.filter(aligned_id=identifier).first()

        # Determine if it's a creation or update
        if existing_aligned:
            serializer = AlignedSerializer(existing_aligned, data=data)
        else:
            serializer = AlignedSerializer(data=data)

        if serializer.is_valid():
            aligned_instance = serializer.save()
            return serializer
        else:
            return serializer

    @staticmethod
    def validate_aligned(data, validator):
        """Validate Aligned

        Validates experiment data against a specified
        JSON schema using a validator instance.
        """

        validator.validate_json(json_object=data, table_name="aligned")
        return validator.get_validation_results()
