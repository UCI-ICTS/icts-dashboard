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
    # path("create_experiments/", CreateOrUpdateExperimentApi.as_view()),
    path(
        "create_short_read_experiment/", CreateOrUpdateExperimentShortReadApi.as_view()
    ),
    path("create_aligned_short_read/", CreateOrUpdateAlignedShortRead.as_view()),
    path("create_pac_bio/", CreateOrUpdateExperimentPacBio.as_view()),
    path("create_aligned_pac_bio/", CreateOrUpdateAlignedPacBio.as_view()),
    path("create_nanopore_experiment/", CreateOrUpdateExperimentNanopore.as_view()),
    path("create_aligned_nanopore/", CreateOrUpdateAlignedNanopore.as_view()),
    path("create_rna_experiment/", CreateOrUpdateExperimentRna.as_view()),
    path("create_aligned_rna/", CreateOrUpdateAlignedRna.as_view()),
]
