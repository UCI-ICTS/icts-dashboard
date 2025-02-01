#!/usr/bin/env python3
# config/services.py

import csv
import os
from io import StringIO, BytesIO
import zipfile
import jsonref
import jsonschema
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from requests.models import PreparedRequest
from django.conf import settings

from metadata.models import (
    Participant,
    Family,
    Analyte,
    GeneticFindings,
    Phenotype
)
from metadata.services import (
    AnalyteSerializer,
    GeneticFindingsSerializer,
    ParticipantInputSerializer,
    ParticipantOutputSerializer,
    FamilySerializer,
    PhenotypeSerializer,
    get_or_create_sub_models,
)

"""DB Level Services

    This module contains service functions that apply to the entire Database.
    It includes utility functions for handling response status determination,
    API data conversion, and constructing standardized response objects.
"""

SCHEMA_VERSION = settings.SCHEMA_VERSION

class TableValidator:
    """
    The Table Validator class is used to validate JSON objects against 
    predefined JSON schemas.

    Methods: 
        validate_json(self, json_object: dict, table_name: str):
            Validates a JSON object against a specified schema

        get_validation_results(self) -> dict:
            Returns the validation results as a dictionary.
    """

    def __init__(self):
        """Initializes the TableValidator with the path to JSON schemas."""
        self.base_path = os.path.join(settings.BASE_DIR, f"utilities/json_schemas/{SCHEMA_VERSION}")
        self.valid = False
        self.errors = []

    def validate_json(self, json_object: dict, table_name: str):
        """
        Validate a JSON object against a specified schema.

        This method validates the provided JSON object against the schema corresponding
        to the specified table name. It updates the instance's `valid` and `errors` attributes
        based on the validation results.

        Args:
            json_object (dict): The JSON object to be validated.
            table_name (str): The name of the table which corresponds to the schema file.

        Returns:
            None
        """
        schema_path = os.path.join(self.base_path, f"{table_name}.json")
        try:
            with open(schema_path, "r") as schema_file:
                schema = jsonref.load(schema_file)

            validator = jsonschema.Draft7Validator(schema)
            self.errors = [
                f"{list(error.path)}: {error.message}"
                for error in validator.iter_errors(json_object)
            ]
            self.valid = len(self.errors) == 0

        except jsonschema.exceptions.ValidationError as e:
            self.valid = False
            self.errors = [str(e)]
        except FileNotFoundError:
            self.valid = False
            self.errors = [f"Schema file not found for {table_name}."]
        except Exception as e:
            self.valid = False
            self.errors = [f"An unexpected error occurred: {str(e)}."]

    def get_validation_results(self) -> dict:
        """
        Returns the validation results as a dictionary.

        This method provides the results of the JSON validation process. The 
        returned dictionary contains two keys: 'valid' and 'errors'. The 
        'valid' key holds a boolean indicating whether the JSON object passed 
        validation, and the 'errors' key holds a list of error messages if 
        any validation errors were encountered.

        Returns:
            dict: A dictionary with 'valid' (bool) and 'errors' (list) keys.
        """

        error_data = [
            {
                "field": error.split(":")[0]
                .strip("[]' ")
                .title(),  # Extract and clean up the field name, then capitalize
                "error": error.split(":")[
                    1
                ].strip(),  # Extract and clean up the error message
            }
            for error in self.errors
        ]

        return {"valid": self.valid, "errors": error_data}


def remove_na(datum: dict) -> dict:
    """
    Remove 'NA' values from submissions.

    This function iterates through a list of submissions and removes any entries
    that have a value of 'NA'.

    Args:
        submissions (list): A list of submissions to process.

    Returns:
        list: The list of submissions with 'NA' values removed.
    """

    parsed_datum = {k: v for k, v in datum.items() if v not in ("NA", "", ["NA"], [""])}

    return parsed_datum

def multi_value_split(datum: dict) -> dict:
    """Multi valu split
    """
    split_datum = {}

    for k, v in datum.items():
        if type(v) is str:
            if '|' in v:
                try:
                    split_datum[k] = [item.strip() for item in v.split('|')]
                except TypeError:
                    split_datum[k] = v
                except AttributeError:
                    pass
                except Exception as oops:
                    error = oops
                    print(error, k, v)
            else:
                split_datum[k] = v.strip()
        else:
                split_datum[k] = v

    return split_datum



