#!/usr/bin/env python
# authentication/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.apis import (
    TokenViewSet,
    UserViewSet,
    PasswordViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r"password", PasswordViewSet, basename="password")
router.register(r"token", TokenViewSet, basename="token")



urlpatterns = [
    path('', include(router.urls)),
]
