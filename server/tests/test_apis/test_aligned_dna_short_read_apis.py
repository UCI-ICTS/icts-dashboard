# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_dna_short_read_apis.py

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


class CreateAlignedDNAShortReadAPITest(APITestCaseWithAuth):
    def test_create_aligned_dna_short_read_api(self):
        url = "/api/experiments/create_aligned_dna_short_read/"

        aligned1 = {  # Prior existing entry, Is valid
            "aligned_dna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_DNA-Aligned-1",
            "experiment_dna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_DNA_1",
            "aligned_dna_short_read_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA.cram",
            "aligned_dna_short_read_index_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA.crai",
            "md5sum": "615fb1d2d88635b7461fd4c978bbc64a",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz",
            "reference_assembly_details": "GRCh38, no alts",
            "alignment_software": "bwa 0.7.17",
            "mean_coverage": None,
            "analysis_details": "Raw reads were trimmed with fastp 0.23.2 and aligned to GRCh38 (no alts) with bwa 0.7.17. Duplicates were marked and removed with GATK 4.3.0 MarkDuplicates, and BQSR was applied. Mean depth was computed with somalier 0.2.16.",
            "quality_issues": ""
        }

        aligned2 = {  # New entry
            "aligned_dna_short_read_id": "UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-2",
            "experiment_dna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_DNA_1",
            "aligned_dna_short_read_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA_1-Aligned-2.cram",
            "aligned_dna_short_read_index_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA_1-Aligned-2.crai",
            "md5sum": "615fb1d2d88635b7461fd4c978bbc64a",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz",
            "reference_assembly_details": "GRCh38, no alts",
            "alignment_software": "bwa 0.7.17",
            "mean_coverage": None,
            "analysis_details": "Raw reads were trimmed with fastp 0.23.2 and aligned to GRCh38 (no alts) with bwa 0.7.17. Duplicates were marked and removed with GATK 4.3.0 MarkDuplicates, and BQSR was applied. Mean depth was computed with somalier 0.2.16.",
            "quality_issues": None,
        }

        aligned3 =  {  # New entry, invalid
            "aligned_dna_short_read_id": "UCI_GREGoR_test-001-003-0_DNA_1-Aligned-2",
            "experiment_dna_short_read_id": None,  # missing
            "aligned_dna_short_read_file": "gs://fc-secure-be182c9d-e20a-43aa-b158-39113ea47705/cram/UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-2.cram",
            "aligned_dna_short_read_index_file": "gs://fc-secure-be182c9d-e20a-43aa-b158-39113ea47705/cram/UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-2.crai",
            "md5sum": "db2b05c08732d8fac11f1089a88374cb",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz",
            "reference_assembly_details": "GRCh38, no alts",
            "alignment_software": "bwa 0.7.17",
            "mean_coverage": None,
            "analysis_details": "Raw reads were trimmed with fastp 0.23.2 and aligned to GRCh38 (no alts) with bwa 0.7.17. Duplicates were marked and removed with GATK 4.3.0 MarkDuplicates, and BQSR was applied. Mean depth was computed with somalier 0.2.16.",
            "quality_issues": None,
        }

        #Checks for the Aligned table before creation
        aligned1_exists = Aligned.objects.filter(
            pk="aligned_dna_short_read.UCI_GREGoR_test-001-001-0-R-1_DNA-Aligned-1"
        ).exists()
        assert aligned1_exists

        aligned2_exists = Aligned.objects.filter(
            pk="aligned_dna_short_read.UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-2"
        ).exists()
        assert not aligned2_exists

        response_200 = self.client.post(url, [aligned2], format='json')
        response_207 = self.client.post(url, [aligned1, aligned3], format='json')
        response_400 = self.client.post(url, [aligned3, aligned3], format='json')

        #import pdb; pdb.set_trace()
        #Checks for the Aligned table after creation
        aligned2_exists = Aligned.objects.filter(
            pk="aligned_dna_short_read.UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-2"
        ).exists()
        aligned3_exists = Aligned.objects.filter(
            pk="aligned_dna_short_read.UCI_GREGoR_test-001-003-0_DNA_1-Aligned-2"
        ).exists()

        assert aligned2_exists
        assert not aligned3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadAlignedDNAShortReadAPITest(APITestCaseWithAuth):
    def test_read_aligned_dna_short_read(self):
        url1 = "/api/experiments/read_aligned_dna_short_read/?ids=UCI_GREGoR_test-001-001-0-R-1_DNA_1-Aligned-1"
        url2 = "/api/experiments/read_aligned_dna_short_read/?ids=UCI_GREGoR_test-001-001-0-R-1_DNA_1-Aligned-1, DNE-01-1"
        url3 = "/api/experiments/read_aligned_dna_short_read/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateDNAShortReadAPITest(APITestCaseWithAuth):
    def test_update_aligned_dna_short_read_api(self):
        url = "/api/experiments/update_aligned_dna_short_read/"

        aligned1 = {  # Valid, added mean_coverage
            "aligned_dna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_DNA_1-Aligned-1",
            "experiment_dna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_DNA_1",
            "aligned_dna_short_read_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA_1-Aligned-2.cram",
            "aligned_dna_short_read_index_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA_1-Aligned-2.crai",
            "md5sum": "615fb1d2d88635b7461fd4c978bbc64a",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz",
            "reference_assembly_details": "GRCh38, no alts",
            "alignment_software": "bwa 0.7.17",
            "mean_coverage": "32.1",  # Added
            "analysis_details": "Raw reads were trimmed with fastp 0.23.2 and aligned to GRCh38 (no alts) with bwa 0.7.17. Duplicates were marked and removed with GATK 4.3.0 MarkDuplicates, and BQSR was applied. Mean depth was computed with somalier 0.2.16.",
            "quality_issues": None,
        }

        aligned2 = {  # Invalid, missing reference assembly, uri, and details
            "aligned_dna_short_read_id": "UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-1",
            "experiment_dna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_DNA_1",
            "aligned_dna_short_read_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA_1-Aligned-2.cram",
            "aligned_dna_short_read_index_file": "gs://fc-secure-3cbd4d3d-7331-46f9-a98f-ebba0a894562/cram/UCI_GREGoR_test-002-001-2-R-1_DNA_1-Aligned-2.crai",
            "md5sum": "615fb1d2d88635b7461fd4c978bbc64a",
            "reference_assembly": None,  # missing
            "reference_assembly_uri": None,
            "reference_assembly_details": None,
            "alignment_software": "bwa 0.7.17",
            "mean_coverage": "38.4",  # Added
            "analysis_details": "Raw reads were trimmed with fastp 0.23.2 and aligned to GRCh38 (no alts) with bwa 0.7.17. Duplicates were marked and removed with GATK 4.3.0 MarkDuplicates, and BQSR was applied. Mean depth was computed with somalier 0.2.16.",
            "quality_issues": None,
        }

        response_200 = self.client.post(url, [aligned1], format='json')
        response_207 = self.client.post(url, [aligned1, aligned2], format='json')
        response_400 = self.client.post(url, [aligned2], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteAlignedDNAShortReadAPITest(APITestCaseWithAuth):
    def test_delete_dna_short_read_api(self):

        #Checks for the Alignment table before deletions
        alignment1_exists = Aligned.objects.filter(
            pk="aligned_dna_short_read.UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-1"
        ).exists()

        assert alignment1_exists

        url2 = "/api/experiments/delete_aligned_dna_short_read/?ids=UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-1, DNE-01-1"
        url3 = "/api/experiments/delete_aligned_dna_short_read/?ids=DNE-1, DNE2"

        response_207 = self.client.delete(url2, format='json')
        response_400 = self.client.delete(url3, format='json')

        #Checks for the Alignment table after deletion
        alignment2_exists = Aligned.objects.filter(
            pk="aligned_dna_short_read.UCI_GREGoR_test-001-002-0-R-1_DNA_1-Aligned-1"
        ).exists()
        assert not alignment2_exists
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
