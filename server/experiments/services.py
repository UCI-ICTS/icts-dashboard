#!/usr/bin/env python3
# experiments/servces.py

from django.db import transaction
from rest_framework import serializers
from experiments.models import AlignedDNAShortRead


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
