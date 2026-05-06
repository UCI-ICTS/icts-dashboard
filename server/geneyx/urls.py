#!/usr/bin/env python
# metadata/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from geneyx.apis import (
    GeneyxGetAllSamplesViewSet,
    GeneyxGetSampleViewSet,
    GeneyxGetAllCasesViewSet,
    GeneyxGetCaseViewSet,
    GeneyxGetCaseNotesViewSet,
)

router = DefaultRouter()
router.register(r'get_samples', GeneyxGetAllSamplesViewSet, basename='get_all_samples')
router.register(r'get_sample', GeneyxGetSampleViewSet, basename='get_sample')
router.register(r'get_cases', GeneyxGetAllCasesViewSet, basename='get_all_cases')
router.register(r'get_case', GeneyxGetCaseViewSet, basename='get_case')
router.register(r'get_case_notes', GeneyxGetCaseNotesViewSet, basename='get_case_notes')
urlpatterns = [
    path('', include(router.urls)),
]
