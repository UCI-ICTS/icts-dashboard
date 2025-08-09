# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_dna_short_read_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from experiments.models import Experiment


class APITestCaseWithAuth(APITestCase):
    fixtures = ["tests/fixtures/test_fixture.json"]

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)


class CreateDNAShortReadAPITest(APITestCaseWithAuth):
    def test_create_dna_short_read_api(self):
        url = "/api/experiments/experiment_dna_short_read/create/"

        experiment1 = {  # Valid
            "experiment_dna_short_read_id": "UCI_GREGoR_test-001-001-0-D-1_DNA_2",
            "analyte_id": "GREGoR_test-001-001-0-D-1",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0-D-1_DNA_2",
            "seq_library_prep_kit_method": "IDT xGen DNA EZ library preparation, Custom 2S Turbo for Invitae",
            "read_length": 150,
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2022-12-29",
            "target_insert_size": 150,
            "sequencing_platform": "NovaSeq",
            "sequencing_event_details": "",
        }

        experiment2 = {  # Valid 2
            "experiment_dna_short_read_id": "UCI_GREGoR_test-002-001-2-D-1_DNA_2",
            "analyte_id": "GREGoR_test-002-001-2-D-1",
            "experiment_sample_id": "UCI_GREGoR_test-002-001-2-D-1_DNA_2",
            "seq_library_prep_kit_method": "IDT xGen DNA EZ library preparation, Custom 2S Turbo for Invitae",
            "read_length": 150,
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2022-07-06",
            "target_insert_size": 150,
            "sequencing_platform": "NovaSeq",
            "sequencing_event_details": "",
        }

        experiment3 = {  # Valid 3
            "experiment_dna_short_read_id": "UCI_GREGoR_test-003-001-1-D-1_DNA_2",
            "analyte_id": "GREGoR_test-003-001-1-D-1",
            "experiment_sample_id": "UCI_GREGoR_test-003-001-1-D-1_DNA_2",
            "seq_library_prep_kit_method": "IDT xGen DNA EZ library preparation, Custom 2S Turbo for Invitae",
            "read_length": 150,
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2022-05-03",
            "target_insert_size": 150,
            "sequencing_platform": "NovaSeq",
            "sequencing_event_details": "",
        }

        response_200 = self.client.post(url, [experiment1, experiment2], format="json")
        response_207 = self.client.post(url, [experiment1, experiment3], format="json")
        response_400 = self.client.post(url, [experiment2, experiment2], format="json")

        # Checks for the Experiment table
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_dna_short_read.UCI_GREGoR_test-001-001-0-D-1_DNA_2"
        ).exists()
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_dna_short_read.UCI_GREGoR_test-002-001-2-D-1_DNA_2"
        ).exists()
        experiment3_exists = Experiment.objects.filter(
            pk="experiment_dna_short_read.UCI_GREGoR_test-003-001-1-D-1_DNA_2"
        ).exists()
        assert experiment1_exists
        assert experiment2_exists
        assert experiment3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "BAD REQUEST")
        self.assertEqual(response_207.data[1]["request_status"], "CREATED")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadDNAShortReadAPITest(APITestCaseWithAuth):
    def test_read_experiment_dna_short_read(self):
        url1 = "/api/experiments/experiment_dna_short_read/?ids=UCI_GREGoR_test-001-001-0-D-1_DNA_1"
        url2 = "/api/experiments/experiment_dna_short_read/?ids=UCI_GREGoR_test-002-001-2-D-1_DNA_1, DNE-01-1"
        url3 = "/api/experiments/experiment_dna_short_read/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateDNAShortReadAPITest(APITestCaseWithAuth):
    def test_update_dna_short_read_api(self):
        url = "/api/experiments/experiment_dna_short_read/update/"
        experiment1 = {  # Valid
            "experiment_dna_short_read_id": "UCI_GREGoR_test-001-001-0-D-1_DNA_1",
            "target_insert_size": 500,  # changed from 150
        }

        experiment2 = {  # Invalid, missing target_insert_size
            "experiment_dna_short_read_id": "UCI_GREGoR_test-002-001-2-D-1_DNA_1",
            "analyte_id": "GREGoR_test-002-001-2-D-1",
            "experiment_sample_id": "UCI_GREGoR_test-002-001-2-D-1_DNA_1",
            "seq_library_prep_kit_method": "IDT xGen DNA EZ library preparation, Custom 2S Turbo for Invitae",
            "read_length": 150,
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2022-07-06",
            "target_insert_size": "",  # missing
            "sequencing_platform": "NovaSeq",
            "sequencing_event_details": "",
        }

        response_207 = self.client.post(url, [experiment1, experiment2], format="json")
        response_200 = self.client.post(url, [experiment1], format="json")  # Returns SUCCESS instead of UPDATED
        response_400 = self.client.post(url, [experiment2, experiment2], format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteDNAShortReadAPITest(APITestCaseWithAuth):
    def test_delete_dna_short_read_api(self):
        url2 = "/api/experiments/experiment_dna_short_read/delete/?ids=UCI_GREGoR_test-001-001-0-D-1_DNA_1, DNE-01-1"
        url3 = "/api/experiments/experiment_dna_short_read/delete/?ids=DNE-1, DNE2"

        response_400_1 = self.client.delete(url2, format="json")
        response_400_2 = self.client.delete(url3, format="json")
        self.assertEqual(response_400_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_400_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_400_1.data[0]["data"][:124],
                         '("Cannot delete some instances of model \'ExperimentDNAShortRead\' because they are referenced through protected foreign keys:')
        self.assertEqual(response_400_1.data[1]["data"], "Not found")


    def test_create_and_delete_dna_short_read_api(self):
        create_url = "/api/experiments/experiment_dna_short_read/create/"
        experiment1 = {  # Valid
            "experiment_dna_short_read_id": "UCI_GREGoR_test-001-001-0-D-1_DNA_2",
            "analyte_id": "GREGoR_test-001-001-0-D-1",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0-D-1_DNA_2",
            "seq_library_prep_kit_method": "IDT xGen DNA EZ library preparation, Custom 2S Turbo for Invitae",
            "read_length": 150,
            "experiment_type": "genome",
            "targeted_regions_method": "",
            "targeted_region_bed_file": "",
            "date_data_generation": "2022-12-29",
            "target_insert_size": 150,
            "sequencing_platform": "NovaSeq",
            "sequencing_event_details": "",
        }
        create_response = self.client.post(create_url, [experiment1], format="json")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)

        # Checks for the Experiment table before deletion
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_dna_short_read.UCI_GREGoR_test-001-001-0-D-1_DNA_2"
        ).exists()
        assert experiment1_exists

        delete_url = "/api/experiments/experiment_dna_short_read/delete/?ids=UCI_GREGoR_test-001-001-0-D-1_DNA_2"
        delete_response = self.client.delete(delete_url, format="json")

        # Checks for the Experiment table after deletion
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_dna_short_read.UCI_GREGoR_test-001-001-0-D-1_DNA_2"
        ).exists()
        assert not experiment2_exists

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data[0]["request_status"], "DELETED")
