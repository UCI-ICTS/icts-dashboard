#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import GetMetadataAPI, CreateParticipantAPI

urlpatterns = [
    path('get_metadata/', GetMetadataAPI.as_view()),
    path('create_participant/', CreateParticipantAPI.as_view())
]