def response_status(accepted_requests: bool, rejected_requests: bool) -> status:
    """Determine Response Status

    Determines the appropriate HTTP response status code based on the
    acceptance or rejection of requests.

    Parameters:
    - accepted_requests (bool):
        Flag indicating whether any requests have been accepted.
    - rejected_requests (bool):
        Flag indicating whether any requests have been rejected.

    Returns:
    - int: The HTTP status code representing the outcome. Possible values are:
        - status.HTTP_400_BAD_REQUEST (400) if all requests are rejected.
        - status.HTTP_207_MULTI_STATUS (207) if there is a mix of accepted and rejected requests.
        - status.HTTP_200_OK (200) if all requests are accepted.
    """

    if accepted_requests is False and rejected_requests == False:
        status_code = status.HTTP_400_BAD_REQUEST

    if accepted_requests is False and rejected_requests == True:
        status_code = status.HTTP_400_BAD_REQUEST

    if accepted_requests is True and rejected_requests is True:
        status_code = status.HTTP_207_MULTI_STATUS

    if accepted_requests is True and rejected_requests is False:
        status_code = status.HTTP_200_OK

    return status_code


def response_constructor(
    identifier: str, request_status: str, code: str, message: str = None, data: dict = None
) -> dict:
    """Constructs a structured response dictionary.

    This function creates a standardized response object for API responses.
    It structures the response with a given identifier as the key and includes
    details such as status, code, an optional message, and optional data.

    Parameters:
    - identifier (str):
        A unique identifier for the response object.
    - status (str):
        The request status (e.g., 'success', 'error')indicating the outcome
        of the operation.
    - code (str):
        The HTTP status code representing the result of the operation.
    - message (str, optional):
        An optional message providing additional information about the
        response or the result of the operation. Default is None.
    - data (dict, optional):
        An optional dictionary containing any data that should be returned in
        the response. This can include the payload of a successful request or
        details of an error. Default is None.
    """

    response_object = {
        "identifier": identifier,
        "request_status": request_status,
        "status_code": code,
    }

    if data is not None:
        response_object["data"] = data
    if message is not None:
        response_object["message"] = message

    return response_object


def validate_cloud_url(url):
    """
    Validates that a given URL is correctly formatted according to the standards
    expected by the Requests library. This validation ensures that the URL can be
    properly handled by Requests without causing errors in the preparation phase.

    Parameters:
    - url (str): The URL to be validated.

    Returns:
    - None: If the URL is valid, the function completes without returning anything.

    Raises:
    - ValidationError: If the URL preparation fails, indicating the URL is not
      valid or well-formed.

    Notes:
    - This function utilizes the `PreparedRequest.prepare_url` method from the
      Requests library, which can throw various exceptions if the URL does not
      meet expected standards. If such an exception is caught, this function
      raises a `ValidationError` with a message describing the issue.
    """

    prepared_request = PreparedRequest()
    try:
        prepared_request.prepare_url(url, None)
    except Exception as exc:
        return ValidationError(f"{url} is not a valid URL. Error: {str(exc)}")


def generate_tsv(data):
    """
    Generate a TSV (Tab-Separated Values) string from a list of dictionaries.

    This function takes a list of dictionaries and converts it into a TSV formatted string.
    The keys of the first dictionary are used as the header row.

    Args:
        data (list): A list of dictionaries containing the data to be converted to TSV.

    Returns:
        str: A string containing the TSV formatted data.
    """
    output = StringIO()
    writer = csv.writer(output, delimiter='\t')
    if data:
        # Write the header row
        writer.writerow(data[0].keys())
        # Write the data rows
        for row in data:
            writer.writerow(row.values())
    tsv_content = output.getvalue()
    output.close()
    return tsv_content


