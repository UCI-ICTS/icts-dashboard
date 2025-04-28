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


class CreateExperimentStageAPITest(APITestCaseWithAuth):
    def test_create_experiment_stage_entry(self):
        url = "/api/metadata/experiment_stage/create/"
        part1 = {  # Valid submission
            "experiment_stage_id": "GREGoR_test-001-001-0-D-2",
            "analyte_id": "GREGoR_test-001-001-0-D-2",
            "test_indication": "Research",
            "requested_test": "10500",
            "collection_date": "2025-01-03",
            "specimen_type": "D",
            "shipment_date": "2025-04-14",
            "status": "Shipped",
            "current_location": "Ambry",
            "tracking_number": "123456789123",
            "experiments": [],
            "alignments": [],
            "external_id": None,
            "comments": None,
            "internal_analysis": None,
        }
        part2 = {  # Valid submission
            "experiment_stage_id": "GREGoR_test-001-001-0-D-3",
            "analyte_id": "GREGoR_test-001-001-0-D-3",
            "test_indication": "Research",
            "requested_test": "10525",
            "collection_date": "2025-01-03",
            "specimen_type": "R",
            "shipment_date": "2025-04-14",
            "status": "Sequenced",
            "current_location": "Ambry",
            "tracking_number": "123456789123",
            "experiments": [],
            "alignments": [],
            "external_id": None,
            "comments": None,
            "internal_analysis": None,
        }
        part3 = {  # Invalid submission; non-existant participant
            "experiment_stage_id": "DNE-002-001-2-D-1",
            "analyte_id": "DNE-002-001-2-D-1",
            "test_indication": "Research",
            "requested_test": "10500",
            "collection_date": "2025-01-03",
            "specimen_type": "D",
            "shipment_date": "2025-04-14",
            "status": "Shipped",
            "current_location": "Ambry",
            "tracking_number": "123456789123",
            "experiments": [],
            "alignments": [],
            "external_id": None,
            "comments": None,
            "internal_analysis": None,
        }
        response_200 = self.client.post(url, [part1], format="json")
        response_207 = self.client.post(url, [part2, part3], format="json")
        response_400 = self.client.post(url, [part3], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadExperimentStageAPITest(APITestCaseWithAuth):
    def test_read_experiment_stage_entry(self):
        url1 = "/api/metadata/experiment_stage/?ids=GREGoR_test-001-001-0-D-1,GREGoR_test-002-001-2-D-1"
        url2 = "/api/metadata/experiment_stage/?ids=GREGoR_test-001-001-0-D-1,GREGoR_test-002-001-2-D-1,DNE-01"
        url3 = "/api/metadata/experiment_stage/?ids=DNE-01,DNE-2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateExperimentStageAPITest(APITestCaseWithAuth):
    def test_update_experiment_stage_entry(self):
        url = "/api/metadata/experiment_stage/update/"
        part1 = {  # Valid submission, stored sample shipped out. New experiment created.
            "experiment_stage_id": "GREGoR_test-001-001-0-D-1",
            "analyte_id": "GREGoR_test-001-001-0-D-1",
            "test_indication": "Research",
            "requested_test": "10500",
            "collection_date": "2025-01-03",
            "specimen_type": "D",
            "shipment_date": "2025-04-14",
            "status": "Shipped",
            "current_location": "Ambry",
            "tracking_number": "123456789123",
            "experiments": ["GREGoR_test-001-001-0-D-1.PB"],
            "alignments": ["GREGoR_test-001-001-0-D-1.PB.aligned"],
            "external_id": None,
            "comments": None,
            "internal_analysis": None,
        }
        part2 = {  # Invalid submission; non-existant experiment_stage_id
            "experiment_stage_id": "GREGoR_test-002-001-2-D-10",
            "analyte_id": "GREGoR_test-002-001-2-D-10",
            "test_indication": "Research",
            "requested_test": "10500",
            "collection_date": "2025-01-03",
            "specimen_type": "D",
            "shipment_date": "2025-04-14",
            "status": "Shipped",
            "current_location": "Ambry",
            "tracking_number": "123456789123",
            "experiments": [],
            "alignments": [],
            "external_id": None,
            "comments": None,
            "internal_analysis": None,
        }
        response_200 = self.client.post(url, [part1], format="json")
        response_207 = self.client.post(url, [part1, part2], format="json")
        response_400 = self.client.post(url, [part2], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteExperimentStageAPITest(APITestCaseWithAuth):
    def test_delete_experiment_stage_entry(self):
        url = "/api/metadata/experiment_stage/delete/?ids=GREGoR_test-002-001-2-D-1"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "DELETED")
