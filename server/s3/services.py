#!/usr/bin/env python
# s3/services.py

import os
import json
import boto3
from django.conf import settings

def get_s3_client():
    """
    Return an S3 client using predefined credentials.

    Credentials should be in the `.secrets` file and loaded via Django 
    """

    session = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRETE_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME)
    
    return session.client("s3")


def fetch_manifest(bucket: str, key: str = "bucket-manifest.json") -> dict:
    """
    Fetch and return the manifest JSON from S3.
    """
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read().decode("utf-8"))


def fetch_file_bytes(bucket: str, key: str) -> bytes:
    """
    Fetch and return a file's raw bytes from S3.
    """
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()


def presign_view_url(bucket: str, key: str, expires_seconds: int = 300) -> str:
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_seconds,
    )