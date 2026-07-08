#!/usr/bin/env python
# anvil/services.py

from django.db import transaction

from anvil.models import AnvilUploadTable


ANVIL_UPLOAD_TABLES = [
    "family",
    "participant",
    "phenotype",
    "analyte",
    "genetic_findings",
    "experiment",
    "experiment_dna_short_read",
    "experiment_rna_short_read",
    "experiment_nanopore",
    "experiment_pac_bio",
    "aligned",
    "aligned_dna_short_read",
    "aligned_rna_short_read",
    "aligned_nanopore",
    "aligned_pac_bio",
    "aligned_dna_short_read_set",
    "aligned_nanopore_set",
    "aligned_pac_bio_set",
    "called_variants_dna_short_read",
    "called_variants_nanopore",
    "called_variants_pac_bio",
]


@transaction.atomic
def initialize_upload_tables(*, upload, changed_by=None):
    """
    Ensure that the upload has one AnvilUploadTable row for every GREGoR table
    expected in the Dashboard-generated AnVIL package.

    This is idempotent: calling it multiple times for the same upload will not
    create duplicate table rows.
    """

    upload_tables = []

    for table_name in ANVIL_UPLOAD_TABLES:
        upload_table, _created = AnvilUploadTable.objects.get_or_create(
            upload=upload,
            table_name=table_name,
            defaults={
                "changed_by": changed_by,
            },
        )
        upload_tables.append(upload_table)

    return upload_tables