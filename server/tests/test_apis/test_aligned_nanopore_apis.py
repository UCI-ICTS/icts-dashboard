# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_nanopore_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from experiments.models import Aligned

class APITestCaseWithAuth(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)


class CreateAlignedNanoporeAPITest(APITestCaseWithAuth):
    def test_create_aligned_nanopore_api(self):
        url = "/api/experiments/aligned_nanopore/create/"

        aligned1 = {   # Existing entry, should fail
            "aligned_nanopore_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1",
            "experiment_nanopore_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_1",
            "aligned_nanopore_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-001-001-0-D-3.bam",
            "aligned_nanopore_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-001-001-0-D-3.bai",
            "md5sum": "ddc246dee454c5b74837aba8ff44c61e",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "Minimap2-2.23-r1111",
            "analysis_details": None,
            "mean_coverage": None,
            "genome_coverage": None,
            "contamination": None,
            "sex_concordance": None,
            "num_reads": None,
            "num_bases": None,
            "read_length_mean": None,
            "num_aligned_reads": None,
            "num_aligned_bases": None,
            "aligned_read_length_mean": None,
            "read_error_rate": None,
            "mapped_reads_pct": None,
            "methylation_called": True,
            "quality_issues": None
        }

        aligned2 = {   # New entry
            "aligned_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_2",
            "experiment_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1",
            "aligned_nanopore_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-006-006-0-D-3.bam",
            "aligned_nanopore_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-006-006-0-D-3.bai",
            "md5sum": "6de703ded5b577276144f38af92787b7",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "Minimap2-2.23-r1111",
            "analysis_details": None,
            "mean_coverage": None,
            "genome_coverage": None,
            "contamination": None,
            "sex_concordance": None,
            "num_reads": None,
            "num_bases": None,
            "read_length_mean": None,
            "num_aligned_reads": None,
            "num_aligned_bases": None,
            "aligned_read_length_mean": None,
            "read_error_rate": None,
            "mapped_reads_pct": None,
            "methylation_called": True,
            "quality_issues": None
        }

        aligned3 =  {   # New entry
            "aligned_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_3",
            "experiment_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1",
            "aligned_nanopore_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-006-006-0-D-3.bam",
            "aligned_nanopore_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-006-006-0-D-3.bai",
            "md5sum": "6de703ded5b577276144f38af92787b7",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "Minimap2-2.23-r1111",
            "analysis_details": None,
            "mean_coverage": None,
            "genome_coverage": None,
            "contamination": None,
            "sex_concordance": None,
            "num_reads": None,
            "num_bases": None,
            "read_length_mean": None,
            "num_aligned_reads": None,
            "num_aligned_bases": None,
            "aligned_read_length_mean": None,
            "read_error_rate": None,
            "mapped_reads_pct": None,
            "methylation_called": True,
            "quality_issues": None
        }

        #Checks for the Aligned table before creation
        aligned1_exists = Aligned.objects.filter(
            pk="aligned_nanopore.UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1"
        ).exists()
        assert aligned1_exists

        aligned2_exists = Aligned.objects.filter(
            pk="aligned_nanopore.UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_2"
        ).exists()
        assert not aligned2_exists

        response_200 = self.client.post(url, [aligned2], format='json')
        response_207 = self.client.post(url, [aligned1, aligned3], format='json')
        response_400 = self.client.post(url, [aligned1, aligned1], format='json')

        #Checks for the Aligned table after creation
        aligned2_exists = Aligned.objects.filter(
            pk="aligned_nanopore.UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_2"
        ).exists()
        aligned3_exists = Aligned.objects.filter(
            pk="aligned_nanopore.UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_3"
        ).exists()

        assert aligned2_exists
        assert aligned3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "BAD REQUEST")
        self.assertEqual(response_207.data[1]["request_status"], "CREATED")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadAlignedNanoporeAPITest(APITestCaseWithAuth):
    def test_read_aligned_nanopore(self):
        url1 = "/api/experiments/aligned_nanopore/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1"
        url2 = "/api/experiments/aligned_nanopore/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1, DNE-01-1"
        url3 = "/api/experiments/aligned_nanopore/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateAlignedNanoporeAPITest(APITestCaseWithAuth):
    def test_update_aligned_nanopore_api(self):
        url = "/api/experiments/aligned_nanopore/update/"

        aligned1 = {  # Valid
            "aligned_nanopore_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1",
            "experiment_nanopore_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_1",
            "aligned_nanopore_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-001-001-0-D-3.bam",
            "aligned_nanopore_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-001-001-0-D-3.bai",
            "md5sum": "ddc246dee454c5b74837aba8ff44c61e",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "Minimap2-2.23-r1111",
            "analysis_details": "Processed with bonito v0.8.1",  # changed
            "mean_coverage": None,
            "genome_coverage": None,
            "contamination": None,
            "sex_concordance": None,
            "num_reads": None,
            "num_bases": None,
            "read_length_mean": None,
            "num_aligned_reads": None,
            "num_aligned_bases": None,
            "aligned_read_length_mean": None,
            "read_error_rate": None,
            "mapped_reads_pct": None,
            "methylation_called": True,
            "quality_issues": None
        }

        aligned2 = {  # Valid
            "aligned_nanopore_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_1-Aligned_1",
            "experiment_nanopore_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_1",
            "aligned_nanopore_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-004-004-0-D-3.bam",
            "aligned_nanopore_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-004-004-0-D-3.bai",
            "md5sum": "6de703ded5b577276144f38af92787b7",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "Minimap2-2.23-r1111",
            "analysis_details": None,
            "mean_coverage": None,
            "genome_coverage": 30.0,  # changed
            "contamination": None,
            "sex_concordance": None,
            "num_reads": None,
            "num_bases": None,
            "read_length_mean": None,
            "num_aligned_reads": None,
            "num_aligned_bases": None,
            "aligned_read_length_mean": None,
            "read_error_rate": None,
            "mapped_reads_pct": None,
            "methylation_called": True,
            "quality_issues": None
        }

        aligned3 =  {  # Invalid, missing alignment_software
            "aligned_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1-Aligned_1",
            "experiment_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_1",
            "aligned_nanopore_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-006-006-0-D-3.bam",
            "aligned_nanopore_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/nanopore/GREGoR_test-006-006-0-D-3.bai",
            "md5sum": "63d609796a14366cf80e85ff6ad283bd",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": None,  # changed
            "analysis_details": None,
            "mean_coverage": None,
            "genome_coverage": None,
            "contamination": None,
            "sex_concordance": None,
            "num_reads": None,
            "num_bases": None,
            "read_length_mean": None,
            "num_aligned_reads": None,
            "num_aligned_bases": None,
            "aligned_read_length_mean": None,
            "read_error_rate": None,
            "mapped_reads_pct": None,
            "methylation_called": True,
            "quality_issues": None
        }

        response_200 = self.client.post(url, [aligned1], format='json')
        response_207 = self.client.post(url, [aligned2, aligned3], format='json')
        response_400 = self.client.post(url, [aligned3], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteAlignedNanoporeAPITest(APITestCaseWithAuth):
    def test_delete_nanopore_api(self):

        #Checks for the Alignment table before deletion

        alignment1_exists = Aligned.objects.filter(
            pk="aligned_nanopore.UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1"
        ).exists()

        assert alignment1_exists

        url2 = "/api/experiments/aligned_nanopore/delete/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1, DNE-01-1"
        url3 = "/api/experiments/aligned_nanopore/delete/?ids=DNE-1, DNE2"

        response_207 = self.client.delete(url2, format='json')
        response_400 = self.client.delete(url3, format='json')

        #Checks for the Alignment table after deletion
        alignment2_exists = Aligned.objects.filter(
            pk="aligned_nanopore.UCI_GREGoR_test-001-001-0-D-3_NANO_1-Aligned_1"
        ).exists()

        assert not alignment2_exists
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
