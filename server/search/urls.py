#!/usr/bin/env python
# # search/urls.py

from django.urls import path

from search.apis import (
    SearchTablesAPI,
    DownloadTablesAPI,
    GetAllTablesAPI,
    GetFamilyTableAPI,
    GetParticipantTableAPI,
    GetPhenotypeTableAPI,
    GetGeneticFindingsTableAPI,
    GetBiobankTableAPI,
    GetExperimentTableAPI,
    GetExperimentDNAShortReadTableAPI,
    GetExperimentRNAShortReadTableAPI,
    GetExperimentPacBioTableAPI,
    GetExperimentNanoporeTableAPI,
    GetAlignedTableAPI,
    GetAlignedDNAShortReadTableAPI,
    GetAlignedRNAShortReadTableAPI,
    GetAlignedPacBioTableAPI,
    GetAlignedNanoporeTableAPI
)

urlpatterns = [
    path("get_all_tables/", GetAllTablesAPI.as_view(), name="get_all_tables"),

    path("get_family_table/", GetFamilyTableAPI.as_view(), name="get_family_table"),
    path("get_participant_table/", GetParticipantTableAPI.as_view(), name="get_participant_table"),
    path("get_phenotype_table/", GetPhenotypeTableAPI.as_view(), name="get_phenotype_table"),
    path("get_genetic_findings_table/", GetGeneticFindingsTableAPI.as_view(), name="get_genetic_findings_table"),
    path("get_biobank_table/", GetBiobankTableAPI.as_view(), name="get_biobank_table"),

    path("get_experiment_table/", GetExperimentTableAPI.as_view(), name="get_experiment_table"),
    path("get_experiment_dna_short_read_table/", GetExperimentDNAShortReadTableAPI.as_view(), name="get_experiment_dna_short_read_table"),
    path("get_experiment_rna_short_read_table/", GetExperimentRNAShortReadTableAPI.as_view(), name="get_experiment_rna_short_read_table"),
    path("get_experiment_pac_bio_table/", GetExperimentPacBioTableAPI.as_view(), name="get_experiment_pac_bio_table"),
    path("get_experiment_nanopore_table/", GetExperimentNanoporeTableAPI.as_view(), name="get_experiment_nanopore_table"),

    path("get_aligned_table/", GetAlignedTableAPI.as_view(), name="get_aligned_table"),
    path("get_aligned_dna_short_read_table/", GetAlignedDNAShortReadTableAPI.as_view(), name="get_aligned_dna_short_read_table"),
    path("get_aligned_rna_short_read_table/", GetAlignedRNAShortReadTableAPI.as_view(), name="get_aligned_rna_short_read_table"),
    path("get_aligned_pac_bio_table/", GetAlignedPacBioTableAPI.as_view(), name="get_aligned_pac_bio_table"),
    path("get_aligned_nanopore_table/", GetAlignedNanoporeTableAPI.as_view(), name="get_aligned_nanopore_table"),
    # path("get_anvil_tables/", DownloadTablesAPI.as_view()),
    # path("<str:model_name>/", SearchTablesAPI.as_view(), name="general_search"),
]
