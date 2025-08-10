# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_family_apis.py

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


class DeleteFamilyAPITest(APITestCaseWithAuth):
    def test_delete_family_api(self):
        url1 = "/api/metadata/family/delete/?ids=GREGoR_test-001"
        url2 = "/api/metadata/family/delete/?ids=GREGoR_test_delete-001"
        bad_response = self.client.delete(url1, format="json")
        good_response = self.client.delete(url2, format="json")
        self.assertEqual(bad_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(bad_response.data[0]["request_status"], "SERVER ERROR")
        self.assertEqual(good_response.status_code, status.HTTP_200_OK)
        self.assertEqual(good_response.data[0]["request_status"], "DELETED")


    def verify_delete_cascade(self):
        urls = {
            "family": "/api/metadata/family/?ids=GREGoR_test-001",
            "participant": "/api/metadata/participant/?ids=" \
                            "GREGoR_test-001-001-0," \
                            "GREGoR_test-003-001-1," \
                            "GREGoR_test-002-001-2",
            "phenotype": "/api/metadata/phenotype/?ids=" \
                        "1.2," \
                        "1.3," \
                        "1.4," \
                        "1.5," \
                        "1.6," \
                        "1.7," \
                        "1.8," \
                        "1.9",
            "analyte": "/api/metadata/analyte/?ids=" \
                        "GREGoR_test-001-001-0-D-1," \
                        "GREGoR_test-001-001-0-D-2," \
                        "GREGoR_test-001-001-0-D-3," \
                        "GREGoR_test-001-001-0-OG-1," \
                        "GREGoR_test-001-001-0-R-1," \
                        "GREGoR_test-001-001-0-R-2," \
                        "GREGoR_test-001-001-0-X-1",
            "experiment_dna_short_read": "/api/experiment/experiment_dna_short_read/?ids=" \
                                        "UCI_GREGoR_test-001-001-0-D-1_DNA_1," \
                                        "UCI_GREGoR_test-002-001-2-D-1_DNA_1," \
                                        "UCI_GREGoR_test-003-001-1-D-1_DNA_1",
            "aligned_dna_short_read": "/api/experiment/aligned_dna_short_read/?ids=" \
                                        "UCI_GREGoR_test-001-001-0-D-1_DNA_1-Aligned_1," \
                                        "UCI_GREGoR_test-002-001-2-D-1_DNA_1-Aligned_1," \
                                        "UCI_GREGoR_test-003-001-1-D-1_DNA_1-Aligned_1",
            "experiment_rna_short_read": "/api/experiment/experiment_rna_short_read/?ids=UCI_GREGoR_test-001-001-0-R-1_RNA_1",
            "aligned_rna_short_read": "/api/experiment/aligned_rna_short_read/?ids=UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1",
            "experiment_pac_bio": "/api/experiment/experiment_pac_bio/?ids=" \
                    "UCI_GREGoR_test-001-001-0-D-2_PB_1," \
                    "UCI_GREGoR_test-002-001-2-D-2_PB_1," \
                    "UCI_GREGoR_test-003-001-1-D-2_PB_1",
            "aligned_pac_bio": "/api/experiment/aligned_pac_bio/?ids=" \
                    "UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1," \
                    "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1," \
                    "UCI_GREGoR_test-003-001-2-D-1_PB_1-Aligned_1",
            "experiment_nanopore": "/api/experiment/experiment_nanopore/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_1",
            "aligned_nanopore": "/api/experiment/aligned_nanopore/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1",
            "biobank": "/api/metadata/biobank/?ids=" \
                    "GREGoR_test-001-001-0-D-1," \
                    "GREGoR_test-001-001-0-D-2," \
                    "GREGoR_test-001-001-0-D-3," \
                    "GREGoR_test-001-001-0-OG-1," \
                    "GREGoR_test-001-001-0-R-1," \
                    "GREGoR_test-001-001-0-X-1," \
                    "GREGoR_test-002-001-2-D-1," \
                    "GREGoR_test-002-001-2-D-2," \
                    "GREGoR_test-002-001-2-R-1," \
                    "GREGoR_test-003-001-1-D-1," \
                    "GREGoR_test-003-001-1-D-2," \
                    "GREGoR_test-003-001-1-R-1",
            "genetic_findings": "/api/metadata/genetic_findings/?ids=" \
                    "10_73792184_GREGoR_test-001-001-0," \
                    "2_6849938_GREGoR_test-001-001-0," \
                    "2_6865407_GREGoR_test-001-001-0," \
                    "5_98899555_GREGoR_test-001-001-0"
        }

        responses = dict()
        for table in urls:
            responses[table] = self.client.get(urls[table], format="json")
            self.assertEqual(responses[table].status_code, status.HTTP_400_BAD_REQUEST)
            for datum in responses[table].data:
                self.assertEqual(datum["request_status"], "NOT FOUND")