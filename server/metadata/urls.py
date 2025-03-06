#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import (
    CrearteParticipantAPI,
    ReadParticipantAPI,
    UpdateParticipantAPI,
    DeleteParticipantAPI,
    CreateOrUpdateGeneticFindings,
    CreateOrUpdateAnalyte,
    CreateOrUpdateFamilyApi,
    CreateOrUpdatePhenotypeApi,
)

urlpatterns = [
    path("create_participants/", CrearteParticipantAPI.as_view()),
    path("read_participants/", ReadParticipantAPI.as_view()),
    path("update_participants/", UpdateParticipantAPI.as_view()),
    path("delete_participants/", DeleteParticipantAPI.as_view()),

    path("submit_families/", CreateOrUpdateFamilyApi.as_view()),
    path("submit_phenotype/", CreateOrUpdatePhenotypeApi.as_view()),
    path("submit_analyte/", CreateOrUpdateAnalyte.as_view()),
    path("submit_genetic_findings/", CreateOrUpdateGeneticFindings.as_view()),
]
