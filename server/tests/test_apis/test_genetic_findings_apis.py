# #!/usr/bin/env python3
# # tests/test_apps/test_metadata/test_apis/test_participant_apis.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

class APITestCaseWithAuth(APITestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

class CreateGeneticFindingsAPITest(APITestCaseWithAuth):
    def test_create_analyte_api(self):
        url = "/api/metadata/create_genetic_findings/"
        part1 = {  # Valid submission
            "genetic_findings_id": "10_73792185_GREGoR_test-001-001-0",
            "participant_id": "GREGoR_test-001-001-0",
            "experiment_id": ["WGS"],
            "variant_type": ["SNV/INDEL"],
            "sv_type": "",
            "variant_reference_assembly": "GRCh38",
            "chrom": "10",
            "chrom_end": "",
            "pos": 73792185,
            "pos_end": "",
            "ref": "G",
            "alt": "A",
            "copy_number": "",
            "ClinGen_allele_ID": "",
            "gene_of_interest": ["ZSWIM8"],
            "transcript": "ENST00000604729.6",
            "hgvsc": "c.1646G>A",
            "hgvsp": "",
            "hgvs": "",
            "zygosity": "Heterozygous",
            "allele_balance_or_heteroplasmy_percentage": "",
            "variant_inheritance": "maternal",
            "linked_variant": "",
            "linked_variant_phase": "",
            "gene_known_for_phenotype": "Candidate",
            "known_condition_name": "",
            "condition_id": "",
            "condition_inheritance": ["Unknown"],
            "GREGoR_variant_classification": "Curation in progress",
            "GREGoR_ClinVar_SCV": "",
            "gene_disease_validity": "Curation in progress",
            "public_database_other": "",
            "public_database_ID_other": "",
            "phenotype_contribution": "",
            "partial_contribution_explained": [],
            "method_of_discovery": ["SR-GS"],
            "notes": "",
            "additional_family_members_with_variant": []
        }
        part2 = {  # Valid submission 2
            "genetic_findings_id": "11_64660832_GREGoR_test-001-003-0",
            "participant_id": "GREGoR_test-001-003-0",
            "experiment_id": ["WGS"],
            "variant_type": ["SNV/INDEL"],
            "sv_type": "",
            "variant_reference_assembly": "GRCh38",
            "chrom": "11",
            "chrom_end": "",
            "pos": 64660832,
            "pos_end": "",
            "ref": "C",
            "alt": "T",
            "copy_number": "",
            "ClinGen_allele_ID": "",
            "gene_of_interest": ["NRXN2"],
            "transcript": "ENST00000265459.11",
            "hgvsc": "c.2108G>A",
            "hgvsp": "",
            "hgvs": "",
            "zygosity": "Heterozygous",
            "allele_balance_or_heteroplasmy_percentage": "",
            "variant_inheritance": "paternal",
            "linked_variant": "",
            "linked_variant_phase": "",
            "gene_known_for_phenotype": "Candidate",
            "known_condition_name": "",
            "condition_id": "",
            "condition_inheritance": ["Unknown"],
            "GREGoR_variant_classification": "Curation in progress",
            "GREGoR_ClinVar_SCV": "",
            "gene_disease_validity": "",
            "public_database_other": "",
            "public_database_ID_other": "",
            "phenotype_contribution": "",
            "partial_contribution_explained": [],
            "method_of_discovery": ["SR-GS"],
            "notes": "",
            "additional_family_members_with_variant": []
        }
        part3 = {  # Invalid submission; missing variant_inheritance
            "genetic_findings_id": "2_6849938_GREGoR_test-001-001-0",
            "participant_id": "GREGoR_test-001-001-0",
            "experiment_id": ["WGS"],
            "variant_type": ["SNV/INDEL"],
            "sv_type": "",
            "variant_reference_assembly": "GRCh38",
            "chrom": "2",
            "chrom_end": "",
            "pos": 6849938,
            "pos_end": "",
            "ref": "C",
            "alt": "T",
            "copy_number": "",
            "ClinGen_allele_ID": "",
            "gene_of_interest": ["CMPK2"],
            "transcript": "ENST00000256722.10",
            "hgvsc": "c.1262G>A",
            "hgvsp": "",
            "hgvs": "",
            "zygosity": "Heterozygous",
            "allele_balance_or_heteroplasmy_percentage": "",
            "variant_inheritance": "",  # changed
            "linked_variant": "2_6865407_GREGoR_test-001-001-0",
            "linked_variant_phase": "in trans",
            "gene_known_for_phenotype": "Candidate",
            "known_condition_name": "",
            "condition_id": "",
            "condition_inheritance": ["Unknown"],
            "GREGoR_variant_classification": "Curation in progress",
            "GREGoR_ClinVar_SCV": "",
            "gene_disease_validity": "Curation in progress",
            "public_database_other": "",
            "public_database_ID_other": "",
            "phenotype_contribution": "",
            "partial_contribution_explained": [],
            "method_of_discovery": ["SR-GS"],
            "notes": "",
            "additional_family_members_with_variant": []
        }
        response_200 = self.client.post(url, [part1], format='json')
        response_207 = self.client.post(url, [part2, part3], format='json')
        response_400 = self.client.post(url, [part3], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "CREATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

class ReadGeneticFindingsAPITest(APITestCaseWithAuth):
    def test_read_analyte_success(self):
        url1 = "/api/metadata/read_genetic_findings/?ids=10_73792184_GREGoR_test-001-001-0,11_64660831_GREGoR_test-001-003-0"
        url2 = "/api/metadata/read_genetic_findings/?ids=10_73792184_GREGoR_test-001-001-0,11_64660831_GREGoR_test-001-003-0,DNE-01"
        url3 = "/api/metadata/read_genetic_findings/?ids=DNE-01,DNE-2"

        response_200 = self.client.get(url1, format='json')
        response_207 = self.client.get(url2, format='json')
        response_400 = self.client.get(url3, format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[1]["request_status"], "SUCCESS")
        self.assertEqual(response_207.data[2]["request_status"], "NOT FOUND")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

class UpdateGeneticFindingsAPITest(APITestCaseWithAuth):
    def test_update_analyte_api(self):
        url = "/api/metadata/update_genetic_findings/"
        part1 = {  # Valid submission
            "genetic_findings_id": "10_73792184_GREGoR_test-001-001-0",
            "participant_id": "GREGoR_test-001-001-0",
            "experiment_id": ["WGS"],
            "variant_type": ["SNV/INDEL"],
            "sv_type": "",
            "variant_reference_assembly": "GRCh38",
            "chrom": "10",
            "chrom_end": "",
            "pos": 73792184,
            "pos_end": "",
            "ref": "C",
            "alt": "T",
            "copy_number": "",
            "ClinGen_allele_ID": "",
            "gene_of_interest": [],  # changed
            "transcript": "ENST00000604729.6",
            "hgvsc": "c.1645C>T",
            "hgvsp": "",
            "hgvs": "",
            "zygosity": "Heterozygous",
            "allele_balance_or_heteroplasmy_percentage": "",
            "variant_inheritance": "maternal",
            "linked_variant": "",
            "linked_variant_phase": "",
            "gene_known_for_phenotype": "Candidate",
            "known_condition_name": "",
            "condition_id": "",
            "condition_inheritance": ["Unknown"],
            "GREGoR_variant_classification": "Curation in progress",
            "GREGoR_ClinVar_SCV": "",
            "gene_disease_validity": "Curation in progress",
            "public_database_other": "",
            "public_database_ID_other": "",
            "phenotype_contribution": "",
            "partial_contribution_explained": [],
            "method_of_discovery": ["SR-GS"],
            "notes": "",
            "additional_family_members_with_variant": []
        }
        part2 = {  # Invalid submission; missing zygosity
            "genetic_findings_id": "11_64660831_GREGoR_test-001-003-0",
            "participant_id": "GREGoR_test-001-003-0",
            "experiment_id": ["WGS"],
            "variant_type": ["SNV/INDEL"],
            "sv_type": "",
            "variant_reference_assembly": "GRCh38",
            "chrom": "11",
            "chrom_end": "",
            "pos": 64660831,
            "pos_end": "",
            "ref": "C",
            "alt": "T",
            "copy_number": "",
            "ClinGen_allele_ID": "",
            "gene_of_interest": [],
            "transcript": "ENST00000265459.11",
            "hgvsc": "c.2107G>A",
            "hgvsp": "",
            "hgvs": "",
            "zygosity": "",  # changed
            "allele_balance_or_heteroplasmy_percentage": "",
            "variant_inheritance": "paternal",
            "linked_variant": "",
            "linked_variant_phase": "",
            "gene_known_for_phenotype": "Candidate",
            "known_condition_name": "",
            "condition_id": "",
            "condition_inheritance": ["Unknown"],
            "GREGoR_variant_classification": "Curation in progress",
            "GREGoR_ClinVar_SCV": "",
            "gene_disease_validity": "",
            "public_database_other": "",
            "public_database_ID_other": "",
            "phenotype_contribution": "",
            "partial_contribution_explained": [],
            "method_of_discovery": ["SR-GS"],
            "notes": "",
            "additional_family_members_with_variant": []
        }
        response_200 = self.client.post(url, [part1], format='json')
        response_207 = self.client.post(url, [part1, part2], format='json')
        response_400 = self.client.post(url, [part2], format='json')
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertEqual(response_207.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(response_207.data[0]["request_status"], "UPDATED")
        self.assertEqual(response_207.data[1]["request_status"], "BAD REQUEST")
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)

class DeleteGeneticFindingsAPITest(APITestCaseWithAuth):
    def test_delete_analyte(self):
        url = "/api/metadata/delete_genetic_findings/?ids=2_6849938_GREGoR_test-001-001-0"
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["request_status"], "DELETED")