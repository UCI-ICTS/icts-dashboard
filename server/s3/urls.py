#!/usr/bin/env python
# s3/urls.py

from django.urls import path
from s3.apis import (
    GetManifestAPI,
    GetPresignedView
)


urlpatterns = [
    path("get_manifest/", GetManifestAPI.as_view(), name="get_manifest"),
    path("get_pre_signed_url/", GetPresignedView.as_view(), name="get_pre_signed_url"),
]