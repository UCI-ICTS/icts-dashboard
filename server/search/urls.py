# search/urls.py

from django.urls import path
from search.apis import SearchTablesAPI

urlpatterns = [
    path('search/<str:table>/', SearchTablesAPI.as_view(), name='general_search'),
]
