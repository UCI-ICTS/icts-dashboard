#!/usr/bin/env python
# geneyx/services.py

import os
import json
import requests
from django.conf import settings


ga_config = {
    "server": "https://analysis.geneyx.com",
    "apiUserId": settings.GENEYX_USER_ID,
    "apiUserKey": settings.GENEYX_USER_KEY,
    "pageSize": settings.GENEYX_PAGE_SIZE
}


def get_ga_cases():
    """
    Return a list of Geneyx analysis IDs
    """

    url=f"{ga_config['server']}/api/Samples"
    response = requests.post(url, data=ga_config)
    if response.json()['Code'] == 'success':\
        return response.json()['Data']
    else:
        print("\tError with Geneyx Samples API request Samples")
        return None


def get_ga_case(case_id):
    """
    Get case details using the Geneyx case ID
    """

    ga_config["CaseSn"] = case_id  # Append participant ID
    url = f"{ga_config['server']}/api/Case"
    response = requests.post(url, data=ga_config)
    if response.json()['Code'] == 'success':
        return response.json()['Data']
    else:
        print(f"\tError with Geneyx Case API request case for {case_id}")
        return None


def get_ga_case(case_id):
    """
    Get case details using the Geneyx case notes
    """

    ga_config["CaseSn"] = case_id  # Append participant ID
    url = f"{ga_config['server']}/api/CaseNotes"
    response = requests.post(url, data=ga_config)
    if response.json()['Code'] == 'success':
        return response.json()['Data']
    else:
        print(f"\tError with Geneyx CaseNotes API request case for {case_id}")
        return None