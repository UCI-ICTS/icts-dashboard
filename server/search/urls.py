#!/usr/bin/env python
# # search/urls.py

from django.urls import path

from search.apis import (
    SearchTablesAPI,
    DounlaodTablesAPI,
    GetAllTablesAPI
)

urlpatterns = [
    path("get_all_tables/", GetAllTablesAPI.as_view()),
    path("get_anvil_tables/", DounlaodTablesAPI.as_view()),
    path("<str:model_name>/", SearchTablesAPI.as_view(), name="general_search"),
]
