"""
URL configuration for GREGoRDB project. 
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

VERSION = settings.VERSION

schema_view = get_schema_view(
    openapi.Info(
        title="UCI-GREGoR Dashboard database API",
        default_version=VERSION,
        description=(
            "This API documentation describes the ways in which one can access " \
            "the UCI-GREGoR Dashboard database. This database stores metadata "\
            "entries based on the GREGoR data model, provide entry retrieval by " \
            " using the search APIs, and also output AnVIL-ready submissions."
        ),
        terms_of_service="terms_of_service",
        contact=openapi.Contact(email="charles.hadley.king@gmail.com"),
        license=openapi.License(name="MIT", url="https://github.com/UCI-GREGoR/GREGor_dashboard/blob/main/LICENSE"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("api/metadata/", include("metadata.urls")),
    path("api/experiments/", include("experiments.urls")),
    path("api/search/", include("search.urls")),
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path("api/admin/", admin.site.urls),
]
