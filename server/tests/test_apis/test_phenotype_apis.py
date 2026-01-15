# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_participant_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from datetime import datetime


testuser = "testuser"


def changed_by(self, response_dict, changed_by):
    """
    Assert changed_by username matches expected changed_by username
    """
    self.assertEqual(response_dict["data"]["instance"]["changed_by"], changed_by)


def timestamps(self, response_dict):
    """
    Assert updated_at and created_at times differ after a successful update
    """
    updated_at = datetime.strptime(
            response_dict["data"]["instance"]["updated_at"].rstrip('Z').split('.')[0],
            "%Y-%m-%dT%H:%M:%S"
            ).timestamp()
    created_at = datetime.strptime(
            response_dict["data"]["instance"]["created_at"].rstrip('Z').split('.')[0],
            "%Y-%m-%dT%H:%M:%S"
            ).timestamp()
    self.assertGreater(updated_at, created_at)


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
        changed_by(self, response_200.data[0], testuser)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        changed_by(self, response_207.data[0], testuser)
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadPhenotypeAPITest(APITestCaseWithAuth):
    def test_read_phenotype_success(self):
        url1 = "/api/metadata/phenotype/?ids=1.2,1.7"
        url2 = "/api/metadata/phenotype/?ids=1.2,1.7,1.99"
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
            "additional_modifiers": ["HP:0025292"],
            "syndromic": "non-syndromic",
        }

        part2 = {  # Invalid submission; invalid syndromic
            "phenotype_id": "1.4",
            "term_id": "HP:0000733",
            "presence": "Present",
            "ontology": "HPO",
            "additional_details": "Stereotypic behavior",
            "onset_age_range": "HP:0003621",
            "additional_modifiers": [],
            "syndromic": "Invalid submission",
            "participant_id": "GREGoR_test-001-001-0"
        }
        response_207 = self.client.post(url, [part1, part2], format="json")
        response_200 = self.client.post(url, [part1], format="json")
        response_400 = self.client.post(url, [part2], format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        changed_by(self, response_200.data[0], testuser)
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        changed_by(self, response_207.data[0], testuser)
        timestamps(self, response_207.data[0])
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class DeletePhenotypeAPITest(APITestCaseWithAuth):
    def test_delete_phenotype(self):
        url = "/api/metadata/phenotype/delete/?ids=1.2"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["data"], "phenotype 1.2 deleted successfully.")


    def test_create_and_delete_analyte_api(self):
        create_url = "/api/metadata/phenotype/create/"
        pheno1 = {  # Valid submission
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
        create_response = self.client.post(create_url, [pheno1], format="json")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)

        delete_url = "/api/metadata/phenotype/delete/?ids=1.10"
        delete_response = self.client.delete(delete_url, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data[0]["request_status"], "DELETED")
