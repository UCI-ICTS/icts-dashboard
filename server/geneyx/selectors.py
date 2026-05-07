#!/usr/bin/env python3
# geneyx/selectors.py

import requests
from settings import GENEYX_APIDB, GENEYX_CONTENT_TYPE, GENEYX_APIDB, GENEYX_PAGE_SIZE, GENEYX_USER_ID, GENEYX_USER_KEY

"""Geneyx Selectors"""

headers = {
    "Content-Type": GENEYX_CONTENT_TYPE,
    "PageSize": GENEYX_PAGE_SIZE,
    "ApiUserId": GENEYX_USER_ID,
    "ApiUserKey": GENEYX_USER_KEY,
}

def get_all_samples():
    response = requests.post(f"{GENEYX_APIDB}/Samples", headers)
    if "data" in response.json():
        return response.json()["data"]
    else:
        return response.json()["text"]

def get_sample(sample_id):
    data = {"SampleSn": sample_id}
    response = requests.post(f"{GENEYX_APIDB}/Sample", data, headers)
    if "data" in response.json():
        return response.json()["data"]
    else:
        return response.json()["text"]

def get_all_cases():
    response = requests.post(f"{GENEYX_APIDB}/Cases", headers)
    if "data" in response.json():
        return response.json()["data"]
    else:
        return response.json()["text"]

def get_case(case_id):
    data = {"CaseSn": case_id}
    response = requests.post(f"{GENEYX_APIDB}/Case", data, headers)
    if "data" in response.json():
        return response.json()["data"]
    else:
        return response.json()["text"]

def get_case_notes(case_id):
    data = {"CaseSn": case_id}
    response = requests.post(f"{GENEYX_APIDB}/CaseNotes", data, headers)
    if "data" in response.json():
        return response.json()["data"]
    else:
        return response.json()["text"]