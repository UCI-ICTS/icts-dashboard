#!/usr/bin/env python
# hpo/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hpo.apis import HPOAutocompleteView, HPOSearchView, HPOExtractPhenotypesView, HPOLookupIDView, PhenotypeCohortViewSet

router = DefaultRouter()
router.register(r"cohorts", PhenotypeCohortViewSet, basename="hpo")

urlpatterns = [
    path("id_lookup/", HPOLookupIDView.as_view(), name="hpo-id-lookup"),
    path("autocomplete/", HPOAutocompleteView.as_view(), name="hpo-autocomplete"),
    path("search/",       HPOSearchView.as_view(),       name="hpo-search"),
    path("extract_phenotypes/", HPOExtractPhenotypesView.as_view(), name="hpo-extract-phenotypes"),
    path('', include(router.urls)),
]
