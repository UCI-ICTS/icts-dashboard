# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_nanopore_apis.py

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


class CreateCalledVariantsNanoporeAPITest(APITestCaseWithAuth):
    def test_create_called_variants_nanopore_api(self):
        url = "/api/experiments/called_variants_nanopore/create/"

        called_variants1 = {  # New entry to be entered twice. Is valid the first time but not the second time
            "called_variants_nanopore_id": "UCI_GREGoR_test-NANO-joint-chr1-SNV_2",
            "aligned_nanopore_set_id": "UCI_GREGoR_test-NANO-joint-chr1-SNV_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/nanopore/GREGoR_test-NANO-joint.chr1.phased.vcf.gz",
            "md5sum": "1a437f17cc113817e59fcd9bb64a50e2",
            "caller_software": [
                "DeepVariant_version=1.5.0",
                "GLNexus_version=v1.4.1"
            ],
            "variant_types": [
                "SNV",
                "INDEL"
            ],
            "analysis_details": "UCSC Nanopore Pipeline 2023-03-03",
            "chrom": "1"
        }

        called_variants2 = {  # New entry
            "called_variants_nanopore_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_1-Aligned_1-SNV_2",
            "aligned_nanopore_set_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_1-Aligned_1-SNV_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/nanopore/GREGoR_test-004-004-0.phased.vcf.gz",
            "md5sum": "7147fbc6543730fbea97acebfb54e961",
            "caller_software": ["DeepVariant_version=1.5.0"],
            "variant_types": [
                "SNV",
                "INDEL"
            ],
            "analysis_details": "UCSC Nanopore Pipeline 2023-03-03",
            "chrom": "ALL"
        }

        called_variants3 = {  # New entry, invalid
            "called_variants_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_1-SNV_2",
            "aligned_nanopore_set_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_1-SNV_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/nanopore/GREGoR_test-006-006-0.phased.vcf.gz",
            "md5sum": "f1665d870d56e4609fbbdff124547176",
            "caller_software": [],  # Invalid, must have a value
            "variant_types": [
                "SNV",
                "INDEL"
            ],
            "analysis_details": "UCSC Nanopore Pipeline 2023-03-03",
            "chrom": "ALL"
        }

        response_200 = self.client.post(url, [called_variants2], format="json")
        response_207 = self.client.post(url, [called_variants1, called_variants3], format="json")
        response_400 = self.client.post(url, [called_variants3, called_variants3], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        changed_by(self, response_200.data[0], testuser)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        changed_by(self, response_207.data[0], testuser)
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadCalledVariantsNanoporeAPITest(APITestCaseWithAuth):
    def test_read_called_variants_nanopore(self):
        url1 = "/api/experiments/called_variants_nanopore/?ids=UCI_GREGoR_test-NANO-joint-chr1-SNV_1"
        url2 = "/api/experiments/called_variants_nanopore/?ids=UCI_GREGoR_test-004-004-0-D-3_NANO_1-Aligned_1-SNV_1,DNE-01-1"
        url3 = "/api/experiments/called_variants_nanopore/?ids=DNE-1,DNE2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateNanoporeAPITest(APITestCaseWithAuth):
    def test_update_called_variants_nanopore_api(self):
        url = "/api/experiments/called_variants_nanopore/update/"
        called_variants1 = {  # Valid, edited analysis_details
            "called_variants_nanopore_id": "UCI_GREGoR_test-NANO-joint-chr1-SNV_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/nanopore/GREGoR_test-NANO-joint.chr1.phased.anno.vcf.gz",  # new vcf file
            "md5sum": "4097b353167528799589bca1d3bdc3b9",  # new md5sum
            "caller_software": [
                "DeepVariant_version=1.5.0",
                "GLNexus_version=v1.4.1",
                "ANNOVAR=20250721",  # New tool added
            ],
            "analysis_details": "UCSC Nanopore Pipeline 2023-03-03. Annotated with ANNOVAR",  # new description
        }

        called_variants2 = {  # Invalid variant_types
            "called_variants_nanopore_id": "UCI_GREGoR_test-002-001-2-D-1_DNA_1-Aligned_1-SNV_1",
            "variant_types": [
                "small variants",  # invalid
            ],
        }

        response_200 = self.client.post(url, [called_variants1], format="json")
        response_207 = self.client.post(url, [called_variants1, called_variants2], format="json")
        response_400 = self.client.post(url, [called_variants2], format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        changed_by(self, response_200.data[0], testuser)
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "NO CHANGE")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteCalledVariantsNanoporeAPITest(APITestCaseWithAuth):
    def test_delete_nanopore_api(self):
        url2 = "/api/experiments/called_variants_nanopore/delete/?ids=UCI_GREGoR_test-004-004-0-D-3_NANO_1-Aligned_1-SNV_1,DNE-01-1"
        url3 = "/api/experiments/called_variants_nanopore/delete/?ids=DNE-1,DNE2"

        response_207 = self.client.delete(url2, format="json")
        response_400 = self.client.delete(url3, format="json")

        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
