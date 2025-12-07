#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import csv
import gzip
import logging
import os
import requests
import sys
import yaml


def get_s3_bucket_prefix(s3_uri):
    """
    Convert an aws s3 uri to discrete bucket name and key path
    """
    uri_list = s3_uri.removeprefix('s3://').split('/')
    bucket = uri_list[0]
    key = '/'.join(uri_list[1::])
    return bucket, key


def get_s3_client(service='s3', region_name='us-east-2'):
    try:
        return boto3.client(service, region_name=region_name)
    except:
        print("Check if aws has been configured yet")
        sys.exit(1)


def get_dashboard_token(dashboard_login):
    """
    Get bearer token for API calls
    """
    login_url = f"{dashboard_login['server']}/api/auth/token/login"
    response = requests.post(login_url, data=dashboard_login['credentials'], headers=dashboard_login['headers'], verify=dashboard_login['verify'])
    if response.status_code == 200:
        dashboard_login['header']['Authorization'] = f"Bearer {response.json()['access']}"
        return dashboard_login


def get_all_dashboard_tables(dashboard_login, dashboard_tables):
    """
    Get all tables to minimize API calls
    """
    if not dashboard_tables:
        tables_url = f"{dashboard_login['server']}/api/search/get_all_tables"
        response = requests.get(tables_url, headers=dashboard_login['headers'], verify=dashboard_login['verify'])
        if response.status_code == 200:
            return response.json()
    else:
        for app in dashboard_tables:
            for model in dashboard_tables[app]:
                table_url = f"{dashboard_login['server']}/api/{app}/{model}/all"
                response = requests.get(tables_url, headers=dashboard_login['headers'], verify=dashboard_login['verify'])
                if response.status_code == 200:
                    dashboard_tables[app][model] = response.json()
        return dashboard_tables


def get_lrs_manifest(s3_client):
    """
    Parse the latest lrs-manifest.tsv in 's3://pmgrc-wgs-long-read-derived-data/alignments/ambry/'
    """
    bucket = 'pmgrc-wgs-long-read-derived-data'
    prefix = 'alignments/ambry/lrs-manifest'
    encoding = 'utf-8'
    lrs_manifest_key = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)['Contents'][0]['Key']  # there should only be one lrs-manifest present
    lrs_manifest_obj = s3_client.get_object(Bucket=bucket, Key=lrs_manifest_key)

    return csv.DictReader(lrs_manifest_obj['Body'].read().decode(encoding).splitlines(), delimiter='\t')


def process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun):
    url = f"{ga_config['server']}/api/Samples"
    response = requests.post(url, data=ga_config)
    if response.json()['Code'] == 'Success':
        ga_samples = response.json()['Data']
    else:
        print("Error with Geneyx API request Samples")
        sys.exit(1)

    for row in lrs_manifest_csv:
        # Only process participants not present in Geneyx
        if row['current_id'] in ga_samples:
            continue
        else:
            sample_uploader(s3_client, ga_config, row['current_id'], all_tables, dryrun)


def create_presigned_urls(s3_client, s3_uri, expiration):
    """
    Create presigned urls for shareable objects for up to 7 days
    """
    try:
        bucket, key = get_s3_bucket_prefix(s3_uri)
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    return response


def find_s3_object(s3_client, analysis_out, ambry_id, suffix):
    """
    Docstring for find_s3_object

    :param s3_client: Description
    :param analysis_out: Description
    :param ambry_id: Description
    :param suffix: Description
    """
    bucket, prefix = get_s3_bucket_prefix(analysis_out)
    objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for object in objects['Contents']:
        if ambry_id in object['Key'] and object['Key'].endswith(suffix):
            return f"s3://{bucket}/{object['Key']}"


def find_sv_vcfs(s3_client, analysis_out, ambry_id):
    """
    Find the following SV VCFs for the pacbio_unify script
    * hificnv -> cnv
    * pbsv -> sv_vcf
    * trgt -> trgt
    """
    bucket, prefix = get_s3_bucket_prefix(analysis_out)
    objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    sv_keys = ["cnv", "sv_vcf", "trgt"]
    sv_vcfs = {}
    for object in objects['Contents']:
        if ambry_id in object['Key'] and object['Key'].endswith('.vcf.gz'):  # Object is a VCF with an Ambry ID in the name
            for key in sv_keys:
                if key in object['Key']:
                    sv_vcfs[key] = s3_client.get_object(Bucket=bucket, Key=object['Key'])['Body'].read()
    for key in sv_keys:
        if key not in sv_vcfs:
            print(f"{ambry_id} is missing its {key} VCF")
    return sv_vcfs


def load_ga_config():
    """
    Requires Geneyx ga.config.yml to be placed in the server/utilites path
    ga.config.yml must have the following attributes:
    * ApiUserKey
    * ApiUserID
    * server - defaults to https://analysis.geneyx.com
    """
    with open('ga.config.yml') as f:
        return yaml.safe_load(f)


def table_query(table, attribute, key):
    return_rows = []
    for row in table:
        if row[attribute] == key:
            return_rows.append(row)
    return return_rows


