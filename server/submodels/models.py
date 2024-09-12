#!/usr/bin/env python
# submodels/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class ReportedRace(models.Model):
    name = models.CharField(
        primary_key=True,
        max_length=100,
        unique=True
    )
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class InternalProjectId(models.Model):
    internal_project_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="An identifier used by GREGoR research centers to identify "
        "a set of participants for their internal tracking",
    )

    def __str__(self):
        return self.internal_project_id


class PmidId(models.Model):
    pmid_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Publication which included participant; Used for "
        "publications which include participant known prior to or after"
        " inclusion in GREGoR",
    )

    def __str__(self):
        return str(self.pmid_id)