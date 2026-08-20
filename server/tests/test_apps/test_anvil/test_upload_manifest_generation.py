#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_manifest_generation.py

import json
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase

from anvil.constants import ANVIL_UPLOAD_TABLES
from anvil.models import AnvilUpload, AnvilUploadArtifact
from anvil.services import (
    generate_upload_manifest,
    generate_upload_tsvs,
    get_upload_manifest_artifact,
    initialize_upload_package,
    validate_upload_source_data,
)


class AnvilUploadManifestGenerationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_manifest_generation_v1",
            changed_by=self.user,
        )
        initialize_upload_package(upload=self.upload, changed_by=self.user)

    def _generate_package(self, temp_dir):
        validate_upload_source_data(upload=self.upload, changed_by=self.user)
        generate_upload_tsvs(
            upload=self.upload,
            output_dir=temp_dir,
            changed_by=self.user,
        )
        return generate_upload_manifest(
            upload=self.upload,
            output_dir=temp_dir,
            changed_by=self.user,
        )

    def test_generate_upload_manifest_writes_manifest_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self._generate_package(temp_dir)

            manifest_path = Path(result["manifest_path"])

            self.assertTrue(manifest_path.exists())
            self.assertEqual(manifest_path.name, "manifest.json")

    def test_generate_upload_manifest_records_manifest_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self._generate_package(temp_dir)

            artifact = result["artifact"]

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

    def test_manifest_file_describes_all_selected_tables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self._generate_package(temp_dir)

            manifest_path = Path(result["manifest_path"])

            with manifest_path.open("r", encoding="utf-8") as file_handle:
                manifest = json.load(file_handle)

            self.assertEqual(
                manifest["manifest_version"],
                "dashboard-anvil-upload-manifest-v0.1",
            )
            self.assertEqual(manifest["manifest_state"], "package_generated")
            self.assertEqual(manifest["upload"]["upload_id"], self.upload.upload_id)
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

    def test_generate_upload_manifest_preserves_the_plan(self):
        """The manifest is the living upload plan: generating the package
        manifest must enrich it, never replace source-validation state."""

        with tempfile.TemporaryDirectory() as temp_dir:
            self._generate_package(temp_dir)

            manifest = get_upload_manifest_artifact(upload=self.upload).metadata

            # Plan state written by initialize + validate-source survives.
            self.assertIn("by_name", manifest["tables"])
            self.assertEqual(
                set(manifest["tables"]["by_name"]),
                set(ANVIL_UPLOAD_TABLES),
            )
            self.assertEqual(manifest["validation"]["source"]["status"], "passed")

            # Enrichment from this stage is present.
            self.assertEqual(len(manifest["artifacts"]["table_tsvs"]), 21)
            self.assertEqual(manifest["manifest_state"], "package_generated")

    def test_generate_upload_manifest_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first_result = self._generate_package(temp_dir)
            second_result = generate_upload_manifest(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            self.assertEqual(
                first_result["artifact"].pk,
                second_result["artifact"].pk,
            )

            self.assertEqual(
                AnvilUploadArtifact.objects.filter(
                    upload=self.upload,
                    artifact_type=AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST,
                ).count(),
                1,
            )

    def test_generate_upload_manifest_requires_initialize(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_manifest_uninitialized_v1",
            changed_by=self.user,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesMessage(ValueError, "Run initialize first"):
                generate_upload_manifest(
                    upload=upload,
                    output_dir=temp_dir,
                    changed_by=self.user,
                )

    def test_generate_upload_manifest_requires_generated_tsvs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesMessage(ValueError, "generate_upload_tsvs"):
                generate_upload_manifest(
                    upload=self.upload,
                    output_dir=temp_dir,
                    changed_by=self.user,
                )
