#!/usr/bin/env python3

import requests
import sys
import aws_calls, dashboard_calls, geneyx_calls


def process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun):
    ga_samples = geneyx_calls.get_ga_samples(ga_config)
    ga_cases = geneyx_calls.get_ga_cases(ga_config)

    families = []
    for row in lrs_manifest_csv:
        # Only process participants not present in Geneyx
        if row['current_id'] in ga_samples:
            continue
        else:
            participant_id = row['current_id']
            participant = dashboard_calls.table_query(all_tables['participant'], 'participant_id', participant_id)[0]
            if participant['family_id'] not in families:
                families.append({ participant['family_id']: {} })
    for family in families:
        for participant in families[family]:
            sample_response = geneyx_calls.sample_uploader(s3_client, ga_config, row['current_id'], all_tables, dryrun)
            if not sample_response == 'Success':
                print()
        case_response = geneyx_calls.case_maker(ga_config, family, all_tables, dryrun)
        if not case_response == 'Success':
            print()


def main(dryrun=True):
    ga_config = {
        "server": "https://analysis.geneyx.com",
        "apiUserId": "MJoD+yyHWMm2qDpXys12kg==",
        "apiUserKey": "SLOTIS2V/4oaI76IQYWQsWotWZhU55ClRRTDqc8BdfzbW9bazQRbvQ==",
        "pageSize": 1000,
    }
    s3_client = aws_calls.get_s3_client()
    dashboard_login = {
        "server": "https://genomics.icts.uci.edu",
        "verify": False,  # curl https verification
        "credentials": {
            "username": "idedios",
            "password": "iBPNlvj79a^tZHQyje#QM@Q5*ULaXJOo",
        }
    }
    dashboard_login = dashboard_calls.get_dashboard_token(dashboard_login)
    dashboard_tables = {
        "metadata": {
            "family": None,
            "participant": None,
            "phenotype": None,
        }
    }
    all_tables = dashboard_calls.get_all_dashboard_tables(dashboard_login, dashboard_tables)
    lrs_manifest_csv = aws_calls.get_lrs_manifest(s3_client)
    process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun)


if __name__ == '__main__':
    main()