#!/usr/bin/env python
# tests/test_apps/test_anvil/models.py

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from anvil.models import (
    AnvilUpload,
    AnvilUploadArtifact,
    AnvilUploadTable,
    AnvilUploadValidationRun,
)


class AnvilUploadModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="test-password",
        )

    def test_anvil_upload_can_be_created(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
            notes="Test upload package.",
        )

        self.assertEqual(upload.upload_id, "UCI_GREGoR_test_upload_v1")
        self.assertEqual(upload.status, AnvilUpload.Status.DRAFT)
        self.assertEqual(upload.gregor_model_version, "1.12")
        self.assertFalse(upload.needs_review)
        self.assertEqual(upload.changed_by, self.user)
        self.assertIsNotNone(upload.created_at)
        self.assertIsNotNone(upload.updated_at)

    def test_anvil_upload_string_representation(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

        self.assertIn("UCI_GREGoR_test_upload_v1", str(upload))
        self.assertIn("Draft", str(upload))

    def test_upload_table_can_be_created(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

        upload_table = AnvilUploadTable.objects.create(
            upload=upload,
            table_name="participant",
            row_count=6,
            column_names=[
                "participant_id",
                "gregor_center",
                "consent_code",
                "family_id",
            ],
            changed_by=self.user,
        )

        self.assertEqual(upload_table.upload, upload)
        self.assertEqual(upload_table.table_name, "participant")
        self.assertEqual(upload_table.row_count, 6)
        self.assertEqual(
            upload_table.generation_status,
            AnvilUploadTable.GenerationStatus.PENDING,
        )
        self.assertEqual(
            upload.upload_tables.get(table_name="participant"),
            upload_table,
        )

    def test_upload_table_is_unique_per_upload_and_table_name(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

        AnvilUploadTable.objects.create(
            upload=upload,
            table_name="participant",
            changed_by=self.user,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AnvilUploadTable.objects.create(
                    upload=upload,
                    table_name="participant",
                    changed_by=self.user,
                )

    def test_same_table_name_can_exist_in_different_uploads(self):
        upload_one = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )
        upload_two = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v2",
            changed_by=self.user,
        )

        AnvilUploadTable.objects.create(
            upload=upload_one,
            table_name="participant",
            changed_by=self.user,
        )
        AnvilUploadTable.objects.create(
            upload=upload_two,
            table_name="participant",
            changed_by=self.user,
        )

        self.assertEqual(
            AnvilUploadTable.objects.filter(table_name="participant").count(),
            2,
        )

    def test_upload_artifact_can_be_created(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

        upload_table = AnvilUploadTable.objects.create(
            upload=upload,
            table_name="participant",
            changed_by=self.user,
        )

        artifact = AnvilUploadArtifact.objects.create(
            upload=upload,
            upload_table=upload_table,
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            relative_path="tables/participant.tsv",
            file_name="participant.tsv",
            content_type="text/tab-separated-values",
            byte_size=1024,
            sha256="a" * 64,
            changed_by=self.user,
        )

        self.assertEqual(artifact.upload, upload)
        self.assertEqual(artifact.upload_table, upload_table)
        self.assertEqual(artifact.artifact_type, AnvilUploadArtifact.ArtifactType.TABLE_TSV)
        self.assertEqual(artifact.generation_status, AnvilUploadArtifact.GenerationStatus.PENDING)
        self.assertEqual(artifact.relative_path, "tables/participant.tsv")
        self.assertEqual(artifact.file_name, "participant.tsv")
        self.assertEqual(artifact.sha256, "a" * 64)

    def test_upload_artifact_path_is_unique_per_upload(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

        AnvilUploadArtifact.objects.create(
            upload=upload,
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            relative_path="tables/participant.tsv",
            file_name="participant.tsv",
            changed_by=self.user,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AnvilUploadArtifact.objects.create(
                    upload=upload,
                    artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
                    relative_path="tables/participant.tsv",
                    file_name="participant.tsv",
                    changed_by=self.user,
                )

    def test_same_artifact_path_can_exist_in_different_uploads(self):
        upload_one = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )
        upload_two = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v2",
            changed_by=self.user,
        )

        AnvilUploadArtifact.objects.create(
            upload=upload_one,
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            relative_path="tables/participant.tsv",
            file_name="participant.tsv",
            changed_by=self.user,
        )
        AnvilUploadArtifact.objects.create(
            upload=upload_two,
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            relative_path="tables/participant.tsv",
            file_name="participant.tsv",
            changed_by=self.user,
        )

        self.assertEqual(
            AnvilUploadArtifact.objects.filter(
                relative_path="tables/participant.tsv",
            ).count(),
            2,
        )

    def test_validation_run_can_be_created_and_marked_running(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

        validation_run = AnvilUploadValidationRun.objects.create(
            upload=upload,
            validator_type=AnvilUploadValidationRun.ValidatorType.DASHBOARD,
            validator_version="dashboard-test",
            changed_by=self.user,
        )

        self.assertEqual(validation_run.status, AnvilUploadValidationRun.Status.QUEUED)
        self.assertEqual(validation_run.error_count, 0)
        self.assertEqual(validation_run.warning_count, 0)

        validation_run.mark_running()
        validation_run.save()

        validation_run.refresh_from_db()
        self.assertEqual(validation_run.status, AnvilUploadValidationRun.Status.RUNNING)
        self.assertIsNotNone(validation_run.started_at)
        self.assertIsNone(validation_run.finished_at)

    def test_validation_run_can_be_marked_complete(self):
        upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

        validation_run = AnvilUploadValidationRun.objects.create(
            upload=upload,
            validator_type=AnvilUploadValidationRun.ValidatorType.DASHBOARD,
            validator_version="dashboard-test",
            changed_by=self.user,
        )

        summary = {
            "tables": {
                "participant": {
                    "included": 6,
                    "excluded": 0,
                }
            }
        }

        validation_run.mark_complete(
            passed=True,
            message="Validation passed.",
            summary=summary,
        )
        validation_run.save()

        validation_run.refresh_from_db()
        self.assertEqual(validation_run.status, AnvilUploadValidationRun.Status.PASSED)
        self.assertEqual(validation_run.message, "Validation passed.")
        self.assertEqual(validation_run.summary, summary)
        self.assertIsNotNone(validation_run.finished_at)