# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_pac_bio_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from experiments.models import Experiment
from datetime import datetime


testuser = "testuser"


def created_by(self, response_dict, created_user):
    """
    Assert created_by username matches expected created_by username
    """
    self.assertEqual(response_dict["data"]["instance"]["created_by"], created_user)


def usernames(self, response_dict):
    """
    Assert updated_by and created_by usernames differ after a successful update
    """
    self.assertNotEqual(
        response_dict["data"]["instance"]["updated_by"],
        response_dict["data"]["instance"]["created_by"]
    )


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


class CreatePacBioAPITest(APITestCaseWithAuth):
    def test_create_pac_bio_api(self):
        url = "/api/experiments/experiment_pac_bio/create/"

        experiment1 = {  # Valid
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-20_PB_1",
            "analyte_id": "GREGoR_test-001-001-0-D-2",
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
            "by_strand": False,
        }

        experiment2 = {  # Valid 2
            "experiment_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-20_PB_1",
            "analyte_id": "GREGoR_test-003-001-1-D-2",
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
            "by_strand": False,
        }

        experiment3 = {  # Invalid, missing experiment_type
            "experiment_pac_bio_id": "UCI_GREGoR_test-002-001-2-D-20_PB_1",
            "analyte_id": "GREGoR_test-002-001-2-D-2",
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
            "by_strand": False,
        }

        response_200 = self.client.post(url, [experiment1], format="json")
        response_207 = self.client.post(url, [experiment2, experiment1], format="json")
        response_400 = self.client.post(url, [experiment3, experiment3], format="json")

        # Checks for the Experiment table
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-001-001-0-D-20_PB_1"
        ).exists()
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-003-001-1-D-20_PB_1"
        ).exists()
        experiment3_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-002-001-2-D-20_PB_1"
        ).exists()
        assert experiment1_exists
        assert experiment2_exists
        assert not experiment3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        created_by(self, response_200.data[0], testuser)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        created_by(self, response_207.data[0], testuser)
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadPacBioPITest(APITestCaseWithAuth):
    def test_read_experiment_pac_bio(self):
        url1 = "/api/experiments/experiment_pac_bio/?ids=UCI_GREGoR_test-001-001-0-D-2_PB_1"
        url2 = "/api/experiments/experiment_pac_bio/?ids=UCI_GREGoR_test-003-001-1-D-2_PB_1, DNE-01-1"
        url3 = "/api/experiments/experiment_pac_bio/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdatePacBioAPITest(APITestCaseWithAuth):
    def test_update_pac_bio_api(self):
        url = "/api/experiments/experiment_pac_bio/update/"
        experiment1 = {  # Valid
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-2_PB_1",
            "fragmentation_method": "Hamilton Microlab Pipette Shearing",
        }

        experiment2 = {  # Invalid, missing experiment_type
            "experiment_pac_bio_id": "UCI_GREGoR_test-003-001-1-D-2_PB_1",
            "analyte_id": "GREGoR_test-003-001-1-D-2",
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
            "by_strand": False,
        }

        response_207 = self.client.post(url, [experiment1, experiment2], format="json")
        response_200 = self.client.post(url, [experiment1], format="json")
        response_400 = self.client.post(url, [experiment2], format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        usernames(self, response_200.data[0])
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        usernames(self, response_207.data[0])
        timestamps(self, response_207.data[0])
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeletePacBioAPITest(APITestCaseWithAuth):
    def test_delete_pac_bio_api(self):
        url2 = "/api/experiments/experiment_pac_bio/delete/?ids=UCI_GREGoR_test-001-001-0-D-2_PB_1, DNE-01-1"
        url3 = "/api/experiments/experiment_pac_bio/delete/?ids=DNE-1, DNE2"

        response_400_1 = self.client.delete(url2, format="json")
        response_400_2 = self.client.delete(url3, format="json")
        self.assertEqual(response_400_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_400_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_400_1.data[0]["data"][:118],
                         '("Cannot delete some instances of model \'ExperimentPacBio\' because they are referenced through protected foreign keys:')
        self.assertEqual(response_400_1.data[1]["data"], "Not found")


    def test_create_and_delete_pac_bio_api(self):
        create_url = "/api/experiments/experiment_pac_bio/create/"
        experiment1 = {  # Valid
            "experiment_pac_bio_id": "UCI_GREGoR_test-001-001-0-D-20_PB_1",
            "analyte_id": "GREGoR_test-001-001-0-D-2",
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
            "by_strand": False,
        }
        create_response = self.client.post(create_url, [experiment1], format="json")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)

        # Checks for the Experiment table before deletion
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-001-001-0-D-20_PB_1"
        ).exists()
        assert experiment1_exists

        delete_url = "/api/experiments/experiment_pac_bio/delete/?ids=UCI_GREGoR_test-001-001-0-D-20_PB_1"
        delete_response = self.client.delete(delete_url, format="json")

        # Checks for the Experiment table after deletion
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_pac_bio.UCI_GREGoR_test-001-001-0-D-20_PB_1"
        ).exists()
        assert not experiment2_exists

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data[0]["request_status"], "DELETED")