def sample_uploader(ga_config, s3_client, lrs_manifest_row, all_tables, dryrun=True):
    """
    Upload SNV and SV VCFs to Geneyx
    """

    specimen_map = {
        "D": "Blood",
        "OG": "Saliva",
        "SC": "Buccal",
        "SG": "Buccal",
        "X": "Other"
    }
    url_expiration = 604800  # 7 days
    participant_id = lrs_manifest_row['current_id']
    specimen_type = specimen_map[lrs_manifest_row['UCI_ID2'].split('-')[-2]]
    ambry_id = lrs_manifest_row['ambry_id']
    analysis_out = lrs_manifest_row['snv_vcf'][0:lrs_manifest_row['snv_vcf'].index('out')]

    # Get AWS objects
    bam_basename = lrs_manifest_row['aligned_bam'].split(';')[0].split('/')[-1]
    bam_url = create_presigned_urls(s3_client, lrs_manifest_row['aligned_bam'], expiration=url_expiration)
    bai_uri = find_s3_object(s3_client, ambry_id, '.bai')
    bai_url = create_presigned_urls(s3_client, bai_uri, expiration=url_expiration)
    methyl_bed_uri = find_s3_object(s3_client, ambry_id, '.bed')
    methyl_bed_url = create_presigned_urls(s3_client, methyl_bed_uri, expiration=url_expiration)

    snv_basename = lrs_manifest_row['snv_vcf'].split(';')[0].split('/')[-1]
    sv_basename = f"{participant_id}.GRCh38.geneyx.unify.sv.vcf.gz"

    sv_vcfs = find_sv_vcfs(s3_client, analysis_out, ambry_id)
    unify_vcf = pacbio_unify_sv(sv_vcfs)

    bucket, snv_vcf_key = get_s3_bucket_prefix(lrs_manifest_row['snv_vcf'])
    files = {  # load binary contents of gzipped files
        'snvFile': s3_client.get_object(Bucket=bucket, Key=snv_vcf_key)['Body'].read(),
        'svFile': unify_vcf,
    }

    ga_url = f"{ga_config['server']}/api/CreateSample"

    participant = table_query(all_tables['participants'], 'participant_id', participant_id)[0]

    sample_relation = participant['proband_relationship']
    if sample_relation == "Self":
        sample_relation = "Matched"

    family = table_query(all_tables['familes'], 'family_id', participant['family_id'])[0]

    geneyx_sample_upload = [{  # sample POST request template with default values
        "ApiUserKey": ga_config["apiUserKey"],
        "ApiUserID": ga_config["apiUserID"],
        "SampleSerialNumber": participant_id,  # participant_id
        "SampleSource": specimen_type,  # biobank or analyte source
        "SampleSequenceMachineId": "REVIO",
        "SampleEnrichmentKitId": "Long Read Sequencing no CADD",  # Current default smart filter set
        "SampleTarget": "WholeGenomeLongRead",
        "SampleGenomeBuild": "hg38",
        "SampleRelation": sample_relation,
        "ExcludeFromLAF": False,
        "bamUrl": bam_url,
        "methylationUrl": methyl_bed_url,
        "SnvFile": snv_basename,  # SNV VCF basename
        "StructFile": sv_basename,  # SV VCF basename. Must be Unify SV VCF or Sawfish VCF
        "SubjectId": participant_id,
        "SubjectGender": participant["sex"],
        "SubjectConsanguinity": family["consanguinity"],
        "SubjectPopulationType": participant["reported_race"],
        "SubjectPaternalAncestry": participant["paternal_id"],
        "SubjectMaternalAncestry": participant["maternal_id"],
        "SubjectFamilyHistory": family["family_history_detail"],
        "SubjectHasBioSample": True,
        "SubjectUseConsentPersonal": True,  # GRU?
        "SubjectUSeConsentClinical": False,
        "SkipAnnotation": False,
    }]
    if not dryrun:
        response = requests.post(ga_url, data=geneyx_sample_upload, files=files)
        return response.json()['Code']


def case_maker(ga_config, family_id, all_tables, dryrun=True):
    """
    Create Geneyx cases
    """
    ga_url = f"{ga_config['server']}/api/CreateCase"
    all_participants = all_tables['participants']
    family_members = []
    for participant in all_participants:
        if participant["family_id_id"] == family_id:
            family_members.append(participant)

    associated_samples = []
    for member in family_members:
        if member.proband_relationship == "Self":
            phenotypes = all_tables['phenotypes']
            phenotype_list = [p.term_id for p in phenotypes]
            geneyx_case = [{
                "ApiUserKey": ga_config["apiUserKey"],
                "ApiUserID": ga_config["apiUserID"],
                "SerialNumber": member["participant_id"],
                "Description": member["phenotype_description"],
                "Phenotypes": ','.join(phenotype_list),  # Comma delimited list of HPO IDs from the Phenotype table
                "ProtocolId": "LR_seq",  # Currently the only Geneyx protocol for Revio
                "SubjectId": member["participant_id"],
                "ProbandSampleId": member["participant_id"],
            }]
        else:  # Only add associated samples that exist in Geneyx
            associated_samples.append({
                "SampleId": member["participant_id"],
                "Relation": member["proband_relationship"],
                "Affected": member["affected_status"],
            })
    geneyx_case["AssociatedSamples"] = associated_samples  # Add associated samples
    if not dryrun:
        response = requests.post(ga_url, data=geneyx_case)
        return response.json()['Code']


def main(dryrun=True):
    ga_config = load_ga_config()
    s3_client = get_s3_client()
    dashboard_login = {
        "server": "https://genomics.icts.uci.edu",
        "headers": {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "",
        },
        "verify": False,
        "credentials": {
            "username": "idedios",
            "password": "iBPNlvj79a^tZHQyje#QM@Q5*ULaXJOo",
        }
    }
    dashboard_login = get_dashboard_token(dashboard_login)
    dashboard_tables = {"metadata": ["family", "participant", "phenotype"]}
    all_tables = get_all_dashboard_tables(dashboard_login, dashboard_tables)
    lrs_manifest_csv = get_lrs_manifest(s3_client)
    process_lrs_manifest(s3_client, ga_config, lrs_manifest_csv, all_tables, dryrun)


if __name__ == '__main__':
    main()