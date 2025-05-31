Updates to the test fixture focus primarily on replicating MGRC participant ID nomenclature.
* The following constraints were applied consistently to all participants tested:
  * All probands must have the same consent ID as the family ID, with the role set to '0'.
  * Relatives to probands must have a later consent ID than the proband's and thus the family's ID.
* The following constraints were applied to all analytes tested:
  * All blood DNA analytes and biobank entries feature the '-D-n' suffix for n incrementing from 1 to infinity.
  * All blood RNA analytes and biobank entries feature the '-R-n' suffix for n incrementing from 1 to infinity.
  * All OCD-100 buccal analytes and biobank entries feature the '-SC-n' suffix for n incrementing from 1 to infinty.
  * All OGR-500 saliva analytes and biobank entries feature the '-OG-n' suffix for n incrementing from 1 to infinty.
  * All OGR-675 buccal analytes and biobank entries feature the '-SG-n' suffix for n incrementing from 1 to infinty.
  * All DNA isolate analytes and biobank entries feature the '-X-n' suffix for n incrementing from 1 to infinity.
  * All RNA isolate analytes and biobank entries feature the '-XR-n' suffix for n incrementing from 1 to infinity.
* The following constraints were applied to all experiments tested:
  * All short-read DNA experiments feature the 'UCI-' prefix and the '_DNA_1' suffix after the analyte ID.
  * All short-read RNA experiments feature the 'UCI-' prefix and the '_RNA_1' suffix after the analyte ID.
  * All PacBio experiments feature the 'UCI-' prefix and the '_PB_1' suffix after the analyte ID.
  * All Nanopore experiments feature the 'UCI-' prefix and the '_NANO_1' suffix after the analyte ID.
* The following constraints were applied to all alignments tested:
  * All alignments feature the '-Aligned_1' suffix after the experiment ID.

The test_fixture.json features the following demo families and their respective participants:
* GREGoR_test-001 - family - trio
  * GREGoR_test-001-001-0 - proband
    * 3 aliquots of frozen blood
    * 2 aliquots of PAXgene RNA
    * 1 aliquot of DNA isolate derived from saliva
    * 1 Short-read DNA experiment + alignment
    * 1 PacBio experiment + alignment
    * 1 Nanopore experiment + alignment
    * 1 Short-read RNA experiment + alignment
  * GREGoR_test-002-001-2 - mother
    * 3 aliquots of frozen blood
    * 1 aliquot of PAXgene RNA
    * 1 Short-read DNA experiment + alignment
    * 1 PacBio experiment/alignment
  * GREGoR_test-003-001-1 - father
    * 3 aliquots of frozen blood
    * 1 aliquot of PAXgene RNA
    * 1 Short-read DNA experiment + alignment
    * 1 PacBio experiment + alignment
* GREGoR_test-004 - family - duo
  * GREGoR_test-004-004-0 - proband
    * 3 aliquots of frozen blood
    * 2 aliquots of PAXgene RNA
    * 1 Short-read DNA experiment + alignment
    * 1 PacBio experiment + alignment
    * 1 Nanopore experiment + alignment
    * 1 Short-read RNA experiment + alignment
  * GREGoR_test-005-004-2 - mother
    * 3 aliquots of frozen blood
    * 1 aliquot of PAXgene RNA
    * 1 Short-read DNA experiment + alignment
    * 1 PacBio experiment/alignment
* GREGoR_test-006 - family - proband-only
  * GREGoR_test-006-006-0 - proband
    * 3 aliquots of frozen blood
    * 2 aliquots of PAXgene RNA
    * 2 aliquots of RNA isolate
    * 2 aliquots of OCD-100 buccal swabs
    * 1 aliquot of DNA isolate derived from both buccal swabs combined
    * 1 Short-read DNA experiment + alignment
    * 1 PacBio experiment + alignment
    * 1 Nanopore experiment + alignment
    * 1 Short-read RNA experiment + alignment