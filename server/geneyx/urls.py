#!/usr/bin/env python
# metadata/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from geneyx.apis import GeneyxViewSet

router = DefaultRouter()
router.register(r'get_all_samples', GeneyxViewSet, basename='get_all_samples')
router.register(r'get_sample', GeneyxViewSet, basename='get_sample')
router.register(r'get_all_cases', GeneyxViewSet, basename='get_all_cases')
router.register(r'get_case', GeneyxViewSet, basename='get_case')
router.register(r'get_case_notes', GeneyxViewSet, basename='get_case_notes')
urlpatterns = [
    path('', include(router.urls)),
]
