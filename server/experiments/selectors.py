#!/usr/bin/env python3
# experiments/selectors.py

"""Experiments Selectors
"""

from experiments.models import (
    Experiment,
    ExperimentDNAShortRead,
    ExperimentNanopore,
    ExperimentPacBio,
    ExperimentRNAShortRead,
    AlignedDNAShortRead,
    AlignedDNAShortReadSet,
    CalledVariantsDNAShortRead,
    AlignedPacBio,
    AlignedPacBioSet,
    CalledVariantsPacBio,
    AlignedNanopore,
    AlignedNanoporeSet,
    CalledVariantsNanopore,
    AlignedRNAShortRead,
)

from metadata.models import Analyte, Participant
from config.selectors import multi_value_split


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
        and short_read_aligned["mean_coverage"] != None
    ):
        try:
            short_read_aligned["mean_coverage"] = int(
                    short_read_aligned["mean_coverage"]
            )
        except ValueError:
            short_read_aligned["mean_coverage"] = "NA"

    return short_read_aligned


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

    return short_read


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
        if pac_bio_aligned["methylation_called"] == "TRUE" or \
            pac_bio_aligned["methylation_called"] == "true":
            try:
                pac_bio_aligned["methylation_called"] = True
            except ValueError:
                pac_bio_aligned["methylation_called"] = "NA"

        if pac_bio_aligned["methylation_called"] == "FALSE" or \
            pac_bio_aligned["methylation_called"] == "false":
            try:
                pac_bio_aligned["methylation_called"] = False
            except ValueError:
                pac_bio_aligned["methylation_called"] = "NA"

    return pac_bio_aligned


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

        if pac_bio_datum["was_barcoded"] == "TRUE" \
            or pac_bio_datum["was_barcoded"] == 'true':
            try:
                pac_bio_datum["was_barcoded"] = True
            except ValueError:
                pac_bio_datum["was_barcoded"] = "NA"

        if pac_bio_datum["was_barcoded"] == "FALSE" \
            or pac_bio_datum["was_barcoded"] == 'false':
            try:
                pac_bio_datum["was_barcoded"] = False
            except ValueError:
                pac_bio_datum["was_barcoded"] = "NA"

    return pac_bio_datum


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
        if nanopore_aligned["methylation_called"] == "TRUE" or \
            nanopore_aligned["methylation_called"] == "true":
            try:
                nanopore_aligned["methylation_called"] = True
            except ValueError:
                nanopore_aligned["methylation_called"] = "NA"

        if nanopore_aligned["methylation_called"] == "FALSE" or \
            nanopore_aligned["methylation_called"] == "false":
            try:
                nanopore_aligned["methylation_called"] = False
            except ValueError:
                nanopore_aligned["methylation_called"] = "NA"

    return nanopore_aligned


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
        if nanopore["was_barcoded"] == "TRUE" or nanopore["was_barcoded"] == 'true':
            try:
                nanopore["was_barcoded"] = True
            except ValueError:
                nanopore["was_barcoded"] = "NA"

        if nanopore["was_barcoded"] == "FALSE" or nanopore["was_barcoded"] == 'false':
            try:
                nanopore["was_barcoded"] = False
            except ValueError:
                nanopore["was_barcoded"] = "NA"

    return nanopore


def parse_rna(rna_datum: dict) -> dict:
    """
    Parses and processes the rna record to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - rna_datum (dict): A dictionary containing rna data.

    Returns:
    - dict: A dictionary with the processed participant data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.
    """

    multi_value = ["library_prep_type", "prep_targets_detail", "experiment_type"]
    split_rna_datum = multi_value_split(rna_datum)

    for key, value in split_rna_datum.items():
        if key in multi_value and not isinstance(value, list):
            split_rna_datum[key] = [value]
        elif value is None:
            continue
        elif key == "read_length":
            try:
                split_rna_datum[key] = int(value)
            except ValueError:
                split_rna_datum[key] = "NA"
        elif key in ["RIN", "total_reads"]:
            try:
                split_rna_datum[key] = float(value)
            except ValueError:
                split_rna_datum[key] = "NA"

    return split_rna_datum


