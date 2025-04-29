#!/usr/bin/env python3
# tests/test_apps/test_experiments/test_models.py

from django.test import TestCase
from experiments.models import (
    Experiment,
    Aligned,
    ExperimentDNAShortRead,
    AlignedDNAShortRead,
    ExperimentRNAShortRead,
    AlignedRNAShortRead,
    ExperimentNanopore,
    AlignedNanopore,
    ExperimentPacBio,
    AlignedPacBio,
)
from metadata.models import Participant, Analyte


class ExperimentModelTest(TestCase):
    fixtures = ["tests/fixtures/test_fixture.json"]

    def setUp(self):
        self.participant = Participant.objects.first()
        # import pdb; pdb.set_trace()
        self.analyte_1, self.analyte_2 = Analyte.objects.filter(
            participant_id=self.participant.participant_id
        )[:2]

    def test_experiment_creation(self):
        experiment = Experiment.objects.create(
            experiment_id="EXP001",
            table_name="experiment_dna_short_read",
            id_in_table="DNA_001",
            participant_id=self.participant,
        )
        self.assertEqual(str(experiment), "experiment_dna_short_read - EXP001")

    def test_aligned_creation(self):
        aligned = Aligned.objects.create(
            table_name="aligned_dna_short_read",
            id_in_table="ALIGNED_001",
            participant_id=self.participant,
            aligned_file="path/to/aligned.bam",
            aligned_index_file="path/to/aligned.bai",
        )
        aligned.save()
        self.assertEqual(aligned.aligned_id, "aligned_dna_short_read.ALIGNED_001")

    def test_experiment_dna_short_read_creation(self):
        identifier = "DNA001"
        experiment = ExperimentDNAShortRead.objects.create(
            experiment_dna_short_read_id=identifier,
            analyte_id=self.analyte_1,
            experiment_sample_id="SAMPLE001",
            read_length=150,
            experiment_type="genome",
        )

        self.assertEqual(
            str(experiment), f"ExperimentDNAShortRead object ({identifier})"
        )

    def test_aligned_dna_short_read_creation(self):
        experiment = ExperimentDNAShortRead.objects.create(
            experiment_dna_short_read_id="DNA002",
            analyte_id=self.analyte_1,
            experiment_sample_id="SAMPLE002",
            read_length=100,
            experiment_type="exome",
        )
        aligned = AlignedDNAShortRead.objects.create(
            aligned_dna_short_read_id="ALIGNED_DNA002",
            experiment_dna_short_read_id=experiment,
            aligned_dna_short_read_file="path/to/aligned_dna.bam",
            aligned_dna_short_read_index_file="path/to/aligned_dna.bai",
            md5sum="abcdef123456",
            reference_assembly="GRCh38",
            alignment_software="BWA",
        )
        self.assertEqual(str(aligned), "ALIGNED_DNA002")

    def test_experiment_rna_short_read_creation(self):
        experiment = ExperimentRNAShortRead.objects.create(
            experiment_rna_short_read_id="RNA001",
            analyte_id=self.analyte_2,
            experiment_sample_id="SAMPLE_RNA001",
            read_length=100,
            sequencing_platform="Illumina",
        )
        self.assertEqual(str(experiment), "RNA001")

    def test_aligned_rna_short_read_creation(self):
        experiment = ExperimentRNAShortRead.objects.create(
            experiment_rna_short_read_id="RNA002",
            analyte_id=self.analyte_2,
            experiment_sample_id="SAMPLE_RNA002",
            read_length=150,
            sequencing_platform="Illumina",
        )
        aligned = AlignedRNAShortRead.objects.create(
            aligned_rna_short_read_id="ALIGNED_RNA002",
            experiment_rna_short_read_id=experiment,
            aligned_rna_short_read_file="path/to/aligned_rna.bam",
            aligned_rna_short_read_index_file="path/to/aligned_rna.bai",
            md5sum="123456abcdef",
            reference_assembly="GRCh37",
        )
        self.assertEqual(str(aligned), "ALIGNED_RNA002")
