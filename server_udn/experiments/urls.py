#!/usr/bin/env python
# experiments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from experiments.apis import (
    ExperimentRNAShortReadViewSet,
    AlignedRNAShortReadViewSet,
    ExperimentDNAShortReadViewSet,
    AlignedDNAShortReadViewSet,
    ExperimentPacBioViewSet,
    AlignedPacBioViewSet,
    ExperimentNanoporeViewSet,
    AlignedNanoporeViewSet,
)

router = DefaultRouter()
router.register(r'experiment_rna_short_read', ExperimentRNAShortReadViewSet, basename='experiment_rna_short_read')
router.register(r'aligned_rna_short_read', AlignedRNAShortReadViewSet, basename='aligned_rna_short_read')
router.register(r'experiment_dna_short_read', ExperimentDNAShortReadViewSet, basename='experiment_dna_short_read')
router.register(r'aligned_dna_short_read', AlignedDNAShortReadViewSet, basename='aligned_dna_short_read')
router.register(r'experiment_pac_bio', ExperimentPacBioViewSet, basename='experiment_pac_bio')
router.register(r'aligned_pac_bio', AlignedPacBioViewSet, basename='aligned_pac_bio')
router.register(r'experiment_nanopore', ExperimentNanoporeViewSet, basename='experiment_nanopore')
router.register(r'aligned_nanopore', AlignedNanoporeViewSet, basename='aligned_nanopore')

urlpatterns = [
    path('', include(router.urls)),
]
