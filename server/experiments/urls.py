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

    CreateExperimentPacBio,
    ReadExperimentPacBio,
    UpdateExperimentPacBio,
    DeleteExperimentPacBio,

    CreateAlignedPacBio,
    ReadAlignedPacBio,
    UpdateAlignedPacBio,
    DeleteAlignedPacBio,

    CreateExperimentNanopore,
    ReadExperimentNanopore,
    UpdateExperimentNanopore,
    DeleteExperimentNanopore,

    CreateAlignedNanopore,
    ReadAlignedNanopore,
    UpdateAlignedNanopore,
    DeleteAlignedNanopore,
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

    path("create_experiment_pac_bio/", CreateExperimentPacBio.as_view()),
    path("read_experiment_pac_bio/", ReadExperimentPacBio.as_view()),
    path("update_experiment_pac_bio/", UpdateExperimentPacBio.as_view()),
    path("delete_experiment_pac_bio/", DeleteExperimentPacBio.as_view()),

    path("create_aligned_pac_bio/", CreateAlignedPacBio.as_view()),
    path("read_aligned_pac_bio/", ReadAlignedPacBio.as_view()),
    path("update_aligned_pac_bio/", UpdateAlignedPacBio.as_view()),
    path("delete_aligned_pac_bio/", DeleteAlignedPacBio.as_view()),

    path("create_experiment_nanopore/", CreateExperimentNanopore.as_view()),
    path("read_experiment_nanopore/", ReadExperimentNanopore.as_view()),
    path("update_experiment_nanopore/", UpdateExperimentNanopore.as_view()),
    path("delete_experiment_nanopore/", DeleteExperimentNanopore.as_view()),

    path("create_aligned_nanopore/", CreateAlignedNanopore.as_view()),
    path("read_aligned_nanopore/", ReadAlignedNanopore.as_view()),
    path("update_aligned_nanopore/", UpdateAlignedNanopore.as_view()),
    path("delete_aligned_nanopore/", DeleteAlignedNanopore.as_view()),
]
