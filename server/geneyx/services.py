#!/usr/bin/env python3
# metadata/servces.py

import re
import requests
from settings import GENEYX_APIDB, GENEYX_CONTENT_TYPE, GENEYX_APIDB, GENEYX_PAGE_SIZE, GENEYX_USER_ID, GENEYX_USER_KEY


headers = {
    "Content-Type": GENEYX_CONTENT_TYPE,
    "PageSize": GENEYX_PAGE_SIZE,
    "ApiUserId": GENEYX_USER_ID,
    "ApiUserKey": GENEYX_USER_KEY,
}

class GeneyxOutputSerializer():
    """
    Base serializer that assigns request.user to _history_user
    on create. Requires 'context["request"]'.
    """

    def get_all_samples(self):
        response = requests.post(f"{GENEYX_APIDB}/Samples", headers)
        if "data" in response.json():
            return response.json()["data"]
        else:
            return response.json()["text"]

    def get_sample(self, attr):
        data = {"SampleSn": attr}
        response = requests.post(f"{GENEYX_APIDB}/Sample", data, headers)
        if "data" in response.json():
            return response.json()["data"]
        else:
            return response.json()["text"]

    def get_all_cases(self):
        response = requests.post(f"{GENEYX_APIDB}/Cases", headers)
        if "data" in response.json():
            return response.json()["data"]
        else:
            return response.json()["text"]

    def get_case(self, attr):
        data = {"CaseSn": attr}
        response = requests.post(f"{GENEYX_APIDB}/Case", data, headers)
        if "data" in response.json():
            return response.json()["data"]
        else:
            return response.json()["text"]

    def get_case_notes(self, attr):
        data = {"CaseSn": attr}
        response = requests.post(f"{GENEYX_APIDB}/CaseNotes", data, headers)
        if "data" in response.json():
            return response.json()["data"]
        else:
            return response.json()["text"]