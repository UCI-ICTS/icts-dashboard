#!/usr/bin/env python
# authentication/urls.py

from django.urls import path
from authentication.apis import (
    DecoratedTokenObtainPairView,
    DecoratedTokenRefreshView,
    DecoratedTokenVerifyView,
    DecoratedTokenBlacklistView   
)

urlpatterns = [
    path("refresh/", DecoratedTokenVerifyView.as_view()),
    path("verify/", DecoratedTokenRefreshView.as_view()),
    path("login/", DecoratedTokenObtainPairView.as_view()),
    path("logout/", DecoratedTokenBlacklistView.as_view()),
]
