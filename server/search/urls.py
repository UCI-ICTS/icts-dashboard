#!/usr/bin/env python
# # search/urls.py

from django.urls import path

from search.apis import (
    SearchTablesAPI,
    DownloadTablesAPI,
    AllTablesAPI,
    SummaryAPI,
    FamilyDetail
)

urlpatterns = [
    path("get_all_tables/", AllTablesAPI.as_view(), name="get_all_tables"),
    path("summary/", SummaryAPI.as_view(), name="get_summary_stats"),
    path("family_detail/", FamilyDetail.as_view(), name="get_family_detail"),
    # path("get_anvil_tables/", DownloadTablesAPI.as_view()),
    # path("<str:model_name>/", SearchTablesAPI.as_view(), name="general_search"),
]
