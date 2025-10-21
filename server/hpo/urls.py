#!/usr/bin/env python
# hpo/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hpo.apis import GetHPOs

urlpatterns = [
    path("get_hpos/", GetHPOs.as_view()),
]