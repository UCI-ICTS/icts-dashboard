#!/usr/bin/env python3

import bgzip
from io import BytesIO
import json
import os
import requests
import subprocess
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
    print("\tLoading geneyx config")
    if os.path.isfile('ga.config.yml'):
        with open('ga.config.yml') as f:
            return yaml.safe_load(f)


def get_ga_samples(ga_config):
    print("\tGetting samples from Geneyx")
    url = f"{ga_config['server']}/api/Samples/"
    response = requests.post(url, data=ga_config)
    if not response.ok:
        print("Error with Geneyx API request Samples")
        sys.exit(1)
    else:

        return response.json()['Data']


def get_ga_cases(ga_config):
    print("\tGetting cases from Geneyx")
    url = f"{ga_config['server']}/api/Cases/"
    response = requests.post(url, data=ga_config)
    if not response.ok:
        print("Error with Geneyx API request Cases")
        sys.exit(1)
    else:

        return response.json()['Data']


def create_roh_variant(line_list):
    # Include ROH bed calls in unify sv
    return '\t'.join([
        line_list[0],  # CHROM
        str(int(line_list[1])+1),  # POS; Bed files are 0-based; Vcf files are 1-based
        ".",  # ID
        "N",  # REF
        "<ROH>",  # ALT
        ".",  # QUAL
        "PASS",  # FILTER
        ';'.join([  # INFO
            f"END={line_list[2]}",  # Bed end pos
            f"SVTYPE=ROH",
            f"ROH_SCORE={line_list[3]}"  # Bed score
            ]),
        "GT",  # FORMAT
        "1/1"  # _
    ])


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
    for chrom in sorted(unsorted_variants.keys()):
        for pos in sorted(unsorted_variants[chrom].keys()):
            sorted_variants.append('\t'.join([chrom, pos] + unsorted_variants[chrom][pos]))
    return sorted_variants


def pacbio_unify_sv(sv_vcfs):
    """
    Docstring for pacbio_unify_sv

    :param sv_vcfs: Description
    """
    print(f"\tUnifying SVs")
    sv_keys = ["roh", "sv_vcf", "trgt", "cnv"]
    sv_vcf_header = []
    unified_variants = []
    for key in sv_keys:
        if key not in sv_vcfs:
            print(f"Cannot unify vcfs, missing {key} VCF")
            sys.exit(1)
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
                    #if not valid_variant(line_list):
                    #    continue
                    unified_variants.append(line)
    return '\n'.join(sv_vcf_header + coordinate_sort_variants(unified_variants))


