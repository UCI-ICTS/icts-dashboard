#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import (
    CreateOrUpdateGeneticFindings,
    CrearteOrUpdateParticipantAPI,
    CreateOrUpdateAnalyte,
    CreateOrUpdateFamilyApi,
    CreateOrUpdatePhenotypeApi,
    GetAllTablesAPI,
    
)

urlpatterns = [
    path("submit_participants/", CrearteOrUpdateParticipantAPI.as_view()),
    path("submit_families/", CreateOrUpdateFamilyApi.as_view()),
    path("submit_phenotype/", CreateOrUpdatePhenotypeApi.as_view()),
    path("submit_analyte/", CreateOrUpdateAnalyte.as_view()),
    path("submit_genetic_findings/", CreateOrUpdateGeneticFindings.as_view()),
    path("get_all_tables/", GetAllTablesAPI.as_view())
]
