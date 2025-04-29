#!/usr/bin/env python3
# tests/test_apps/test_experiments/test_services.py

from django.test import TestCase
from experiments.models import ExperimentRNAShortRead
from experiments.services import (
    ExperimentRnaInputSerializer,
    ExperimentRnaOutputSerializer,
    ExperimentSerializer,
    AlignedRnaSerializer,
)
from metadata.models import Analyte, Participant


class ExperimentServiceTest(TestCase):
    fixtures = ["tests/fixtures/test_fixture.json"]

    def setUp(self):
        self.participant = Participant.objects.first()
        analyte_list = Analyte.objects.filter(
            participant_id=self.participant.participant_id
        )
        self.analyte_1 = analyte_list[0]
        self.analyte_2 = analyte_list[1]

    def test_create_experiment(self):
        data = {
            "experiment_id": "EXP001",
            "table_name": "experiment_dna_short_read",
            "id_in_table": "DNA_001",
            "participant_id": self.participant.participant_id,
        }
        serializer = ExperimentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.experiment_id, "EXP001")

    def test_create_experiment_rna(self):
        data = {
            "experiment_rna_short_read_id": "RNA001",
            "analyte_id": self.analyte_1.analyte_id,
            "experiment_sample_id": "SAMPLE001",
            "read_length": 100,
            "sequencing_platform": "Illumina",
            "library_prep_type": ["rRNA depletion"],
            "experiment_type": ["paired-end", "untargeted"],
            "single_or_paired_ends": "paired-end",
            "within_site_batch_name": "RNA 234A",
        }
        serializer = ExperimentRnaInputSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.experiment_rna_short_read_id, "RNA001")

    def test_create_aligned_rna(self):
        experiment = ExperimentRNAShortRead.objects.create(
            experiment_rna_short_read_id="RNA002",
            analyte_id=self.analyte_2,
            experiment_sample_id="SAMPLE_RNA002",
            read_length=150,
            sequencing_platform="Illumina",
        )
        data = {
            "aligned_rna_short_read_id": "ALIGNED_RNA002",
            "experiment_rna_short_read_id": experiment.experiment_rna_short_read_id,
            "aligned_rna_short_read_file": "path/to/aligned_rna.bam",
            "aligned_rna_short_read_index_file": "path/to/aligned_rna.bai",
            "md5sum": "123456abcdef",
            "reference_assembly": "GRCh37",
            "alignment_software": "STARv2.7.10a",
            "gene_annotation": "GENCODEv41",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "gene_annotation_details": "gencode_comprehensive_chr",
        }
        serializer = AlignedRnaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.aligned_rna_short_read_id, "ALIGNED_RNA002")
