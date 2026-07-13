#!/usr/bin/env python
# tests/test_apps/test_anvil/test_upload_fixtures.py

from django.apps import apps
from django.test import TestCase


Family = apps.get_model("metadata", "family")
Participant = apps.get_model("metadata", "participant")
Phenotype = apps.get_model("metadata", "phenotype")
Analyte = apps.get_model("metadata", "analyte")
GeneticFindings = apps.get_model("metadata", "geneticfindings")

Experiment = apps.get_model("experiments", "experiment")
Aligned = apps.get_model("experiments", "aligned")

ExperimentDnaShortRead = apps.get_model("experiments", "experimentdnashortread")
ExperimentRnaShortRead = apps.get_model("experiments", "experimentrnashortread")
ExperimentNanopore = apps.get_model("experiments", "experimentnanopore")
ExperimentPacBio = apps.get_model("experiments", "experimentpacbio")

AlignedDnaShortRead = apps.get_model("experiments", "aligneddnashortread")
AlignedRnaShortRead = apps.get_model("experiments", "alignedrnashortread")
AlignedNanopore = apps.get_model("experiments", "alignednanopore")
AlignedPacBio = apps.get_model("experiments", "alignedpacbio")

AlignedDnaShortReadSet = apps.get_model("experiments", "aligneddnashortreadset")
AlignedNanoporeSet = apps.get_model("experiments", "alignednanoporeset")
AlignedPacBioSet = apps.get_model("experiments", "alignedpacbioset")

CalledVariantsDnaShortRead = apps.get_model(
    "experiments",
    "calledvariantsdnashortread",
)
CalledVariantsNanopore = apps.get_model(
    "experiments",
    "calledvariantsnanopore",
)
CalledVariantsPacBio = apps.get_model(
    "experiments",
    "calledvariantspacbio",
)


class AnvilUploadFixtureTests(TestCase):
    fixtures = ["tests/fixtures/test_fixture_valid.json"]

    def test_valid_upload_fixture_has_expected_core_counts(self):
        self.assertEqual(Family.objects.count(), 4)
        self.assertEqual(Participant.objects.count(), 6)
        self.assertEqual(Phenotype.objects.count(), 21)
        self.assertEqual(Analyte.objects.count(), 31)
        self.assertEqual(GeneticFindings.objects.count(), 5)

    def test_valid_upload_fixture_has_expected_generic_experiment_and_alignment_counts(self):
        self.assertEqual(Experiment.objects.count(), 13)
        self.assertEqual(Aligned.objects.count(), 13)

    def test_valid_upload_fixture_has_expected_detailed_experiment_counts(self):
        self.assertEqual(ExperimentDnaShortRead.objects.count(), 6)
        self.assertEqual(ExperimentRnaShortRead.objects.count(), 1)
        self.assertEqual(ExperimentNanopore.objects.count(), 3)
        self.assertEqual(ExperimentPacBio.objects.count(), 3)

    def test_valid_upload_fixture_has_expected_detailed_alignment_counts(self):
        self.assertEqual(AlignedDnaShortRead.objects.count(), 6)
        self.assertEqual(AlignedRnaShortRead.objects.count(), 1)
        self.assertEqual(AlignedNanopore.objects.count(), 3)
        self.assertEqual(AlignedPacBio.objects.count(), 3)

    def test_valid_upload_fixture_has_expected_alignment_set_counts(self):
        self.assertEqual(AlignedDnaShortReadSet.objects.count(), 26)
        self.assertEqual(AlignedNanoporeSet.objects.count(), 7)
        self.assertEqual(AlignedPacBioSet.objects.count(), 16)

    def test_valid_upload_fixture_has_expected_called_variant_counts(self):
        self.assertEqual(CalledVariantsDnaShortRead.objects.count(), 26)
        self.assertEqual(CalledVariantsNanopore.objects.count(), 7)
        self.assertEqual(CalledVariantsPacBio.objects.count(), 16)

    def test_valid_upload_fixture_removed_known_delete_alignment_sets(self):
        self.assertFalse(
            AlignedDnaShortReadSet.objects.filter(
                pk__contains="-delete",
            ).exists()
        )
        self.assertFalse(
            AlignedNanoporeSet.objects.filter(
                pk__contains="-delete",
            ).exists()
        )
        self.assertFalse(
            AlignedPacBioSet.objects.filter(
                pk__contains="-delete",
            ).exists()
        )

    def test_valid_upload_fixture_has_no_duplicate_generated_phenotype_rows(self):
        generated_keys = set()

        for phenotype in Phenotype.objects.all():
            generated_key = (
                phenotype.participant_id_id,
                phenotype.term_id,
                phenotype.presence,
            )

            self.assertNotIn(generated_key, generated_keys)
            generated_keys.add(generated_key)

    def test_valid_upload_fixture_has_no_unknown_phenotype_onset_values(self):
        self.assertFalse(
            Phenotype.objects.filter(onset_age_range="unknown").exists()
        )

    def test_valid_upload_fixture_fixes_invalid_participant_solve_status(self):
        participant = Participant.objects.get(
            pk="GREGoR_test-006-006-0",
        )

        self.assertEqual(participant.solve_status, "Unsolved")