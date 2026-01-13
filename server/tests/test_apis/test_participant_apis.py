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


class CreateParticipantAPITest(APITestCaseWithAuth):
    def test_create_participant_api(self):
        url = "/api/metadata/participant/create/"
        part1 = {  # Valid submission
            "participant_id": "P-002-101-0",
            "gregor_center": "UCI",
            "consent_code": "HMB",
            "family_id": "GREGoR_test-001",
            "paternal_id": "0",
            "maternal_id": "0",
            "proband_relationship": "Self",
            "sex": "Male",
            # "reported_race": "More than one",
            # "reported_ethnicity": "Unknown",
            "age_at_last_observation": 20,
            "affected_status": "Unaffected",
            "age_at_enrollment": 20,
            "solve_status": "Unsolved",
            "missing_variant_case": "No",
        }
        part2 = {  # Invalid submission; missing participant_id
            "gregor_center": "UCI",
            "consent_code": "GRU",
            "family_id": "GREGoR_test-001",
            "paternal_id": "0",
            "maternal_id": "0",
            "proband_relationship": "Mother",
            "proband_relationship_detail": "",
            "sex": "Female",
            "sex_detail": "",
            "reported_race": [],
            "reported_ethnicity": "Hispanic or Latino",
            "ancestry_detail": "",
            "age_at_last_observation": 45.1,
            "affected_status": "Unaffected",
            "age_at_enrollment": 45.1,
            "solve_status": "Unaffected",
            "missing_variant_case": "Unknown",
        }
        part3 = {  # Valid submission
            "participant_id": "P-003-101-2",
            "gregor_center": "UCI",
            "consent_code": "GRU",
            "family_id": "GREGoR_test-001",
            "paternal_id": "0",
            "maternal_id": "0",
            "proband_relationship": "Mother",
            "proband_relationship_detail": "",
            "sex": "Female",
            "sex_detail": "",
            "reported_race": [],
            "reported_ethnicity": "Hispanic or Latino",
            "ancestry_detail": "",
            "age_at_last_observation": 45.1,
            "affected_status": "Unaffected",
            "age_at_enrollment": 45.1,
            "solve_status": "Unaffected",
            "missing_variant_case": "Unknown",
        }
        response_200 = self.client.post(url, [part3], format="json")
        response_207 = self.client.post(url, [part1, part3], format="json")
        response_400 = self.client.post(url, [part2], format="json")
        changed_by(self, response_200.data[0], testuser)
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        changed_by(self, response_207.data[0], testuser)
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")


class ReadParticipantAPITest(APITestCaseWithAuth):
    def test_read_participant(self):
        url1 = (
            "/api/metadata/participant/?ids=GREGoR_test-001-001-0,GREGoR_test-002-001-2"
        )
        url2 = "/api/metadata/participant/?ids=GREGoR_test-001-001-0,GREGoR_test-002-001-2,DNE-01-1"
        url3 = "/api/metadata/participant/?ids=DNE-01-1,DNE-2-2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateParticipantAPITest(APITestCaseWithAuth):
    def test_update_participant(self):
        url = "/api/metadata/participant/update/"

        part1 = {  # Valid case.
            "participant_id": "GREGoR_test-004-004-0",
            "age_at_last_observation": 20,
            "age_at_enrollment": 20,
        }

        part2 = {  # Non-existant case; should fail.
            "participant_id": "GREGoR_test-001-000-0",
            "gregor_center": "UCI",
            "consent_code": "GRU",
            "recontactable": "Yes",
            "prior_testing": [
                "neuromuscular panel: VUS in FLNC maternally inherited (c.4334A>G), VUS in GUS1 c.314G>A heterozygous maternally inherited, VUS in NEB c.8968A>G heterozygous, maternally inherited. VUS on WES, CHD1:c.1010C>T, p.(T337I), heterozygous, de novo"
            ],
            "family_id": "GREGoR_test-001",
            "paternal_id": "GREGoR_test-003-001-1",
            "maternal_id": "GREGoR_test-002-001-2",
            "proband_relationship": "Self",
            "proband_relationship_detail": "",
            "sex": "Male",
            "sex_detail": "",
            "reported_ethnicity": "Hispanic or Latino",
            "ancestry_detail": "",
            "age_at_last_observation": 9.0,
            "affected_status": "Affected",
            "phenotype_description": [
                "early childhood onset weakness, early motor delay, hypotonia, dysarthria, autism spectrum disorder, stereotypic behavior"
            ],
            "age_at_enrollment": 9.0,
            "solve_status": "Unsolved",
            "missing_variant_case": "Yes",
            "missing_variant_details": "Het NM_032125.3(TMEM222):c.214G>A (p.Gly72Ser), possible OMIM 619470",
            "internal_project_id": [],
            "pmid_id": [],
            "twin_id": ["0"],
            "reported_race": ["White"]
        }

        response_207 = self.client.post(url, [part1, part2], format="json")
        response_200 = self.client.post(url, [part1], format="json")
        response_400 = self.client.post(url, [part2, part2], format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        changed_by(self, response_200.data[0], testuser)
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        changed_by(self, response_207.data[0], testuser)
        timestamps(self, response_207.data[0])
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteParticipantAPITest(APITestCaseWithAuth):
    def test_delete_participant(self):
        delete_url = "/api/metadata/participant/delete/?ids=GREGoR_test-001-001-0"
        delete_response = self.client.delete(delete_url, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(delete_response.data[0]["data"][:113],
                         '("Cannot delete some instances of model \'Participant\' because they are referenced through protected foreign keys:')


    def test_create_and_delete_participant_api(self):
        create_url = "/api/metadata/participant/create/"
        part1 = {  # Valid submission
            "participant_id": "P-002-101-0",
            "gregor_center": "UCI",
            "consent_code": "HMB",
            "family_id": "GREGoR_test-001",
            "paternal_id": "0",
            "maternal_id": "0",
            "proband_relationship": "Self",
            "sex": "Male",
            # "reported_race": "More than one",
            # "reported_ethnicity": "Unknown",
            "age_at_last_observation": 20,
            "affected_status": "Unaffected",
            "age_at_enrollment": 20,
            "solve_status": "Unsolved",
            "missing_variant_case": "No",
        }
        create_response = self.client.post(create_url, [part1], format="json")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)

        delete_url = "/api/metadata/participant/delete/?ids=P-002-101-0"
        delete_response = self.client.delete(delete_url, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data[0]["request_status"], "DELETED")


class ListAllParticipants(APITestCaseWithAuth):
    def test_list_all_participants(self):
        url = "/api/metadata/participant/all/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
