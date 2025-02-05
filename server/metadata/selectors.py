#!/usr/bin/env python3
# metadata/selectors.py

"""Metadata Selectors
"""

from metadata.models import Family, Phenotype, Analyte, Participant, GeneticFindings

def get_analyte(analyte_id: str) -> Family:
    """Retrieve an analyte instance by its ID or return None if not found."""
    try:
        analyte_instance = Analyte.objects.get(analyte_id=analyte_id)
        return analyte_instance
    except Analyte.DoesNotExist:
        return None


def get_genetic_findings(genetic_findings_id: str) -> GeneticFindings:
    """Retrieve a GeneticFindings instance by its ID or return None if not found."""
    try:
        get_genetic_findings_instance = GeneticFindings.objects.get(
            genetic_findings_id=genetic_findings_id
        )
        return get_genetic_findings_instance
    except GeneticFindings.DoesNotExist:
        return None


def get_phenotype(phenotype_id: str) -> Family:
    """Retrieve a phenotype instance by its ID or return None if not found."""
    try:
        phenotype_instance = Phenotype.objects.get(phenotype_id=phenotype_id)
        return phenotype_instance
    except Phenotype.DoesNotExist:
        return None


def get_family(family_id: str) -> Family:
    """
    Retrieve a family instance by its ID or return None if not found.

    Args:
        family_id (str): Family object identifier

    Returns:
        Family: The family instance if found, otherwise None.
    """
    try:
        family_instance = Family.objects.get(family_id=family_id)
        return family_instance
    except Family.DoesNotExist:
        return None


def get_participant(participant_id: str) -> Participant:
    """
    Retrieve a participant instance by its ID or return None if not found.

    Args:
        participant_id (str): Participant object identifier

    Returns:
        Participant: The participant instance if found, otherwise None.
    """
    try:
        participant_instance = Participant.objects.get(
            participant_id=participant_id
        )
        return participant_instance
    except Participant.DoesNotExist:
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

        for key in multi_value:
            try:
                if not isinstance(split_findings[key], list):
                    split_findings[key] = [split_findings[key]]
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
            if not isinstance(split_participant[key], list):
                split_participant[key] = [split_participant[key]]
        except Exception as error:
            oops = error
            split_participant[key] = [oops]

    return split_participant
