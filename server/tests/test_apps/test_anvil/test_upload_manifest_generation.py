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

    def test_generate_upload_manifest_writes_manifest_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            validate_upload_source_data(
                upload=self.upload,
                changed_by=self.user,
            )
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            result = generate_upload_manifest(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            manifest_path = Path(result["manifest_path"])

            self.assertTrue(manifest_path.exists())
            self.assertEqual(manifest_path.name, "manifest.json")

    def test_generate_upload_manifest_records_manifest_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            result = generate_upload_manifest(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

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

    def test_manifest_describes_21_generated_tables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )
            result = generate_upload_manifest(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            manifest_path = Path(result["manifest_path"])

            with manifest_path.open("r", encoding="utf-8") as file_handle:
                manifest = json.load(file_handle)

            self.assertEqual(
                manifest["manifest_version"],
                "dashboard-anvil-upload-manifest-v0.1",
            )
            self.assertEqual(manifest["upload"]["upload_id"], self.upload.upload_id)
            self.assertEqual(manifest["summary"]["table_count"], 21)
            self.assertEqual(manifest["summary"]["table_tsv_artifact_count"], 21)

            table_names = {
                table_entry["table_name"]
                for table_entry in manifest["tables"]
            }

            self.assertEqual(table_names, set(ANVIL_UPLOAD_TABLES))

    def test_manifest_includes_tsv_artifact_checksums(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )
            result = generate_upload_manifest(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            manifest = result["manifest"]

            self.assertEqual(len(manifest["table_tsv_artifacts"]), 21)

            for artifact in manifest["table_tsv_artifacts"]:
                self.assertTrue(artifact["relative_path"].endswith(".tsv"))
                self.assertGreater(artifact["byte_size"], 0)
                self.assertTrue(artifact["sha256"])

    def test_generate_upload_manifest_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            first_result = generate_upload_manifest(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )
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

    def test_generate_upload_manifest_requires_generated_tsvs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                generate_upload_manifest(
                    upload=self.upload,
                    output_dir=temp_dir,
                    changed_by=self.user,
                )