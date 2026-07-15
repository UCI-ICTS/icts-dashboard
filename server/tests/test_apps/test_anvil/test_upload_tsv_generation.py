#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_tsv_generation.py

import csv
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase

from anvil.constants import ANVIL_UPLOAD_TABLES
from anvil.models import AnvilUpload, AnvilUploadArtifact
from anvil.services import generate_upload_tsvs


class AnvilUploadTsvGenerationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_tsv_generation_v1",
            changed_by=self.user,
        )

    def test_generate_upload_tsvs_writes_21_tsv_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            tables_dir = Path(result["tables_dir"])

            for table_name in ANVIL_UPLOAD_TABLES:
                expected_path = tables_dir / f"{table_name}.tsv"
                self.assertTrue(
                    expected_path.exists(),
                    msg=f"Missing generated TSV: {expected_path}",
                )

    def test_generate_upload_tsvs_updates_artifacts_as_generated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            artifacts = AnvilUploadArtifact.objects.filter(
                upload=self.upload,
                artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            )

            self.assertEqual(artifacts.count(), 21)

            for artifact in artifacts:
                self.assertGreater(artifact.byte_size, 0)
                self.assertTrue(artifact.sha256)
                self.assertTrue(artifact.storage_uri)
                self.assertTrue(artifact.relative_path.endswith(".tsv"))

    def test_generate_upload_tsvs_updates_table_row_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            upload_tables = self.upload.upload_tables.all()

            self.assertEqual(upload_tables.count(), 21)

            table_row_counts = {
                upload_table.table_name: upload_table.row_count
                for upload_table in upload_tables
            }

            self.assertEqual(table_row_counts["family"], 4)
            self.assertEqual(table_row_counts["participant"], 6)
            self.assertEqual(table_row_counts["phenotype"], 21)
            self.assertEqual(table_row_counts["analyte"], 31)
            self.assertEqual(table_row_counts["genetic_findings"], 5)

    def test_generated_participant_tsv_has_header_and_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            participant_path = Path(result["tables_dir"]) / "participant.tsv"

            with participant_path.open("r", newline="", encoding="utf-8") as file_handle:
                reader = csv.DictReader(file_handle, delimiter="\t")
                rows = list(reader)

            self.assertEqual(len(rows), 6)
            self.assertIn("participant_id", reader.fieldnames)
            self.assertIn("family_id_id", reader.fieldnames)
            self.assertIn("solve_status", reader.fieldnames)

    def test_generate_upload_tsvs_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first_result = generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )
            second_result = generate_upload_tsvs(
                upload=self.upload,
                output_dir=temp_dir,
                changed_by=self.user,
            )

            self.assertEqual(
                len(first_result["generated"]),
                len(second_result["generated"]),
            )

            self.assertEqual(
                AnvilUploadArtifact.objects.filter(upload=self.upload).count(),
                21,
            )