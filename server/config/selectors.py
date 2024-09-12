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


"""DB Level Services

    This module contains service functions that apply to the entire Database.
    It includes utility functions for handling response status determination,
    API data conversion, and constructing standardized response objects.
"""


class TableValidator:
    """Table Validator class to validate JSON objects against predefined JSON schemas."""

    def __init__(self):
        """Initializes the TableValidator with the path to JSON schemas."""
        self.base_path = os.path.join(settings.BASE_DIR, "utilities/json_schemas/")
        self.valid = False
        self.errors = []

    def validate_json(self, json_object: dict, table_name: str):
        """
        Validates a JSON object against a specified schema and updates the instance's valid and errors attributes.

        Parameters:
        - json_object (dict): The JSON object to be validated.
        - table_name (str): The name of the table which corresponds to the schema file.
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

    def get_validation_results(self):
        """
        Returns the validation results as a dictionary.

        Returns:
        - dict: A dictionary with 'valid' and 'errors' keys.
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
    """Remove NA
    Remove `NA` from submissions
    """

    parsed_datum = {k: v for k, v in datum.items() if v not in ("NA", "", ["NA"])}

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
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_name, content in files.items():
            zip_file.writestr(file_name, content)
    zip_buffer.seek(0)
    return zip_buffer

def compare_data(old_data:dict, new_data:dict) -> dict:
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
