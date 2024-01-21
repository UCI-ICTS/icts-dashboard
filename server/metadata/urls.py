# metadata/urls.py

from django.urls import path
from metadata.apis import GetMetadataAPI, SubmitMetadataAPI

urlpatterns = [
    path('get/', GetMetadataAPI.as_view()),
    path('post/', SubmitMetadataAPI.as_view())
]