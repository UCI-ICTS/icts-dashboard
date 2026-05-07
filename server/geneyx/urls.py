#!/usr/bin/env python
# metadata/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from geneyx.apis import GeneyxViewSet

router = DefaultRouter()
router.register(r'geneyx_apis', GeneyxViewSet, basename='geneyx_apis')
urlpatterns = [
    path('', include(router.urls)),
]
