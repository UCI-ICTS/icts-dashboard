#!/usr/bin/env python
# tests/test_apps/test_anvil/test_services.py

from django.contrib.auth.models import User
from django.test import TestCase

from anvil.models import AnvilUpload, AnvilUploadTable
from anvil.services import initialize_upload_tables, ANVIL_UPLOAD_TABLES


class AnvilUploadServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="test-password",
        )
        self.upload = AnvilUpload.objects.create(
            upload_id="UCI_GREGoR_test_upload_v1",
            changed_by=self.user,
        )

    def test_initialize_upload_tables_creates_expected_21_tables(self):
        upload_tables = initialize_upload_tables(
            upload=self.upload,
            changed_by=self.user,
        )

        self.assertEqual(len(upload_tables), 21)
        self.assertEqual(AnvilUploadTable.objects.count(), 21)

        actual_table_names = set(
            AnvilUploadTable.objects.values_list("table_name", flat=True)
        )

        self.assertEqual(actual_table_names, set(ANVIL_UPLOAD_TABLES))

    def test_initialize_upload_tables_is_idempotent(self):
        initialize_upload_tables(
            upload=self.upload,
            changed_by=self.user,
        )
        initialize_upload_tables(
            upload=self.upload,
            changed_by=self.user,
        )

        self.assertEqual(AnvilUploadTable.objects.count(), 21)

    def test_initialize_upload_tables_sets_changed_by_on_created_rows(self):
        initialize_upload_tables(
            upload=self.upload,
            changed_by=self.user,
        )

        for upload_table in AnvilUploadTable.objects.all():
            self.assertEqual(upload_table.changed_by, self.user)