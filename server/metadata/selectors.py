#!/usr/bin/env python3
# metadata/selectors.py

"""Metadata Selectors
"""

from metadata.models import (
    Family, Analyte,
)

def get_analyte(analyte_id: str) -> Family:
    """Retrieve an analyte instance by its ID or return None if not found."""
    try:
        analyte_instance = Analyte.objects.get(analyte_id=analyte_id)
        return analyte_instance
    except Analyte.DoesNotExist:
        return None


def genetic_findings_parser(genetic_findings: dict) -> dict:
    """
    """
    from config.selectors import multi_value_split
    multi_value = [
        "experiment_id",
        "variant_type",
        "gene_of_interest", 
        "condition_inheritance",
        "method_of_discovery"
    ]

    for key, value in genetic_findings.items():
        if value is None:
            continue
        if isinstance(value, str) and "|" in value:
            genetic_findings[key] = value.split("|")
        if key == "pos" and genetic_findings[key] != "NA":
            try:
                genetic_findings["pos"] = float(genetic_findings["pos"])
            except ValueError:
                genetic_findings["pos"] = "NA"
        if (
            key == "allele_balance_or_heteroplasmy_percentage"
            and genetic_findings[key] != "NA"
        ):
            try:
                genetic_findings[key] = int(genetic_findings[key])
            except ValueError:
                genetic_findings[key] = "NA"
        if (
            key == "partial_contribution_explained"
            and type(genetic_findings[key]) == str
        ):
            genetic_findings[key] = [value]
        
        split_findings = multi_value_split(genetic_findings)
        
        for value in multi_value:
            try:
                if value in split_findings and not isinstance(split_findings[value], list):
                    split_findings[value] = [split_findings[value]]
            except Exception as error:
                oops = error
                split_findings[key] = [oops]

    return split_findings


def participant_parser(participant: dict) -> dict:
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
    from config.selectors import multi_value_split
    multi_value = [
        "pmid_id",
        "twin_id",
        "internal_project_id", "prior_testing",
        "phenotype_description",
        "reported_race"
    ]
    if "reported_race" in participant: 
        if participant["reported_race"] == "Unknown" or participant["reported_race"] == "More than one race":
            participant["reported_race"] = ["NA"]
    if "reported_ethnicity" in participant:
        if participant["reported_ethnicity"] == "Unknown":
            participant["reported_ethnicity"] = ["NA"]

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
    split_participant = multi_value_split(participant)

    for key in multi_value:
        try:
            if key in split_participant and not isinstance(split_participant[key], list):
                split_participant[key] = [split_participant[key]]
        except Exception as error:
            oops = error
            split_participant[key] = [oops]

    return split_participant