def sample_uploader(ga_config, s3_client, lrs_manifest_row, all_tables, dryrun):
    """
    Upload SNV and SV VCFs to Geneyx
    """
    url_expiration = 604800  # 7 days
    encoding = 'utf-8'

    participant_id = lrs_manifest_row['current_id']
    print(f"\tStarting Geneyx VCF uploader for {participant_id}")
    ambry_id = lrs_manifest_row['ambry_id']
    snv_vcf_uri = lrs_manifest_row['snv_vcf'].split(';')[0]
    analysis_out = snv_vcf_uri[0:snv_vcf_uri.index('out')]

    specimen_map = {
        "D": "Blood",
        "OG": "Saliva",
        "SC": "Buccal",
        "SG": "Buccal",
        "X": "Other"
    }
    specimen_type = specimen_map[lrs_manifest_row['UCI_ID2'].split('-')[-2]]

    # Get AWS objects
    bam_uri = lrs_manifest_row['aligned_bam'].split(';')[0]  # Only process the first bam
    bam_url, bai_url = aws_calls.get_bam_bai_temp_urls(s3_client, analysis_out, bam_uri, url_expiration)
    methyl_bed_url = aws_calls.get_cpg_bed_temp_url(s3_client, analysis_out, ambry_id, url_expiration)

    file_out = f"sample_uploader/{participant_id}/"
    if not os.path.exists(file_out):
        os.makedirs(file_out)

    print(f"\tDownloading SNV VCF")
    snv_vcf_binary = aws_calls.get_snv_vcf(s3_client, snv_vcf_uri)
    snv_basename = snv_vcf_uri.split('/')[-1]  # If there are multiple, only process the first
    with open(f"{file_out}/{snv_basename}", 'wb') as raw:
        raw.write(snv_vcf_binary)

    print(f"\tDownloading SV VCFs")
    sv_vcfs = aws_calls.find_sv_vcfs(s3_client, analysis_out, ambry_id)
    print(f"\tUnifying SV VCFs")
    unify_sv_vcf = pacbio_unify_sv(sv_vcfs)
    unify_sv_basename = f"{participant_id}.GRCh38.geneyx.unify.sv.vcf"
    with open(f"{file_out}/{unify_sv_basename}.gz", 'wb') as raw:
        with bgzip.BGZipWriter(raw) as fh:
            fh.write(bytes(unify_sv_vcf, encoding=encoding))

    files = {  # load complete file contents in bulk
        'snvFile': (
            snv_basename,
            BytesIO(snv_vcf_binary)
        ),
        'svFile': (
            unify_sv_basename,
            BytesIO(unify_sv_vcf.encode(encoding))
        ),
    }

    ga_url = f"{ga_config['server']}/api/createSample"

    participant = dashboard_calls.table_query(all_tables['metadata']['participant'], 'participant_id', participant_id)[0]
    sample_relation = participant['proband_relationship']
    if sample_relation == "Self":
        sample_relation = "Matched"
    sample_notes = '|'.join(participant['phenotype_description'])
    population_type = '|'.join(participant["reported_race"] + participant["reported_ethnicity"])

    family = dashboard_calls.table_query(all_tables['metadata']['family'], 'family_id', participant['family_id'])[0]
    subject_consanguinity = {
        "None suspected": "Non-Consanguineous",
        "Suspected": "Consanguineous",
        "Present": "Consanguineous",
        "Unknown": "Unknown",
    }

    geneyx_sample = {  # sample POST request template
        "ApiUserKey": ga_config["apiUserKey"],
        "ApiUserID": ga_config["apiUserId"],
        "SampleSerialNumber": participant_id,  # participant_id
        "SampleSource": specimen_type,  # biobank or analyte source
        "SampleSequenceMachineId": "REVIO",
        "SampleEnrichmentKitId": "Long Read Sequencing no CADD",  # Current default smart filter set
        "SampleTarget": "WholeGenomeLongRead",
        "SampleGenomeBuild": "hg38",
        "SampleRelation": sample_relation,
        "SampleNotes": sample_notes,
        "ExcludeFromLAF": False,
        "BamUrl": bam_url,
        "methylationUrl": methyl_bed_url,
        "SnvFile": snv_basename,  # SNV VCF basename
        "StructFile": unify_sv_basename,  # SV VCF basename. Must be Unify SV VCF or Sawfish VCF
        "SubjectId": participant_id,
        "SubjectPopulationType": population_type,
        "SubjectConsanguinity": subject_consanguinity[family["consanguinity"]],
        "SubjectHasBioSample": True,
        "SubjectUseConsentPersonal": True,  # GRU?
        "SubjectUSeConsentClinical": False,
        "SkipAnnotation": False,
    }

    # Optional fields that should only be set if they have allowed values
    if participant["sex"] != "Unknown":
        geneyx_sample['SubjectGender'] = participant["sex"][0],  # First character of sex only
    if participant["paternal_id"] != "0":
        geneyx_sample["SubjectPaternalAncestry"] = participant["paternal_id"]
    if participant["maternal_id"] != "0":
        geneyx_sample["SubjectMaternalAncestry"] = participant["maternal_id"]
    if family["family_history_detail"]:
        geneyx_sample["SubjectFamilyHistory"] = family["family_history_detail"]

    # Save finalized POST request to file
    with open(f"{file_out}/{participant_id}.json", 'wt') as f:
        json.dump(geneyx_sample, f)

    # Send POST request
    if not dryrun:
        print(f"\tGeneyx Request POST CreateSample {participant_id}")
        response = requests.post(ga_url, data=geneyx_sample, files=files)
        if response.ok:
            print(f"\t{response.json()}")
        else:
            print(f"\tCompleted upload of {participant_id} VCFs to Geneyx")
    else:
        print(f"\tCompleted mock upload of {participant_id} VCFs to Geneyx")



def case_maker(ga_config, ga_samples, ga_cases, family_members, all_tables, dryrun):
    """
    Create Geneyx cases
    """
    ga_url = f"{ga_config['server']}/api/CreateCase"

    associated_samples = []
    for member in family_members:
        if member in ga_samples:  # Only include previously uploaded samples
            if member["proband_relationship"] == "Self":
                proband_id = member["participant_id"]
                print(f"\tCreating Geneyx case for proband {member['participant_id']}")
                phenotypes = dashboard_calls.table_query(all_tables['metadata']['phenotype'], 'participant_id', member['participant_id'])
                phenotype_list = ','.join([p["term_id"] for p in phenotypes])
                geneyx_case = {
                    "ApiUserKey": ga_config["apiUserKey"],
                    "ApiUserID": ga_config["apiUserId"],
                    "SerialNumber": member["participant_id"],
                    "Description": member["phenotype_description"],
                    "Phenotypes": phenotype_list,  # Comma delimited list of HPO IDs from the Phenotype table
                    "ProtocolId": "LR_seq",  # Currently the only Geneyx protocol for Revio
                    "SubjectId": member["participant_id"],
                    "ProbandSampleId": member["participant_id"],
                }
            else:  # Only add associated samples that exist in Geneyx
                associated_samples.append({
                    "SampleId": member["participant_id"],
                    "Relation": member["proband_relationship"],
                    "Affected": member["affected_status"],
                })
    geneyx_case["AssociatedSamples"] = associated_samples  # Add associated samples
    file_out = f"case_maker/{proband_id}/"
    if not os.path.exists(file_out):
        os.makedirs(file_out)
    with open(f"{file_out}/{proband_id}.json", 'wt') as f:
        json.dump(geneyx_case, f)
    if not dryrun:
        print(f"\tSending POST request for {proband_id}")
        response = requests.post(ga_url, data=geneyx_case)

        if response.json()['Code'].lower() != "success":
            print(f"\t{response.json()}")
        else:
            print(f"\tCompleted creating Geneyx case for {member['participant_id']}")
    else:
        print(f"\tCompleted creating mock Geneyx case for {member['participant_id']}")


if __name__ == '__main__':
    pacbio_unify_sv()  # Troubleshoot discrepancies of unify_sv