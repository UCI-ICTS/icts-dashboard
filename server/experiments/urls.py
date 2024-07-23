#!/usr/bin/env python
# experiments/urls.py

from django.urls import path
from experiments.apis import (
    # CreateOrUpdateExperimentApi,
    CreateOrUpdateExperimentShortReadApi,
    CreateOrUpdateAlignedShortRead,
    CreateOrUpdateAlignedPacBio,
    CreateOrUpdateExperimentPacBio,
)

urlpatterns = [
    # path("create_experiments/", CreateOrUpdateExperimentApi.as_view()),
    path(
        "create_short_read_experiment/", CreateOrUpdateExperimentShortReadApi.as_view()
    ),
    path("create_aligned_short_read/", CreateOrUpdateAlignedShortRead.as_view()),
    path("create_aligned_pac_bio", CreateOrUpdateAlignedPacBio.as_view()),
    path("create_pac_bio_experiment", CreateOrUpdateExperimentPacBio.as_view()),
]
