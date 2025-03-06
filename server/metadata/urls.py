#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import (
    CrearteParticipantAPI,
    ReadParticipantAPI,
    UpdateParticipantAPI,
    DeleteParticipantAPI,

    CreateOrUpdateFamilyAPI,
    ReadFamilyAPI,
    DeleteFamilyAPI,

    CreateOrUpdateGeneticFindingsAPI,
    ReadGeneticFindingsAPI,
    DeleteGeneticFindingsAPI,

    CreateOrUpdateAnalyteAPI,
    ReadAnalyteAPI,
    DeleteAnalyteAPI,

    CreateOrUpdatePhenotypeAPI,
    ReadPhenotypeAPI,
    DeletePhenotypeAPI
)

urlpatterns = [
    path("create_participants/", CrearteParticipantAPI.as_view()),
    path("read_participants/", ReadParticipantAPI.as_view()),
    path("update_participants/", UpdateParticipantAPI.as_view()),
    path("delete_participants/", DeleteParticipantAPI.as_view()),

    path("submit_families/", CreateOrUpdateFamilyAPI.as_view()),
    path("read_families/", ReadFamilyAPI.as_view()),
    path("delete_families/", DeleteFamilyAPI.as_view()),

    path("submit_genetic_findings/", CreateOrUpdateGeneticFindingsAPI.as_view()),
    path("read_genetic_findings/", ReadGeneticFindingsAPI.as_view()),
    path("delete_genetic_findings/", DeleteGeneticFindingsAPI.as_view()),

    path("submit_analytes/", CreateOrUpdateAnalyteAPI.as_view()),
    path("read_analytes/", ReadAnalyteAPI.as_view()),
    path("delete_analytes/", DeleteAnalyteAPI.as_view()),

    path("submit_phenotypes/", CreateOrUpdatePhenotypeAPI.as_view()),
    path("read_phenotypes/", ReadPhenotypeAPI.as_view()),
    path("delete_phenotypes/", DeletePhenotypeAPI.as_view())
]
