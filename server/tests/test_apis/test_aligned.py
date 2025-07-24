# #!/usr/bin/env python3
# tests/test_apis/test_aligned.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from experiments.models import Experiment


class APITestCaseWithAuth(APITestCase):
    fixtures = ["tests/fixtures/test_fixture.json"]

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)


class ReadAlignedTest(APITestCaseWithAuth):
    def test_read_experiment_dna_short_read(self):
        id1 = "aligned_dna_short_read.UCI_GREGoR_test-001-001-0-D-1_DNA_1-Aligned_1"
        id2 = "aligned_nanopore.UCI_GREGoR_test-004-004-0-D-3_NANO_1-Aligned_1"
        id3 = "aligned_pac_bio.UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1"
        bad_id = "BadId"

        url1 = f"/api/experiments/aligned/?ids={id1},{id2}"
        url2 = f"/api/experiments/aligned/?ids={id1},{bad_id}"
        url3 = f"/api/experiments/aligned/?ids={bad_id}"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ListAlignedTest(APITestCaseWithAuth):
    def test_read_experiment_dna_short_read(self):
        url1 = "/api/experiments/aligned/all/"

        response_200 = self.client.get(url1, format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
