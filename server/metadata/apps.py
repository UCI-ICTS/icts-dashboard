#!/usr/bin/env python
# metadata/apps.py

from django.apps import AppConfig


class Metadata(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "metadata"
