"""Tests that the Dashboard can take database records and generate the full upload package.

family.tsv
participant.tsv
phenotype.tsv
analyte.tsv
genetic_findings.tsv

experiment.tsv
experiment_dna_short_read.tsv
experiment_rna_short_read.tsv
experiment_nanopore.tsv
experiment_pac_bio.tsv

aligned.tsv
aligned_dna_short_read.tsv
aligned_rna_short_read.tsv
aligned_nanopore.tsv
aligned_pac_bio.tsv

aligned_dna_short_read_set.tsv
aligned_nanopore_set.tsv
aligned_pac_bio_set.tsv

called_variants_dna_short_read.tsv
called_variants_nanopore.tsv
called_variants_pac_bio.tsv"""

#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_package.py

from django.contrib.auth import get_user_model
from django.test import TestCase

from anvil.services import ANVIL_UPLOAD_TABLES
from anvil.models import AnvilUpload, AnvilUploadArtifact, AnvilUploadTable
from anvil.services import build_upload_tsv_package


class AnvilUploadBuilderTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

    def test_build_upload_tsv_package_creates_21_upload_tables(self):
        result = build_upload_tsv_package(
            upload=self.upload,
            changed_by=self.user,
        )

        self.assertEqual(len(result["upload_tables"]), 21)
        self.assertEqual(AnvilUploadTable.objects.count(), 21)

        actual_table_names = set(
            AnvilUploadTable.objects.values_list("table_name", flat=True)
        )

        self.assertEqual(actual_table_names, set(ANVIL_UPLOAD_TABLES))

    def test_build_upload_tsv_package_creates_21_tsv_artifacts(self):
        result = build_upload_tsv_package(
            upload=self.upload,
            changed_by=self.user,
        )

        self.assertEqual(len(result["tsv_artifacts"]), 21)

        table_tsv_artifacts = AnvilUploadArtifact.objects.filter(
            upload=self.upload,
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
        )

        self.assertEqual(table_tsv_artifacts.count(), 21)

        actual_paths = set(
            table_tsv_artifacts.values_list("relative_path", flat=True)
        )
        expected_paths = {
            f"tables/{table_name}.tsv"
            for table_name in ANVIL_UPLOAD_TABLES
        }

        self.assertEqual(actual_paths, expected_paths)

    def test_build_upload_tsv_package_links_each_artifact_to_upload_table(self):
        build_upload_tsv_package(
            upload=self.upload,
            changed_by=self.user,
        )

        for table_name in ANVIL_UPLOAD_TABLES:
            upload_table = AnvilUploadTable.objects.get(
                upload=self.upload,
                table_name=table_name,
            )

            artifact = AnvilUploadArtifact.objects.get(
                upload=self.upload,
                relative_path=f"tables/{table_name}.tsv",
            )

            self.assertEqual(artifact.upload_table, upload_table)
            self.assertEqual(artifact.file_name, f"{table_name}.tsv")
            self.assertEqual(artifact.content_type, "text/tab-separated-values")
            self.assertEqual(
                artifact.generation_status,
                AnvilUploadArtifact.GenerationStatus.PENDING,
            )

    def test_build_upload_tsv_package_is_idempotent(self):
        build_upload_tsv_package(
            upload=self.upload,
            changed_by=self.user,
        )
        build_upload_tsv_package(
            upload=self.upload,
            changed_by=self.user,
        )

        self.assertEqual(AnvilUploadTable.objects.count(), 21)
        self.assertEqual(
            AnvilUploadArtifact.objects.filter(
                upload=self.upload,
                artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            ).count(),
            21,
        )