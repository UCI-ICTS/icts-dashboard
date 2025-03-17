# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_nanopore_apis.py

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


class CreateNanoporeAPITest(APITestCaseWithAuth):
    def test_create_nanopore_api(self):
        url = "/api/experiments/create_experiment_nanopore/"

        experiment1 = {  # Valid
            "experiment_nanopore_id": "UCI_GREGoR_test-001-003-0_NANO_2",
            "analyte_id": "GREGoR_test-001-003-0-R-3",
            "experiment_sample_id": "UCI_GREGoR_test-001-003-0_NANO_1",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None
        }

        experiment2 = {  # Valid 2
            "experiment_nanopore_id": "UCI_GREGoR_test-003-003-2_NANO_2",
            "analyte_id": "GREGoR_test-003-003-2-R-3",
            "experiment_sample_id": "UCI_GREGoR_test-003-003-2_NANO_1",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None
        }

        experiment3 = {  # Invalid, missing experiment_type
            "experiment_nanopore_id": "UCI_GREGoR_test-003-003-2_NANO_3",
            "analyte_id": "GREGoR_test-003-003-2-R-3",
            "experiment_sample_id": "UCI_GREGoR_test-003-003-2_NANO_1",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": None,  # changed
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None
        }

        response_200 = self.client.post(url, [experiment1], format='json')
        response_207 = self.client.post(url, [experiment2, experiment1], format='json')
        response_400 = self.client.post(url, [experiment3, experiment3], format='json')

        #Checks for the Experiment table
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-001-003-0_NANO_2"
        ).exists()
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-003-003-2_NANO_2"
        ).exists()
        experiment3_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-003-003-2_NANO_3"
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


class ReadNanoporePITest(APITestCaseWithAuth):
    def test_read_experiment_nanopore(self):
        url1 = "/api/experiments/read_experiment_nanopore/?ids=UCI_GREGoR_test-001-003-0_NANO_1"
        url2 = "/api/experiments/read_experiment_nanopore/?ids=UCI_GREGoR_test-003-003-2_NANO_1, DNE-01-1"
        url3 = "/api/experiments/read_experiment_nanopore/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateNanoporeAPITest(APITestCaseWithAuth):
    def test_update_nanopore_api(self):
        url = "/api/experiments/update_experiment_nanopore/"
        experiment1 = {  # Valid
            "experiment_nanopore_id": "UCI_GREGoR_test-001-003-0_NANO_1",
            "analyte_id": "GREGoR_test-001-003-0-R-3",
            "experiment_sample_id": "UCI_GREGoR_test-001-003-0_NANO_1",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": "Covaris g-TUBE",
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None
        }

        experiment2 = {  # Invalid, missing was_barcoded
            "experiment_nanopore_id": "UCI_GREGoR_test-003-003-2_NANO_1",
            "analyte_id": "GREGoR_test-003-003-2-R-3",
            "experiment_sample_id": "UCI_GREGoR_test-003-003-2_NANO_1",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": None,  # changed
            "barcode_kit": None
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


class DeleteNanoporeAPITest(APITestCaseWithAuth):
    def test_delete_nanopore_api(self):

        #Checks for the Experiment table before deletion

        experiment1_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-001-003-0_NANO_1"
        ).exists()

        assert experiment1_exists

        url2 = "/api/experiments/delete_experiment_nanopore/?ids=UCI_GREGoR_test-001-003-0_NANO_1, DNE-01-1"
        url3 = "/api/experiments/delete_experiment_nanopore/?ids=DNE-1, DNE2"

        response_207 = self.client.delete(url2, format='json')
        response_400 = self.client.delete(url3, format='json')

        #Checks for the Experiment table after deletion
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-001-003-0_NANO_1"
        ).exists()
        assert not experiment2_exists

        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response_207.data[0]["request_status"], "DELETED")
        self.assertEqual(response_207.data[1]["request_status"], "NOT FOUND")
