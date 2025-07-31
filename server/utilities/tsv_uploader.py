#!/usr/bin/env python3

import argparse
import csv
import json
import jsonref
import jsonschema
import os
import re
import requests
import sys


# Global args
table_load_order = [
    'metadata/family',
    'metadata/participant',
    'metadata/phenotype',
    'metadata/analyte',
    'experiments/experiment_dna_short_read',
    'experiments/experiment_rna_short_read',
    'experiments/experiment_pac_bio',
    'experiments/experiment_nanopore',
    'experiments/aligned_dna_short_read',
    'experiments/aligned_rna_short_read',
    'experiments/aligned_pac_bio',
    'experiments/aligned_nanopore',
    'metadata/biobank',
    'metadata/genetic_findings',
]
branch="dev"
schema_version = "v1.8"
schema_uri = f"https://raw.githubusercontent.com/UCI-ICTS/icts-dashboard/refs/heads/{branch}/server/utilities/json_schemas/{schema_version}"


def get_args():
    parser = argparse.ArgumentParser(
        prog='tsv_uploader.py',
        description="Take a TSV/JSON file and parse entries as API calls to an instance"
    )
    parser.add_argument(
        '-c', '--config',
        help='config file with CSRF token'
    )
    parser.add_argument(
        '--host',
        help='host base URL if not in config (e.g. http://localhost:8000/)'
    )
    parser.add_argument(
        '--token',
        help='CSRF token if no config provided'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='TSV/JSON filepath'
    )
    parser.add_argument(
        '-n', '--table_name',
        help='table name'
    )
    return parser.parse_args()


def parse_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


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

    import pdb; pdb.set_trace()
    try:
        schema = jsonref.load_uri(f"{schema_uri}/{table_name}.json")

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


def parse_input(input_file, table_name):
    if not table_name:
        table_name = os.path.basename(input_file).split('.')[0]
    table_list = list()
    if input_file.endswith(".json"):
        table_list = json.load(open(input_file))
    elif input_file.endswith(".tsv"):
        csv_reader = csv.DictReader(open(input_file, 'r'), delimiter='\t')
        output_file = re.sub('.tsv$', '', input_file) + '.json'
        for row in csv_reader:
            if table_name == 'biobank' and 'completed' in row:
                completed_status = row['completed'].upper()
                if completed_status == 'TRUE':
                    row['completed'] = True
                elif completed_status == 'FALSE':
                    row['completed'] = False
            table_list.append(row)
        json.dump(table_list, open(output_file, 'w'), indent=2)
    return table_list


def table_list_to_dict(table_list, table_name):
    id_field = table_name + '_id'
    table_dict = dict()
    #import pdb; pdb.set_trace()
    for i, x in enumerate(table_list):
        id = table_list[i][id_field]
        table_dict[id] = table_list[i]
    return table_dict


def coerce_table_name(table_name):
    # Check table name
    for tname in table_load_order:
        if table_name == tname.split('/')[1]:
            table_name = tname
            return table_name
    print(f"{table_name} is an invalid table name")
    sys.exit(1)


def get_tokens(config):
    api_url = config['host']
    if not config['api_token']:
        print("No API Token set. Please retrieve a token from the login profile page.")
        sys.exit(1)
    response = requests.get(url=f"{api_url}/api/health")
    assert response.status_code == 200
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'Authorization': f"Bearer {config['api_token']}",
        'X-CSRFToken': response.cookies['csrftoken'],
    }
    client = {
        'api_url': api_url,
        'headers': headers,
    }
    return client


def response_log(id_field, responses):
    response_list = list()
    for response in responses.json():
        id = response['identifier']
        main_message = f"{response['request_status']},{id_field},{id}"
        if response['request_status'] == 'NO CHANGE' or response['request_status'] == 'CREATED':
            print(main_message)
            response_list.append(main_message)
        elif response['request_status'] == 'UPDATED':
            print(f"{main_message},{response['data']['updates']}")
            response_list.append(f"{main_message},{response['data']['updates']}")
        else:
            print(f"{main_message},{response['data']}")
            response_list.append(f"{main_message},{response['data']}")
    return response_list


def post_requests(client, table_dict, table_name):
    get_all_response = requests.get(url=f"{client['api_url']}/api/{table_name}/all/", headers=client['headers'])
    assert get_all_response.status_code == 200
    id_field = table_name.split('/')[1] + '_id'
    existing_ids = list()
    update_list = list()
    create_list = list()
    log = list()
    for existing_entry in get_all_response.json():
        id = existing_entry[id_field]
        existing_ids.append(id)
        if id in table_dict:
            update_list.append(table_dict[id])
    for new_id in table_dict:
        if new_id not in existing_ids:
            create_list.append(table_dict[new_id])
    # Updates
    if update_list:
        update_responses = requests.post(url=f"{client['api_url']}/api/{table_name}/update/", json=update_list, headers=client['headers'])
        if update_responses.status_code == 400:
            print(f"All bad update requests")
        elif update_responses.status_code == 207 or update_responses.status_code == 200:
            log = log + response_log(id_field, update_responses)
    # Creates
    if create_list:
        create_responses = requests.post(url=f"{client['api_url']}/api/{table_name}/create/", json=create_list, headers=client['headers'])
        if create_responses.status_code == 400:
            import pdb; pdb.set_trace()
            print(f"All bad create requests")
        if create_responses.status_code == 207 or create_responses.status_code == 200:
            log = log + response_log(id_field, create_responses)
    return log


def post_log(log, log_file):
    header = "response,field,id,info"
    with open(log_file, 'w') as f:
        f.write(f"{header}\n")
        for row in log:
            f.write(f"{row}\n")


if __name__ == '__main__':
    args = get_args()
    if not args.config:
        config = {
            "host": args.host,
            "api_token": args.token,
        }
    else:
        config = parse_config(args.config)
    table_name = args.table_name
    if not table_name:
        table_name = os.path.basename(args.input).split('.')[0]
    table_list = parse_input(args.input, table_name)
    table_dict = table_list_to_dict(table_list, table_name)
    table_name = coerce_table_name(table_name)
    client = get_tokens(config)
    log = post_requests(client, table_dict, table_name)
    post_log(log, f"{os.path.dirname(args.input)}/{table_name.split('/')[1]}.log.csv")
