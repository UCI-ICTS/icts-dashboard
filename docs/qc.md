# QC Logic 
## Conceptual flow:

### Biobank (sample)
- May or may not have downstream Analyte, Experiment, Alignment records.
- Must have correct participant_id and metadata (collection date, tube barcode, etc.)

### Analyte
Must match participant_id of its Biobank.
- Should link back to a Biobank if it was derived from a collected sample.

### Experiment
Must match participant_id.
- Must link to a valid Analyte (or valid sample ID derived from Analyte or Biobank)

### Alignment
- Must be traceable to an Experiment, which must link back to a valid Analyte, and ideally to a Biobank.


## **Practical Rule Summary**
| Source → Target | Required?	| Notes |
|-----------------|-------------|-------|
Biobank → Analyte | Optional | Only if sample was sequenced
Analyte → Biobank | Required (if analyte comes from sample) | Must match participant_id
Experiment → Analyte | Required	| Must match participant_id
Alignment → Experiment | Required | Must match participant_id
Analyte, Experiment, Alignment → Biobank | Ideally inferable | Validate consistency, not presence


## Proposed QC Tests
1. For Biobank entries:
    - Validate metadata fields (status, barcode uniqueness, etc.)
    - Log if there are no linked analytes but status is Data delivered or Sequenced (these might be inconsistent)

2. For Analytes:
    - Confirm they link to a Biobank (if derived from real sample)
    - Confirm participant_id match

3. For Experiments:
    - Check that their analyte_id maps to a valid Analyte
    - Confirm participant_id match

4. For Alignments:
    - Check that their experiment_id maps to a valid Experiment
    - Confirm participant_id match

5. Cross-Traceability:
    - For any alignment: can you trace back → experiment → analyte → biobank?
    - For each path, validate that participant is consistent across all linked models
    - Ready to scaffold the QC report generator based on this corrected flow? I can write the starter function.