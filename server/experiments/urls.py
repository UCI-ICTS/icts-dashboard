#!/usr/bin/env python
# experiments/urls.py

from django.urls import path
from experiments.apis import (
    CreateExperimentRnaShortRead,
    ReadExperimentRnaShortRead,
    UpdateExperimentRnaShortRead,
    DeleteExperimentRnaShortRead,

    CreateAlignedRnaShortRead,
    ReadAlignedRnaShortRead,
    UpdateAlignedRnaShortRead,
    DeleteAlignedRnaShortRead,

    CreateExperimentDnaShortRead,
    ReadExperimentDnaShortRead,
    UpdateExperimentDnaShortRead,
    DeleteExperimentDnaShortRead,

    CreateAlignedDnaShortRead,
    ReadAlignedDnaShortRead,
    UpdateAlignedDnaShortRead,
    DeleteAlignedDnaShortRead,
)

urlpatterns = [
    path("create_experiment_rna_short_read/", CreateExperimentRnaShortRead.as_view()),
    path("read_experiment_rna_short_read/", ReadExperimentRnaShortRead.as_view()),
    path("update_experiment_rna_short_read/", UpdateExperimentRnaShortRead.as_view()),
    path("delete_experiment_rna_short_read/", DeleteExperimentRnaShortRead.as_view()),

    path("create_aligned_rna_short_read/", CreateAlignedRnaShortRead.as_view()),
    path("read_aligned_rna_short_read/", ReadAlignedRnaShortRead.as_view()),
    path("update_aligned_rna_short_read/", UpdateAlignedRnaShortRead.as_view()),
    path("delete_aligned_rna_short_read/", DeleteAlignedRnaShortRead.as_view()),

    path("create_experiment_dna_short_read/", CreateExperimentDnaShortRead.as_view()),
    path("read_experiment_dna_short_read/", ReadExperimentDnaShortRead.as_view()),
    path("update_experiment_dna_short_read/", UpdateExperimentDnaShortRead.as_view()),
    path("delete_experiment_dna_short_read/", DeleteExperimentDnaShortRead.as_view()),

    path("create_aligned_dna_short_read/", CreateAlignedDnaShortRead.as_view()),
    path("read_aligned_dna_short_read/", ReadAlignedDnaShortRead.as_view()),
    path("update_aligned_dna_short_read/", UpdateAlignedDnaShortRead.as_view()),
    path("delete_aligned_dna_short_read/", DeleteAlignedDnaShortRead.as_view()),
]
