#!/usr/bin/env python
# utilities/schema_maker.py

import os
import csv
import json
import sys
import argparse


__version__ = "0.1"
__status__ = "TEST"

# Map custom data_type strings to JSON Schema types.
DATA_TYPE_MAP = {
    "string": "string",
    "date": "string",      # you might add "format": "date" if desired
    "integer": "integer",
    "float": "number",
    "boolean": "boolean",
    "object": "object",
    "array": "array",
    # sometimes you may have types like "enumeration" that you want to map to string with an enum
    "enumeration": "string"
}

def usr_args():
    """User supplied arguments for functions
    """

    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(
        prog='schema_maker',
        usage='%(prog)s [options]')

    # version
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ' + __version__)
    
    parser.add_argument(
        '-i', '--input',
        help="input"
    )
    parser.add_argument(
        '-o', '--output',
        default="utilities/json_schemas/v1.7/",
        help="output directory"
    )
    if len(sys.argv) <= 1:
        sys.argv.append('--help')

    return parser.parse_args()


def convert_column(column: dict) -> dict:
    """
    Convert a single column definition from the schema-like object into a JSON Schema property.
    
    - If the column has "multi_value_delimiter": "|", it is treated as an array of items.
    - If enumerations are provided, they are added.
    - Any 'notes' are appended to the description.
    - If "is_bucket_path": true, a URL pattern is enforced.
    - If the "required" property is a conditional expression (a string starting with "CONDITIONAL"),
      then it is stored in the schema as "x-required-condition".
    """
    # Build the base schema from the column attributes.
    data_type = column.get("data_type", "string").lower()
    json_type = DATA_TYPE_MAP.get(data_type, "string")
    base_schema = {"type": json_type}

    # Add enum if provided.
    if "enumerations" in column and column["enumerations"] != "":
        enum_val = column["enumerations"]
        enum_val = enum_val.split(",")
        if not isinstance(enum_val, list):
            enum_val = [enum_val]
        base_schema["enum"] = enum_val
        # import pdb; pdb.set_trace()

    # Add description and append notes if provided.
    description = column.get("description", "")
    notes = column.get("notes")
    if notes:
        if description:
            description += "\n\nNotes: " + notes
        else:
            description = "Notes: " + notes
    if description:
        base_schema["description"] = description

    # Add examples ensuring it's an array.
    if "examples" in column:
        ex = column["examples"]
        if not isinstance(ex, list):
            ex = [ex]
        base_schema["examples"] = ex

    # Handle bucket paths: add a custom annotation and a pattern for validating URLs.
    if column.get("is_bucket_path") is True:
        base_schema["x-is_bucket_path"] = True
        base_schema["pattern"] = r"^(https?|gs|s3):\/\/.+$"

    # If the required field is conditional (a string starting with "CONDITIONAL"), store it as an annotation.
    req = column.get("required")
    if isinstance(req, str) and req.startswith("CONDITIONAL"):
        base_schema["x-required-condition"] = req

    # If the column has a multi-value delimiter, wrap the base schema in an array.
    if column.get("multi_value_delimiter") == "|":
        return {
            "type": "array",
            "items": base_schema
        }
    else:
        return base_schema


def table_2_schema(input_file: str, out_dir:str)-> dict:
    """Create Schema JSON
    """

    raw_url = "https://raw.githubusercontent.com/UCI-GREGoR/GREGor_dashboard/blob/main/server/utilities/v1.7/json_schemas"
    table_name = input_file.split("/")[-1].split(".")[0]
    table_schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        '$id': f"{raw_url}/{table_name}.json",
        'title': table_name,
        'version': "1.7.1", #data["version"],
        'type': 'object',
        'required':[],
        'definitions': {},
        'properties':{}
    }
    property_keys = ['required', 'column', 'data_type', 'references', 'description', 'example_value', 'enumerations', 'multi_value_delimiter', 'notes']
    with open(input_file, "r", encoding="utf-8") as file:
        data = csv.reader(file, delimiter="\t")
        next(data)
        headers = next(data)
        next(data)
        
        for line in data:
            result_dict = dict(zip(property_keys, line))
            if result_dict["required"] == "yes":
                table_schema["required"].append(result_dict["column"])
            table_schema["properties"][result_dict["column"]] = convert_column(result_dict)
        
    write_schema(
        schema=table_schema,
        schema_name=f"{table_name}.json",
        out_dir=out_dir
    )
    

def write_schema(schema: dict, schema_name: str, out_dir: str):
    """Write JSON Schema to a file, ensuring that the output directory exists."""
    out_dir = os.path.abspath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_file = os.path.join(out_dir, schema_name)
    print(out_file)
    with open(out_file, "w", encoding="utf-8") as outfile:
        json.dump(schema, outfile, indent=4)


def main():
    """
    Main function
    """

    options = usr_args()
    print(options)
    table_2_schema(
        input_file=options.input,
        out_dir=options.output
    )

if __name__ == "__main__":
    main()
