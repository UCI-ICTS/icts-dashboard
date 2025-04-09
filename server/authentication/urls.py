#!/usr/bin/env python
# authentication/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.apis import (
    DecoratedTokenObtainPairView,
    DecoratedTokenRefreshView,
    DecoratedTokenVerifyView,
    DecoratedTokenBlacklistView,
    UserViewSet,
    PasswordViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r"password", PasswordViewSet, basename="password")


urlpatterns = [
    path("refresh/", DecoratedTokenVerifyView.as_view()),
    path("verify/", DecoratedTokenRefreshView.as_view()),
    path("login/", DecoratedTokenObtainPairView.as_view()),
    path("logout/", DecoratedTokenBlacklistView.as_view()),
    path('', include(router.urls)),
]
