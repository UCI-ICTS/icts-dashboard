#!/usr/bin/env python
# authentication/firecloud_utils.py

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.cloud import storage
from google.oauth2.credentials import Credentials

from authentication.models import GoogleCredential


def get_google_credentials(user):
    try:
        stored = GoogleCredential.objects.get(user=user)
    except GoogleCredential.DoesNotExist:
        return None

    creds = Credentials(
        token=stored.access_token,
        refresh_token=stored.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )

    if timezone.now() >= stored.expires_at:
        creds.refresh(GoogleAuthRequest())
        stored.access_token = creds.token
        stored.expires_at = timezone.now() + timedelta(seconds=3600)
        stored.save(update_fields=["access_token", "expires_at"])

    return creds


def upload_to_workspace(creds, bucket_name, google_project_id, destination_path, file_obj):
    client = storage.Client(credentials=creds, project=None)
    bucket = client.bucket(bucket_name, user_project=google_project_id)
    blob = bucket.blob(destination_path)
    blob.upload_from_file(file_obj)
    return f"gs://{bucket_name}/{destination_path}"