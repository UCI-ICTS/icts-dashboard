# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_nanopore_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from experiments.models import Experiment
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


class CreateNanoporeAPITest(APITestCaseWithAuth):
    def test_create_nanopore_api(self):
        url = "/api/experiments/experiment_nanopore/create/"

        experiment1 = {  # Valid
            "experiment_nanopore_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_2",
            "analyte_id": "GREGoR_test-001-001-0-D-3",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_2",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None,
        }

        experiment2 = {  # Valid 2
            "experiment_nanopore_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_2",
            "analyte_id": "GREGoR_test-004-004-0-D-3",
            "experiment_sample_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_2",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None,
        }

        experiment3 = {  # Invalid, missing experiment_type
            "experiment_nanopore_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_2",
            "analyte_id": "GREGoR_test-006-006-0-D-3",
            "experiment_sample_id": "UCI_GREGoR_test-006-006-0-D-3_NANO_2",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": None,  # changed
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None,
        }

        response_200 = self.client.post(url, [experiment1], format="json")
        response_207 = self.client.post(url, [experiment2, experiment1], format="json")
        response_400 = self.client.post(url, [experiment3, experiment3], format="json")

        # Checks for the Experiment table
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-001-001-0-D-3_NANO_2"
        ).exists()
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-004-004-0-D-3_NANO_2"
        ).exists()
        experiment3_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-006-006-0-D-3_NANO_2"
        ).exists()
        assert experiment1_exists
        assert experiment2_exists
        assert not experiment3_exists

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_200.data[0]["request_status"], "CREATED")
        changed_by(self, response_200.data[0], testuser)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        changed_by(self, response_207.data[0], testuser)
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class ReadNanoporePITest(APITestCaseWithAuth):
    def test_read_experiment_nanopore(self):
        url1 = "/api/experiments/experiment_nanopore/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_1"
        url2 = "/api/experiments/experiment_nanopore/?ids=UCI_GREGoR_test-004-004-0-D-3_NANO_1, DNE-01-1"
        url3 = "/api/experiments/experiment_nanopore/?ids=DNE-1, DNE2"

        response_200 = self.client.get(url1, format="json")
        response_207 = self.client.get(url2, format="json")
        response_400 = self.client.get(url3, format="json")
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateNanoporeAPITest(APITestCaseWithAuth):
    def test_update_nanopore_api(self):
        url = "/api/experiments/experiment_nanopore/update/"
        experiment1 = {  # Valid
            "experiment_nanopore_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_1",
            "fragmentation_method": "Covaris g-TUBE",
        }

        experiment2 = {  # Invalid, missing was_barcoded
            "experiment_nanopore_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_1",
            "analyte_id": "GREGoR_test-004-004-0-D-3",
            "experiment_sample_id": "UCI_GREGoR_test-004-004-0-D-3_NANO_1",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": None,  # changed
            "barcode_kit": None,
        }

        response_207 = self.client.post(url, [experiment1, experiment2], format="json")
        response_200 = self.client.post(url, [experiment1], format="json")
        response_400 = self.client.post(url, [experiment2], format="json")

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        changed_by(self, response_200.data[0], testuser)
        timestamps(self, response_200.data[0])
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        changed_by(self, response_207.data[0], testuser)
        timestamps(self, response_207.data[0])
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.data[0]["request_status"], "BAD REQUEST")


class DeleteNanoporeAPITest(APITestCaseWithAuth):
    def test_delete_nanopore_api(self):
        url2 = "/api/experiments/experiment_nanopore/delete/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_1, DNE-01-1"
        url3 = "/api/experiments/experiment_nanopore/delete/?ids=DNE-1, DNE2"

        response_400_1 = self.client.delete(url2, format="json")
        response_400_2 = self.client.delete(url3, format="json")
        self.assertEqual(response_400_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_400_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_400_1.data[0]["data"][:120],
                         '("Cannot delete some instances of model \'ExperimentNanopore\' because they are referenced through protected foreign keys:')
        self.assertEqual(response_400_1.data[1]["data"], "Not found")


    def test_create_and_delete_nanopore_api(self):
        create_url = "/api/experiments/experiment_nanopore/create/"
        experiment1 = {  # Valid
            "experiment_nanopore_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_2",
            "analyte_id": "GREGoR_test-001-001-0-D-3",
            "experiment_sample_id": "UCI_GREGoR_test-001-001-0-D-3_NANO_2",
            "seq_library_prep_kit_method": "Kit 14",
            "fragmentation_method": None,
            "experiment_type": "genome",
            "targeted_regions_method": None,
            "targeted_region_bed_file": None,
            "date_data_generation": "2023-10-10",
            "sequencing_platform": "Oxford Nanopore PromethION 48",
            "chemistry_type": "R10.4.1",
            "was_barcoded": False,
            "barcode_kit": None,
        }
        create_response = self.client.post(create_url, [experiment1], format="json")
        self.assertEqual(create_response.status_code, status.HTTP_200_OK)

        # Checks for the Experiment table before deletion
        experiment1_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-001-001-0-D-3_NANO_2"
        ).exists()
        assert experiment1_exists

        delete_url = "/api/experiments/experiment_nanopore/delete/?ids=UCI_GREGoR_test-001-001-0-D-3_NANO_2"
        delete_response = self.client.delete(delete_url, format="json")

        # Checks for the Experiment table after deletion
        experiment2_exists = Experiment.objects.filter(
            pk="experiment_nanopore.UCI_GREGoR_test-001-001-0-D-3_NANO_2"
        ).exists()
        assert not experiment2_exists

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data[0]["request_status"], "DELETED")
