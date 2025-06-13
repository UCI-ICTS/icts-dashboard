#!/usr/bin/env python3
"""
Data Converters

This module provides a class to convert tabular data (CSV/TSV) into JSON objects,
and then call an existing API function (create_or_update) to create or update model instances.
If a header column is found that starts with "entity:", its value is used as the table/entity identifier.
An internal mapping (SCHEMA_MAPPING) is available to locate the schema file if needed,
but in this version we assume that the create function handles validation.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
import sys
import csv
import argparse
import json
from config.selectors import bulk_model_retrieve
from metadata.services import create_metadata
from metadata.models import (
    Participant,
    Family,
    Analyte,
    GeneticFindings,
    Phenotype,
    Biobank,
)

from experiments.services import create_aligned, create_experiment
from experiments.models import (
    ExperimentDNAShortRead,
    ExperimentRNAShortRead,
    ExperimentPacBio,
    ExperimentNanopore,
    AlignedNanopore,
    AlignedDNAShortRead,
    AlignedPacBio,
    AlignedRNAShortRead,
)


class TableConverter:
    """
    Class for converting tabular data (CSV/TSV) to JSON objects and then
    calling create for each record.
    """

    @staticmethod
    def convert_to_json(table_file: str) -> tuple[list, str]:
        """
        Converts a CSV/TSV file to a list of JSON objects (dictionaries).

        If a header field starts with "entity:", that field is renamed (removing the "entity:" prefix)
        and its corresponding entity name is extracted (with an optional strip of a trailing "_id").

        Args:
            table_file (str): The path to the CSV/TSV file.

        Returns:
            tuple:
                - list: A list of dictionaries representing rows in the file.
                - str: The extracted entity name (if found), otherwise None.
        """
        data_list = []
        entity = None

        # Determine delimiter based on file extension.
        delimiter = "\t" if table_file.lower().endswith("tsv") else ","
        with open(table_file, "r", encoding="utf-8") as file:
            reader = list(csv.reader(file, delimiter=delimiter))
            if not reader:
                return data_list, entity
            header = reader[0]
            new_header = []
            for col in header:
                if col.startswith("entity:"):
                    col_clean = col[len("entity:") :]
                    # Optionally, remove trailing "_id" if present.
                    if col_clean.endswith("_id"):
                        entity = col_clean[:-3]
                    else:
                        entity = col_clean
                    new_header.append(col_clean)
                else:
                    new_header.append(col)
            for row in reader[1:]:
                data_list.append(dict(zip(new_header, row)))

        return data_list, entity

    def process_table(self, table_file: str, table_name: str = None) -> None:
        """
        Converts the table file into a list of JSON objects and for each record
        calls the create function.

        If table_name is not provided, it is determined from the TSV header (the value of the column starting with "entity:").

        Args:
            table_file (str): Path to the CSV/TSV file.
            table_name (str, optional): The name of the table (model). If not provided,
                the entity extracted from the file header will be used.
        """
        data_list, entity = self.convert_to_json(table_file)
        with open("filename.json", "w") as f:
            json.dump(data_list, f, indent=4)
        print(f"Found {len(data_list)} records in the file.")
        models = {
            "participant": Participant,
            "family": Family,
            "biobank": Biobank,
            "analyte": Analyte,
            "phenotype": Phenotype,
            "genetic_findings": GeneticFindings,
            "experiment_dna_short_read": ExperimentDNAShortRead,
            "experiment_nanopore": ExperimentNanopore,
            "experiment_pac_bio": ExperimentPacBio,
            "experiment_rna_short_read": ExperimentRNAShortRead,
            "aligned_dna_short_read": AlignedDNAShortRead,
            "aligned_nanopore": AlignedNanopore,
            "aligned_pac_bio": AlignedPacBio,
            "aligned_rna_short_read": AlignedRNAShortRead,
        }
        metadata_models = [
            "participant",
            "analyte",
            "family",
            "genetic_findings",
            "phenotype",
            "biobank",
        ]
        experiment_models = [
            "experiment_dna_short_read",
            "experiment_rna_short_read",
            "experiment_nanopore",
            "experiment_pac_bio",
        ]
        alignment_models = [
            "aligned_dna_short_read",
            "aligned_rna_short_read",
            "aligned_nanopore",
            "aligned_pac_bio",
        ]

        if not table_name:
            if entity:
                table_name = entity
                print(f"Determined table name as '{table_name}' from header.")
            else:
                print("No table name provided and none found in header.")
                sys.exit(1)
        # Determine the unique identifier. In this example we assume that the identifier
        # is in a field named "<table_name>_id" (e.g. "participant_id").
        identifier_field = f"{table_name}_id"

        model_instances = bulk_model_retrieve(
            request_data=data_list, model_class=models[table_name], id=identifier_field
        )

        if table_name in metadata_models:
            create = create_metadata
        if table_name in experiment_models:
            create = create_experiment
        if table_name in alignment_models:
            create = create_aligned

        results = []

        for record in data_list:
            identifier = record.get(identifier_field)
            if not identifier:
                print(f"No identifier ({identifier_field}) found in record: {record}")
                continue

            model_instance = model_instances.get(record[identifier_field])
            # if model_instance:
            #     result_entry = {
            #         "identifier": identifier,
            #         "request_status": "NO CHANGE",

            #         "updates": "NA",
            #         "validation_fails": "NA"
            #     }
            #     results.append(result_entry)
            # else:
            response, status = create(
                table_name, identifier, record
            )
            result_entry = {
                "identifier": identifier,
                "request_status": (
                    "NO CHANGE"
                    if response["request_status"] == "CREATED"
                    else response.get("request_status", "UNKNOWN")
                ),
                "validation_fails": response["data"],
            }
            results.append(result_entry)
            #if result_entry['request_status'] == "CREATED":
            #import pdb; pdb.set_trace()
        self.write_results(table_file.split(".")[0], results)

    def write_results(self, table_file: str, results: list):
        """
        Writes the results to a TSV file with identifier, request_status, and updates (if applicable).

        Args:
            table_file (str): The original input file path (used to generate output file name).
            results (list): A list of dictionaries containing 'identifier', 'request_status', and 'updates'.
        """
        output_dir = os.path.join(
            os.path.dirname(table_file), "update_results"
        )  # Construct path
        os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
        table_name = table_file.split("/")[-1]
        output_file = os.path.join(
            output_dir, f"{table_name}_results.tsv"
        )  # Generate full path

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(
                ["identifier", "request_status", "updates", "validation errors"]
            )  # Header
            for result in results:
                writer.writerow(
                    [
                        result["identifier"],
                        result["request_status"],
                        (
                            ", ".join(result["updates"])
                            if result["request_status"] == "UPDATED"
                            else ""
                        ),
                        result["validation_fails"],
                    ]
                )

    @staticmethod
    def usr_args():
        """
        Parse user arguments for the command-line invocation.

        Returns:
            argparse.Namespace: Parsed arguments.
        """
        parser = argparse.ArgumentParser(
            prog="data_converter",
            usage="%(prog)s [options]",
            description="Convert a CSV/TSV file to JSON and submit each record using create_or_update.",
        )
        parser.add_argument(
            "-t", "--table", required=True, help="Path to the table file (CSV or TSV)."
        )
        # Optionally allow an override for the table name.
        parser.add_argument(
            "-n",
            "--name",
            required=False,
            help="The table name (if not determined from header).",
        )

        if len(sys.argv) <= 1:
            parser.print_help()
            sys.exit(1)
        return parser.parse_args()


def main():
    """Main function to run the table conversion and submission process."""
    args = TableConverter.usr_args()
    converter = TableConverter()
    # If the user provided a table name, use it; otherwise let process_table determine it.
    converter.process_table(args.table, table_name=args.name)


if __name__ == "__main__":
    main()
