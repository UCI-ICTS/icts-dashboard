#!/usr/bin/env python
# # search/urls.py

from django.urls import path

from search.apis import (
    SearchTablesAPI,
    DownloadTablesAPI,
    GetAllTablesAPI,
)

urlpatterns = [
    path("get_all_tables/", GetAllTablesAPI.as_view(), name="get_all_tables"),
    # path("get_anvil_tables/", DownloadTablesAPI.as_view()),
    # path("<str:model_name>/", SearchTablesAPI.as_view(), name="general_search"),
]
