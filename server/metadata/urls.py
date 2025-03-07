#!/usr/bin/env python
# metadata/urls.py

from django.urls import path
from metadata.apis import (
    CrearteParticipantAPI,
    ReadParticipantAPI,
    UpdateParticipantAPI,
    DeleteParticipantAPI,

    CreateFamilyAPI,
    ReadFamilyAPI,
    UpdateFamilyAPI,
    DeleteFamilyAPI,
)

urlpatterns = [
    path("create_participants/", CrearteParticipantAPI.as_view()),
    path("read_participants/", ReadParticipantAPI.as_view()),
    path("update_participants/", UpdateParticipantAPI.as_view()),
    path("delete_participants/", DeleteParticipantAPI.as_view()),

    path("create_families/", CreateFamilyAPI.as_view()),
    path("read_families/", ReadFamilyAPI.as_view()),
    path("update_families/", UpdateFamilyAPI.as_view()),
    path("delete_families/", DeleteFamilyAPI.as_view()),
]
