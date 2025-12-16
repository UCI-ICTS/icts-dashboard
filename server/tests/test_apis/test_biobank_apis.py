# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_biobankn_apis.py

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


class CreateBiobankAPITest(APITestCaseWithAuth):
    def test_create_biobank_entry(self):
        url = "/api/metadata/biobank/create/"
        part1 = {  # Valid submission
            "biobank_id": "GREGoR_test-002-001-2-D-3",
            "participant_id": "GREGoR_test-002-001-2",
            "received_date": "2025-01-03",
            "specimen_type": "D",
            "current_location": "UCI",
            "freezer_id": "ULT #1",
            "shelf_id": "ULT #1 Shelf 1",
            "rack_id": "PMGRC Blood Rack 2",
            "box_type": "SBS plate",
            "box_id": "PMGRC EDTA Blood Plate 1",
            "box_position": "A12",
            "tube_barcode": "308109402",
            "plate_barcode": "47609194",
            "status": "Stored",
            "shipment_date": None,
            "tracking_number": None,
            "test_indication": None,
            "requested_test": None,
            "child_analytes": [],
            "experiments": [],
            "alignments": [],
            "internal_analysis": None,
            "comments": None,
        }
        part2 = {  # Valid submission
            "biobank_id": "GREGoR_test-002-001-2-D-20",
            "participant_id": "GREGoR_test-002-001-2",
            "received_date": "2025-01-03",
            "specimen_type": "D",
            "current_location": "UCI",
            "freezer_id": "ULT #1",
            "shelf_id": "ULT #1 Shelf 1",
            "rack_id": "PMGRC Blood Rack 1",
            "box_type": "9x9 cryobox",
            "box_id": "PMGRC Box 20",
            "box_position": "A6",
            "tube_barcode": None,
            "plate_barcode": None,
            "status": "Stored",
            "shipment_date": None,
            "tracking_number": None,
            "test_indication": None,
            "requested_test": None,
            "child_analytes": [],
            "experiments": [],
            "alignments": [],
            "internal_analysis": None,
            "comments": None,
        }
        part3 = {  # Invalid submission; non-existant participant
            "biobank_id": "DNE-002-002-2-X-1",
            "participant_id": "DNE-002-002-2",
            "received_date": "2025-01-03",
            "specimen_type": "X",
            "current_location": "UCI",
            "freezer_id": "ULT #1",
            "shelf_id": "ULT #1 Shelf 1",
            "rack_id": "PMGRC DNA Rack 1",
            "box_type": "9x9 cryobox",
            "box_id": "PMGRC DNA Box 1",
            "box_position": "I7",
            "tube_barcode": None,
            "plate_barcode": None,
            "status": "Stored",
            "shipment_date": None,
            "tracking_number": None,
            "test_indication": None,
            "requested_test": None,
            "child_analytes": [],
            "experiments": [],
            "alignments": [],
            "internal_analysis": None,
            "comments": None,
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


class ReadBiobankAPITest(APITestCaseWithAuth):
    def test_read_biobank_entry(self):
        url1 = "/api/metadata/biobank/?ids=GREGoR_test-001-001-0-R-1,GREGoR_test-002-001-2-R-1"
        url2 = "/api/metadata/biobank/?ids=GREGoR_test-001-001-0-R-1,GREGoR_test-002-001-2-R-1,DNE-01"
        url3 = "/api/metadata/biobank/?ids=DNE-01,DNE-2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateBiobankAPITest(APITestCaseWithAuth):
    def test_update_biobank_entry(self):
        url = "/api/metadata/biobank/update/"
        part1 = {  # Valid submission, data-delivered sample ready for analysis
            "biobank_id": "GREGoR_test-001-001-0-R-1",
            "status": "Ready for variant analysis",
        }
        part2 = {  # Invalid submission; non-existant biobank_id
            "biobank_id": "DNE-001-001-1",
            "participant_id": "GREGoR_test-002-002-2",
            "received_date": "2024-07-07",
            "specimen_type": "D",
            "current_location": "UCI",
            "freezer_id": "ULT #1",
            "shelf_id": "ULT #1 Shelf 1",
            "rack_id": "PAX RNA Rack 1",
            "box_type": "9x9 cryobox",
            "box_id": "12",
            "box_position": "A2",
            "tube_barcode": None,
            "plate_barcode": None,
            "status": "Stored",
            "shipment_date": None,
            "tracking_number": None,
            "testing_indication": None,
            "requested_test": None,
            "child_analytes": [],
            "experiments": [],
            "alignments": [],
            "internal_analysis": None,
            "comments": None,
        }
        part3 = {  # Analysis complete, closing case
            "biobank_id": "GREGoR_test-001-001-0-R-1",
            "completed": True,
        }
        response_200 = self.client.post(url, [part1], format="json")
        response_207 = self.client.post(url, [part3, part2], format="json")
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


class DeleteBiobankAPITest(APITestCaseWithAuth):
    def test_delete_biobank_entry(self):
        url = "/api/metadata/biobank/delete/?ids=GREGoR_test-002-001-2-R-1"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "DELETED")
