"""Tests the generated manifest and WDL input JSON.

It should verify:

- upload ID
- GREGoR data model version
- expected table names
- table row counts
- SHA-256 hash for each generated TSV
- source record counts
- expected GCS output URI pattern
- generated validate_gregor_model input JSON"""

EXPECTED_TABLES = {
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
}