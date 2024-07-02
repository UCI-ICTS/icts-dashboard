#!/usr/bin/env python
# experiments/urls.py

from django.urls import path
from experiments.apis import (
    CreateOrUpdateExperimentApi,
    CreateOrUpdateExperimentShortReadApi
)

urlpatterns = [
    path("create_experiments/", CreateOrUpdateExperimentApi.as_view()),
    path("create_short_read_experiment/", CreateOrUpdateExperimentShortReadApi.as_view()),
]