#!/usr/bin/env python3
# tests/test_apps/test_metadata/test_apis.py

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from metadata.models import Family, Participant

class FamilyModelTest(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_family_creation(self):
        family = Family.objects.first()
        self.assertIsNotNone(family)
        self.assertTrue(hasattr(family, 'family_id'))

class APITestCaseWithAuth(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

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
