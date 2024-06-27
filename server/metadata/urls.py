#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import (
    GetMetadataAPI,
    CreateParticipantAPI,
    CreateOrUpdateAnalyte,
    CreateOrUpdateFamilyApi,
    CreateOrUpdatePhenotypeApi,
)

urlpatterns = [
    path("get_metadata/", GetMetadataAPI.as_view()),
    path("create_participants/", CreateParticipantAPI.as_view()),
    path("create_families/", CreateOrUpdateFamilyApi.as_view()),
    path("create_phenotype/", CreateOrUpdatePhenotypeApi.as_view()),
    path("create_analyte/", CreateOrUpdateAnalyte.as_view()),
]
