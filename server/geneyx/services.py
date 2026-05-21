#!/usr/bin/env python
# geneyx/services.py

import json
import requests
from django.conf import settings


header = {
    "server": settings.GENEYX_APIDB,
    "content-type": settings.GENEYX_CONTENT_TYPE,
    "pageSize": settings.GENEYX_PAGE_SIZE,
    "apiUserId": settings.GENEYX_USER_ID,
    "apiUserKey": settings.GENEYX_USER_KEY,
}

def fetch_vcf_samples() -> dict:
    """
    Fetch and return the list of VCF samples from Geneyx.
    """

    response = requests.post(f"{settings.GENEYX_APIDB}/Samples", data=header)
    return response.json()["Data"]


def fetch_vcf_sample(participant_id) -> dict:
    """
    Fetch and return details of a given VCF sample from Geneyx.
    """
    header["SampleSn"] = participant_id
    response = requests.post(f"{settings.GENEYX_APIDB}/Sample", data=header)
    return response.json()["Data"]


def fetch_cases() -> dict:
    """
    Fetch and return the list of cases from Geneyx.
    """

    response = requests.post(f"{settings.GENEYX_APIDB}/Cases", data=header)
    return response.json()["Data"]


def fetch_case(participant_id) -> dict:
    """
    Fetch and return the details of a given case from Geneyx.
    """
    header["CaseSn"] = participant_id
    response = requests.post(f"{settings.GENEYX_APIDB}/Case", data=header)
    return response.json()["Data"]


def fetch_case_notes(participant_id) -> dict:
    """
    Fetch and return the case notes of a given case from Geneyx.
    """
    header["CaseSn"] = participant_id
    response = requests.post(f"{settings.GENEYX_APIDB}/CaseNotes", data=header)
    return response.json()["Data"]