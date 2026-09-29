#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_manifest_generation.py

"""
Manifest lifecycle tests (v0.2).

The manifest is a living record: initialize creates it, and every stage that
mutates it re-serializes manifest.json to disk. There is no separate
generate-manifest step; generate_upload_tsvs embeds the TSV artifact catalog
and syncs the file itself.
"""

import json
import tempfile
from pathlib import Path
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from anvil.constants import ANVIL_UPLOAD_TABLES
from anvil.models import AnvilUpload, AnvilUploadArtifact
from anvil.services import (
    MANIFEST_VERSION,
    generate_upload_tsvs,
    get_upload_manifest_artifact,
    initialize_upload_package,
    validate_upload_source_data,
)


class AnvilUploadManifestLifecycleTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_manifest_generation_v1",
            changed_by=self.user,
        )

    def _initialize(self):
        initialize_upload_package(upload=self.upload, changed_by=self.user)

    def _generate_package(self):
        self._initialize()
        validate_upload_source_data(upload=self.upload, changed_by=self.user)
        return generate_upload_tsvs(
            upload=self.upload,
            changed_by=self.user,
        )

    def test_initialize_writes_manifest_json(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            self._initialize()

            artifact = get_upload_manifest_artifact(upload=self.upload)
            manifest_path = Path(artifact.storage_uri)

            self.assertTrue(manifest_path.exists())
            self.assertEqual(manifest_path.name, "manifest.json")

            with manifest_path.open("r", encoding="utf-8") as file_handle:
                manifest = json.load(file_handle)

            self.assertEqual(manifest["manifest_version"], MANIFEST_VERSION)
            self.assertEqual(manifest["manifest_state"], "initialized")
            self.assertEqual(
                manifest["validation"],
                {"source": None, "files": None, "package": None},
            )

    def test_generate_tsvs_embeds_artifacts_and_syncs_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            result = self._generate_package()

            manifest_path = Path(result["manifest_path"])
            self.assertTrue(manifest_path.exists())

            with manifest_path.open("r", encoding="utf-8") as file_handle:
                manifest = json.load(file_handle)

            self.assertEqual(manifest["manifest_version"], MANIFEST_VERSION)
            self.assertEqual(manifest["manifest_state"], "package_generated")
            self.assertEqual(
                manifest["upload"]["upload_id"], self.upload.upload_id
            )
            self.assertEqual(
                set(manifest["tables"]["included"]),
                set(ANVIL_UPLOAD_TABLES),
            )

            tsv_entries = manifest["artifacts"]["table_tsvs"]
            self.assertEqual(len(tsv_entries), 21)

            for entry in tsv_entries:
                self.assertTrue(entry["relative_path"].endswith(".tsv"))
                self.assertGreater(entry["byte_size"], 0)
                self.assertTrue(entry["sha256"])

            self.assertEqual(
                manifest["artifacts"]["manifest"],
                {"relative_path": "manifest.json"},
            )

    def test_manifest_artifact_records_file_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            self._generate_package()

            artifact = get_upload_manifest_artifact(upload=self.upload)

            self.assertEqual(
                artifact.artifact_type,
                AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST,
            )
            self.assertEqual(artifact.relative_path, "manifest.json")
            self.assertEqual(artifact.file_name, "manifest.json")
            self.assertEqual(artifact.content_type, "application/json")
            self.assertGreater(artifact.byte_size, 0)
            self.assertTrue(artifact.sha256)
            self.assertTrue(artifact.storage_uri)
            self.assertEqual(
                artifact.generation_status,
                AnvilUploadArtifact.GenerationStatus.GENERATED,
            )

    def test_generate_tsvs_preserves_the_plan(self):
        """Generating the package must enrich the manifest, never replace
        source-validation state."""

        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            self._generate_package()

            manifest = get_upload_manifest_artifact(upload=self.upload).metadata

            self.assertIn("by_name", manifest["tables"])
            self.assertEqual(
                set(manifest["tables"]["by_name"]),
                set(ANVIL_UPLOAD_TABLES),
            )
            self.assertEqual(
                manifest["validation"]["source"]["status"], "passed"
            )
            self.assertEqual(len(manifest["artifacts"]["table_tsvs"]), 21)
            self.assertEqual(manifest["manifest_state"], "package_generated")

    def test_generate_tsvs_invalidates_downstream_validations(self):
        """Regenerated TSVs supersede prior file/package validation results."""

        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            self._generate_package()

            artifact = get_upload_manifest_artifact(upload=self.upload)
            manifest = artifact.metadata
            manifest["validation"]["files"] = {"status": "passed"}
            manifest["validation"]["package"] = {"status": "passed"}
            artifact.metadata = manifest
            artifact.save()

            generate_upload_tsvs(upload=self.upload, changed_by=self.user)

            manifest = get_upload_manifest_artifact(
                upload=self.upload
            ).metadata
            self.assertIsNone(manifest["validation"]["files"])
            self.assertIsNone(manifest["validation"]["package"])
            self.assertEqual(
                manifest["validation"]["source"]["status"], "passed"
            )

    def test_single_manifest_artifact_across_reruns(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            self._generate_package()
            generate_upload_tsvs(upload=self.upload, changed_by=self.user)

            self.assertEqual(
                AnvilUploadArtifact.objects.filter(
                    upload=self.upload,
                    artifact_type=(
                        AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST
                    ),
                ).count(),
                1,
            )


class DerivedUploadStatusTests(TestCase):
    """Regression tests for the stale-status bug: a passing later stage must
    clear validation_failed, and status must reflect all stages, not the
    last one to run."""

    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_status_machine_v1",
            changed_by=self.user,
        )

    def test_passing_file_validation_clears_failed_status(self):
        import shutil
        import tempfile as tempfile_module
        from pathlib import Path as PathClass

        from anvil.file_checks import LocalFileProvider
        from anvil.services import validate_upload_files

        fixture_root = (
            PathClass(__file__).resolve().parents[2] / "fixtures" / "files"
        )

        with tempfile_module.TemporaryDirectory() as temp_dir, \
                override_settings(ANVIL_PACKAGE_ROOT=temp_dir):
            initialize_upload_package(
                upload=self.upload, changed_by=self.user
            )
            validate_upload_source_data(
                upload=self.upload, changed_by=self.user
            )

            staging = PathClass(temp_dir) / "staging"
            shutil.copytree(fixture_root, staging)

            # First: fail file validation via an empty provider root.
            empty = PathClass(temp_dir) / "empty"
            empty.mkdir()

            # Tamper one staged file to force a genuine FAIL (not warning).
            tampered = next(staging.rglob("*.cram"))
            with tampered.open("ab") as file_handle:
                file_handle.write(b"tampered")

            failed_run = validate_upload_files(
                upload=self.upload,
                changed_by=self.user,
                provider=LocalFileProvider(root=staging),
            )
            self.upload.refresh_from_db()

            self.assertEqual(failed_run.status, failed_run.Status.FAILED)
            self.assertEqual(
                self.upload.status, AnvilUpload.Status.VALIDATION_FAILED
            )

            # Then: fix the file and revalidate. Status must recover without
            # rerunning any other stage.
            shutil.rmtree(staging)
            shutil.copytree(fixture_root, staging)

            passed_run = validate_upload_files(
                upload=self.upload,
                changed_by=self.user,
                provider=LocalFileProvider(root=staging),
            )
            self.upload.refresh_from_db()

            self.assertEqual(passed_run.status, passed_run.Status.PASSED)
            self.assertEqual(
                self.upload.status, AnvilUpload.Status.READY_FOR_REVIEW
            )

    def test_failed_source_blocks_ready_even_after_passing_files(self):
        from anvil.services import derive_upload_status

        manifest = {
            "validation": {
                "source": {"status": "failed"},
                "files": {"status": "passed"},
                "package": None,
            },
        }
        self.assertEqual(
            derive_upload_status(manifest=manifest),
            AnvilUpload.Status.VALIDATION_FAILED,
        )

    def test_no_completed_stages_is_draft(self):
        from anvil.services import derive_upload_status

        manifest = {
            "validation": {"source": None, "files": None, "package": None},
        }
        self.assertEqual(
            derive_upload_status(manifest=manifest),
            AnvilUpload.Status.DRAFT,
        )
