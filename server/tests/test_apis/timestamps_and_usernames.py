# #!/usr/bin/env python3
# # tests/test_apis/timestamps_and_usernames.py

from datetime import datetime


def set_username(api_client, username, app, model, ids):
    """
    Verify that a newly created row matches the username that created it
    """
    base_url = f"/api/{app}/{model}/?{ids}"
    response = api_client.get(base_url, format="json")
    responses = []
    for data in response["data"]:
        if response["data"][data]["created_by"] == username:
            responses.append(True)
    return responses


def updated_timestamp(api_client, app, model, ids):
    """
    Verify that a newly created row matches the username that created it
    """
    base_url = f"/api/{app}/{model}/?{ids}"
    response = api_client.get(base_url, format="json")
    responses = []
    for data in response["data"]:
        if response["data"][data]["created_at"] != response["data"][data]["updated_at"]:
            responses.append(True)
    return responses