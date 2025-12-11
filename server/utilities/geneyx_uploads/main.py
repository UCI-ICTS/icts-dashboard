#!/usr/bin/env python3

import sys
import aws_calls, dashboard_calls, geneyx_calls


def process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun):
    ga_samples = geneyx_calls.get_ga_samples(ga_config)
    ga_cases = geneyx_calls.get_ga_cases(ga_config)

    print(f"Processing lrs_manifest_csv")
    families = {}
    for row in lrs_manifest_csv:
        participant_id = row['current_id']
        participant = dashboard_calls.table_query(all_tables['metadata']['participant'], 'participant_id', participant_id)[0]
        proband_relationship = participant['proband_relationship']
        family_id = participant['family_id']
        if family_id not in families:
            families[family_id] = {}
        families[family_id][participant_id] = {
            "proband_relationship": proband_relationship,
            "manifest": row,
        }

    sorted_family_list = []
    for family_id in families:
        sorted_family_list.append(family_id.removeprefix("PMGRC-"))  # Sort families numerically
    sorted_family_list = sorted(sorted_family_list)

    for family_id in sorted_family_list:
        family_id = "PMGRC-" + family_id
        proband_present = False
        for participant_id in families[family_id]:
            if families[family_id][participant_id]['proband_relationship'] == "Self":
                proband_present = True
        for participant_id in families[family_id]:
            if participant_id in ga_samples:  # Only process participants not already present in Geneyx
                continue
            if not proband_present:  # Only process families with probands
                continue
            print(f"Calling sample uploader for {participant_id}")
            geneyx_calls.sample_uploader(ga_config, s3_client, row, all_tables, dryrun)
        print(f"Calling case maker for {family_id}")
        import pdb; pdb.set_trace()
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
    #geneyx_calls.update_temp_links(s3_client, ga_config, lrs_manifest_csv, dryrun)


if __name__ == '__main__':
    main()