#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_package_validation.py

import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase

from anvil.models import (
    AnvilUpload,
    AnvilUploadArtifact,
    AnvilUploadValidationRun,
)
from anvil.services import (
    generate_upload_manifest,
    generate_upload_tsvs,
    validate_upload_package,
    validate_upload_source_data,
)


class AnvilUploadPackageValidationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_package_validation_v1",
            changed_by=self.user,
        )

    def _build_package(self, temp_dir):
        validate_upload_source_data(
            upload=self.upload,
            changed_by=self.user,
        )
        generate_upload_tsvs(
            upload=self.upload,
            output_dir=temp_dir,
            changed_by=self.user,
        )
        generate_upload_manifest(
            upload=self.upload,
            output_dir=temp_dir,
            changed_by=self.user,
        )

    def test_validate_upload_package_passes_for_generated_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self._build_package(temp_dir)

            validation_run = validate_upload_package(
                upload=self.upload,
                changed_by=self.user,
            )

            validation_run.refresh_from_db()
            self.upload.refresh_from_db()

            self.assertEqual(
                validation_run.status,
                AnvilUploadValidationRun.Status.PASSED,
            )
            self.assertEqual(validation_run.error_count, 0)
            self.assertTrue(validation_run.summary["passed"])

    def test_validate_upload_package_requires_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            validation_run = validate_upload_package(
                upload=self.upload,
                changed_by=self.user,
            )

            error_codes = {
                error["code"]
                for error in validation_run.summary["errors"]
            }

            self.assertEqual(
                validation_run.status,
                AnvilUploadValidationRun.Status.FAILED,
            )
            self.assertIn("missing_upload_manifest_artifact", error_codes)

    def test_validate_upload_package_detects_missing_tsv_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self._build_package(temp_dir)

            artifact = self.upload.artifacts.get(
                relative_path="tables/participant.tsv"
            )
            Path(artifact.storage_uri).unlink()

            validation_run = validate_upload_package(
                upload=self.upload,
                changed_by=self.user,
            )

            error_codes = {
                error["code"]
                for error in validation_run.summary["errors"]
            }

            self.assertEqual(
                validation_run.status,
                AnvilUploadValidationRun.Status.FAILED,
            )
            self.assertIn("missing_artifact_file", error_codes)

    def test_validate_upload_package_detects_tsv_row_count_mismatch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self._build_package(temp_dir)

            upload_table = self.upload.upload_tables.get(table_name="participant")
            upload_table.row_count = upload_table.row_count + 1
            upload_table.save()

            validation_run = validate_upload_package(
                upload=self.upload,
                changed_by=self.user,
            )

            error_codes = {
                error["code"]
                for error in validation_run.summary["errors"]
            }

            self.assertEqual(
                validation_run.status,
                AnvilUploadValidationRun.Status.FAILED,
            )
            self.assertIn("tsv_row_count_mismatch", error_codes)
            self.assertIn("manifest_table_row_count_mismatch", error_codes)

    def test_validate_upload_package_detects_artifact_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self._build_package(temp_dir)

            artifact = self.upload.artifacts.get(
                relative_path="tables/participant.tsv"
            )

            path = Path(artifact.storage_uri)

            with path.open("a", encoding="utf-8") as file_handle:
                file_handle.write("\n")

            validation_run = validate_upload_package(
                upload=self.upload,
                changed_by=self.user,
            )

            error_codes = {
                error["code"]
                for error in validation_run.summary["errors"]
            }

            self.assertEqual(
                validation_run.status,
                AnvilUploadValidationRun.Status.FAILED,
            )
            self.assertIn("artifact_sha256_mismatch", error_codes)

    def test_validate_upload_package_detects_duplicate_tsv_primary_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self._build_package(temp_dir)

            artifact = self.upload.artifacts.get(
                relative_path="tables/participant.tsv"
            )

            path = Path(artifact.storage_uri)
            lines = path.read_text(encoding="utf-8").splitlines()

            # Append the first data row again.
            path.write_text(
                "\n".join(lines + [lines[1]]) + "\n",
                encoding="utf-8",
            )

            # Keep byte_size and sha256 synchronized so this test specifically
            # proves the duplicate-primary-key check works.
            artifact.byte_size = path.stat().st_size
            artifact.sha256 = self._sha256(path)
            artifact.save()

            validation_run = validate_upload_package(
                upload=self.upload,
                changed_by=self.user,
            )

            error_codes = {
                error["code"]
                for error in validation_run.summary["errors"]
            }

            self.assertEqual(
                validation_run.status,
                AnvilUploadValidationRun.Status.FAILED,
            )
            self.assertIn("duplicate_tsv_primary_keys", error_codes)

    def test_validate_upload_package_creates_second_dashboard_validation_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self._build_package(temp_dir)

            validate_upload_package(
                upload=self.upload,
                changed_by=self.user,
            )

            self.assertEqual(self.upload.validation_runs.count(), 2)

    @staticmethod
    def _sha256(path):
        import hashlib

        digest = hashlib.sha256()

        with path.open("rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()
