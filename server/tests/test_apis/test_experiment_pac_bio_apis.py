# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_pac_bio_apis.py

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


class CreatePacBioAPITest(APITestCaseWithAuth):
    def test_create_pac_bio_api(self):
        url = "/api/experiments/create_experiment_pac_bio/"

        experiment1 = {  # Valid
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-002-0-R-20_PB",
            "analyte_id": "GREGoR_test-001-002-0-R-2",
            "experiment_sample_id": "UCI-014",
            "seq_library_prep_kit_method": "SMRTbell prep kit 3.0",
            "fragmentation_method": "",
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2023-09-29",
            "sequencing_platform": "PacBio Revio",
            "was_barcoded": True,
            "barcode_kit": "",
            "application_kit": "",
            "smrtlink_server_version": "13.0.0.207600",
            "instrument_ics_version": "13.0.1.212553",
            "size_selection_method": "",
            "library_size": "",
            "smrt_cell_kit": "",
            "smrt_cell_id": "",
            "movie_name": "",
            "polymerase_kit": "",
            "sequencing_kit": "",
            "movie_length_hours": None,
            "includes_kinetics": False,
            "includes_CpG_methylation": False,
            "by_strand": False
        }

        experiment2 = {  # Valid 2
            "experiment_pac_bio_id": "UCI_GREGoR_test-002-002-2-R-20_PB",
            "analyte_id": "GREGoR_test-003-002-1-R-2",
            "experiment_sample_id": "UCI-068",
            "seq_library_prep_kit_method": "SMRTbell prep kit 3.0",
            "fragmentation_method": "",
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2023-09-29",
            "sequencing_platform": "PacBio Revio",
            "was_barcoded": True,
            "barcode_kit": "",
            "application_kit": "",
            "smrtlink_server_version": "12.0.0.176214",
            "instrument_ics_version": "12.0.4.197734",
            "size_selection_method": "",
            "library_size": "",
            "smrt_cell_kit": "",
            "smrt_cell_id": "",
            "movie_name": "",
            "polymerase_kit": "",
            "sequencing_kit": "",
            "movie_length_hours": None,
            "includes_kinetics": False,
            "includes_CpG_methylation": False,
            "by_strand": False
        }

        experiment3 = {  # Invalid, missing experiment_type
            "experiment_pac_bio_id": "UCI_GREGoR_test-003-002-1-R-20_PB",
            "analyte_id": "GREGoR_test-003-002-1-R-2",
            "experiment_sample_id": "UCI-056",
            "seq_library_prep_kit_method": "SMRTbell prep kit 3.0",
            "fragmentation_method": "",
            "experiment_type": None,  # changed
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2023-09-29",
            "sequencing_platform": "PacBio Revio",
            "was_barcoded": True,
            "barcode_kit": "",
            "application_kit": "",
            "smrtlink_server_version": "12.0.0.176214",
            "instrument_ics_version": "12.0.4.197734",
            "size_selection_method": "",
            "library_size": "",
            "smrt_cell_kit": "",
            "smrt_cell_id": "",
            "movie_name": "",
            "polymerase_kit": "",
            "sequencing_kit": "",
            "movie_length_hours": None,
            "includes_kinetics": False,
            "includes_CpG_methylation": False,
            "by_strand": False
        }

        response_200 = self.client.post(url, [experiment1], format='json')
        response_207 = self.client.post(url, [experiment2, experiment1], format='json')
        response_400 = self.client.post(url, [experiment3, experiment3], format='json')

        #Checks for the Experiment table
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-001-002-0-R-20_PB"
        ).exists()
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-002-002-2-R-20_PB"
        ).exists()
        experiment3_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-003-002-1-R-20_PB"
        ).exists()
        assert experiment1_exists
        assert experiment2_exists
        assert not experiment3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadPacBioPITest(APITestCaseWithAuth):
    def test_read_experiment_pac_bio(self):
        url1 = "/api/experiments/read_experiment_pac_bio/?ids=UCI_GREGoR_test-001-002-0-R-2_PB"
        url2 = "/api/experiments/read_experiment_pac_bio/?ids=UCI_GREGoR_test-002-002-2-R-2_PB, DNE-01-1"
        url3 = "/api/experiments/read_experiment_pac_bio/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdatePacBioAPITest(APITestCaseWithAuth):
    def test_update_pac_bio_api(self):
        url = "/api/experiments/update_experiment_pac_bio/"
        experiment1 = {  # Valid
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-002-0-R-2_PB",
            "analyte_id": "GREGoR_test-001-002-0-R-2",
            "experiment_sample_id": "UCI-014",
            "seq_library_prep_kit_method": "SMRTbell prep kit 3.0",
            "fragmentation_method": "",
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2023-09-29",
            "sequencing_platform": "PacBio Revio",
            "was_barcoded": True,
            "barcode_kit": "",
            "application_kit": "",
            "smrtlink_server_version": "13.0.0.207600",
            "instrument_ics_version": "13.0.1.212553",
            "size_selection_method": "",
            "library_size": "",
            "smrt_cell_kit": "",
            "smrt_cell_id": "",
            "movie_name": "",
            "polymerase_kit": "",
            "sequencing_kit": "",
            "movie_length_hours": None,
            "includes_kinetics": False,
            "includes_CpG_methylation": False,
            "by_strand": False
        }

        experiment2 = {  # Invalid, missing experiment_type
            "experiment_pac_bio_id": "UCI_GREGoR_test-002-002-2-R-2_PB",
            "analyte_id": "GREGoR_test-003-002-1-R-2",
            "experiment_sample_id": "UCI-068",
            "seq_library_prep_kit_method": "SMRTbell prep kit 3.0",
            "fragmentation_method": "",
            "experiment_type": None,  # changed
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2023-09-29",
            "sequencing_platform": "PacBio Revio",
            "was_barcoded": True,
            "barcode_kit": "",
            "application_kit": "",
            "smrtlink_server_version": "12.0.0.176214",
            "instrument_ics_version": "12.0.4.197734",
            "size_selection_method": "",
            "library_size": "",
            "smrt_cell_kit": "",
            "smrt_cell_id": "",
            "movie_name": "",
            "polymerase_kit": "",
            "sequencing_kit": "",
            "movie_length_hours": None,
            "includes_kinetics": False,
            "includes_CpG_methylation": False,
            "by_strand": False
        }

        response_200 = self.client.post(url, [experiment1], format='json')
        response_207 = self.client.post(url, [experiment1, experiment2], format='json')
        response_400 = self.client.post(url, [experiment2], format='json')

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeletePacBioAPITest(APITestCaseWithAuth):
    def test_delete_pac_bio_api(self):

        #Checks for the Experiment table before deletion

        experiment1_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-001-002-0-R-2_PB"
        ).exists()

        assert experiment1_exists

        url2 = "/api/experiments/delete_experiment_pac_bio/?ids=UCI_GREGoR_test-001-002-0-R-2_PB, DNE-01-1"
        url3 = "/api/experiments/delete_experiment_pac_bio/?ids=DNE-1, DNE2"

        response_207 = self.client.delete(url2, format='json')
        response_400 = self.client.delete(url3, format='json')

        #Checks for the Experiment table after deletion
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-001-002-0-R-2_PB"
        ).exists()
        assert not experiment2_exists

        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
