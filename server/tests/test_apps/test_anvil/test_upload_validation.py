"""Tests that upload-level errors are found before export.

Examples:

- missing generic experiment row
- genetic finding references experiment absent from experiment.tsv
- aligned row references absent experiment
- callset references absent alignment set
- invalid solve_status
- invalid phenotype onset term
- duplicate generated phenotype identifier
- expected file URI missing
- deleted/test-only rows included in upload"""


from django.contrib.auth import get_user_model
from django.test import TestCase

from anvil.models import AnvilUpload, AnvilUploadValidationRun
from anvil.services import validate_upload_source_data


class InvalidAnvilUploadValidationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_invalid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_invalid_upload_v1",
            changed_by=self.user,
        )

    def test_invalid_upload_source_data_fails_validation(self):
        validation_run = validate_upload_source_data(
            upload=self.upload,
            changed_by=self.user,
        )

        validation_run.refresh_from_db()
        self.upload.refresh_from_db()

        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.FAILED,
        )
        self.assertEqual(
            self.upload.status,
            AnvilUpload.Status.VALIDATION_FAILED,
        )
        self.assertGreater(validation_run.error_count, 0)
        self.assertFalse(validation_run.summary["passed"])

    def test_invalid_upload_source_data_reports_known_error_codes(self):
        validation_run = validate_upload_source_data(
            upload=self.upload,
            changed_by=self.user,
        )

        error_codes = {
            error["code"]
            for error in validation_run.summary["errors"]
        }

        self.assertIn("invalid_solve_status", error_codes)
        self.assertIn("invalid_onset_age_range", error_codes)
        self.assertIn("delete_marked_alignment_set", error_codes)

    def test_invalid_upload_source_data_reports_invalid_solve_status_record(self):
        validation_run = validate_upload_source_data(
            upload=self.upload,
            changed_by=self.user,
        )

        errors = validation_run.summary["errors"]

        matching_errors = [
            error
            for error in errors
            if (
                error["code"] == "invalid_solve_status"
                and error["pk"] == "GREGoR_test-006-006-0"
                and error["field"] == "solve_status"
                and error["value"] == "Affected"
            )
        ]

        self.assertEqual(len(matching_errors), 1)

    def test_invalid_upload_source_data_reports_unknown_onset_values(self):
        validation_run = validate_upload_source_data(
            upload=self.upload,
            changed_by=self.user,
        )

        errors = validation_run.summary["errors"]

        matching_errors = [
            error
            for error in errors
            if (
                error["code"] == "invalid_onset_age_range"
                and error["field"] == "onset_age_range"
                and error["value"] == "unknown"
            )
        ]

        self.assertGreaterEqual(len(matching_errors), 1)

    def test_invalid_upload_source_data_creates_one_validation_run(self):
        validate_upload_source_data(
            upload=self.upload,
            changed_by=self.user,
        )

        self.assertEqual(
            AnvilUploadValidationRun.objects.filter(upload=self.upload).count(),
            1,
        )


class ValidAnvilUploadValidationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_valid_upload_v1",
            changed_by=self.user,
        )

    def test_valid_upload_source_data_passes_first_validation_slice(self):
        validation_run = validate_upload_source_data(
            upload=self.upload,
            changed_by=self.user,
        )

        validation_run.refresh_from_db()
        self.upload.refresh_from_db()

        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.PASSED,
        )
        self.assertEqual(
            self.upload.status,
            AnvilUpload.Status.READY_FOR_REVIEW,
        )
        self.assertEqual(validation_run.error_count, 0)
        self.assertTrue(validation_run.summary["passed"])
        self.assertEqual(validation_run.summary["errors"], [])