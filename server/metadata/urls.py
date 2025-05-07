#!/usr/bin/env python
# metadata/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
    BiobankViewSet,
    ExperimentStageViewSet,
)

router = DefaultRouter()
router.register(r"biobank", BiobankViewSet, basename="biobank")
router.register(
    r"experiment_stage", ExperimentStageViewSet, basename="experiment_stage"
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
    path("create_phenotype/", CreatePhenotypeAPI.as_view()),
    path("read_phenotype/", ReadPhenotypeAPI.as_view()),
    path("update_phenotype/", UpdatePhenotypeAPI.as_view()),
    path("delete_phenotype/", DeletePhenotypeAPI.as_view()),
    path("create_genetic_findings/", CreateGeneticFindingsAPI.as_view()),
    path("read_genetic_findings/", ReadGeneticFindingsAPI.as_view()),
    path("update_genetic_findings/", UpdateGeneticFindingsAPI.as_view()),
    path("delete_genetic_findings/", DeleteGeneticFindingsAPI.as_view()),
    path("", include(router.urls)),
]
