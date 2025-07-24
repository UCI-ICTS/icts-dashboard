#!/usr/bin/env python3
# tests/test_metadata/test_services.py

import json
from collections import defaultdict
from django.core.management import call_command
from django.test import TestCase
from io import StringIO
from typing import Dict, Any
from metadata.models import Participant, Biobank, Analyte
from experiments.models import Experiment, Aligned
from metadata.services import (
    GeneticFindingsSerializer,
    AnalyteSerializer,
    FamilySerializer,
    ParticipantInputSerializer,
)


class ServicesTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture.json"]

    def test_genetic_findings_serializer_create(self):
        data = {
            "genetic_findings_id": "GF001",
            "participant_id": Participant.objects.first().participant_id,
            "experiment_id": [
                "experiment_nanopore.UCI_GREGoR_test-004-004-0-D-3_NANO_1",
                "experiment_pac_bio.UCI_GREGoR_test-001-001-0-D-2_PB_1",
            ],
            "variant_reference_assembly": "GRCh38",
            "chrom": "1",
            "pos": 123456,
            "ref": "A",
            "alt": "T",
            "zygosity": "Homozygous",
            "variant_inheritance": "biparental",
        }
        serializer = GeneticFindingsSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.genetic_findings_id, "GF001")

    def test_analyte_serializer_create(self):
        data = {
            "analyte_id": "A001",
            "participant_id": Participant.objects.first().participant_id,
            "analyte_type": "DNA",
            "primary_biosample": "UBERON:0000178",
        }
        serializer = AnalyteSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.analyte_id, "A001")

    def test_family_serializer_create(self):
        data = {"family_id": "F001"}
        serializer = FamilySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.family_id, "F001")

    def test_participant_serializer_create(self):
        data = {
            "participant_id": "P001",
            "consent_code": "HMB",
            "solve_status": "Unsolved",
            "gregor_center": "UCI",
        }
        serializer = ParticipantInputSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.participant_id, "P001")
