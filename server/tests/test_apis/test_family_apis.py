# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_family_apis.py

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
            username=testuser, password="testpassword"
        )
        self.client.force_authenticate(user=self.user)


class CreateFamilyAPITest(APITestCaseWithAuth):
    def test_create_family_api(self):
        url = "/api/metadata/family/create/"
        part1 = {  # Valid submission
            "family_id": "P-101",
            "consanguinity": "Unknown",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": "",
        }
        part2 = {  # Valid submission 2
            "family_id": "P-102",
            "consanguinity": "Present",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": "",
        }
        part3 = {  # Invalid submission; missing consanguinity
            "family_id": "P-103",
            "consanguinity": "",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": "",
        }
        response_200 = self.client.post(url, [part1], format="json")
        response_207 = self.client.post(url, [part2, part3], format="json")
        response_400 = self.client.post(url, [part3], format="json")
        changed_by(self, response_200.data[0], testuser)
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        changed_by(self, response_207.data[0], testuser)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadFamilyAPITest(APITestCaseWithAuth):
    def test_read_family_success(self):
        url1 = "/api/metadata/family/?ids=GREGoR_test-006,GREGoR_test-004"
        url2 = "/api/metadata/family/?ids=GREGoR_test-006,GREGoR_test-004,DNE-01"
        url3 = "/api/metadata/family/?ids=DNE-01,DNE-2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateFamilyAPITest(APITestCaseWithAuth):
    def test_update_family_api(self):
        url = "/api/metadata/family/update/"
        part1 = {  # Valid submission
            "family_id": "GREGoR_test-006",
            "consanguinity": "Unknown",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "New pedigree found",
            "family_history_detail": "Non contributory",
        }
        part2 = {  # Invalid submission; missing consanguinity
            "family_id": "GREGoR_test-004",
            "consanguinity": "",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": "New family history finding",
        }

        response_207 = self.client.post(url, [part1, part2], format="json")
        response_200 = self.client.post(url, [part1], format="json")
        response_400 = self.client.post(url, [part2, part2], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        changed_by(self, response_200.data[0], testuser)
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        changed_by(self, response_200.data[0], testuser)
        timestamps(self, response_207.data[0])
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteFamilyAPITest(APITestCaseWithAuth):
    def test_delete_family_api(self):
        url = "/api/metadata/family/delete/?ids=GREGoR_test-001"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0]["data"][:108],
                         '("Cannot delete some instances of model \'Family\' because they are referenced through protected foreign keys:')


    def test_create_and_delete_family_api(self):
        create_url = "/api/metadata/family/create/"
        fam1 = {  # Valid submission
            "changed_by": testuser,
            "family_id": "P-101",
            "consanguinity": "Unknown",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": "",
        }
        create_response = self.client.post(create_url, [fam1], format="json")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)

        delete_url = "/api/metadata/family/delete/?ids=P-101"
        response = self.client.delete(delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "DELETED")


class ListAllFamilyAPITest(APITestCaseWithAuth):
    def test_list_all_families(self):
        url = "/api/metadata/family/all/"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertIn("family_id", response.data[0])

    def test_list_all_families_suppresses_requested_fields(self):
        base_url = "/api/metadata/family/all/"
        baseline_response = self.client.get(base_url, format="json")
        suppressed_response = self.client.get(
            f"{base_url}?suppress=consanguinity,pedigree_file_detail",
            format="json",
        )

        self.assertEqual(baseline_response.status_code, status.HTTP_200_OK)
        self.assertEqual(suppressed_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(baseline_response.data), 0)
        self.assertEqual(len(suppressed_response.data), len(baseline_response.data))
        self.assertIn("consanguinity", baseline_response.data[0])
        self.assertIn("pedigree_file_detail", baseline_response.data[0])

        for family in suppressed_response.data:
            self.assertIn("family_id", family)
            self.assertNotIn("consanguinity", family)
            self.assertNotIn("pedigree_file_detail", family)

