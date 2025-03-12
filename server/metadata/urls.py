#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import (
    CrearteParticipantAPI,
    ReadParticipantAPI,
    UpdateParticipantAPI,
    DeleteParticipantAPI,

    CreateFamilyAPI,
    ReadFamilyAPI,
    UpdateFamilyAPI,
    DeleteFamilyAPI,

    CreateAnalyteAPI,
    ReadAnalyteAPI,
    UpdateAnalyteAPI,
    DeleteAnalyteAPI,
    
    CreatePhenotypeAPI,
    ReadPhenotypeAPI,
    UpdatePhenotypeAPI,
    DeletePhenotypeAPI,

    CreateGeneticFindingsAPI,
    ReadGeneticFindingsAPI,
    UpdateGeneticFindingsAPI,
    DeleteGeneticFindingsAPI,
)

urlpatterns = [
    path("create_participants/", CrearteParticipantAPI.as_view()),
    path("read_participants/", ReadParticipantAPI.as_view()),
    path("update_participants/", UpdateParticipantAPI.as_view()),
    path("delete_participants/", DeleteParticipantAPI.as_view()),

    path("create_families/", CreateFamilyAPI.as_view()),
    path("read_families/", ReadFamilyAPI.as_view()),
    path("update_families/", UpdateFamilyAPI.as_view()),
    path("delete_families/", DeleteFamilyAPI.as_view()),

    path("create_analytes/", CreateAnalyteAPI.as_view()),
    path("read_analytes/", ReadAnalyteAPI.as_view()),
    path("update_analytes/", UpdateAnalyteAPI.as_view()),
    path("delete_analytes/", DeleteAnalyteAPI.as_view()),

    path("create_phenotypes/", CreatePhenotypeAPI.as_view()),
    path("read_phenotypes/", ReadPhenotypeAPI.as_view()),
    path("update_phenotypes/", UpdatePhenotypeAPI.as_view()),
    path("delete_phenotypes/", DeletePhenotypeAPI.as_view()),
    
    path("create_genetic_findings/", CreateGeneticFindingsAPI.as_view()),
    path("read_genetic_findings/", ReadGeneticFindingsAPI.as_view()),
    path("update_genetic_findings/", UpdateGeneticFindingsAPI.as_view()),
    path("delete_genetic_findings/", DeleteGeneticFindingsAPI.as_view()),
]
