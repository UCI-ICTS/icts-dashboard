# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_participant_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from datetime import datetime


testuser = "testuser"


def created_by(self, response_dict, created_user):
    """
    Assert created_by username matches expected created_by username
    """
    self.assertEqual(response_dict["data"]["instance"]["created_by"], created_user)


def usernames(self, response_dict):
    """
    Assert updated_by and created_by usernames differ after a successful update
    """
    self.assertNotEqual(
        response_dict["data"]["instance"]["updated_by"],
        response_dict["data"]["instance"]["created_by"]
    )


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


class CreateAnalyteAPITest(APITestCaseWithAuth):
    def test_create_analyte_api(self):
        url = "/api/metadata/analyte/create/"
        part1 = {  # Valid submission
            "analyte_id": "P-101-101-0-D-1",
            "participant_id": "GREGoR_test-001-001-0",
            "analyte_type": "frozen whole blood",
            "primary_biosample": "UBERON:0000178",
        }
        part2 = {  # Valid submission
            "analyte_id": "P-101-101-0-D-2",
            "participant_id": "GREGoR_test-001-001-0",
            "analyte_type": "frozen whole blood",
            "primary_biosample": "UBERON:0000178",
        }
        part3 = {  # Invalid submission; analyte_type
            "analyte_id": "P-101-101-0-D-3",
            "participant_id": "GREGoR_test-001-001-0",
            "analyte_type": "",
            "primary_biosample": "UBERON:0000178",
        }
        response_200 = self.client.post(url, [part1], format="json")
        response_207 = self.client.post(url, [part2, part3], format="json")
        response_400 = self.client.post(url, [part3], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        created_by(self, response_200.data[0], testuser)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        created_by(self, response_207.data[0], testuser)
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadAnalyteAPITest(APITestCaseWithAuth):
    def test_read_analyte_success(self):
        url1 = "/api/metadata/analyte/?ids=GREGoR_test-001-001-0-R-1,GREGoR_test-001-001-0-R-2"
        url2 = "/api/metadata/analyte/?ids=GREGoR_test-001-001-0-R-1,GREGoR_test-001-001-0-R-2,DNE-01"
        url3 = "/api/metadata/analyte/?ids=DNE-01,DNE-2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateAnalyteAPITest(APITestCaseWithAuth):
    def test_update_analyte_api(self):
        url = "/api/metadata/analyte/update/"
        part1 = {  # Valid submission
            "analyte_id": "GREGoR_test-001-001-0-R-1",
            "participant_id": "GREGoR_test-001-001-0",
            "analyte_type": "frozen whole blood",
            "primary_biosample": "UBERON:0000178",
        }
        part2 = {  # Invalid submission; analyte_type
            "analyte_id": "GREGoR_test-001-001-0-R-1",
            "participant_id": "GREGoR_test-001-001-0",
            "analyte_type": "",
            "primary_biosample": "UBERON:0000178",
        }

        response_207 = self.client.post(url, [part1, part2], format="json")
        response_200 = self.client.post(url, [part1], format="json")
        response_400 = self.client.post(url, [part2], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        usernames(self, response_200.data[0])
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        usernames(self, response_207.data[0])
        timestamps(self, response_207.data[0])
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteAnalyteAPITest(APITestCaseWithAuth):
    def test_delete_analyte(self):
        url = "/api/metadata/analyte/delete/?ids=GREGoR_test-001-001-0-R-1"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0]["data"][:109],
                         '("Cannot delete some instances of model \'Analyte\' because they are referenced through protected foreign keys:')


    def test_create_and_delete_analyte_api(self):
        create_url = "/api/metadata/analyte/create/"
        analyte1 = {  # Valid submission
            "analyte_id": "P-101-101-0-D-1",
            "participant_id": "GREGoR_test-001-001-0",
            "analyte_type": "frozen whole blood",
            "primary_biosample": "UBERON:0000178",
        }
        create_response = self.client.post(create_url, [analyte1], format="json")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)

        delete_url = "/api/metadata/analyte/delete/?ids=P-101-101-0-D-1"
        delete_response = self.client.delete(delete_url, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data[0]["request_status"], "DELETED")