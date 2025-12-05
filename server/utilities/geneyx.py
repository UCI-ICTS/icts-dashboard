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

from metadata.models import Family, Participant, Phenotype, Analyte, Biobank


def get_s3_bucket_prefix(s3_uri):
    """
    Convert an aws s3 uri to discrete bucket name and key path
    """
    uri_list = s3_uri.removeprefix('s3://').split('/')
    bucket = uri_list[0]
    key = '/'.join(uri_list[1::])
    return bucket, key


def get_s3_client(service='s3', region_name='us-east-2'):
    return boto3.client(service, region_name=region_name)


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


def process_lrs_manifest(ga_config, lrs_manifest_csv):
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
            sample_uploader(ga_config, row['current_id'])



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


def get_s3_binary(s3_client, s3_uri):
    bucket, key = get_s3_bucket_prefix(s3_uri)
    return s3_client.get_object(Bucket=bucket, Key=key)['Body'].read()


def find_sv_vcfs(s3_client, analysis_out, ambry_id):
    """
    Find the following SV VCFs for the pacbio_unify script
    * hifiCNV
    * pbsv
    * trgt
    """
    bucket, prefix = get_s3_bucket_prefix(analysis_out)
    objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    vcfs = {}
    for object in objects['Contents']:
        if ambry_id in object['Key'] and object['Key'].endswith('.vcf.gz'):
            if "cnv" in object['Key']:
                vcfs['hificnv'] = s3_client.get_object(Bucket=bucket, Key=object['Key'])['Body'].read()
            elif "sv_vcf" in object['Key']:
                vcfs['pbsv'] = s3_client.get_object(Bucket=bucket, Key=object['Key'])['Body'].read()
            elif "trgt" in object['Key']:
                vcfs['trgt'] = s3_client.get_object(Bucket=bucket, Key=object['Key'])['Body'].read()
    if "hificnv" in vcfs and "pbsv" in vcfs and "trgt" in vcfs:
        return vcfs
    else:
        print(f"{ambry_id} is missing an structural vcf")
        sys.exit(1)


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


def sample_uploader(ga_config, s3_client, lrs_manifest_row):
    """
    Upload SNV and SV VCFs to Geneyx
    """
    url_expiration = 604800  # 7 days
    participant_id = lrs_manifest_row['current_id']
    bam_url = create_presigned_urls(s3_client, lrs_manifest_row['aligned_bam'], expiration=url_expiration)
    bucket, snv_key = get_s3_bucket_prefix(lrs_manifest_row['snv_vcf'])
    snv_basename = lrs_manifest_row['snv_vcf'].split('/')[-1]
    sv_basename = f"{lrs_manifest_row['current_id']}.GRCh38.geneyx.unify.sv.vcf.gz"
    wdl_out = lrs_manifest_row['snv_vcf'][0:lrs_manifest_row['snv_vcf'].index('out')]
    sv_vcfs = find_sv_vcfs(s3_client, wdl_out, lrs_manifest_row['ambry_id'])

    files = {  # load binary contents of gzipped files
        'snvFile': s3_client.get_object(Bucket=bucket, Key=snv_key)['Body'].read(),

    }

    url = f"{ga_config['server']}/api/CreateSample"
    participant = Participant.objects.get(pk=participant_id)
    sample_relation = participant.proband_relationship
    if sample_relation == "Self":
        sample_relation = "Matched"
    family = Family.objects.get(pk=participant.family_id)
    analytes = Analyte.objects.filter(participant_id=participant_id)

    geneyx_sample_upload = [{  # sample POST request template with default values
        "ApiUserKey": ga_config["apiUserKey"],
        "ApiUserID": ga_config["apiUserID"],
        "SampleSerialNumber": participant.participant_id,  # participant_id
        "SampleSource": "",  # biobank or analyte source
        "SampleSequenceMachineId": "REVIO",
        "SampleEnrichmentKitId": "Long Read Sequencing no CADD",  # Current default smart filter set
        "SampleTarget": "WholeGenomeLongRead",
        "SampleGenomeBuild": "hg38",
        "SampleRelation": sample_relation,
        "ExcludeFromLAF": False,
        "bamUrl": bam_url,
        "methylationUrl": "",
        "SnvFile": snv_basename,  # SNV VCF basename
        "StructFile": sv_basename,  # SV VCF basename. Must be Unify SV VCF or Sawfish VCF
        "SubjectId": participant.participant_id,
        "SubjectGender": participant.sex,
        "SubjectConsanguinity": family.consanguinity,
        "SubjectPopulationType": participant.reported_race,
        "SubjectPaternalAncestry": participant.paternal_id,
        "SubjectMaternalAncestry": participant.maternal_id,
        "SubjectFamilyHistory": family.family_history_detail,
        "SubjectHasBioSample": True,
        "SubjectUseConsentPersonal": True,  # GRU?
        "SubjectUSeConsentClinical": False,
        "SkipAnnotation": False,
    }]
    response = requests.post(url, data=geneyx_sample_upload, files=files)

    return response.json()['Code']


def case_maker(ga_config, family_id):
    """
    Create Geneyx cases
    """
    url = f"{ga_config['server']}/api/CreateCase"
    family_members = Participant.objects.filter(family_id=family_id)

    associated_samples = []
    for member in family_members:
        if member.proband_relationship == "Self":
            phenotypes = Phenotype.objects.filter(participant_id=member.participant_id)
            phenotype_list = [p.term_id for p in phenotypes]
            geneyx_case = [{
                "ApiUserKey": ga_config["apiUserKey"],
                "ApiUserID": ga_config["apiUserID"],
                "SerialNumber": member.participant_id,
                "Description": member.phenotype_description,
                "Phenotypes": ','.join(phenotype_list),  # Comma delimited list of HPO IDs from the Phenotype table
                "ProtocolId": "LR_seq",  # Currently the only Geneyx protocol for Revio
                "SubjectId": member.participant_id,
                "ProbandSampleId": member.participant_id,
            }]
        else:  # Only add associated samples that exist in Geneyx
            associated_samples.append({
                "SampleId": member.participant_id,
                "Relation": member.proband_relationship,
                "Affected": member.affected_status,
            })
    geneyx_case["AssociatedSamples"] = associated_samples  # Add associated samples
    response = requests.post(url, data=geneyx_case)

    return response.json()['Code']


def main():
    ga_config = load_ga_config()
    s3_client = get_s3_client()
    lrs_manifest_csv = get_lrs_manifest(s3_client)
    process_lrs_manifest(ga_config, lrs_manifest_csv)


if __name__ == '__main__':
    main()