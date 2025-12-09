#!/usr/bin/env python3

import sys
import aws_calls, dashboard_calls, geneyx_calls


def process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun):
    ga_samples = geneyx_calls.get_ga_samples(ga_config)
    ga_cases = geneyx_calls.get_ga_cases(ga_config)

    families = {}
    print(f"Processing lrs_manifest_csv")
    for row in lrs_manifest_csv:
        # Only process participants not present in Geneyx
        if row['current_id'] in ga_samples:
            continue
        else:
            participant_id = row['current_id']
            geneyx_calls.sample_uploader(ga_config, s3_client, row, all_tables, dryrun)
            participant = dashboard_calls.table_query(all_tables['metadata']['participant'], 'participant_id', participant_id)[0]
            if participant['family_id'] not in families:
                families[participant['family_id']] = []
            families[participant['family_id']].append(participant)

    ga_samples = geneyx_calls.get_ga_samples(ga_config)  # Get updated list after uploading
    for family_id in families:
        geneyx_calls.case_maker(ga_config, ga_samples, ga_cases, families[family_id], all_tables, dryrun)


def main(dryrun=False):
    ga_config = {
        "server": "https://analysis.geneyx.com",
        "apiUserId": "MJoD+yyHWMm2qDpXys12kg==",
        "apiUserKey": "SLOTIS2V/4oaI76IQYWQsWotWZhU55ClRRTDqc8BdfzbW9bazQRbvQ==",
        "pageSize": 1000,
    }
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
    s3_client = aws_calls.get_s3_client()
    lrs_manifest_csv = aws_calls.get_lrs_manifest(s3_client)
    process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun)


if __name__ == '__main__':
    main()