#!/usr/bin/env python
# metadata/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metadata.apis import (

    BiobankViewSet,
    ParticipantViewSet,
    FamilyViewSet,
    AnalyteViewSet,
    PhenotypeViewSet,
    GeneticFindingsViewSet,
)

router = DefaultRouter()
router.register(r'participant', ParticipantViewSet, basename='participant')
router.register(r'family', FamilyViewSet, basename='family')
router.register(r'analyte', AnalyteViewSet, basename='analyte')
router.register(r'phenotype', PhenotypeViewSet, basename='phenotype')
router.register(r'genetic_findings', GeneticFindingsViewSet, basename='genetic_findings')
router.register(r'biobank', BiobankViewSet, basename='biobank')

urlpatterns = [
    path('', include(router.urls)),
]
