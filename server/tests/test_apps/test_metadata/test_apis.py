#!/usr/bin/env python3
# tests/test_metadata/test_apis.py

import json
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from metadata.models import Family, Participant, Phenotype, GeneticFindings, Analyte
from metadata.selectors import get_analyte, genetic_findings_parser, participant_parser
from metadata.services import (
    GeneticFindingsSerializer, AnalyteSerializer, PhenotypeSerializer,
    FamilySerializer, ParticipantInputSerializer, ParticipantOutputSerializer
)

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

class APITestCaseWithAuth(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

    def test_create_participant(self):
        url = "/api/metadata/submit_participants/"
        data = [
            {
                "participant_id": "P-002-001-0",
                "consent_code": "HMB",
                "gregor_center": "UCI",
                "family_id": "P-001",
                "paternal_id": "0",
                "maternal_id": "0",
                "proband_relationship": "Self",
                "sex": "Male",
                "affected_status": "Unaffected",
                "solve_status": "Unsolved",
                "age_at_last_observation": 20,
                "age_at_enrollment": 20,
                "missing_variant_case": "No"
            }
        ]

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")

    def test_update_participant(self):
        url = "/api/metadata/submit_participants/"
        data = [
            {
                "participant_id": "GREGoR_test-001-002-0",
                "consent_code": "HMB",
                "gregor_center": "UCI",
                "family_id": "P-001",
                "paternal_id": "0",
                "maternal_id": "0",
                "proband_relationship": "Self",
                "sex": "Female",
                "affected_status": "Unaffected",
                "solve_status": "Unsolved",
                "age_at_last_observation": 20,
                "age_at_enrollment": 20,
                "missing_variant_case": "No"
            }
        ]

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "UPDATED")

    def test_create_family(self):
        url = "/api/metadata/submit_families/"
        data = [{"family_id": "F002", "consanguinity": "Unknown"}]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")

    def test_create_analyte(self):
        url = "/api/metadata/submit_analyte/"
        data = [{
            "analyte_id": "A002",
            "participant_id": "GREGoR_test-001-003-0",
            "analyte_type": "RNA",
            "primary_biosample": "UBERON:0000178",
        }]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")
        
    def test_create_genetic_finding(self):
        url = "/api/metadata/submit_genetic_findings/"
        data = [{
            "genetic_findings_id": "GF002",
            "participant_id": "GREGoR_test-001-003-0",
            "experiment_id": ["EXP3"],
            "variant_reference_assembly": "GRCh38",
            "chrom": "2",
            "pos": 456789,
            "ref": "G",
            "alt": "C",
            "zygosity": "Heterozygous",
            "variant_inheritance": "biparental",
            "variant_type": "SNV/INDEL",
            "gene_known_for_phenotype": "Candidate"
        }]
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")
