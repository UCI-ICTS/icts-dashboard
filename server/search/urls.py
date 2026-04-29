#!/usr/bin/env python
# # search/urls.py

from django.urls import path

from search.apis import (
    SearchTablesAPI,
    DownloadTablesAPI,
    AllTablesZipAPI,
    SummaryAPI,
    FamilyDetail,
    CaseQueue,
)

urlpatterns = [
    path("download_all_tables/", AllTablesZipAPI.as_view(), name="download_all_tables_zip"),
    path("summary/", SummaryAPI.as_view(), name="get_summary_stats"),
    path("family_detail/", FamilyDetail.as_view(), name="get_family_detail"),
    path("case_queue/", CaseQueue.as_view(), name="get_case_queue")
    # path("<str:model_name>/", SearchTablesAPI.as_view(), name="general_search"),
]
