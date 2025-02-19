#!/usr/bin/env python3
# tests/test_apps/test_experiments/test_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from experiments.models import (
    Aligned,
    Experiment,
    ExperimentRNAShortRead,
    ExperimentPacBio,
    ExperimentDNAShortRead,
    ExperimentNanopore
)
from metadata.models import Analyte, Participant

class ExperimentAPITestCase(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.participant = Participant.objects.first()
        self.analyte_1, self.analyte_2 = Analyte.objects.filter(
            participant_id=self.participant.participant_id
        )

    def test_create_experiment_rna(self):
        url = "/api/experiments/submit_experiment_rna_short_read/"

        data = [{
            "experiment_rna_short_read_id": "RNA001",
            "analyte_id": self.analyte_1.analyte_id,
            "experiment_sample_id": "SAMPLE001",
            "read_length": 100,
            "sequencing_platform": "Illumina",
            "library_prep_type": ["rRNA depletion"],
            "experiment_type": ["paired-end","untargeted"],
            "single_or_paired_ends": "paired-end",
            "within_site_batch_name": "RNA 234A"
        }]
        identifier = data[0]['experiment_rna_short_read_id']
        response = self.client.post(url, data, format='json')
        
        # Verify that the experiment was added to the Experiment table
        self.assertIsNotNone(Experiment.objects.get(
            experiment_id=f"experiment_rna_short_read.{identifier}"
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")

    def test_create_aligned_rna(self):
        experiment_rna_id = ExperimentRNAShortRead.objects.all()[0].pk
        url = "/api/experiments/submit_aligned_rna_short_read/"
        data = [{
            "aligned_rna_short_read_id": f"{experiment_rna_id}-ALIGNED-2",
            "experiment_rna_short_read_id": experiment_rna_id,
            "aligned_rna_short_read_file": "gs://path/to/aligned_rna.bam",
            "aligned_rna_short_read_index_file": "gs://path/to/aligned_rna.bai",
            "md5sum": "abcdef654321",
            "reference_assembly": "GRCh38",
            "gene_annotation": "GENCODEv41",
            "alignment_software": "STARv2.7.10a",
            "gene_annotation_details": "gencode_comprehensive_chr",
            "reference_assembly_uri": "http://ftp.1000genomes.ebi.ac.uk",
        }]
        identifier = data[0]["aligned_rna_short_read_id"]
        response = self.client.post(url, data, format='json')
        self.assertIsNotNone(Aligned.objects.get(aligned_id__contains=identifier))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")
        

    def test_create_experiment_dna(self):
        url = "/api/experiments/submit_experiment_dna_short_read/"
        data = [{
            "experiment_dna_short_read_id": "DNA001",
            "analyte_id": self.analyte_1.analyte_id,
            "experiment_sample_id": "SAMPLE_DNA001",
            "read_length": 150,
            "experiment_type": "genome",
            "sequencing_platform": "Illumina"
        }]
        identifier = data[0]["experiment_dna_short_read_id"]
        response = self.client.post(url, data, format='json')
        
        self.assertIsNotNone(Experiment.objects.get(
            experiment_id=f"experiment_dna_short_read.{identifier}"
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")

    def test_create_aligned_dna(self):
        experiment_dna_short_read_id = ExperimentDNAShortRead.objects.all()[0].pk

        url = "/api/experiments/submit_aligned_dna_short_read/"
        
        data = [{
            "aligned_dna_short_read_id": f"{experiment_dna_short_read_id}-ALIGNED",
            "experiment_dna_short_read_id": experiment_dna_short_read_id,
            "aligned_dna_short_read_file": "gs://path/to/aligned_dna.bam",
            "aligned_dna_short_read_index_file": "gs://path/to/aligned_dna.bai",
            "md5sum": "abcdef123456",
            "reference_assembly": "GRCh38",
            "alignment_software": "BWA"
        }]
        identifier = data[0]["aligned_dna_short_read_id"]
        response = self.client.post(url, data, format='json')

        # Verify that the aligned experiment was added to the Aligned table
        self.assertIsNotNone(Aligned.objects.get(aligned_id__contains=identifier))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")
    
    def test_create_experiment_pac_bio(self):
        url = "/api/experiments/submit_pac_bio/"
        data = [{
            "experiment_pac_bio_id": "PACBIO001",
            "analyte_id": self.analyte_1.analyte_id,
            "experiment_sample_id": "SAMPLE_PB001",
            "seq_library_prep_kit_method": "SMRTbell prep kit 3.0",
            "sequencing_platform": "PacBio Sequel IIe",
            "experiment_type": "genome",
            "was_barcoded": "TRUE",
            "smrtlink_server_version": "13.0.0.207600",
            "instrument_ics_version": "12.0.4.197734"
        }]
        identifier = data[0]["experiment_pac_bio_id"]
        response = self.client.post(url, data, format='json')
        
        # Verify that the experiment was added to the Experiment table
        self.assertIsNotNone(Experiment.objects.get(
            experiment_id=f"experiment_pac_bio.{identifier}"
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")

    def test_create_aligned_pac_bio(self):
        experiment_pac_bio_id = ExperimentPacBio.objects.all()[0].pk
        url = "/api/experiments/submit_aligned_pac_bio/"
        data = [{
            "aligned_pac_bio_id": f"{experiment_pac_bio_id}-ALIGNED-2",
            "experiment_pac_bio_id": experiment_pac_bio_id,
            "aligned_pac_bio_file": "gs://path/to/aligned_pac_bio.bam",
            "aligned_pac_bio_index_file": "gs://path/to/aligned_pac_bio.bai",
            "md5sum": "abcdef987654",
            "reference_assembly": "GRCh38",
            "alignment_software": "PBMM2",
            "methylation_called": False
        }]
        identifier = data[0]["aligned_pac_bio_id"]
        response = self.client.post(url, data, format='json')
        self.assertIsNotNone(Aligned.objects.get(aligned_id__contains=identifier))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")
    
    def test_create_experiment_nanopore(self):
        url = "/api/experiments/submit_experiment_nanopore/"
        data = [{
            "experiment_nanopore_id": "NANOPORE001",
            "analyte_id": self.analyte_1.analyte_id,
            "experiment_sample_id": "SAMPLE_NP001",
            "seq_library_prep_kit_method": "LSK109",
            "sequencing_platform": "Oxford Nanopore PromethION 24",
            "experiment_type": "genome",
            "was_barcoded": "TRUE",
            "barcode_kit": "EXP-NBD104",
            "date_data_generation": "2023-10-10",
            "chemistry_type": "R10.4.1"
        }]
        identifier = data[0]["experiment_nanopore_id"]
        response = self.client.post(url, data, format='json')

        self.assertIsNotNone(Experiment.objects.get(
            experiment_id=f"experiment_nanopore.{identifier}"
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")
    
    def test_create_aligned_nanopore(self):
        experiment_nanopore_id = ExperimentNanopore.objects.all()[0].pk
        url = "/api/experiments/submit_aligned_nanopore/"
        data = [{
            "aligned_nanopore_id": f"{experiment_nanopore_id}-ALIGNED-2",
            "experiment_nanopore_id": experiment_nanopore_id,
            "aligned_nanopore_file": "gs://path/to/aligned_nanopore.bam",
            "aligned_nanopore_index_file": "gs://path/to/aligned_nanopore.bai",
            "md5sum": "abcdef789012",
            "reference_assembly": "GRCh38",
            "alignment_software": "Minimap2",
            "methylation_called": False
        }]
        identifier = data[0]["aligned_nanopore_id"]
        response = self.client.post(url, data, format='json')
        self.assertIsNotNone(Aligned.objects.get(aligned_id__contains=identifier))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "CREATED")

