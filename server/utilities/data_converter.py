#!/usr/bin/env python3
"""Data Converters
"""

import sys
import csv
import json
import argparse


class TableConverter:
    """Class for converting tabular data"""

    @staticmethod
    def convert_to_json(input_data: dict) -> json:
        """Converts a CSV or TSV to a list of JSON objects"""
        sheet = []
        extension = input_data.split(".")[-1]
        delimiter = "\t" if extension == "tsv" else ","

        with open(input_data, "r", encoding="utf-8") as file:
            data = csv.reader(file, delimiter=delimiter)
            header = next(data)
            for datum in data:
                sheet.append(datum)

        data_list = []
        for row in sheet:
            line = {}
            for count, item in enumerate(header):
                line[item] = row[count]
            data_list.append(line)

        json_list = json.dumps(data_list, indent=4)
        return json_list

    def usr_args():
        """User Arguments

        arguments for command line invocation
        """

        parser = argparse.ArgumentParser()

        # set usages options
        parser = argparse.ArgumentParser(
            prog="data_converter", usage="%(prog)s [options]"
        )

        # # version
        # parser.add_argument(
        #     '-v', '--version',
        #     action='version',
        #     version='%(prog)s ' + __version__)

        parser.add_argument(
            "-t", "--table", required=True, help="table file to convert."
        )

        # parser.add_argument('-s', '--schema',
        #                             # type = argparse.FileType('r'),
        #                             help="Root json schema to parse")

        # Print usage message if no args are supplied.
        if len(sys.argv) <= 1:
            sys.argv.append("--help")

        options = parser.parse_args()
        return options


if __name__ == "__main__":
    options = TableConverter.usr_args()

    json_output = TableConverter.convert_to_json(options.table)
    print(json_output)
