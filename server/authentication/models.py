#!/usr/bin/env python
# authentication/models.py

from django.db import models
from django.contrib.auth.models import User


class GoogleCredential(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()