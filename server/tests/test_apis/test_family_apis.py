# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_family_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

class APITestCaseWithAuth(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

class CreateFamilyAPITest(APITestCaseWithAuth):
    def test_create_family_api(self):
        url = "/api/metadata/create_families/"
        part1 = {  # Valid submission
            "family_id": "P-101",
            "consanguinity": "Unknown",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": ""
        }
        part2 = {  # Valid submission 2
            "family_id": "P-102",
            "consanguinity": "Present",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": ""
        }
        part3 = {  # Invalid submission; missing consanguinity
            "family_id": "P-103",
            "consanguinity": "",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": ""
        }
        response_200 = self.client.post(url, [part1], format='json')
        response_207 = self.client.post(url, [part2, part3], format='json')
        response_400 = self.client.post(url, [part3], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadFamilyAPITest(APITestCaseWithAuth):
    def test_read_family_success(self):
        url1 = "/api/metadata/read_families/?ids=GREGoR_test-001,GREGoR_test-002"
        url2 = "/api/metadata/read_families/?ids=GREGoR_test-001,GREGoR_test-002,DNE-01"
        url3 = "/api/metadata/read_families/?ids=DNE-01,DNE-2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

class UpdateFamilyAPITest(APITestCaseWithAuth):
    def test_update_family_api(self):
        url = "/api/metadata/update_families/"
        part1 = {  # Valid submission
            "family_id": "GREGoR_test-001",
            "consanguinity": "Present",
            "consanguinity_detail": "New consanguinity detail found",
            "pedigree_file": "s3://gregor-data/P-101/P-101.ped",
            "pedigree_file_detail": "New pedigree found",
            "family_history_detail": ""
        }
        part2 = {  # Invalid submission; missing consanguinity
            "family_id": "GREGoR_test-002",
            "consanguinity": "",
            "consanguinity_detail": "",
            "pedigree_file": "",
            "pedigree_file_detail": "",
            "family_history_detail": "New family history finding"
        }
        response_200 = self.client.post(url, [part1], format='json')
        response_207 = self.client.post(url, [part1, part2], format='json')
        response_400 = self.client.post(url, [part2, part2], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

class DeleteFamilyAPITest(APITestCaseWithAuth):
    def test_delete_family_api(self):
        url = "/api/metadata/delete_families/?ids=GREGoR_test-001"
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "DELETED")