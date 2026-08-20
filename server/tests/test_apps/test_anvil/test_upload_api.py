#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_api.py

import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from anvil.models import AnvilUpload, AnvilUploadArtifact


class AnvilUploadApiTests(APITestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="wheel")
        self.client.force_authenticate(user=self.user)

        self.upload_id = "UCI_GREGoR_test_api_workflow_v1"
        self.base_url = "/api/anvil/uploads/"

    def upload_detail_url(self):
        return f"{self.base_url}{self.upload_id}/"

    def upload_action_url(self, action):
        return f"{self.base_url}{self.upload_id}/{action}/"

    def test_upload_api_full_workflow(self):
        with tempfile.TemporaryDirectory() as temp_dir, override_settings(
            ANVIL_PACKAGE_ROOT=temp_dir,
        ):
            create_response = self.client.post(
                self.base_url,
                data={
                    "upload_id": self.upload_id,
                    "gregor_model_version": "1.12",
                    "notes": "API workflow test upload.",
                },
                format="json",
            )

            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

            initialize_response = self.client.post(
                self.upload_action_url("initialize"),
                data={},
                format="json",
            )

            self.assertEqual(initialize_response.status_code, status.HTTP_200_OK)

            upload = AnvilUpload.objects.get(upload_id=self.upload_id)
            self.assertEqual(upload.upload_tables.count(), 21)
            self.assertEqual(
                upload.artifacts.filter(
                    artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
                ).count(),
                21,
            )

            source_validation_response = self.client.post(
                self.upload_action_url("validate-source"),
                data={},
                format="json",
            )

            self.assertEqual(
                source_validation_response.status_code,
                status.HTTP_200_OK,
            )
            self.assertTrue(source_validation_response.data["passed"])
            self.assertEqual(source_validation_response.data["error_count"], 0)

            generate_tsvs_response = self.client.post(
                self.upload_action_url("generate-tsvs"),
                data={"output_dir": temp_dir},
                format="json",
            )

            self.assertEqual(generate_tsvs_response.status_code, status.HTTP_200_OK)
            self.assertEqual(generate_tsvs_response.data["generated_count"], 21)

            generate_manifest_response = self.client.post(
                self.upload_action_url("generate-manifest"),
                data={"output_dir": temp_dir},
                format="json",
            )

            self.assertEqual(
                generate_manifest_response.status_code,
                status.HTTP_200_OK,
            )
            self.assertEqual(
                generate_manifest_response.data["table_count"],
                21,
            )
            self.assertEqual(
                generate_manifest_response.data["table_tsv_artifact_count"],
                21,
            )
            self.assertEqual(
                generate_manifest_response.data["manifest_state"],
                "package_generated",
            )

            package_validation_response = self.client.post(
                self.upload_action_url("validate-package"),
                data={},
                format="json",
            )

            self.assertEqual(
                package_validation_response.status_code,
                status.HTTP_200_OK,
            )
            self.assertTrue(package_validation_response.data["passed"])
            self.assertEqual(package_validation_response.data["error_count"], 0)

            upload.refresh_from_db()

            self.assertEqual(upload.status, AnvilUpload.Status.READY_FOR_REVIEW)
            self.assertEqual(upload.upload_tables.count(), 21)
            self.assertEqual(upload.artifacts.count(), 22)
            self.assertGreaterEqual(upload.validation_runs.count(), 2)

            detail_response = self.client.get(
                self.upload_detail_url(),
                format="json",
            )

            self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
            self.assertEqual(detail_response.data["upload_id"], self.upload_id)
