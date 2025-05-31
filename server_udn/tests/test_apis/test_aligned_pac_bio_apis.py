# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_pac_bio_apis.py

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


class CreateAlignedPacBioAPITest(APITestCaseWithAuth):
    def test_create_aligned_pac_bio_api(self):
        url = "/api/experiments/aligned_pac_bio/create/"

        aligned1 = {   # Existing entry, should fail
            "aligned_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1",
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1",
            "aligned_pac_bio_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-001-001-0.bam",
            "aligned_pac_bio_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-001-001-0.bai",
            "md5sum": "6e06cbe92700dfc5cd7ad07d7f6d3b8a",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "pbmm2 v1.10.0",
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
            "methylation_called": True
        }

        aligned2 = {   # New entry
            "aligned_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_2",
            "experiment_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1",
            "aligned_pac_bio_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-003-001-1.bam",
            "aligned_pac_bio_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-003-001-1.bai",
            "md5sum": "1e4020ccca6fe9c93c64747afa59eff1",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "pbmm2 v1.10.0",
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
            "methylation_called": True
        }

        aligned3 =  {   # New entry
            "aligned_pac_bio_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_2",
            "experiment_pac_bio_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1",
            "aligned_pac_bio_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-002-001-2.bam",
            "aligned_pac_bio_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-002-001-2.bai",
            "md5sum": "727f9869058ef757cc3ff66503f1e036",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "pbmm2 v1.10.0",
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
            "methylation_called": True
        }

        #Checks for the Aligned table before creation
        aligned1_exists = Aligned.objects.filter(
            pk="aligned_pac_bio.UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1"
        ).exists()
        assert aligned1_exists

        aligned2_exists = Aligned.objects.filter(
            pk="aligned_pac_bio.UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_2"
        ).exists()
        assert not aligned2_exists

        response_200 = self.client.post(url, [aligned2], format='json')
        response_207 = self.client.post(url, [aligned1, aligned3], format='json')
        response_400 = self.client.post(url, [aligned1, aligned1], format='json')

        #Checks for the Aligned table after creation
        aligned2_exists = Aligned.objects.filter(
            pk="aligned_pac_bio.UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_2"
        ).exists()
        aligned3_exists = Aligned.objects.filter(
            pk="aligned_pac_bio.UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_2"
        ).exists()

        assert aligned2_exists
        assert aligned3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "BAD REQUEST")
        self.assertEqual(response_207.data[1]["request_status"], "CREATED")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadAlignedPacBioAPITest(APITestCaseWithAuth):
    def test_read_aligned_pac_bio(self):
        url1 = "/api/experiments/aligned_pac_bio/?ids=UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1"
        url2 = "/api/experiments/aligned_pac_bio/?ids=UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_1, DNE-01-1"
        url3 = "/api/experiments/aligned_pac_bio/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateAlignedPacBioAPITest(APITestCaseWithAuth):
    def test_update_aligned_pac_bio_api(self):
        url = "/api/experiments/aligned_pac_bio/update/"

        aligned1 = {  # Valid
            "aligned_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1",
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1",
            "aligned_pac_bio_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-001-001-0.bam",
            "aligned_pac_bio_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-001-001-0.bai",
            "md5sum": "6e06cbe92700dfc5cd7ad07d7f6d3b8a",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "pbmm2 v1.10.0",
            "analysis_details": None,
            "mean_coverage": 30.0,  # changed
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
            "methylation_called": True
        }

        aligned2 = {  # Valid
            "aligned_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1-Aligned_1",
            "experiment_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1",
            "aligned_pac_bio_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-003-001-1.bam",
            "aligned_pac_bio_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-003-001-1.bai",
            "md5sum": "727f9869058ef757cc3ff66503f1e036",
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "pbmm2 v2.0",  # changed
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
            "methylation_called": True
        }

        aligned3 =  {  # Invalid, missing alignment_software
            "aligned_pac_bio_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1-Aligned_1",
            "experiment_pac_bio_id": "UCI_GREGoR_test-002-001-2-D-2_PB_1",
            "aligned_pac_bio_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-002-001-2.bam",
            "aligned_pac_bio_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-002-001-2.bai",
            "md5sum": "1e4020ccca6fe9c93c64747afa59eff1",
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
            "methylation_called": True
        }

        aligned4 =  {  # Invalid, swaps md5sum with a different sample
            "aligned_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1",
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1",
            "aligned_pac_bio_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-001-001-0.bam",
            "aligned_pac_bio_index_file": "gs://fc-secure-1b1e1ff4-3496-466f-8952-12f034c3c469/bam/pacbio/GREGoR_test-001-001-0.bai",
            "md5sum": "1e4020ccca6fe9c93c64747afa59eff1",  # changed but already exists in db.
            "reference_assembly": "GRCh38_noalt",
            "alignment_software": "pbmm2 v1.10.0",
            "analysis_details": None,
            "mean_coverage": 30.0,
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
            "methylation_called": True
        }


        response_200 = self.client.post(url, [aligned1], format='json')
        response_207 = self.client.post(url, [aligned2, aligned3, aligned4], format='json')
        response_400 = self.client.post(url, [aligned3], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_207.data[2]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteAlignedPacBioAPITest(APITestCaseWithAuth):
    def test_delete_pac_bio_api(self):

        #Checks for the Alignment table before deletion

        alignment1_exists = Aligned.objects.filter(
            pk="aligned_pac_bio.UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1"
        ).exists()

        assert alignment1_exists

        url2 = "/api/experiments/aligned_pac_bio/delete/?ids=UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1, DNE-01-1"
        url3 = "/api/experiments/aligned_pac_bio/delete/?ids=DNE-1, DNE2"

        response_207 = self.client.delete(url2, format='json')
        response_400 = self.client.delete(url3, format='json')

        #Checks for the Alignment table after deletion
        alignment2_exists = Aligned.objects.filter(
            pk="aligned_pac_bio.UCI_GREGoR_test-001-001-0-D-2_PB_1-Aligned_1"
        ).exists()

        assert not alignment2_exists
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
