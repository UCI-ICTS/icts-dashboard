#!/usr/bin/env python3
"""Data Converters
"""
import sys
import csv
import json
import argparse
from django.conf import settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# def usr_args():
#     """User Arguments

#     arguments for command line invocation
#     """

#     parser = argparse.ArgumentParser()

#     # set usages options
#     parser = argparse.ArgumentParser(
#         prog="data_getter", usage="%(prog)s [options]"
#     )

#     # # version
#     # parser.add_argument(
#     #     '-v', '--version',
#     #     action='version',
#     #     version='%(prog)s ' + __version__)

#     parser.add_argument(
#         "-t", "--table", required=True, help="table file to convert."
#     )

#     # parser.add_argument('-s', '--schema',
#     #                             # type = argparse.FileType('r'),
#     #                             help="Root json schema to parse")

#     # Print usage message if no args are supplied.
#     if len(sys.argv) <= 1:
#         sys.argv.append("--help")

#     options = parser.parse_args()
#     return options

def get_tables():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('gregor-key.json', scope)

    # Authorize the clientsheet 
    client = gspread.authorize(creds)
    # Make sure you share your Google sheet with the email address of your service account
    url = "https://docs.google.com/spreadsheets/d/1YQGia8SHe9Egg7ccQg34CaTE1EIYZWaDclCYTfSAnEA/edit?gid=67759237#gid=67759237"
    import pdb; pdb.set_trace()
    sheet = client.open_by_url(url)

    # Get the first sheet of the Google Sheet
    worksheet = sheet.get_worksheet(4)

    # Get all records of the data as a list of dictionaries
    records = worksheet.get_all_records()
    print(records)


if __name__ == "__main__":
    # options = usr_args()
    get_tables()
    
    # print(options)
