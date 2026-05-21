#!/usr/bin/env python
# geneyx/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from geneyx.apis import (
    GetAllVCFSamples,
    GetVCFSample,
    GetAllCases,
    GetCase,
    GetCaseNotes,
)


urlpatterns = [
    path("get_all_vcf_samples/", GetAllVCFSamples.as_view(), name="get_all_vcf_samples"),
    path("get_vcf_sample/", GetVCFSample.as_view(), name="get_vcf_sample"),
    path("get_all_cases/", GetAllCases.as_view(), name="get_all_cases"),
    path("get_case/", GetCase.as_view(), name="get_case"),
    path("get_case_notes/", GetCaseNotes.as_view(), name="get_case_notes"),
]
