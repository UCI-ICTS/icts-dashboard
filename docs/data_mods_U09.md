# Data Modifications for U09

## Download:
- go to https://anvil.terra.bio/ and log in using google.
- Go to `Workspaces` and selected `AnVIL_GREGoR_UCI_U09_GRU`
- Click on `Data` and then download each of the tables:
```shell
        aligned_dna_short_read.tsv
        aligned_nanopore.tsv
        aligned_pac_bio.tsv
        aligned_rna_short_read.tsv
        analyte.tsv
        experiment_dna_short_read.tsv
        experiment_nanopore.tsv
        experiment_pac_bio.tsv
        experiment_rna_short_read.tsv
        family.tsv
        genetic_findings.tsv
        participant.tsv
        phenotype.tsv
```
## Table modification:
### participant.tsv
- A significant number of the `pmid_id` values contained values that were supposed to be in the `internal_project_id` column. No values for `pmid_id` exisit in the UCI tables
- 

## Upload functions
### Upload order:
- Participant
- Family
- Analyte
- Phenotype
- experiment_pac_bio
- experiment_nanopore
- experiment_rna_short_read
- experiment_dna_short_read
- aligned_dna_short_read
- aligned_pac_bio
- aligned_nanopore
- aligned_rna_short_read
- Genetic Findings