def parse_rna_aligned(rna_aligned: dict) -> dict:
    """
    Parses and processes the rna_aligned dictionary to format and clean specific fields.

    The function handles specific fields that may contain delimiters or need conversion to different data types.
    It removes or transforms values based on their content to ensure consistent data handling downstream.

    Parameters:
    - nanopore_aligned (dict): A dictionary containing nanopore data.

    Returns:
    - dict: A dictionary with the processed nanopore data. Fields with 'NA' values are excluded, and lists or numeric
      fields are properly formatted.

    """

    identifier = rna_aligned.get("aligned_rna_short_read_id")
    experiment_rna_short_read_id = rna_aligned.get("experiment_rna_short_read_id")
    try:
        # Fetch the Experiment RNA along with the related Analyte and Participant in a single query
        experiment_rna = ExperimentRNAShortRead.objects.select_related(
            "analyte_id__participant_id"
        ).get(experiment_rna_short_read_id=experiment_rna_short_read_id)
        participant_id = experiment_rna.analyte_id.participant_id.participant_id

    except ExperimentRNAShortRead.DoesNotExist:
        participant_id = "NA"
    except Analyte.DoesNotExist:
        participant_id = "NA"
    except Participant.DoesNotExist:
        participant_id = "NA"

    aligned_data = {
        "aligned_id": "aligned_rna_short_read" + "." + identifier,
        "table_name": "aligned_rna_short_read",
        "id_in_table": identifier,
        "participant_id": participant_id,
        "aligned_file": rna_aligned["aligned_rna_short_read_file"],
        "aligned_index_file": rna_aligned["aligned_rna_short_read_index_file"],
    }

    float_fields = [
        "percent_rRNA",
        "percent_mRNA",
        "percent_mtRNA",
        "percent_Globin",
        "percent_UMI",
        "5prime3prime_bias",
        "percent_GC",
        "percent_chrX_Y"
    ]

    for key, value in rna_aligned.items():
        if value is None:
            continue
        if key in float_fields:
            try:
                rna_aligned[key] = float(rna_aligned[key])
            except ValueError:
                print("oops!")
                rna_aligned[key] = "NA"

    return rna_aligned


def swap_experiment_aligned(text: str) -> str:
    """
    Swap 'aligned' with 'experiment' and vice versa in a given string.

    Args:
        text (str): The input string.

    Returns:
        str: The modified string with swapped words.
    """
    replacements = {
        "aligned": "experiment",
        "experiment": "aligned"
    }

    words = text.split("_")
    modified_words = [replacements.get(word, word) for word in words]
    return "_".join(modified_words)


def get_experiment(experiment_id: str) -> Experiment:
    """Retrieve an experiment instance by its ID or return None if not found."""

    try:
        experiment_instance = Experiment.objects.get(experiment_id=experiment_id)
        return experiment_instance
    except Experiment.DoesNotExist:
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


def get_experiment_nanopore(experiment_nanopore_id: str) -> ExperimentNanopore:
    """Retrieve an ExperimentNanopore instance by its ID or return None if not found."""

    try:
        experiment_nanopore_instance = ExperimentNanopore.objects.get(
            experiment_nanopore_id=experiment_nanopore_id
        )
        return experiment_nanopore_instance
    except ExperimentNanopore.DoesNotExist:
        return None


def get_experiment_rna(experiment_rna: str) -> ExperimentRNAShortRead:
    """Retrieve an ExperimentRNAShortRead instance by its ID or return None if not found."""

    try:
        experiment_rna_instance = ExperimentRNAShortRead.objects.get(
            experiment_rna_short_read_id=experiment_rna
        )
        return experiment_rna_instance
    except ExperimentRNAShortRead.DoesNotExist:
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


def get_aligned_rna(aligned_rna_short_read_id: str) -> AlignedNanopore:
    """Retrieve an AlignedRNAShortRead instance by its ID or return None if not found."""

    try:
        aligned_rna_instance = AlignedRNAShortRead.objects.get(
            aligned_rna_short_read_id=aligned_rna_short_read_id
        )
        return aligned_rna_instance
    except AlignedRNAShortRead.DoesNotExist:
        return None
