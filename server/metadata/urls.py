#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import GetMetadataAPI, CreateParticipantAPI, CreateFamilyApi

urlpatterns = [
    path('get_metadata/', GetMetadataAPI.as_view()),
    path('create_participants/', CreateParticipantAPI.as_view()),
    path('create_families/', CreateFamilyApi.as_view()),
]