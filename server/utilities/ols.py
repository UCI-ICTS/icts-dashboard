#!/usr/bin/env python3

import argparse
import json
import re
import requests
import urllib

EBI_OLS_API = "https://www.ebi.ac.uk/ols4/api"
LANG = "en"


def get_args():
    parser = argparse.ArgumentParser(
        prog='ols.py',
        description="Query the EBI OLS for ontologies given an ontology and a term id"
    )
    parser.add_argument(
        '-t', '--term',
        required=True,
        help='term id (e.g. HP:0000017, MONDO:000547, OMIM:, etc.)'
    )
    return parser.parse_args()


def query_ols(term_id):
    # Determine if EBI OLS is online and healthy
    health_response = requests.get(
        url=f"{EBI_OLS_API}/v2/health",
        headers={'accept':'*/*'})
    assert health_response.ok

    if term_id.startswith('ORPHA'):
        term_id = re.sub('ORPHA', 'ORDO', term_id)
    term_id = urllib.parse.quote(term_id)  # Format term to url
    term_response = requests.get(
        url=f"{EBI_OLS_API}/terms?obo_id={term_id}&lang={LANG}",
        headers={'accept':'application/json'})
    if term_response.ok:
        json_response = json.loads(term_response.content)
        last_term_desc = ""  # dedup responses
        #import pdb; pdb.set_trace()
        for term in json_response['_embedded']['terms']:
            if last_term_desc == term['description']:
                continue
            print(term['label'], term['description'])
            last_term_desc = term['description']


if __name__ == "__main__":
    args = get_args()
    query_ols(args.term)
