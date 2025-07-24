#!/usr/bin/env python3
# tests/test_apis/test_experiment.py

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


class ReadExperimentsTest(APITestCaseWithAuth):
    def test_read_experiment_dna_short_read(self):
        id1 = "experiment_dna_short_read.UCI_GREGoR_test-001-001-0-D-1_DNA_1"
        id2 = "experiment_pac_bio.UCI_GREGoR_test-001-001-0-D-2_PB_1"
        id3 = "experiment_nanopore.UCI_GREGoR_test-006-006-0-D-3_NANO_1"
        bad_id = "BadId"

        url1 = f"/api/experiments/experiment/?ids={id1},{id2}"
        url2 = f"/api/experiments/experiment/?ids={id1},{bad_id}"
        url3 = f"/api/experiments/experiment/?ids={bad_id}"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ListExperimentsTest(APITestCaseWithAuth):
    def test_read_experiment_dna_short_read(self):
        url1 = "/api/experiments/experiment/all/"

        response_200 = self.client.get(url1, format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
