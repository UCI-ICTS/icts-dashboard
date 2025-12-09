#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import csv
import gzip
import logging
import sys


# Global vars
encoding = "utf-8"


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


def get_lrs_manifest(s3_client):
    """
    Parse the latest lrs-manifest.tsv in 's3://pmgrc-wgs-long-read-derived-data/alignments/ambry/'
    """
    bucket = 'pmgrc-wgs-long-read-derived-data'
    prefix = 'alignments/ambry/lrs-manifest'
    lrs_manifest_key = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)['Contents'][0]['Key']  # there should only be one lrs-manifest present
    lrs_manifest_obj = s3_client.get_object(Bucket=bucket, Key=lrs_manifest_key)

    return csv.DictReader(lrs_manifest_obj['Body'].read().decode(encoding).splitlines(), delimiter='\t')


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


def get_s3_object(s3_client, bucket, prefix):

    return s3_client.get_object(Bucket=bucket, Key=prefix)


def get_snv_vcf(s3_client, vcf_path):
    bucket, snv_vcf_key = get_s3_bucket_prefix(vcf_path)
    if snv_vcf_key.endswith(".gz"):
        with gzip.GzipFile(fileobj=s3_client.get_object(Bucket=bucket,Key=snv_vcf_key)['Body']) as snvVcfGzFile:
            return snvVcfGzFile.read().decode(encoding)
    else:
        return get_s3_object(s3_client, bucket, snv_vcf_key)['Body'].read().decode(encoding)


def find_sv_vcfs(s3_client, analysis_out, ambry_id):
    """
    Find the following SV VCFs for the pacbio_unify script
    * hificnv -> cnv
    * pbsv -> sv_vcf
    * trgt -> trgt
    Process the ROH bed file separately. WDL v1 does not bgzip it
    """
    bucket, prefix = get_s3_bucket_prefix(analysis_out)
    objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    sv_keys = ["sv_vcf", "trgt", "cnv"]
    sv_vcfs = {}
    for object in objects['Contents']:
        if ambry_id in object['Key'] and ".vcf" in object['Key'] and not object['Key'].endswith(".tbi"):  # Object is a VCF with an Ambry ID in the name
            for key in sv_keys:
                if key in object['Key']:
                    if object['Key'].endswith(".gz"):
                        with gzip.GzipFile(fileobj=get_s3_object(s3_client, bucket, object['Key'])['Body']) as svVcfGzFile:
                            sv_vcfs[key] = svVcfGzFile.read().decode(encoding).splitlines()
                    else:  # Also allow for uncompressed files
                        print(object['Key'])
                        sv_vcfs[key] = get_s3_object(s3_client, bucket, object['Key'])['Body'].read().decode(encoding).splitlines()
        elif ambry_id in object['Key'] and 'roh.bed' in object['Key']:  # Get ROH bed file
            if object['Key'].endswith('.gz'):
                with gzip.GzipFile(fileobj=get_s3_object(s3_client, bucket, object['Key'])['Body']) as rohBedGzFile:
                    sv_vcfs["roh"] = rohBedGzFile.read().decode(encoding).splitlines()
            else:
                sv_vcfs["roh"] = get_s3_object(s3_client, bucket, object['Key'])['Body'].read().decode(encoding).splitlines()
    for key in sv_keys:
        if key not in sv_vcfs:
            print(f"{ambry_id} is missing its {key} VCF")

    return sv_vcfs


def find_cpg_bed(s3_client, analysis_out, ambry_id, expiration):
    """
    Find combined cpg bed file, with the suffix 'combined.bed', and return a shareable url
    """
    bucket, prefix = get_s3_bucket_prefix(analysis_out)
    objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for object in objects['Contents']:
        if ambry_id in object['Key'] \
                and ('cpg_pileup_beds' in object['Key'] \
                    or 'cpg_combined_bed' in object['Key']) \
                and 'combined.bed' in object['Key']:
            return create_presigned_urls(s3_client, f"s3://{bucket}/{object['Key']}", expiration)


def find_bai(s3_client, analysis_out, bam_basename, expiration):
    """
    Find the bam index given the bam basename, and return a shareable url
    """
    bucket, prefix = get_s3_bucket_prefix(analysis_out)
    objects = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for object in objects['Contents']:
        if f"{bam_basename}.bai" in object['Key']:
            return create_presigned_urls(s3_client, f"s3://{bucket}/{object['Key']}", expiration)