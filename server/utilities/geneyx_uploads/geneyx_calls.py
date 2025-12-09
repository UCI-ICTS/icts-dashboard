#!/usr/bin/env python3

from io import BytesIO
import os
import requests
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
    if not response.json()['Code'].lower() == 'success':
        print("Error with Geneyx API request Samples")
        sys.exit(1)
    else:

        return response.json()['Data']


def get_ga_cases(ga_config):
    print("\tGetting cases from Geneyx")
    url = f"{ga_config['server']}/api/Cases/"
    response = requests.post(url, data=ga_config)
    if not response.json()['Code'].lower() == 'success':
        print("Error with Geneyx API request Cases")
        sys.exit(1)
    else:

        return response.json()['Data']


def create_roh_variant(line_list):
    # Include ROH bed calls in unify sv
    return '\t'.join([
        line_list[0],  # CHROM
        str(int(line_list[1]) + 1),  # POS; Bed files are 0-based; Vcf files are 1-based
        ".",  # ID
        "N",  # REF
        "<ROH>",  # ALT
        ".",  # QUAL
        "PASS",  # FILTER
        ';'.join([  # INFO
            f"END={str(int(line_list[2]))}",  # Bed end pos
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
                    if not valid_variant(line_list):
                        continue
                    unified_variants.append(line)
    return '\n'.join(sv_vcf_header + coordinate_sort_variants(unified_variants))


def sample_uploader(ga_config, s3_client, lrs_manifest_row, all_tables, dryrun):
    """
    Upload SNV and SV VCFs to Geneyx
    """
    url_expiration = 604800  # 7 days
    encoding = "utf-8"

    participant_id = lrs_manifest_row['current_id']
    print(f"\tUploading {participant_id} VCFs to Geneyx")
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
    unify_sv_basename = f"{participant_id}.GRCh38.geneyx.unify.sv.vcf.gz"

    snv_vcf = aws_calls.get_snv_vcf(s3_client, lrs_manifest_row['snv_vcf'])

    sv_vcfs = aws_calls.find_sv_vcfs(s3_client, analysis_out, ambry_id)
    unify_sv_vcf = pacbio_unify_sv(sv_vcfs)

    files = {  # load complete file contents in bulk
        'snvFile': (
            snv_basename,
            BytesIO(snv_vcf.encode(encoding)),
            'text/plain'
        ),
        'svFile': (
            unify_sv_basename,
            BytesIO(unify_sv_vcf.encode(encoding)),
            'text/plain'
        ),
    }

    ga_url = f"{ga_config['server']}/api/CreateSample/"

    participant = dashboard_calls.table_query(all_tables['metadata']['participant'], 'participant_id', participant_id)[0]

    sample_relation = participant['proband_relationship']
    if sample_relation == "Self":
        sample_relation = "Matched"

    family = dashboard_calls.table_query(all_tables['metadata']['family'], 'family_id', participant['family_id'])[0]

    geneyx_sample_upload = {  # sample POST request template with default values
        "ApiUserKey": ga_config["apiUserKey"],
        "ApiUserID": ga_config["apiUserId"],
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
        "StructFile": unify_sv_basename,  # SV VCF basename. Must be Unify SV VCF or Sawfish VCF
        "SubjectId": participant_id,
        "SubjectGender": participant["sex"],
        "SubjectConsanguinity": family["consanguinity"],
        "SubjectPopulationType": participant["reported_race"][0],  # only provide the first race if multiple are present
        "SubjectPaternalAncestry": participant["paternal_id"],
        "SubjectMaternalAncestry": participant["maternal_id"],
        "SubjectFamilyHistory": family["family_history_detail"],
        "SubjectHasBioSample": True,
        "SubjectUseConsentPersonal": True,  # GRU?
        "SubjectUSeConsentClinical": False,
        "SkipAnnotation": False,
    }
    if not dryrun:
        response = requests.post(ga_url, data=geneyx_sample_upload, files=files)
        import pdb; pdb.set_trace()
        if response.json()['Code'].lower() != "success":
            print(f"\t{response.json()}")
        else:
            print(f"\tCompleted upload of {participant_id} VCFs to Geneyx")
    else:
        print(f"\tCompleted mock upload of {participant_id} VCFs to Geneyx")


def case_maker(ga_config, ga_samples, ga_cases, family_members, all_tables, dryrun):
    """
    Create Geneyx cases
    """
    ga_url = f"{ga_config['server']}/api/CreateCase/"

    associated_samples = []
    for member in family_members:
        if member in ga_samples:  # Only include previously uploaded samples
            if member["proband_relationship"] == "Self":
                print(f"\tCreating Geneyx case for {member['participant_id']}")
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
    if not dryrun:
        response = requests.post(ga_url, data=geneyx_case)

        if response.json()['Code'].lower() != "success":
            print(f"\t{response.json()}")
        else:
            print(f"\tCompleted creating Geneyx case for {member['participant_id']}")
    else:
        print(f"\tCompleted creating mock Geneyx case for {member['participant_id']}")