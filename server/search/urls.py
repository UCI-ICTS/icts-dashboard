# search/urls.py

from django.urls import path
from search.apis import SearchTablesAPI, DounlaodTablesAPI

urlpatterns = [
    path("get_anvil_tables/", DounlaodTablesAPI.as_view()),
    path("<str:model_name>/", SearchTablesAPI.as_view(), name="general_search"),
]
