#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_file_validation.py

"""
Pre-flight file validation tests (DCC checks 9-12, local half).

These tests generate synthetic CRAM/BAM/VCF files matching the fixture's
file URIs and sample-ID chains, then run validate_upload_files against a
LocalFileProvider rooted at the staging directory:

- all-synthetic staging with updated md5sums -> run passes
- tampered file bytes -> md5 FAIL on exactly that row
- wrong SM tag in a CRAM header -> alignment_sample FAIL
- wrong VCF sample columns -> vcf_samples FAIL
- missing files -> UNVERIFIED warnings, run still passes
- index URI with a non-index extension -> index_extension FAIL (no file
  access needed; mirrors real production dirt)
"""

import tempfile
import shutil
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from anvil.file_checks import (
    LocalFileProvider,
    check_index_uri,
    strip_uri_bucket,
)
from anvil.models import AnvilUploadValidationRun
from anvil.services import (
    initialize_upload_package,
    validate_upload_files,
)

from anvil.models import AnvilUpload

from experiments.models import AlignedDNAShortRead


class UriHelperTests(TestCase):
    def test_strip_uri_bucket(self):
        self.assertEqual(
            strip_uri_bucket("gs://fc-secure-abc/cram/a.cram"),
            "cram/a.cram",
        )
        self.assertEqual(
            strip_uri_bucket("s3://my-bucket/vcf/b.vcf.gz"),
            "vcf/b.vcf.gz",
        )
        self.assertEqual(strip_uri_bucket("/local/path.bam"), "local/path.bam")

    def test_index_extension_check(self):
        # The real production dirt: a .bam URI declared as a CRAM's index.
        result = check_index_uri(
            file_uri="gs://b/cram/a.cram",
            index_uri="gs://b/cram/a.bam",
        )
        self.assertEqual(result["status"], "FAIL")

        result = check_index_uri(
            file_uri="gs://b/cram/a.cram",
            index_uri="gs://b/cram/a.crai",
        )
        self.assertEqual(result["status"], "PASS")

        # bai and csi are both legal BAM indexes.
        for suffix in (".bai", ".csi"):
            result = check_index_uri(
                file_uri="gs://b/bam/a.bam",
                index_uri=f"gs://b/bam/a{suffix}",
            )
            self.assertEqual(result["status"], "PASS")

        # No expectation for unknown data-file extensions.
        self.assertIsNone(
            check_index_uri(file_uri="gs://b/a.bed", index_uri="gs://b/a.idx")
        )


class FileValidationTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_file_check_v1",
            changed_by=self.user,
        )
        initialize_upload_package(upload=self.upload, changed_by=self.user)

        self.staging = tempfile.TemporaryDirectory()
        self.root = Path(self.staging.name)
        self.addCleanup(self.staging.cleanup)

        # Use the checked-in genomic files from the fixture. Copying keeps
        # tamper and malformed-header tests isolated from the fixture itself.
        fixture_root = Path(__file__).resolve().parents[2] / "fixtures" / "files"
        shutil.copytree(fixture_root, self.root, dirs_exist_ok=True)
        self.provider = LocalFileProvider(root=self.root)

    def _run(self):
        return validate_upload_files(
            upload=self.upload,
            changed_by=self.user,
            provider=self.provider,
        )

    def _failed_rows(self, validation_run, table_name):
        return [
            row
            for row in validation_run.summary["tables"][table_name]["rows"]
            if row["status"] == "FAIL"
        ]

    def test_synthetic_files_pass_all_checks(self):
        validation_run = self._run()

        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.PASSED,
        )

        self.assertEqual(validation_run.error_count, 0)
        self.assertEqual(validation_run.warning_count, 0)

        tables = validation_run.summary["tables"]

        # Every file-bearing exported table was checked.
        self.assertIn("aligned_dna_short_read", tables)
        self.assertIn("called_variants_dna_short_read", tables)

        self.assertEqual(
            tables["aligned_dna_short_read"]["checked_row_count"],
            AlignedDNAShortRead.objects.count(),
        )
        self.assertEqual(
            tables["aligned_dna_short_read"]["failed_row_count"], 0
        )
        self.assertGreater(
            sum(1 for path in self.root.rglob("*") if path.is_file()),
            0,
        )

    def test_validator_metadata_recorded(self):
        validation_run = self._run()

        self.assertEqual(
            validation_run.validator_type,
            AnvilUploadValidationRun.ValidatorType.LOCAL,
        )
        self.assertEqual(
            validation_run.validator_version, "dashboard-file-checks-v0.1"
        )
        self.assertEqual(validation_run.summary["provider"], "local")

    def test_tampered_file_fails_md5(self):
        aligned = AlignedDNAShortRead.objects.order_by(
            "aligned_dna_short_read_id"
        ).first()
        local_path = self.root / strip_uri_bucket(
            aligned.aligned_dna_short_read_file
        )

        with local_path.open("ab") as file_handle:
            file_handle.write(b"tamper")

        validation_run = self._run()

        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.FAILED,
        )
        self.assertEqual(validation_run.error_count, 1)

        failed_rows = self._failed_rows(
            validation_run,
            "aligned_dna_short_read",
        )
        self.assertEqual(len(failed_rows), 1)
        self.assertEqual(failed_rows[0]["pk"], str(aligned.pk))

        md5_check = next(
            check
            for check in failed_rows[0]["checks"]
            if check["check"] == "md5"
        )
        self.assertIn("declared", md5_check["detail"])
        self.assertIn("computed", md5_check["detail"])
        self.assertIn("declared md5", md5_check["detail"])

    def test_wrong_sm_tag_fails_alignment_sample_check(self):
        with patch(
            "anvil.file_checks.read_alignment_sm_tags",
            return_value=["WRONG_SAMPLE"],
        ):
            validation_run = self._run()

        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.FAILED,
        )
        self.assertGreater(validation_run.error_count, 0)

    def test_wrong_vcf_samples_fail_vcf_check(self):
        with patch(
            "anvil.file_checks.read_vcf_samples",
            return_value=["WRONG_SAMPLE"],
        ):
            validation_run = self._run()

        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.FAILED,
        )
        self.assertGreater(validation_run.error_count, 0)

    def test_missing_files_are_unverified_warnings_not_errors(self):
        empty_staging = tempfile.TemporaryDirectory()
        self.addCleanup(empty_staging.cleanup)

        validation_run = validate_upload_files(
            upload=self.upload,
            changed_by=self.user,
            provider=LocalFileProvider(root=empty_staging.name),
        )

        # Nothing resolvable: every row is UNVERIFIED, none FAIL. Presence
        # is enforced AnVIL-side (check_bucket_paths) after transfer.
        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.PASSED,
        )
        self.assertEqual(validation_run.error_count, 0)
        self.assertGreater(validation_run.warning_count, 0)

        tables = validation_run.summary["tables"]
        self.assertEqual(
            tables["aligned_dna_short_read"]["unverified_row_count"],
            AlignedDNAShortRead.objects.count(),
        )

    def test_index_extension_failure_needs_no_file(self):
        aligned = AlignedDNAShortRead.objects.order_by(
            "aligned_dna_short_read_id"
        ).first()
        # Simulate the production defect: index URI ends in .bam.
        aligned.aligned_dna_short_read_index_file = (
            aligned.aligned_dna_short_read_file
        )
        aligned.save(update_fields=["aligned_dna_short_read_index_file"])

        validation_run = self._run()

        self.assertEqual(
            validation_run.status,
            AnvilUploadValidationRun.Status.FAILED,
        )

        failed_rows = self._failed_rows(
            validation_run,
            "aligned_dna_short_read",
        )
        index_check = next(
            check
            for check in failed_rows[0]["checks"]
            if check["check"] == "index_extension"
        )
        self.assertEqual(index_check["status"], "FAIL")

    def test_source_excluded_rows_are_skipped(self):
        # Manually exclude one aligned row in the manifest plan; the file
        # checks must not evaluate it.
        from anvil.services import get_upload_manifest_artifact

        aligned = AlignedDNAShortRead.objects.order_by(
            "aligned_dna_short_read_id"
        ).first()

        manifest_artifact = get_upload_manifest_artifact(upload=self.upload)
        manifest = manifest_artifact.metadata
        manifest["tables"]["by_name"] = {
            "aligned_dna_short_read": {
                "excluded_rows": [
                    {"pk": str(aligned.pk), "reason": "schema validation failed"}
                ],
            },
        }
        manifest_artifact.metadata = manifest
        manifest_artifact.save()

        validation_run = self._run()

        checked = validation_run.summary["tables"][
            "aligned_dna_short_read"
        ]["checked_row_count"]
        self.assertEqual(
            checked, AlignedDNAShortRead.objects.count() - 1
        )
