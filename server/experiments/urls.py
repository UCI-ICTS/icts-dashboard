#!/usr/bin/env python
# experiments/urls.py

from django.urls import path
from experiments.apis import (
    # CreateOrUpdateExperimentApi,
    CreateOrUpdateExperimentShortReadApi,
    CreateOrUpdateAlignedShortRead,
    CreateOrUpdateAlignedPacBio,
    CreateOrUpdateExperimentPacBio,
    CreateOrUpdateAlignedNanopore,
    CreateOrUpdateExperimentNanopore,
    CreateOrUpdateAlignedRna,
    CreateExperimentRnaShortRead,
    ReadExperimentRnaShortRead,
    UpdateExperimentRnaShortRead,
    DeleteExperimentRnaShortRead
)

urlpatterns = [
    # path("submit_experiment/", CreateOrUpdateExperimentApi.as_view()),
    path("submit_experiment_dna_short_read/", CreateOrUpdateExperimentShortReadApi.as_view()),
    path("submit_aligned_dna_short_read/", CreateOrUpdateAlignedShortRead.as_view()),
    path("submit_pac_bio/", CreateOrUpdateExperimentPacBio.as_view()),
    path("submit_aligned_pac_bio/", CreateOrUpdateAlignedPacBio.as_view()),
    
    path("create_experiment_rna_short_read/", CreateExperimentRnaShortRead.as_view()),
    path("read_experiment_rna_short_read/", ReadExperimentRnaShortRead.as_view()),
    path("update_experiment_rna_short_read/", UpdateExperimentRnaShortRead.as_view()),
    path("delete_experiment_rna_short_read/", DeleteExperimentRnaShortRead.as_view()),

    # path("create_aligned_rna_short_read/", CreateExperimentRnaShortRead.as_view()),
    # path("read_aligned_rna_short_read/", ReadExperimentRnaShortRead.as_view()),
    # path("update_aligned_rna_short_read/", UpdateExperimentRnaShortRead.as_view()),
    # path("delete_aligned_rna_short_read/", DeleteExperimentRnaShortRead.as_view()),

    path("submit_aligned_rna_short_read/", CreateOrUpdateAlignedRna.as_view()),
    path("submit_experiment_nanopore/", CreateOrUpdateExperimentNanopore.as_view()),
    path("submit_aligned_nanopore/", CreateOrUpdateAlignedNanopore.as_view()),
]
