#!/usr/bin/env python3
# experiments/servces.py

from django.db import transaction
from rest_framework import serializers
from experiments.models import AlignedDNAShortRead, Experiment, ExperimentDNAShortRead

class ExperimentShortReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentDNAShortRead
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentDNAShortRead instance using the validated data"""

        experiment_dna_short_read_id = validated_data.get("experiment_dna_short_read_id")
        experiment_dna_short_read, created = ExperimentDNAShortRead.objects.get_or_create(
            experiment_dna_short_read_id=experiment_dna_short_read_id,
            defaults=validated_data
        )
        return experiment_dna_short_read

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance

class ExperimentService:
    @staticmethod
    def create_or_update_experiment(data):
        identifier = data["experiment_id"]
        existing_experiment = Experiment.objects.filter(experiment_id=identifier).first()
        
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


class AlignedDNAShortReadSerializer(serializers.ModelSerializer):
    """add a validation step in your serializer to enforce these conditions
    more contextually, especially if the relationships and business logic are
    more suited to be checked at the API level.
    Works well within the context of Django REST Framework and is ideal for
    API-driven projects."""

    class Meta:
        model = AlignedDNAShortRead
        fields = "__all__"

    def validate(self, data):
        instance = AlignedDNAShortRead(**data)
        if (
            not instance.aligned_dna_short_read_set.exists()
            and not instance.called_variants_dna_short_read.exists()
        ):
            raise serializers.ValidationError(
                "Either aligned_dna_short_read_set or called_variants_dna_short_read is required."
            )
        return data
