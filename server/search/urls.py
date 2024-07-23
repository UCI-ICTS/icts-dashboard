# search/urls.py

from django.urls import path
from search.apis import SearchTablesAPI, TestConnection

urlpatterns = [
    path("<str:model_name>/", SearchTablesAPI.as_view(), name="general_search"),
    path("test", TestConnection.as_view(), name="test"),
]
