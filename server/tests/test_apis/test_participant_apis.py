# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_participant_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

class APITestCaseWithAuth(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
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
            "missing_variant_case": "No"
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
            "missing_variant_case": "Unknown"
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
            "missing_variant_case": "Unknown"
        }
        response_200 = self.client.post(url, [part3], format='json')
        response_207 = self.client.post(url, [part1, part3], format='json')
        response_400 = self.client.post(url, [part2], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")

class ReadParticipantAPITest(APITestCaseWithAuth):
    def test_read_participant(self):
        url1 = "/api/metadata/participant/?ids=GREGoR_test-001-001-0,GREGoR_test-002-001-2"
        url2 = "/api/metadata/participant/?ids=GREGoR_test-001-001-0,GREGoR_test-002-001-2,DNE-01-1"
        url3 = "/api/metadata/participant/?ids=DNE-01-1,DNE-2-2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

class UpdateParticipantAPITest(APITestCaseWithAuth):
    def test_update_participant(self):
        url = "/api/metadata/participant/update/"

        part1= {  # Valid case.
            "participant_id": "GREGoR_test-001-001-0",
            "consent_code": "HMB",
            "gregor_center": "UCI",
            "family_id": "GREGoR_test-001",
            "paternal_id": "0",
            "maternal_id": "0",
            "proband_relationship": "Self",
            "sex": "Female",
            "affected_status": "Unaffected",
            "solve_status": "Unsolved",
            "age_at_last_observation": 20,
            "age_at_enrollment": 20,
            "missing_variant_case": "No"
        }
        part2 = {  # Non-existant case; should fail.
            "participant_id": "GREGoR_test-001-000-0",
            "consent_code": "HMB",
            "gregor_center": "UCI",
            "family_id": "P-001-000",
            "paternal_id": "0",
            "maternal_id": "0",
            "proband_relationship": "Self",
            "sex": "Female",
            "affected_status": "Unaffected",
            "solve_status": "Unsolved",
            "age_at_last_observation": 20,
            "age_at_enrollment": 20,
            "missing_variant_case": "No"
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

class DeleteParticipantAPITest(APITestCaseWithAuth):
    def test_delete_participant(self):
        url = "/api/metadata/participant/delete/?ids=GREGoR_test-001-001-0"
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.data[0]["request_status"], "DELETED")
