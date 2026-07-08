"""Tests that upload-level errors are found before export.

Examples:

- missing generic experiment row
- genetic finding references experiment absent from experiment.tsv
- aligned row references absent experiment
- callset references absent alignment set
- invalid solve_status
- invalid phenotype onset term
- duplicate generated phenotype identifier
- expected file URI missing
- deleted/test-only rows included in upload"""