# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_rna_short_read_apis.py

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


class CreateAlignedRnaShortReadAPITest(APITestCaseWithAuth):
    def test_create_aligned_rna_short_read_api(self):
        url = "/api/experiments/aligned_rna_short_read/create/"

        aligned1 = {   # Existing entry, should fail
            "aligned_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1",
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1",
            "aligned_rna_short_read_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram",
            "aligned_rna_short_read_index_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram.crai",
            "md5sum": "25129ce37d1d28d765074f50e7a49660",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "reference_assembly_details": None,
            "gene_annotation": "GENCODEv41",
            "gene_annotation_details": "gencode_comprehensive_chr",
            "alignment_software": "STARv2.7.10a",
            "alignment_log_file": None,
            "alignment_postprocessing": None,
            "mean_coverage": None,
            "percent_uniquely_aligned": None,
            "percent_multimapped": None,
            "percent_unaligned": None,
            "quality_issues": None,
            "alignment_QC_output_file": None,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None

        }

        aligned2 = {   # New entry
            "aligned_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_2",
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1",
            "aligned_rna_short_read_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram",
            "aligned_rna_short_read_index_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram.crai",
            "md5sum": "25129ce37d1d28d765074f50e7a49660",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "reference_assembly_details": None,
            "gene_annotation": "GENCODEv41",
            "gene_annotation_details": "gencode_comprehensive_chr",
            "alignment_software": "STARv2.7.10a",
            "alignment_log_file": None,
            "alignment_postprocessing": None,
            "mean_coverage": None,
            "percent_uniquely_aligned": None,
            "percent_multimapped": None,
            "percent_unaligned": None,
            "quality_issues": None,
            "alignment_QC_output_file": None,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None
        }

        aligned3 =  {   # New entry
            "aligned_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_3",
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1",
            "aligned_rna_short_read_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram",
            "aligned_rna_short_read_index_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram.crai",
            "md5sum": "25129ce37d1d28d765074f50e7a49660",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "reference_assembly_details": None,
            "gene_annotation": "GENCODEv41",
            "gene_annotation_details": "gencode_comprehensive_chr",
            "alignment_software": "STARv2.7.10a",
            "alignment_log_file": None,
            "alignment_postprocessing": None,
            "mean_coverage": None,
            "percent_uniquely_aligned": None,
            "percent_multimapped": None,
            "percent_unaligned": None,
            "quality_issues": None,
            "alignment_QC_output_file": None,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None
        }

        #Checks for the Aligned table before creation
        aligned1_exists = Aligned.objects.filter(
            pk="aligned_rna_short_read.UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1"
        ).exists()
        assert aligned1_exists

        aligned2_exists = Aligned.objects.filter(
            pk="aligned_rna_short_read.UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_2"
        ).exists()
        assert not aligned2_exists

        response_200 = self.client.post(url, [aligned2], format='json')
        response_207 = self.client.post(url, [aligned1, aligned3], format='json')
        response_400 = self.client.post(url, [aligned1, aligned1], format='json')

        #Checks for the Aligned table after creation
        aligned2_exists = Aligned.objects.filter(
            pk="aligned_rna_short_read.UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_2"
        ).exists()
        aligned3_exists = Aligned.objects.filter(
            pk="aligned_rna_short_read.UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_3"
        ).exists()

        assert aligned2_exists
        assert aligned3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "BAD REQUEST")
        self.assertEqual(response_207.data[1]["request_status"], "CREATED")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadAlignedRnaShortReadAPITest(APITestCaseWithAuth):
    def test_read_aligned_rna_short_read(self):
        url1 = "/api/experiments/aligned_rna_short_read/?ids=UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1"
        url2 = "/api/experiments/aligned_rna_short_read/?ids=UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1, DNE-01-1"
        url3 = "/api/experiments/aligned_rna_short_read/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateRNAShortReadAPITest(APITestCaseWithAuth):
    def test_update_aligned_rna_short_read_api(self):
        url = "/api/experiments/aligned_rna_short_read/update/"

        aligned1 = {
            "aligned_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1",
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1",
            "aligned_rna_short_read_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram",
            "aligned_rna_short_read_index_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram.crai",
            "md5sum": "25129ce37d1d28d765074f50e7a49660",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "reference_assembly_details": None,
            "gene_annotation": "GENCODEv41",
            "gene_annotation_details": "gencode_comprehensive_chr",
            "alignment_software": "STARv2.7.10a",
            "alignment_log_file": None,
            "alignment_postprocessing": None,
            "mean_coverage": None,
            "percent_uniquely_aligned": None,
            "percent_multimapped": None,
            "percent_unaligned": None,
            "quality_issues": None,
            "alignment_QC_output_file": None,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None
        }

        aligned2 = {
            "aligned_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_2",
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1",
            "aligned_rna_short_read_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram",
            "aligned_rna_short_read_index_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram.crai",
            "md5sum": "25129ce37d1d28d765074f50e7a49660",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "reference_assembly_details": None,
            "gene_annotation": "GENCODEv41",
            "gene_annotation_details": "gencode_comprehensive_chr",
            "alignment_software": "STARv2.7.10a",
            "alignment_log_file": None,
            "alignment_postprocessing": None,
            "mean_coverage": None,
            "percent_uniquely_aligned": None,
            "percent_multimapped": None,
            "percent_unaligned": None,
            "quality_issues": None,
            "alignment_QC_output_file": None,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None
        }

        aligned3 =  {
            "aligned_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_3",
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0-R-1_RNA_1",
            "aligned_rna_short_read_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram",
            "aligned_rna_short_read_index_file": "gs://fc-secure-e3641cc8-359e-4504-97ff-51d8d9580f55/cram/RNA/UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned.cram.crai",
            "md5sum": "25129ce37d1d28d765074f50e7a49660",
            "reference_assembly": "GRCh38",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "reference_assembly_details": None,
            "gene_annotation": "GENCODEv41",
            "gene_annotation_details": "gencode_comprehensive_chr",
            "alignment_software": "STARv2.7.10a",
            "alignment_log_file": None,
            "alignment_postprocessing": None,
            "mean_coverage": None,
            "percent_uniquely_aligned": None,
            "percent_multimapped": None,
            "percent_unaligned": None,
            "quality_issues": None,
            "alignment_QC_output_file": None,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None
        }


        response_200 = self.client.post(url, [aligned1], format='json')
        response_207 = self.client.post(url, [aligned1, aligned2], format='json')
        response_400 = self.client.post(url, [aligned2, aligned3], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteAlignedRnaShortReadAPITest(APITestCaseWithAuth):
    def test_delete_rna_short_read_api(self):

        #Checks for the Alignment table before deletion

        alignment1_exists = Aligned.objects.filter(
            pk="aligned_rna_short_read.UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1"
        ).exists()

        assert alignment1_exists

        url2 = "/api/experiments/aligned_rna_short_read/delete/?ids=UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1, DNE-01-1"
        url3 = "/api/experiments/aligned_rna_short_read/delete/?ids=DNE-1, DNE2"

        response_207 = self.client.delete(url2, format='json')
        response_400 = self.client.delete(url3, format='json')

        #Checks for the Alignment table after deletion
        alignment2_exists = Aligned.objects.filter(
            pk="aligned_rna_short_read.UCI_GREGoR_test-001-001-0-R-1_RNA_1-Aligned_1"
        ).exists()

        assert not alignment2_exists
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
