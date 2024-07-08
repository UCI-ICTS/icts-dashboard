#!/usr/bin/env python3
# metadata/selectors.py

"""Metadata Selectors
"""

from metadata.models import Family, Phenotype, Analyte, Participant
from config.selectors import remove_na

def get_analyte(analyte_id: str) -> Family:
    """Retrieve an analyte instance by its ID or return None if not found."""
    try:
        analyte_instance = Analyte.objects.get(analyte_id=analyte_id)
        return analyte_instance
    except Analyte.DoesNotExist:
        return None

def get_phenotype(phenotype_id: str) -> Family:
    """Retrieve a phenotype instance by its ID or return None if not found."""
    try:
        phenotype_instance = Phenotype.objects.get(phenotype_id=phenotype_id)
        return phenotype_instance
    except Phenotype.DoesNotExist:
        return None


def get_family(family_id: str) -> Family:
    """Retrieve a family instance by its ID or return None if not found."""
    try:
        family_instance = Family.objects.get(family_id=family_id)
        return family_instance
    except Family.DoesNotExist:
        return None
    
def get_participant(participant_id: str) -> Participant:
    """Retrieve a family instance by its ID or return None if not found."""
    try:
        participant_instance = Participant.objects.get(participant_id=participant_id)
        return participant_instance
    except Participant.DoesNotExist:
        return None


def parse_participant(participant: dict) -> dict:
    """
    Parses and processes the participant dictionary to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - participant (dict): A dictionary containing participant data. Expected keys include 'twin_id', 'internal_project_id',
      'prior_testing', 'age_at_last_observation', and 'age_at_enrollment'.

    Returns:
    - dict: A dictionary with the processed participant data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.

    Notes:
    - 'twin_id' and 'internal_project_id': Splits the string by '|' into a list if not 'NA'.
    - 'prior_testing': Converts the string to a list containing the original string if not 'NA'.
    - 'age_at_last_observation' and 'age_at_enrollment': Converts the string to a float. Sets to 0 if conversion fails.
    """

    if "twin_id" in participant and participant["twin_id"] != "NA":
        try:
            participant["twin_id"] = participant["twin_id"].split("|")
        except ValueError:
            participant["twin_id"] = "NA"

    if (
        "internal_project_id" in participant
        and participant["internal_project_id"] != "NA"
    ):
        try:
            participant["internal_project_id"] = participant[
                "internal_project_id"
            ].split("|")
        except ValueError:
            participant["internal_project_id"] = "NA"

    if "prior_testing" in participant and participant["prior_testing"] != "NA":
        try:
            participant["prior_testing"] = [participant["prior_testing"]]
        except ValueError:
            participant["prior_testing"] = "NA"
    try:
        participant["age_at_last_observation"] = float(
            participant["age_at_last_observation"]
        )
    except ValueError:
        participant["age_at_last_observation"] = 0

    try:
        participant["age_at_enrollment"] = float(participant["age_at_enrollment"])
    except ValueError:
        participant["age_at_enrollment"] = 0

    parsed_participant = remove_na(datum=participant)

    return parsed_participant
