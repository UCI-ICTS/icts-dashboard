#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_tsv_generation.py

import csv
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from anvil.constants import ANVIL_UPLOAD_TABLES
from anvil.models import AnvilUpload, AnvilUploadArtifact
from anvil.services import (
    generate_upload_tsvs,
    get_upload_manifest_artifact,
    initialize_upload_package,
    validate_upload_source_data,
)


class AnvilUploadTsvGenerationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_tsv_generation_v1",
            changed_by=self.user,
        )
        initialize_upload_package(upload=self.upload, changed_by=self.user)

    def test_generate_upload_tsvs_requires_initialize(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_tsv_uninitialized_v1",
            changed_by=self.user,
        )

        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            with self.assertRaisesMessage(ValueError, "Run initialize first"):
                generate_upload_tsvs(
                    upload=upload,
                    
                    changed_by=self.user,
                )

    def test_generate_upload_tsvs_writes_21_tsv_files(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            result = generate_upload_tsvs(
                upload=self.upload,
                
                changed_by=self.user,
            )

            tables_dir = Path(result["tables_dir"])

            for table_name in ANVIL_UPLOAD_TABLES:
                expected_path = tables_dir / f"{table_name}.tsv"
                self.assertTrue(
                    expected_path.exists(),
                    msg=f"Missing generated TSV: {expected_path}",
                )

    def test_generate_upload_tsvs_writes_only_selected_tables(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_tsv_partial_v1",
            changed_by=self.user,
        )
        initialize_upload_package(
            upload=upload,
            tables=["family", "participant"],
            changed_by=self.user,
        )

        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            result = generate_upload_tsvs(
                upload=upload,
                
                changed_by=self.user,
            )

            tables_dir = Path(result["tables_dir"])
            written = sorted(path.name for path in tables_dir.iterdir())

            self.assertEqual(written, ["family.tsv", "participant.tsv"])

    def test_generate_upload_tsvs_updates_artifacts_as_generated(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            generate_upload_tsvs(
                upload=self.upload,
                
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
                self.assertEqual(
                    artifact.generation_status,
                    AnvilUploadArtifact.GenerationStatus.GENERATED,
                )

    def test_generate_upload_tsvs_updates_table_row_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            generate_upload_tsvs(
                upload=self.upload,
                
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

    def test_generated_participant_tsv_uses_gregor_schema_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            result = generate_upload_tsvs(
                upload=self.upload,
                
                changed_by=self.user,
            )

            participant_path = Path(result["tables_dir"]) / "participant.tsv"

            with participant_path.open("r", newline="", encoding="utf-8") as file_handle:
                reader = csv.DictReader(file_handle, delimiter="\t")
                rows = list(reader)

            self.assertEqual(len(rows), 6)
            self.assertIn("participant_id", reader.fieldnames)
            self.assertIn("solve_status", reader.fieldnames)

            # FK columns must use the schema key, not the DB column.
            self.assertIn("family_id", reader.fieldnames)
            self.assertNotIn("family_id_id", reader.fieldnames)


    def test_generated_set_tsv_expands_m2m_members_to_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            result = generate_upload_tsvs(
                upload=self.upload,
                changed_by=self.user,
            )

            set_path = (
                Path(result["tables_dir"]) / "aligned_dna_short_read_set.tsv"
            )

            with set_path.open("r", newline="", encoding="utf-8") as file_handle:
                reader = csv.DictReader(file_handle, delimiter="\t")
                rows = list(reader)

            self.assertIn("aligned_dna_short_read_id", reader.fieldnames)

            self.assertTrue(
                all(
                    "|" not in row["aligned_dna_short_read_id"]
                    for row in rows
                )
            )

            set_ids = [
                row["aligned_dna_short_read_set_id"]
                for row in rows
            ]

            # Multi-member sets produce repeated set IDs, one row per member.
            self.assertGreater(len(set_ids), len(set(set_ids)))


    def test_generate_upload_tsvs_skips_manifest_excluded_rows(self):
        validate_upload_source_data(upload=self.upload, changed_by=self.user)

        # Simulate a review decision: exclude one participant row in the plan.
        manifest_artifact = get_upload_manifest_artifact(upload=self.upload)
        manifest = manifest_artifact.metadata
        participant_plan = manifest["tables"]["by_name"]["participant"]
        participant_plan["excluded_rows"] = [
            {
                "pk": "GREGoR_test-006-006-0",
                "reason": "excluded for test",
                "errors": [],
            }
        ]
        manifest_artifact.metadata = manifest
        manifest_artifact.save()

        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            result = generate_upload_tsvs(
                upload=self.upload,
                
                changed_by=self.user,
            )

            participant_path = Path(result["tables_dir"]) / "participant.tsv"

            with participant_path.open("r", newline="", encoding="utf-8") as file_handle:
                reader = csv.DictReader(file_handle, delimiter="\t")
                participant_ids = [row["participant_id"] for row in reader]

            self.assertEqual(len(participant_ids), 5)
            self.assertNotIn("GREGoR_test-006-006-0", participant_ids)

        participant_table = self.upload.upload_tables.get(table_name="participant")
        self.assertEqual(participant_table.row_count, 5)

    def test_generate_upload_tsvs_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            first_result = generate_upload_tsvs(
                upload=self.upload,
                
                changed_by=self.user,
            )
            second_result = generate_upload_tsvs(
                upload=self.upload,
                
                changed_by=self.user,
            )

            self.assertEqual(
                len(first_result["generated"]),
                len(second_result["generated"]),
            )

            self.assertEqual(
                AnvilUploadArtifact.objects.filter(
                    upload=self.upload,
                    artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
                ).count(),
                21,
            )
