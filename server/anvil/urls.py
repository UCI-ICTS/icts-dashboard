#!/usr/bin/env python
# anvil/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from anvil.apis import AnvilUploadViewSet

router = DefaultRouter()
router.register(r"uploads", AnvilUploadViewSet, basename="upload")

urlpatterns = [
    path('', include(router.urls)),
]
