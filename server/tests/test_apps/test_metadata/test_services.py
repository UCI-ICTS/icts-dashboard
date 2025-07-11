#!/usr/bin/env python3
# tests/test_metadata/test_services.py

import json
from io import StringIO
from django.test import TestCase
from metadata.models import Participant, Biobank, Analyte
from django.core.management import call_command
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
            "experiment_id": ["EXP1", "EXP2"],
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


# class BioBanklTests(TestCase):
#     # fixtures = ['tests/fixtures/test_fixture.json']
#     fixtures = ['dump.json']

#     def dump_test_data(self, file_name:str="test_results.json")-> None:
#         out = StringIO()
#         call_command('dumpdata', '--exclude', 'contenttypes', '--indent', '2', stdout=out)
#         with open(file_name, 'w') as f:
#             f.write(out.getvalue())

#     def test_validate_biobank_traceability(self):
#         for sample in Biobank.objects.all():
#             result = validate_biobank_traceability(sample)
#             if result["status"] == "invalid":
#                 print(result)

#     def fix_all_biobank_entries(self):
#         results = {}

#         orphaned_analytes = Analyte.objects.filter(biobank__isnull=True)
#         homed_analytes = Analyte.objects.filter(biobank__isnull=False)
#         import pdb; pdb.set_trace()
#         # for analyte in orphaned_analytes:


#     def full_fix_all_biobank_entries(self):
# results = []
# for biobank in Biobank.objects.all():
#     result = repair_biobank_links(biobank)
#     results.append(result)
# return results
