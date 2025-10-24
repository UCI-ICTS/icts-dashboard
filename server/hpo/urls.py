#!/usr/bin/env python
# hpo/urls.py

from django.urls import path
from .apis import HPOAutocompleteView, HPOSearchView, HPOExtractPhenotypesView

urlpatterns = [
    path("autocomplete/", HPOAutocompleteView.as_view(), name="hpo-autocomplete"),
    path("search/",       HPOSearchView.as_view(),       name="hpo-search"),
    path("extract_phenotypes/", HPOExtractPhenotypesView.as_view(), name="hpo-extract-phenotypes"),
]
