#!/usr/bin/env python3
# metadata/selectors.py

"""Metadata Selectors
"""

from metadata.models import (
    InternalProjectId,
    PmidId,
    Family,
    TwinId
    )

def parse_participant(participant: dict) -> dict:
    """"""
    if "twin_id" in participant and participant["twin_id"] != 'NA':
        try:
            participant["twin_id"] = participant["twin_id"].split("|")
        except ValueError:
            participant["twin_id"] = "NA"

    if "internal_project_id" in participant and participant["internal_project_id"] != 'NA':
        try:
            participant["internal_project_id"] = participant["internal_project_id"].split("|")
        except ValueError:
            participant["internal_project_id"] = "NA"
    
    if "prior_testing" in participant and participant["prior_testing"] != 'NA':
        try:
            participant["prior_testing"] = [participant["prior_testing"]]
        except ValueError:
            participant["prior_testing"] = "NA"
    try:
        participant["age_at_last_observation"] = float(participant["age_at_last_observation"])
    except ValueError:
        participant["age_at_last_observation"] = 0
    
    try:
        participant["age_at_enrollment"] = float(participant["age_at_enrollment"])
    except ValueError:
        participant["age_at_enrollment"] = 0
        
    parsed_participant = {k: v for k, v in participant.items() if v != 'NA'}

    return parsed_participant
