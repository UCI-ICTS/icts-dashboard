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


class CreateCalledVariantsPacBioAPITest(APITestCaseWithAuth):
    def test_create_called_variants_pac_bio_api(self):
        url = "/api/experiments/called_variants_pac_bio/create/"

        called_variants1 = {  # New entry to be entered twice. Is valid the first time but not the second time
            "called_variants_pac_bio_id": "UCI_GREGoR_test-001-joint-deepvariant-chr1_vcf_2",
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-001-joint-deepvariant-chr1_vcf_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/pacbio/GREGoR_test-001.GRCh38.deepvariant.chr1.vcf.gz",
            "md5sum": "d92071f2cacb695713c46194ec0024ad",
            "caller_software": [
                "DeepVariant_version=1.5.0",
                "GLNexus_version=v1.4.1"
            ],
            "variant_types": [
                "SNV",
                "INDEL"
            ],
            "analysis_details": "PacBio HiFi-Human-WGS-WDL v1.0",
            "chrom": "1"
        }

        called_variants2 = {  # New entry
            "called_variants_pac_bio_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_2",
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/pacbio/GREGoR_test-002-001-2-D-2.GRCh38.deepvariant.phased.vcf.gz",
            "md5sum": "e57cfed8c9df0622b0c46e2362a568e1",
            "caller_software": ["DeepVariant_version=1.5.0"],
            "variant_types": [
                "SNV",
                "INDEL"
            ],
            "analysis_details": "PacBio HiFi-Human-WGS-WDL v1.0",
            "chrom": "ALL"
        }

        called_variants3 = {  # New entry, invalid
            "called_variants_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_1-deepvariant_phased_2",
            "aligned_pac_bio_set_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_1-deepvariant_phased_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/pacbio/GREGoR_test-003-001-1-D-2.GRCh38.deepvariant.phased.vcf.gz",
            "md5sum": "61f59856ad25c0070463bf8d85fcf0d8",
            "caller_software": ["DeepVariant_version=1.5.0"],
            "variant_types": [],  # invalid, must have value
            "analysis_details": "PacBio HiFi-Human-WGS-WDL v1.0",
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


class ReadCalledVariantsPacBioAPITest(APITestCaseWithAuth):
    def test_read_called_variants_pac_bio(self):
        url1 = "/api/experiments/called_variants_pac_bio/?ids=UCI_GREGoR_test-001-joint-deepvariant-chr1_vcf_1"
        url2 = "/api/experiments/called_variants_pac_bio/?ids=UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_1,DNE-01-1"
        url3 = "/api/experiments/called_variants_pac_bio/?ids=DNE-1,DNE2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdatePacBioAPITest(APITestCaseWithAuth):
    def test_update_called_variants_pac_bio_api(self):
        url = "/api/experiments/called_variants_pac_bio/update/"
        called_variants1 = {  # Valid, edited analysis_details
            "called_variants_pac_bio_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_1",
            "called_variants_dna_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/vcf/pacbio/GREGoR_test-002-001-2-D-2.GRCh38.deepvariant.phased.anno.vcf.gz",
            "md5sum": "41e92abcd6542df847ce4632e2358712",
            "caller_software": ["DeepVariant_version=1.5.0", "ANNOVAR=20250721"],
            "analysis_details": "PacBio HiFi-Human-WGS-WDL v1.0. Annotated with ANNOVAR",
            "chrom": "ALL"
        }

        called_variants2 = {  # Invalid variant_types
            "called_variants_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_1-deepvariant_phased_1",
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


class DeleteCalledVariantsPacBioAPITest(APITestCaseWithAuth):
    def test_delete_pac_bio_api(self):
        url2 = "/api/experiments/called_variants_pac_bio/delete/?ids=UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1-deepvariant_phased_1,DNE-01-1"
        url3 = "/api/experiments/called_variants_pac_bio/delete/?ids=DNE-1,DNE2"

        response_207 = self.client.delete(url2, format="json")
        response_400 = self.client.delete(url3, format="json")

        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
