# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_participant_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User


class APITestCaseWithAuth(APITestCase):
    fixtures = ["tests/fixtures/test_fixture.json"]

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)


class CreatePhenotypeAPITest(APITestCaseWithAuth):
    def test_create_analyte_api(self):
        url = "/api/metadata/phenotype/create/"
        part1 = {  # Valid submission
            "phenotype_id": "1.10",
            "participant_id": "GREGoR_test-001-001-0",
            "term_id": "HP:0002194",
            "presence": "Present",
            "ontology": "HPO",
            "additional_details": "gross motor delay",
            "onset_age_range": "HP:0011463",
            "additional_modifiers": [],
            "syndromic": "non-syndromic",
        }
        part2 = {  # Valid submission 2
            "phenotype_id": "1.11",
            "participant_id": "GREGoR_test-001-001-0",
            "term_id": "HP:0002195",
            "presence": "Present",
            "ontology": "HPO",
            "additional_details": "Dysgenesis of the cerebellar vermis",
            "onset_age_range": "HP:0011463",
            "additional_modifiers": [],
            "syndromic": "non-syndromic",
        }
        part3 = {  # Invalid submission; missing ontology
            "phenotype_id": "1.12",
            "participant_id": "GREGoR_test-001-001-0",
            "term_id": "HP:0002196",
            "presence": "Present",
            "ontology": "",
            "additional_details": "Myelopathy",
            "onset_age_range": "HP:0011463",
            "additional_modifiers": [],
            "syndromic": "non-syndromic",
        }
        response_200 = self.client.post(url, [part1], format="json")
        response_207 = self.client.post(url, [part2, part3], format="json")
        response_400 = self.client.post(url, [part3], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadPhenotypeAPITest(APITestCaseWithAuth):
    def test_read_phenotype_success(self):
        url1 = "/api/metadata/phenotype/?ids=1.2,1.3"
        url2 = "/api/metadata/phenotype/?ids=1.2,1.3,1.99"
        url3 = "/api/metadata/phenotype/?ids=1.99,1.100"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdatePhenotypeAPITest(APITestCaseWithAuth):
    def test_update_phenotype_api(self):
        url = "/api/metadata/phenotype/update/"
        part1 = {  # Valid submission
            "phenotype_id": "1.2",
            "participant_id": "GREGoR_test-001-001-0",
            "term_id": "HP:0002194",
            "presence": "Present",
            "ontology": "HPO",
            "additional_details": "gross motor delay",
            "onset_age_range": "HP:0011463",
            "additional_modifiers": ["HP:0025292"],
            "syndromic": "non-syndromic",
        }
        part2 = {  # Invalid submission; invalid additional_modifiers
            "phenotype_id": "1.3",
            "participant_id": "GREGoR_test-002-001-2",
            "term_id": "HP:0002076",
            "presence": "Present",
            "ontology": "HPO",
            "additional_details": "migraines",
            "onset_age_range": "HP:0003621",
            "additional_modifiers": ["feeding difficulties"],
            "syndromic": "non-syndromic",
        }
        response_200 = self.client.post(url, [part1], format="json")
        response_207 = self.client.post(url, [part1, part2], format="json")
        response_400 = self.client.post(url, [part2], format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class DeletePhenotypeAPITest(APITestCaseWithAuth):
    def test_delete_phenotype(self):
        url = "/api/metadata/phenotype/delete/?ids=1.2"
        response = self.client.delete(url, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "DELETED")
