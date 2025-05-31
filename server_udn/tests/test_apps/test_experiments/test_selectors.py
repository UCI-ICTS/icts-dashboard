#!/usr/bin/env python3
# tests/test_apps/test_experiments/test_selectors.py

import json
from django.test import TestCase
from experiments.models import (
    AlignedDNAShortRead, AlignedPacBio, AlignedNanopore, AlignedRNAShortRead,
    Experiment, ExperimentNanopore, ExperimentPacBio, ExperimentRNAShortRead,
)
from experiments.selectors import (
    parse_short_read_aligned, parse_pac_bio, parse_nanopore_aligned,
    get_experiment, get_experiment_pac_bio, get_experiment_nanopore,
    get_experiment_rna, get_aligned_dna_short_read, get_aligned_pac_bio,
    get_aligned_nanopore, get_aligned_rna
)
from experiments.services import (
    AlignedDNAShortReadSerializer, AlignedNanoporeSerializer,
    ExperimentPacBioSerializer
)

class ExperimentSelectorsTest(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.experiment = Experiment.objects.first()
        self.pac_bio_experiment = ExperimentPacBio.objects.first()
        self.nanopore_experiment = ExperimentNanopore.objects.first()
        self.rna_experiment = ExperimentRNAShortRead.objects.first()

        self.aligned_dna = AlignedDNAShortRead.objects.first()
        self.aligned_pac_bio = AlignedPacBio.objects.first()
        self.aligned_nanopore = AlignedNanopore.objects.first()
        self.aligned_rna = AlignedRNAShortRead.objects.first()

    def test_parse_short_read_aligned(self):
        data = AlignedDNAShortReadSerializer(self.aligned_dna).data
        data['mean_coverage'] = "30"
        self.assertFalse(isinstance(data["mean_coverage"], int))
        parsed = parse_short_read_aligned(data)
        self.assertTrue(isinstance(parsed["mean_coverage"], int))

    def test_parse_pac_bio(self):
        data = ExperimentPacBioSerializer(self.pac_bio_experiment).data
        data["was_barcoded"] = "true"
        self.assertFalse(isinstance(data["was_barcoded"], bool))
        data["was_barcoded"] = "FALSE"
        self.assertFalse(isinstance(data["was_barcoded"], bool))
        parsed = parse_pac_bio(data)
        self.assertTrue(isinstance(parsed["was_barcoded"], bool))

    def test_parse_nanopore_aligned(self):
        data = AlignedNanoporeSerializer(self.aligned_nanopore).data
        data["methylation_called"] = "true"
        self.assertFalse(isinstance(data["methylation_called"], bool))
        data["methylation_called"] = "FALSE"
        self.assertFalse(isinstance(data["methylation_called"], bool))
        parsed = parse_nanopore_aligned(data)
        self.assertTrue(isinstance(parsed["methylation_called"], bool))
        self.assertFalse(parsed["methylation_called"])

    def test_get_experiment(self):
        not_experiment = get_experiment(experiment_id="EXP001")
        experiment = get_experiment(experiment_id="experiment_dna_short_read.UCI_GREGoR_test-001-001-0-D-1_DNA_1")
        self.assertIsNone(not_experiment)
        self.assertIsNotNone(experiment)

    def test_get_experiment_pac_bio(self):
        not_experiment = get_experiment_pac_bio(experiment_pac_bio_id="EXP_PB999")
        experiment = get_experiment_pac_bio(experiment_pac_bio_id=self.pac_bio_experiment.experiment_pac_bio_id)
        self.assertIsNone(not_experiment)
        self.assertIsNotNone(experiment)

    def test_get_experiment_nanopore(self):
        not_experiment = get_experiment_nanopore(experiment_nanopore_id="EXP_NP999")
        experiment = get_experiment_nanopore(experiment_nanopore_id=self.nanopore_experiment.experiment_nanopore_id)
        self.assertIsNone(not_experiment)
        self.assertIsNotNone(experiment)

    def test_get_experiment_rna(self):
        not_experiment = get_experiment_rna(experiment_rna="EXP_RNA999")
        experiment = get_experiment_rna(experiment_rna=self.rna_experiment.experiment_rna_short_read_id)
        self.assertIsNone(not_experiment)
        self.assertIsNotNone(experiment)

    def test_get_aligned_dna_short_read(self):
        not_aligned = get_aligned_dna_short_read(aligned_dna_short_read_id="ALIGNED_DNA999")
        aligned = get_aligned_dna_short_read(aligned_dna_short_read_id=self.aligned_dna.aligned_dna_short_read_id)
        self.assertIsNone(not_aligned)
        self.assertIsNotNone(aligned)

    def test_get_aligned_pac_bio(self):
        not_aligned = get_aligned_pac_bio(aligned_pac_bio_id="ALIGNED_PB999")
        aligned = get_aligned_pac_bio(aligned_pac_bio_id=self.aligned_pac_bio.aligned_pac_bio_id)
        self.assertIsNone(not_aligned)
        self.assertIsNotNone(aligned)

    def test_get_aligned_nanopore(self):
        not_aligned = get_aligned_nanopore(aligned_nanopore_id="ALIGNED_NP999")
        aligned = get_aligned_nanopore(aligned_nanopore_id=self.aligned_nanopore.aligned_nanopore_id)
        self.assertIsNone(not_aligned)
        self.assertIsNotNone(aligned)

    def test_get_aligned_rna(self):
        not_aligned = get_aligned_rna(aligned_rna_short_read_id="ALIGNED_RNA999")
        aligned = get_aligned_rna(aligned_rna_short_read_id=self.aligned_rna.aligned_rna_short_read_id)
        self.assertIsNone(not_aligned)
        self.assertIsNotNone(aligned)
