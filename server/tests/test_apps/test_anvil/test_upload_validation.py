#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_validation.py

"""Source-data validation tests for the schema-based upload workflow.

Source validation reads the selected tables from the initialized upload
manifest, validates every row against the GREGoR JSON schema, records
excluded rows (with reasons) in the manifest plan, and writes summaries to
AnvilUploadTable.source_summary and AnvilUploadValidationRun.summary.

The invalid fixture contains rows that violate schema enums, e.g.:
- participant solve_status "Affected" (not in the solve_status enum)
- phenotype onset_age_range "unknown" (not an HP: term from the enum)
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from anvil.models import AnvilUpload, AnvilUploadValidationRun
from anvil.services import (
    get_upload_manifest_artifact,
    initialize_upload_package,
    validate_upload_source_data,
)


class SourceValidationRequiresInitializeTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def test_validate_source_without_initialize_raises(self):
        user = get_user_model().objects.get(username="wheel")
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_uninitialized_v1",
            changed_by=user,
        )

        with self.assertRaisesMessage(ValueError, "Run initialize first"):
            validate_upload_source_data(upload=upload, changed_by=user)


class InvalidAnvilUploadValidationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_invalid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_invalid_upload_v1",
            changed_by=self.user,
        )
        initialize_upload_package(upload=self.upload, changed_by=self.user)

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

    def test_invalid_solve_status_row_is_excluded_with_schema_error(self):
        validate_upload_source_data(upload=self.upload, changed_by=self.user)

        manifest = get_upload_manifest_artifact(upload=self.upload).metadata
        participant = manifest["tables"]["by_name"]["participant"]

        excluded_by_pk = {
            row["pk"]: row for row in participant["excluded_rows"]
        }

        self.assertIn("GREGoR_test-006-006-0", excluded_by_pk)

        errors = excluded_by_pk["GREGoR_test-006-006-0"]["errors"]
        self.assertTrue(
            any("'Affected' is not one of" in error["error"] for error in errors),
            msg=f"Expected solve_status enum error, got: {errors}",
        )

    def test_invalid_onset_age_range_rows_are_excluded_with_schema_error(self):
        validate_upload_source_data(upload=self.upload, changed_by=self.user)

        manifest = get_upload_manifest_artifact(upload=self.upload).metadata
        phenotype = manifest["tables"]["by_name"]["phenotype"]

        self.assertGreater(phenotype["excluded_row_count"], 0)

        onset_errors = [
            error
            for row in phenotype["excluded_rows"]
            for error in row["errors"]
            if "'unknown' is not one of" in error["error"]
        ]

        self.assertGreaterEqual(len(onset_errors), 1)

    def test_source_summaries_are_written_to_upload_tables(self):
        validate_upload_source_data(upload=self.upload, changed_by=self.user)

        participant_table = self.upload.upload_tables.get(table_name="participant")
        summary = participant_table.source_summary

        self.assertEqual(summary["source_status"], "failed")
        self.assertEqual(
            summary["source_row_count"],
            summary["included_row_count"] + summary["excluded_row_count"],
        )
        self.assertGreater(summary["excluded_row_count"], 0)

    def test_invalid_upload_source_data_creates_one_validation_run(self):
        validate_upload_source_data(upload=self.upload, changed_by=self.user)

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
        initialize_upload_package(upload=self.upload, changed_by=self.user)

    def test_valid_upload_source_data_passes(self):
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

    def test_valid_run_records_plan_in_manifest(self):
        validate_upload_source_data(upload=self.upload, changed_by=self.user)

        manifest = get_upload_manifest_artifact(upload=self.upload).metadata

        self.assertEqual(manifest["manifest_state"], "source_validated")
        self.assertEqual(manifest["validation"]["source"]["status"], "passed")

        by_name = manifest["tables"]["by_name"]
        self.assertEqual(set(by_name), set(manifest["tables"]["included"]))

        for table_name, table_result in by_name.items():
            self.assertEqual(
                table_result["excluded_rows"],
                [],
                msg=f"Valid fixture should have no exclusions in {table_name}",
            )

    def test_selected_tables_only_validates_selection(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_valid_partial_v1",
            changed_by=self.user,
        )
        initialize_upload_package(
            upload=upload,
            tables=["family", "participant"],
            changed_by=self.user,
        )

        validation_run = validate_upload_source_data(
            upload=upload,
            changed_by=self.user,
        )

        self.assertEqual(
            set(validation_run.summary["tables"]),
            {"family", "participant"},
        )
