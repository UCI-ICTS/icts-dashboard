#!/usr/bin/env python3
# tests/test_apps/test_metadata/test_models.py

"""Metadata Tests: Models and selectors
"""

import json
from django.test import TestCase
from metadata.models import Family, Participant, Phenotype, GeneticFindings, Analyte
from metadata.selectors import get_analyte, genetic_findings_parser, participant_parser

class FamilyModelTest(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_family_creation(self):
        family = Family.objects.first()
        self.assertIsNotNone(family)
        self.assertTrue(hasattr(family, 'family_id'))

class ParticipantModelTest(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_participant_creation(self):
        participant = Participant.objects.first()
        self.assertIsNotNone(participant)
        self.assertTrue(hasattr(participant, 'participant_id'))

    def test_participant_family_relationship(self):
        participant = Participant.objects.first()
        self.assertTrue(hasattr(participant, 'family_id'))
        self.assertTrue(participant.family_id is None or isinstance(participant.family_id, Family))

class PhenotypeModelTest(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_phenotype_creation(self):
        phenotype = Phenotype.objects.first()
        self.assertIsNotNone(phenotype)
        self.assertTrue(hasattr(phenotype, 'phenotype_id'))

class GeneticFindingsModelTest(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_genetic_findings_creation(self):
        genetic_finding = GeneticFindings.objects.first()
        self.assertIsNotNone(genetic_finding)
        self.assertTrue(hasattr(genetic_finding, 'genetic_findings_id'))

    def test_genetic_findings_parser(self):
        test_data = {
            "experiment_id": "EXP1|EXP2",
            "pos": "100",
            "allele_balance_or_heteroplasmy_percentage": "50",
            "gene_of_interest": "GENE1|GENE2",
            "method_of_discovery": "METHOD1|METHOD2",
            "condition_inheritance": "INHERIT1|INHERIT2"
        }
        parsed_data = genetic_findings_parser(test_data)

        self.assertIsInstance(parsed_data["experiment_id"], list)
        self.assertEqual(parsed_data["pos"], 100.0)
        self.assertEqual(parsed_data["allele_balance_or_heteroplasmy_percentage"], 50)
        self.assertIsInstance(parsed_data["gene_of_interest"], list)
        self.assertIsInstance(parsed_data["method_of_discovery"], list)
        self.assertIsInstance(parsed_data["condition_inheritance"], list)

class AnalyteModelTest(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_analyte_creation(self):
        analyte = Analyte.objects.first()
        self.assertIsNotNone(analyte)
        self.assertTrue(hasattr(analyte, 'analyte_id'))

    def test_analyte_participant_relationship(self):
        analyte = Analyte.objects.first()
        self.assertTrue(hasattr(analyte, 'participant_id'))
        self.assertIsInstance(analyte.participant_id, Participant)

class SelectorTests(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_get_analyte(self):
        analyte = Analyte.objects.first()
        retrieved_analyte = get_analyte(analyte.analyte_id)
        self.assertEqual(retrieved_analyte, analyte)

    def test_get_analyte_not_found(self):
        self.assertIsNone(get_analyte("nonexistent_id"))

    def test_participant_parser(self):
        test_data = {"twin_id": "T1|T2", "age_at_last_observation": "30", "age_at_enrollment": "25"}
        parsed_data = participant_parser(test_data)
        self.assertIsInstance(parsed_data["twin_id"], list)
        self.assertEqual(parsed_data["age_at_last_observation"], 30.0)
        self.assertEqual(parsed_data["age_at_enrollment"], 25.0)
