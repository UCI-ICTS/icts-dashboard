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
    CreateOrUpdateExperimentRna,
)

urlpatterns = [
    # path("submit_experiment/", CreateOrUpdateExperimentApi.as_view()),
    path("submit_experiment_dna_short_read/", CreateOrUpdateExperimentShortReadApi.as_view()),
    path("submit_experiment_rna_short_read/", CreateOrUpdateExperimentRna.as_view()),
    path("submit_pac_bio/", CreateOrUpdateExperimentPacBio.as_view()),
    path("submit_nanopore/", CreateOrUpdateExperimentNanopore.as_view()),
    path("submit_aligned_dna_short_read/", CreateOrUpdateAlignedShortRead.as_view()),
    path("create_aligned_pac_bio/", CreateOrUpdateAlignedPacBio.as_view()),
    path("create_aligned_nanopore/", CreateOrUpdateAlignedNanopore.as_view()),
    path("submit_aligned_rna_short_read/", CreateOrUpdateAlignedRna.as_view()),
]
