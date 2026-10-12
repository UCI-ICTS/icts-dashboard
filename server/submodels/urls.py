#!/usr/bin/env python
# submodels/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from submodels.apis import (
    ReportedRaceViewSet,
    #InternalProjectIdViewSet,
    #PmidIdViewSet,
    #TwinIdViewSet,
    #PrepTargetsDetailViewSet,
)

router = DefaultRouter()
router.register(r'reported_race', ReportedRaceViewSet, basename='reported_race')
#router.register(r'internal_project_id', InternalProjectIdViewSet, basename='internal_project_id')
#router.register(r'pmid_id', PmidIdViewSet, basename='pmid_id')
#router.register(r'twin_id', TwinIdViewSet, basename='twin_id')
#router.register(r'prep_targets_detail', PrepTargetsDetailViewSet, basename='prep_targets_detail')

urlpatterns = [
    path('', include(router.urls)),
]
