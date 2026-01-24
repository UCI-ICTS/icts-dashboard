#!/usr/bin/env python
# hpo/urls.py

from django.urls import path
from .apis import HPOSetupArtifacts, HPOAutocompleteView, HPOSearchView, HPOExtractPhenotypesView, HPOLookupIDView

urlpatterns = [
    path("setup_artifacts/", HPOSetupArtifacts.as_view(), name="hpo-setup-artifacts"),
    path("id_lookup/", HPOLookupIDView.as_view(), name="hpo-id-lookup"),
    path("autocomplete/", HPOAutocompleteView.as_view(), name="hpo-autocomplete"),
    path("search/", HPOSearchView.as_view(), name="hpo-search"),
    path("extract_phenotypes/", HPOExtractPhenotypesView.as_view(), name="hpo-extract-phenotypes"),
]
