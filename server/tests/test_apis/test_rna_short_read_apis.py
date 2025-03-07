# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_rna_short_read_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from experiments.models import Experiment

class APITestCaseWithAuth(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)


class CreateRNAShortReadAPITest(APITestCaseWithAuth):
    def test_create_rna_short_read_api(self):
        url = "/api/experiments/create_experiment_rna_short_read/"

        experiment1 = {
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0_RNA",
            "analyte_id": "GREGoR_test-001-001-0-R-2",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0_RNA",
            "seq_library_prep_kit_method": "Watchmaker ribosomal and globin depletion",
            "read_length": 150,
            "single_or_paired_ends": "paired-end",
            "date_data_generation": "2023-03-18",
            "sequencing_platform": "NovaSeq",
            "within_site_batch_name": "RNA 2A",
            "RIN": None,
            "estimated_library_size": None,
            "total_reads": 240349679.0,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None,
            "library_prep_type": [
                "rRNA depletion",
                "globin depletion"
            ],
            "experiment_type": [
                "paired-end",
                "untargeted"
            ]
        }

        experiment2 = {
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0_RNA_2",
            "analyte_id": "GREGoR_test-001-001-0-R-2",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0_RNA",
            "seq_library_prep_kit_method": "Watchmaker ribosomal and globin depletion",
            "read_length": 150,
            "single_or_paired_ends": "paired-end",
            "date_data_generation": "2023-03-18",
            "sequencing_platform": "NovaSeq",
            "within_site_batch_name": "RNA 2A",
            "RIN": None,
            "estimated_library_size": None,
            "total_reads": 240349679.0,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None,
            "library_prep_type": [
                "rRNA depletion",
                "globin depletion"
            ],
            "experiment_type": [
                "paired-end",
                "untargeted"
            ]
        }

        experiment3 = {
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0_RNA_3",
            "analyte_id": "GREGoR_test-001-001-0-R-2",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0_RNA",
            "seq_library_prep_kit_method": "Watchmaker ribosomal and globin depletion",
            "read_length": 150,
            "single_or_paired_ends": "paired-end",
            "date_data_generation": "2023-03-18",
            "sequencing_platform": "NovaSeq",
            "within_site_batch_name": "RNA 2A",
            "RIN": None,
            "estimated_library_size": None,
            "total_reads": 240349679.0,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None,
            "library_prep_type": [
                "rRNA depletion",
                "globin depletion"
            ],
            "experiment_type": [
                "paired-end",
                "untargeted"
            ]
        }
  
        response_200 = self.client.post(url, [experiment2], format='json')
        response_207 = self.client.post(url, [experiment1, experiment3], format='json')
        response_400 = self.client.post(url, [experiment1, experiment1], format='json')
        
        #Checks for the Experiment table
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_rna_short_read.UCI_GREGoR_test-001-001-0_RNA"
        ).exists()
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_rna_short_read.UCI_GREGoR_test-001-001-0_RNA_2"
        ).exists()
        experiment3_exists = Experiment.objects.filter(
            pk="experiment_rna_short_read.UCI_GREGoR_test-001-001-0_RNA_3"
        ).exists()
        assert experiment1_exists
        assert experiment2_exists
        assert experiment3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        

class ReadRNAShortReadAPITest(APITestCaseWithAuth):
    def test_read_participant(self):
        url1 = "/api/experiments/read_experiment_rna_short_read/?ids=UCI_GREGoR_test-001-001-0_RNA"
        url2 = "/api/experiments/read_experiment_rna_short_read/?ids=UCI_GREGoR_test-001-001-0_RNA, DNE-01-1"
        url3 = "/api/experiments/read_experiment_rna_short_read/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateRNAShortReadAPITest(APITestCaseWithAuth):
    def test_update_rna_short_read_api(self):
        url = "/api/experiments/update_experiment_rna_short_read/"
        experiment1 = {
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0_RNA",
            "analyte_id": "GREGoR_test-001-001-0-R-2",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0_RNA",
            "seq_library_prep_kit_method": "Watchmaker ribosomal and globin depletion",
            "read_length": 150,
            "single_or_paired_ends": "paired-end",
            "date_data_generation": "2023-03-18",
            "sequencing_platform": "NovaSeq",
            "within_site_batch_name": "RNA 2A",
            "RIN": None,
            "estimated_library_size": None,
            "total_reads": 240349679.0,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None,
            "library_prep_type": [
                "rRNA depletion",
                "globin depletion"
            ],
            "experiment_type": [
                "paired-end",
                "untargeted"
            ]
        }

        experiment2 = {
            "experiment_rna_short_read_id": "UCI_GREGoR_test-001-001-0_RNA_2",
            "analyte_id": "GREGoR_test-001-001-0-R-2",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0_RNA",
            "seq_library_prep_kit_method": "Watchmaker ribosomal and globin depletion",
            "read_length": 150,
            "single_or_paired_ends": "paired-end",
            "date_data_generation": "2023-03-18",
            "sequencing_platform": "NovaSeq",
            "within_site_batch_name": "RNA 2A",
            "RIN": None,
            "estimated_library_size": None,
            "total_reads": 240349679.0,
            "percent_rRNA": None,
            "percent_mRNA": None,
            "percent_mtRNA": None,
            "percent_Globin": None,
            "percent_UMI": None,
            "five_prime_three_prime_bias": None,
            "percent_GC": None,
            "percent_chrX_Y": None,
            "library_prep_type": [
                3,
                4
            ],
            "experiment_type": [
                2,
                4
            ]
        }
  
        response_200 = self.client.post(url, [experiment1], format='json')
        response_207 = self.client.post(url, [experiment1, experiment2], format='json')
        response_400 = self.client.post(url, [experiment2, experiment2], format='json')
  
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[1]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[0]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteRNAShortReadAPITest(APITestCaseWithAuth):
    def test_delete_rna_short_read_api(self):
        
        #Checks for the Experiment table before deletion
        
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_rna_short_read.UCI_GREGoR_test-001-001-0_RNA"
        ).exists()
        
        assert experiment1_exists

        url2 = "/api/experiments/delete_experiment_rna_short_read/?ids=UCI_GREGoR_test-001-001-0_RNA, DNE-01-1"
        url3 = "/api/experiments/delete_experiment_rna_short_read/?ids=DNE-1, DNE2"

        response_207 = self.client.delete(url2, format='json')
        response_400 = self.client.delete(url3, format='json')
        
        #Checks for the Experiment table after deletion
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_rna_short_read.UCI_GREGoR_test-001-001-0_RNA"
        ).exists()
        assert not experiment2_exists

        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
