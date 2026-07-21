#!/usr/bin/env python
# anvil/constants.py


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

TSV_CONTENT_TYPE = "text/tab-separated-values"

ANVIL_UPLOAD_TABLE_MODEL_MAP = {
    "family": ("metadata", "family"),
    "participant": ("metadata", "participant"),
    "phenotype": ("metadata", "phenotype"),
    "analyte": ("metadata", "analyte"),
    "genetic_findings": ("metadata", "geneticfindings"),

    "experiment": ("experiments", "experiment"),
    "experiment_dna_short_read": ("experiments", "experimentdnashortread"),
    "experiment_rna_short_read": ("experiments", "experimentrnashortread"),
    "experiment_nanopore": ("experiments", "experimentnanopore"),
    "experiment_pac_bio": ("experiments", "experimentpacbio"),

    "aligned": ("experiments", "aligned"),
    "aligned_dna_short_read": ("experiments", "aligneddnashortread"),
    "aligned_rna_short_read": ("experiments", "alignedrnashortread"),
    "aligned_nanopore": ("experiments", "alignednanopore"),
    "aligned_pac_bio": ("experiments", "alignedpacbio"),

    "aligned_dna_short_read_set": ("experiments", "aligneddnashortreadset"),
    "aligned_nanopore_set": ("experiments", "alignednanoporeset"),
    "aligned_pac_bio_set": ("experiments", "alignedpacbioset"),

    "called_variants_dna_short_read": ("experiments", "calledvariantsdnashortread"),
    "called_variants_nanopore": ("experiments", "calledvariantsnanopore"),
    "called_variants_pac_bio": ("experiments", "calledvariantspacbio"),
}

MANIFEST_CONTENT_TYPE = "application/json"
