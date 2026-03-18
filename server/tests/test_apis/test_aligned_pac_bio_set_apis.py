# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_pac_bio_apis.py

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


class CreateAlignedPacBioSetAPITest(APITestCaseWithAuth):
    def test_create_aligned_pac_bio_set_api(self):
        url = "/api/experiments/aligned_pac_bio_set/create/"

        aligned1 = {  # New entry to be entered twice. Is valid the first time but not the second time
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1-deepvariant_phased_2",
            "aligned_pac_bio_id": ["UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1"],
        }

        aligned2 = {  # New entry
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_2",
            "aligned_pac_bio_id": ["UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1"],
        }

        aligned3 = {  # New entry, invalid
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_1-deepvariant_phased_2",
            "aligned_pac_bio_id": [],  # missing
        }

        response_200 = self.client.post(url, [aligned2], format="json")
        response_207 = self.client.post(url, [aligned1, aligned3], format="json")
        response_400 = self.client.post(url, [aligned1], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        changed_by(self, response_200.data[0], testuser)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        changed_by(self, response_207.data[0], testuser)
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadAlignedPacBioSetAPITest(APITestCaseWithAuth):
    def test_read_aligned_pac_bio_set(self):
        url1 = "/api/experiments/aligned_pac_bio_set/?ids=UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1-deepvariant_phased_1"
        url2 = "/api/experiments/aligned_pac_bio_set/?ids=UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_1,DNE-01-1"
        url3 = "/api/experiments/aligned_pac_bio_set/?ids=DNE-1,DNE2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdatePacBioSetAPITest(APITestCaseWithAuth):
    def test_update_aligned_pac_bio_set_api(self):
        url = "/api/experiments/aligned_pac_bio_set/update/"

        aligned1 = {  # Valid, added aligned ID to existing set
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1-deepvariant_phased_1",
            "aligned_pac_bio_id": [
                "UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1",
                "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1",
            ],
        }

        aligned2 = {  # Invalid, missing aligned ids
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_1",
            "aligned_pac_bio_id": [],  # missing
        }

        response_200 = self.client.post(url, [aligned1], format="json")
        response_207 = self.client.post(url, [aligned1, aligned2], format="json")
        response_400 = self.client.post(url, [aligned2], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        changed_by(self, response_200.data[0], testuser)
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "NO CHANGE")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteAlignedPacBioSetAPITest(APITestCaseWithAuth):
    def test_delete_pac_bio_set_api(self):
        url2 = "/api/experiments/aligned_pac_bio_set/delete/?ids=UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1-deepvariant_phased_1-delete,DNE-01-1"
        url3 = "/api/experiments/aligned_pac_bio_set/delete/?ids=DNE-1,DNE2"

        response_207 = self.client.delete(url2, format="json")
        response_400 = self.client.delete(url3, format="json")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
