#!/usr/bin/env python3

import json
import os
import aws_calls, dashboard_calls, geneyx_calls


def process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun):
    ga_samples = geneyx_calls.get_ga_samples(ga_config)
    ga_cases_current = geneyx_calls.get_ga_cases(ga_config)

    ga_samples_sanitized = []
    for sample in ga_samples:  # sanitize geneyx sample IDs
        ga_samples_sanitized.append(sample.split('_')[0])
    ga_samples = ga_samples_sanitized

    print(f"Processing lrs_manifest_csv")
    families = {}
    for row in lrs_manifest_csv:  # Get participant metadata, relationship, and family structure
        participant_id = row['current_id']
        participant = dashboard_calls.table_query(all_tables['metadata']['participant'], 'participant_id', participant_id)[0]
        phenotypes = dashboard_calls.table_query(all_tables['metadata']['phenotype'], 'participant_id', participant_id)
        family_id = participant['family_id']
        if family_id not in families:
            families[family_id] = {}
        families[family_id][participant_id] = participant
        families[family_id][participant_id]['manifest'] = row
        families[family_id][participant_id]['phenotypes'] = phenotypes

    sorted_family_list = []
    for family_id in families:
        sorted_family_list.append(int(family_id.removeprefix("PMGRC-")))  # Sort families numerically
    sorted_family_list = sorted(sorted_family_list)

    ga_cases_main_samples = []  # Get Cases and their main sample
    ga_cache = "geneyx_cache/ga_cases.json"
    if os.path.exists(ga_cache):
        with open(ga_cache, 'rt') as f:
            ga_cases_json = json.load(f)
        for case in list(ga_cases_json):
            if case not in ga_cases_current:  # Remove cases deleted upstream
                del ga_cases_json[case]
                continue
            else:
                main_sample = ga_cases_json[case]["MainSampleSerialNumber"]
                ga_cases_main_samples.append(main_sample)
        for upstream_case in ga_cases_current:  # Add new cases created upstream to the cache
            if upstream_case not in ga_cases_json:
                ga_cases_json[upstream_case] = geneyx_calls.get_ga_case(ga_config, upstream_case)
    else:
        ga_cases_json = {}
        for case in ga_cases_current:
            ga_case = geneyx_calls.get_ga_case(ga_config, case)
            ga_cases_json[case] = ga_case
            ga_cases_main_samples.append(ga_case["MainSampleSerialNumber"])

    if not os.path.exists(ga_cache.split('/')[0]):  # save Geneyx cases to file
        os.makedirs(ga_cache.split('/')[0])
    with open(ga_cache, "wt") as f:
        json.dump(ga_cases_json, f)

    for family_id in sorted_family_list:
        family_id = "PMGRC-" + str(family_id)
        family = dashboard_calls.table_query(all_tables['metadata']['family'], 'family_id', family_id)[0]
        proband = None
        for participant_id in families[family_id]:
            if families[family_id][participant_id]['proband_relationship'] == "Self":
                proband = participant_id
        for participant_id in families[family_id]:
            if participant_id in ga_samples:  # Only process participants not already present in Geneyx
                continue
            if not proband:  # Only process families with probands
                continue
            print(f"Calling Geneyx Sample Uploader for {participant_id}")
            participant = families[family_id][participant_id]
            sample_upload_response = geneyx_calls.sample_uploader(ga_config, s3_client, participant, family, dryrun)
            if sample_upload_response == 'success':
                ga_samples.append(participant_id)

        if proband and proband not in ga_cases_main_samples:  # Only create new cases
            print(f"Calling Geneyx Case Maker for {family_id}")
            case_maker_response = geneyx_calls.case_maker(ga_config, ga_samples, families[family_id], dryrun)
            if case_maker_response == 'success':
                ga_cases_current.append(proband)

    with open(ga_cache, "wt") as f:  # Save changes before exit
        json.dump(ga_cases_json, f)


def main(dryrun=False):
    geneyx_cache = "geneyx_cache/"
    if os.path.exists(f"{geneyx_cache}/ga_config.json"):
        with open(f"{geneyx_cache}/ga_config.json", 'rt') as f:
            ga_config = json.load(f)
    if os.path.exists(f"{geneyx_cache}/dashboard_login.json"):
        with open(f"{geneyx_cache}/dashboard_login.json", 'rt') as f:
            dashboard_login = json.load(f)
            dashboard_login = dashboard_calls.get_dashboard_token(dashboard_login)  # Do not cache login token
    if os.path.exists(f"{geneyx_cache}/dashboard_tables.json"):
        with open(f"{geneyx_cache}/dashboard_tables.json", 'rt') as f:
            dashboard_tables = json.load(f)
    all_tables = dashboard_calls.get_all_dashboard_tables(dashboard_login, dashboard_tables)
    s3_client = aws_calls.get_s3_client()
    lrs_manifest_csv = aws_calls.get_lrs_manifest(s3_client)
    process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun)
    #geneyx_calls.update_temp_links(s3_client, ga_config, lrs_manifest_csv, dryrun)


if __name__ == '__main__':
    main()