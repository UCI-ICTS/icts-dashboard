#!/usr/bin/env python3
# experiments/selectors.py

"""Experiments Selectors
"""

from experiments.models import Experiment, ExperimentDNAShortRead
from config.selectors import remove_na

def parse_short_read(short_read: dict) -> dict:
    #TODO: document
    """
    Parses and processes the short_read dictionary to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - short_read (dict): A dictionary containing short_read data.

    Returns:
    - dict: A dictionary with the processed participant data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.

    """
    if "read_length" in short_read and short_read["read_length"] != "NA":
        try:
            short_read["read_length"] = int(short_read["read_length"])
        except ValueError:
            short_read["read_length"] = "NA"
    
    if "target_insert_size" in short_read and short_read["target_insert_size"] != "NA":
        try:
            short_read["target_insert_size"] = int(short_read["read_length"])
        except ValueError:
            short_read["target_insert_size"] = "NA"



    parsed_short_read = remove_na(datum=short_read)
    return parsed_short_read

def get_experiment(experiment_id: str) -> Experiment:
    """Retrieve an experiment instance by its ID or return None if not found."""
    try:
        experiment_instance = Experiment.objects.get(experiment_id=experiment_id)
        return experiment_instance
    except Experiment.DoesNotExist:
        return None
    

def get_experiment_dna_short_read(experiment_dna_short_read_id: str) -> ExperimentDNAShortRead:
    """Retrieve an experiment instance by its ID or return None if not found."""
    try:
        experiment_dna_short_read_instance = ExperimentDNAShortRead.objects.get(experiment_dna_short_read_id=experiment_dna_short_read_id)
        return experiment_dna_short_read_instance
    except ExperimentDNAShortRead.DoesNotExist:
        return None
