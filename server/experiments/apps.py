#!/usr/bin/env python
# experiments/admin.py

from django.apps import AppConfig


class Experiment(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "experiments"