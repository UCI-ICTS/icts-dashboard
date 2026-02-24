#!/usr/bin/env python
# geneyx/urls.py

from django.urls import path
from geneyx.apis import (
    GetCases,
    GetCase,
    GetCaseNotes,
)


urlpatterns = [
    path("get_cases/", GetCases.as_view(), name="get_cases"),
    path("get_case/", GetCase.as_view(), name="get_case"),
    path("get_case_notes/", GetCaseNotes.as_view(), name="get_case_notes"),
]