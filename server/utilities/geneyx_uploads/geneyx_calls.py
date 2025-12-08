#!/usr/bin/env python3

import gzip
import requests
import os
import sys
import yaml
import aws_calls, dashboard_calls


def load_ga_config():
    """
    Requires Geneyx ga.config.yml to be placed in the server/utilites path
    ga.config.yml must have the following attributes:
    * ApiUserKey
    * ApiUserID
    * server - defaults to https://analysis.geneyx.com
    """
    if os.path.isfile('ga.config.yml'):
        with open('ga.config.yml') as f:
            return yaml.safe_load(f)


def get_ga_samples(ga_config):
    url = f"{ga_config['server']}/api/Samples/"
    response = requests.post(url, data=ga_config)
    if not response.json()['Code'] == 'Success':
        print("Error with Geneyx API request Samples")
        sys.exit(1)
    else:

        return response.json()['Data']


def get_ga_cases(ga_config):
    url = f"{ga_config['server']}/api/Cases/"
    response = requests.post(url, data=ga_config)
    if not response.json()['Code'] == 'Success':
        print("Error with Geneyx API request Cases")
        sys.exit(1)
    else:

        return response.json()['Data']


def create_roh_variant(line_list):
    # Include ROH bed calls in unify sv
    chrom = line_list[0]
    pos_start = int(line_list[1])
    pos_end = int(line_list[2])
    roh_score = line_list[3]
    vcf_pos = str(min([pos_start, pos_end]) + 1)  # Bed files are 0-based; Vcf files are 1-based
    vcf_pos_end = str(max([pos_start, pos_end]))
    roh_variant = '\t'.join([
        chrom,
        vcf_pos,
        ".",
        "N",
        "<ROH>",
        ".",
        "PASS",
        f"END={vcf_pos_end}",
        f"SVTYPE=ROH;ROH_SCORE={roh_score}",
        "GT",
        "1/1\n"
    ])
    return roh_variant


def append_trgt_info_field(line_list):
    # Append SVTYPE=REP to all INFO fields for TRGT variants
    line_list[7] = line_list[7] + ";SVTYPE=REP"
    return '\t'.join(line_list)


def valid_variant(line_list):
    info = line_list[7]
    format = line_list[8]
    gt_idx = format.split(':').index('GT')
    gt = format.split(':')[gt_idx]
    # Skip non SV calls or ref/ref calls
    if "SVTYPE=" not in info or gt == "./.":
        return False
    else:
        return True


def coordinate_sort_variants(variants):
    """
    Sort unified variants to and return a list of lines
    """
    unsorted_variants = {}
    sorted_variants = []
    for v in variants:
        v_line = v.split('\t')
        unsorted_variants[v_line[0]] = {v_line[1]: v_line[2:]}
    for chrom in unsorted_variants.sort():
        for pos in unsorted_variants[chrom].sort():
            sorted_variants.append('\t'.join([chrom, pos] + unsorted_variants[chrom][pos]))
    return sorted_variants


def pacbio_unify_sv(sv_vcfs):
    """
    Docstring for pacbio_unify_sv

    :param sv_vcfs: Description
    """
    sv_keys = ["roh", "sv_vcf", "trgt", "cnv"]
    unified_variants = []
    for key in sv_keys:
        if key not in sv_vcfs:
            print(f"Cannot unify vcfs, missing {key} VCF")
            sys.exit(1)
        sv_vcf_header = []
        for line in sv_vcfs[key]:
            # Save sv_vcf header for UnifyVCF output
            if line.startswith("#"):
                if key == "sv_vcf":
                    sv_vcf_header.append(line)
            else:
                line_list = line.split('\t')
                if key == "roh":
                    # Include ROH bed calls in unify sv
                    unified_variants.append(create_roh_variant(line_list))
                else:
                    if key == "trgt":
                        line = append_trgt_info_field(line_list)
                    if not valid_variant(line_list):
                        continue
                    unified_variants.append(line)
    return ''.join([sv_vcf_header + coordinate_sort_variants(unified_variants)])  # Lines already have \n endings


def sample_uploader(ga_config, s3_client, lrs_manifest_row, all_tables, dryrun=True):
    """
    Upload SNV and SV VCFs to Geneyx
    """
    url_expiration = 604800  # 7 days

    participant_id = lrs_manifest_row['current_id']
    ambry_id = lrs_manifest_row['ambry_id']
    analysis_out = lrs_manifest_row['snv_vcf'][0:lrs_manifest_row['snv_vcf'].index('out')]

    specimen_map = {
        "D": "Blood",
        "OG": "Saliva",
        "SC": "Buccal",
        "SG": "Buccal",
        "X": "Other"
    }
    specimen_type = specimen_map[lrs_manifest_row['UCI_ID2'].split('-')[-2]]

    # Get AWS objects
    bam_basename = lrs_manifest_row['aligned_bam'].split(';')[0].split('/')[-1]
    bam_url = aws_calls.create_presigned_urls(s3_client, lrs_manifest_row['aligned_bam'], url_expiration)
    bai_url = aws_calls.find_bai(s3_client, analysis_out, bam_basename, url_expiration)
    methyl_bed_url = aws_calls.find_cpg_bed(s3_client, analysis_out, ambry_id, url_expiration)

    snv_basename = lrs_manifest_row['snv_vcf'].split(';')[0].split('/')[-1]
    sv_basename = f"{participant_id}.GRCh38.geneyx.unify.sv.vcf.gz"

    sv_vcfs = aws_calls.find_sv_vcfs(s3_client, analysis_out, ambry_id)
    unify_vcf = pacbio_unify_sv(sv_vcfs)

    bucket, snv_vcf_key = aws_calls.get_s3_bucket_prefix(lrs_manifest_row['snv_vcf'])
    with gzip.GzipFile(fileobj=s3_client.get_object(Bucket=bucket,Key=snv_vcf_key)['Body']) as snvVcfGzFile:
        snvFile = snvVcfGzFile.read()
    files = {  # load complete file contents in bulk
        'snvFile': snvFile,
        'svFile': unify_vcf,
    }

    ga_url = f"{ga_config['server']}/api/CreateSample/"

    participant = dashboard_calls.table_query(all_tables['participant'], 'participant_id', participant_id)[0]

    sample_relation = participant['proband_relationship']
    if sample_relation == "Self":
        sample_relation = "Matched"

    family = dashboard_calls.table_query(all_tables['family'], 'family_id', participant['family_id'])[0]

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
    ga_url = f"{ga_config['server']}/api/CreateCase/"
    family_members = dashboard_calls.table_query(all_tables['participant'], 'family_id', family_id)

    associated_samples = []
    for member in family_members:
        if member.proband_relationship == "Self":
            phenotypes = dashboard_calls.table_query(all_tables['phenotype'], 'participant_id', member['participant_id'])
            phenotype_list = ','.join([p.term_id for p in phenotypes])
            geneyx_case = [{
                "ApiUserKey": ga_config["apiUserKey"],
                "ApiUserID": ga_config["apiUserID"],
                "SerialNumber": member["participant_id"],
                "Description": member["phenotype_description"],
                "Phenotypes": phenotype_list,  # Comma delimited list of HPO IDs from the Phenotype table
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