def generate_zip(files):
    """
    Generate a ZIP file from a dictionary of file names and contents.

    This function takes a dictionary where the keys are file names and the values are
    the file contents, and creates a ZIP file containing these files.

    Args:
        files (dict): A dictionary where keys are file names and values are file contents.

    Returns:
        BytesIO: A BytesIO object containing the ZIP file data.
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_name, content in files.items():
            zip_file.writestr(file_name, content)
    zip_buffer.seek(0)
    return zip_buffer


def compare_data(old_data:dict, new_data:dict) -> dict:
    """
    Compare two dictionaries and return a dictionary of changes.

    Args:
        old_data (dict): The original data dictionary.
        new_data (dict): The new data dictionary to compare against the 
        original.

    Returns:
        dict: A dictionary containing the changes. The keys are the attributes 
        that have changed, and the values are strings describing the change 
        (e.g., "old_value to new_value").
        If an attribute is not found in old_data, the change is noted as "NA 
        to new_value". If an error occurs during comparison, the change is 
        noted as "Error with attr: error_message".
    """
    changes = {}
    for attr, value in new_data.items():
        try:
            if old_data[attr] != value and old_data[attr] != str(value):
                print(f"{attr}: {old_data[attr]} to {value}")
                changes[attr] = f"{old_data[attr]} to {value}"
        except KeyError as error:
            print("ERROR: ", error)
            changes[attr] = f"NA to {value}"
        except Exception as excp:
            error = str(excp)
            changes[attr] = f"Error with {attr}: {error}"

    return changes


def bulk_retrieve(request_data: dict, model_class, id: str) -> dict:
    """
    Retrieve multiple instances of a model class based on a list of IDs.

    Args:
        request_data (dict): A dictionary containing the data with IDs to 
            retrieve.
        model_class: The Django model class to query.
        id (str): The key in request_data that contains the IDs.

    Returns:
        dict: A dictionary of model instances keyed by their IDs.
    """
    model_dict = model_class.objects.in_bulk([datum[id] for datum in request_data])

    return model_dict

def create_or_update(table_name: str, identifier: str, model_instance, datum: dict):
    """
    Create or update a model instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create or update.
        identifier (str): The unique identifier for the model instance.
        model_instance: The existing model instance to update, or None to create 
            a new instance.
        datum (dict): The data to create or update the model instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
   
    table_serializers = {
        "participant": {
            "input_serializer": ParticipantInputSerializer,
            "output_serializer": ParticipantOutputSerializer
        },
        "family":{
            "input_serializer": FamilySerializer,
            "output_serializer": FamilySerializer
        },
        "genetic_findings": {
            "input_serializer": GeneticFindingsSerializer,
            "output_serializer": GeneticFindingsSerializer
        }
    }

    model_input_serializer = table_serializers[table_name]["input_serializer"]
    model_output_serializer = table_serializers[table_name]["output_serializer"]

    datum = remove_na(datum=datum) 
    table_validator = TableValidator()
    table_validator.validate_json(json_object=datum, table_name=table_name)
    results = table_validator.get_validation_results()
    if results["valid"]:
        changes = compare_data(
            old_data=model_output_serializer(model_instance).data,
            new_data=datum
        ) if model_instance else {identifier:"CREATED"}
        #create needed submodules before serialization
        if table_name == "participant":
            datum = get_or_create_sub_models(datum=datum) 
        serializer = model_input_serializer(model_instance, data=datum)
        if serializer.is_valid():
            updated_instance = serializer.save()
            if not changes:
                return response_constructor(
                    identifier=identifier,
                    request_status="SUCCESS",
                    code=200,
                    message=f"{table_name} {identifier} had no changes.",
                    data={
                        "updates": None,
                        "instance": model_output_serializer(updated_instance).data
                    }
                ), "accepted_request"

            return response_constructor(
                identifier=identifier,
                request_status="UPDATED" if model_instance else "CREATED",
                code=200 if model_instance else 201,
                message=(
                    f"{table_name} {identifier} updated." if model_instance 
                    else f"{table_name} {identifier} created."
                ),
                data={
                    "updates": changes,
                    "instance": model_output_serializer(updated_instance).data
                }
            ), "accepted_request"
            
        else:
            error_data = [
                {item: serializer.errors[item]}
                for item in serializer.errors
            ]
            return response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=error_data,
            ), "rejected_request"
        
    else:
        return response_constructor(
            identifier=identifier,
            request_status="BAD REQUEST",
            code=400,
            data=results["errors"],
        ), "rejected_request"
