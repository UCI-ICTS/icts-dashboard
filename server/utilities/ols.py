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
        help='term id (e.g. HP:0000017, MONDO:000547, ORPHA:, etc.)'
    )
    return parser.parse_args()


def query_ols(term_id):
    # Determine if EBI OLS is online and healthy
    health_response = requests.get(
        url=f"{EBI_OLS_API}/v2/health",
        headers={'accept':'*/*'})
    assert health_response.ok

    # Ontology IDs and IRIs
    onto_lookup = {
        "HP": "http://purl.obolibrary.org/obo/",
        "MONDO": "http://purl.obolibrary.org/obo/",
        "ORDO": "http://www.orpha.net/ORDO/",
        "SNOMED": "http://snomed.info/id/",
    }

    term_id = re.sub(':', '_', term_id)  # Short-form name, no colon
    onto = term_id.split('_')[0]
    if onto == "ORPHA":
        term_id = re.sub("ORPHA", "Orphanet", term_id).strip()
        onto = "ORDO"
    elif onto == "SNOMED":
        term_id = re.sub("SNOMED_", "", term_id)
    iri = onto_lookup[onto] + term_id
    iri = urllib.parse.quote(iri, safe='', encoding='utf-8', errors='strict')  # double URL encoding
    iri = urllib.parse.quote(iri, safe='', encoding='utf-8', errors='strict')  # double URL encoding
    request_url = f"{EBI_OLS_API}/ontologies/{onto}/terms/{iri}?lang={LANG}"
    ancestors_url = f"{EBI_OLS_API}/ontologies/{onto}/terms/{iri}/ancestors?lang={LANG}"
    print(request_url)
    term_response = requests.get(
        url=request_url,
        headers={'accept':'application/json'}
    )
    assert term_response.ok
    ancestors_response = requests.get(
        url=ancestors_url,
        headers={'accept':'application/json'}
    )
    assert ancestors_response.ok

    term_json = json.loads(term_response.content)
    ancestors_json = json.loads(ancestors_response.content)

    print(f"obo_id: {term_json['obo_id']}")
    print(f"label: {term_json['label']}")
    print(f"synonyms: {term_json['synonyms']}")
    print(f"cross reference: {term_json['annotation']['database_cross_reference']}")

    nodes_ignore = [  # List of nodes to ignore from MONDO, HP, and ORDO
        "entity",
        "continuant",
        "specifically dependent continuant",
        "realizable entity",
        "disposition",
        "disease",
        "human disease",
        "All",
        "Phenotypic abnormality",
        "clinical entity",
        "Disease",
        "disorder",
    ]

    if "_embedded" in ancestors_json:
        if "terms" in ancestors_json["_embedded"]:
            print("\nAncestor nodes:")
            tab_counter = ""
            for term in ancestors_json["_embedded"]["terms"][::-1]:
                if term["label"] in nodes_ignore:
                    continue
                print(f"{tab_counter}- {term['label']}")
                tab_counter += " "


if __name__ == "__main__":
    args = get_args()
    query_ols(args.term)
