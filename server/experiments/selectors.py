#!/usr/bin/env python3
# experiments/selectors.py

"""Experiments Selectors
"""

from experiments.models import (
    AlignedDNAShortRead,
    AlignedPacBio,
    AlignedNanopore,
    Experiment,
    ExperimentDNAShortRead,
    ExperimentNanopore,
    ExperimentPacBio,
)

from config.selectors import remove_na


def parse_short_read_aligned(short_read_aligned: dict) -> dict:
    """
    Parses and processes the short_read_aligned dictionary to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - short_read_aligned (dict): A dictionary containing short_read data.

    Returns:
    - dict: A dictionary with the processed participant data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.

    """

    if (
        "mean_coverage" in short_read_aligned
        and short_read_aligned["mean_coverage"] != "NA"
    ):
        try:
            short_read_aligned["mean_coverage"] = int(
                short_read_aligned["mean_coverage"]
            )
        except ValueError:
            short_read_aligned["mean_coverage"] = "NA"

    parsed_short_read_aligned = remove_na(datum=short_read_aligned)
    return parsed_short_read_aligned


def parse_short_read(short_read: dict) -> dict:
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


def parse_pac_bio_aligned(pac_bio_aligned: dict) -> dict:
    """
    Parses and processes the parse_pac_bio_aligned dictionary to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - pac_bio_aligned (dict): A dictionary containing pac_bio data.

    Returns:
    - dict: A dictionary with the processed pac_bio data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.

    """

    if (
        "methylation_called" in pac_bio_aligned
        and pac_bio_aligned["methylation_called"] != "NA"
    ):
        if pac_bio_aligned["methylation_called"] == "TRUE":
            try:
                pac_bio_aligned["methylation_called"] = True
            except ValueError:
                pac_bio_aligned["methylation_called"] = "NA"

        if pac_bio_aligned["methylation_called"] == "FALSE":
            try:
                pac_bio_aligned["methylation_called"] = False
            except ValueError:
                pac_bio_aligned["methylation_called"] = "NA"

    parsed_pac_bio_aligned = remove_na(datum=pac_bio_aligned)

    return parsed_pac_bio_aligned


def parse_pac_bio(pac_bio_datum: dict) -> dict:
    """
    Parses and processes the pac_bio to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - pac_bio (dict): A dictionary containing pac_bio data.

    Returns:
    - dict: A dictionary with the processed participant data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.
    """

    if "was_barcoded" in pac_bio_datum and pac_bio_datum["was_barcoded"] != "NA":
        if pac_bio_datum["was_barcoded"] == "TRUE":
            try:
                pac_bio_datum["was_barcoded"] = True
            except ValueError:
                pac_bio_datum["was_barcoded"] = "NA"

        if pac_bio_datum["was_barcoded"] == "FALSE":
            try:
                pac_bio_datum["was_barcoded"] = False
            except ValueError:
                pac_bio_datum["was_barcoded"] = "NA"

    parsed_pac_bio = remove_na(datum=pac_bio_datum)
    return parsed_pac_bio


def parse_nanopore_aligned(nanopore_aligned: dict) -> dict:
    """
    Parses and processes the nanopore_aligned dictionary to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - nanopore_aligned (dict): A dictionary containing nanopore data.

    Returns:
    - dict: A dictionary with the processed nanopore data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.

    """

    if (
        "methylation_called" in nanopore_aligned
        and nanopore_aligned["methylation_called"] != "NA"
    ):
        if nanopore_aligned["methylation_called"] == "TRUE":
            try:
                nanopore_aligned["methylation_called"] = True
            except ValueError:
                nanopore_aligned["methylation_called"] = "NA"

        if nanopore_aligned["methylation_called"] == "FALSE":
            try:
                nanopore_aligned["methylation_called"] = False
            except ValueError:
                nanopore_aligned["methylation_called"] = "NA"

    parsed_pac_bio_aligned = remove_na(datum=nanopore_aligned)

    return parsed_pac_bio_aligned


def parse_nanopore(nanopore: dict) -> dict:
    """
    Parses and processes the nanopore dict to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - pac_bio (dict): A dictionary containing nanopore data.

    Returns:
    - dict: A dictionary with the processed participant data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.
    """

    if "was_barcoded" in nanopore and nanopore["was_barcoded"] != "NA":
        if nanopore["was_barcoded"] == "TRUE":
            try:
                nanopore["was_barcoded"] = True
            except ValueError:
                nanopore["was_barcoded"] = "NA"

        if nanopore["was_barcoded"] == "FALSE":
            try:
                nanopore["was_barcoded"] = False
            except ValueError:
                nanopore["was_barcoded"] = "NA"

    parsed_nanopore = remove_na(datum=nanopore)
    return parsed_nanopore


def get_experiment(experiment_id: str) -> Experiment:
    """Retrieve an experiment instance by its ID or return None if not found."""

    try:
        experiment_instance = Experiment.objects.get(experiment_id=experiment_id)
        return experiment_instance
    except Experiment.DoesNotExist:
        return None


def get_experiment_dna_short_read(
    experiment_dna_short_read_id: str,
) -> ExperimentDNAShortRead:
    """Retrieve an experiment instance by its ID or return None if not found."""

    try:
        experiment_dna_short_read_instance = ExperimentDNAShortRead.objects.get(
            experiment_dna_short_read_id=experiment_dna_short_read_id
        )
        return experiment_dna_short_read_instance
    except ExperimentDNAShortRead.DoesNotExist:
        return None


def get_experiment_pac_bio(experiment_pac_bio_id: str) -> ExperimentPacBio:
    """Retrieve an experiment instance by its ID or return None if not found."""

    try:
        experiment_pac_bio_instance = ExperimentPacBio.objects.get(
            experiment_pac_bio_id=experiment_pac_bio_id
        )
        return experiment_pac_bio_instance
    except ExperimentPacBio.DoesNotExist:
        return None


def get_aligned_dna_short_read(aligned_dna_short_read_id: str) -> AlignedDNAShortRead:
    """Retrieve an aligned AlignedDNAShortRead instance by its ID or return None if not found."""

    try:
        get_aligned_dna_short_read_instance = AlignedDNAShortRead.objects.get(
            aligned_dna_short_read_id=aligned_dna_short_read_id
        )
        return get_aligned_dna_short_read_instance
    except AlignedDNAShortRead.DoesNotExist:
        return None


def get_aligned_pac_bio(aligned_pac_bio_id: str) -> AlignedPacBio:
    """Retrieve an AlignedPacBio instance by its ID or return None if not found."""

    try:
        aligned_pac_bio_instance = AlignedPacBio.objects.get(
            aligned_pac_bio_id=aligned_pac_bio_id
        )
        return aligned_pac_bio_instance
    except AlignedPacBio.DoesNotExist:
        return None


def get_aligned_nanopore(aligned_nanopore_id: str) -> AlignedNanopore:
    """Retrieve an AlignedPacBio instance by its ID or return None if not found."""

    try:
        aligned_nanopore_instance = AlignedNanopore.objects.get(
            aligned_nanopore_id=aligned_nanopore_id
        )
        return aligned_nanopore_instance
    except AlignedNanopore.DoesNotExist:
        return None


def get_experiment_nanopore(experiment_nanopore_id: str) -> ExperimentNanopore:
    """Retrieve an ExperimentNanopore instance by its ID or return None if not found."""

    try:
        experiment_nanopore_instance = ExperimentNanopore.objects.get(
            experiment_nanopore_id=experiment_nanopore_id
        )
        return experiment_nanopore_instance
    except ExperimentNanopore.DoesNotExist:
        return None
