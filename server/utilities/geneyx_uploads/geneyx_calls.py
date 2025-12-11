#!/usr/bin/env python3

from Bio import bgzf
import gzip
from io import BytesIO
import json
import os
import requests
import aws_calls


def get_ga_samples(ga_config):
    print("\tGetting samples from Geneyx")
    url = f"{ga_config['server']}/api/Samples"
    response = requests.post(url, data=ga_config)
    if response.json()['Code'] == 'success':\
        return response.json()['Data']
    else:
        print("\tError with Geneyx API request Samples")
        return None


def get_ga_cases(ga_config):
    print("\tGetting cases from Geneyx")
    url = f"{ga_config['server']}/api/cases"
    response = requests.post(url, data=ga_config)
    if response.json()['Code'] == 'success':
        return response.json()['Data']
    else:
        print("\tError with Geneyx API request cases")
        return None


def get_ga_case(ga_config, participant_id):
    print(f"\tGetting case for {participant_id} from Geneyx")
    url = f"{ga_config['server']}/api/Case"
    ga_config["CaseSn"] = participant_id
    response = requests.post(url, data=ga_config)
    if response.json()['Code'] == 'success':
        return response.json()['Data']
    else:
        print(f"\tError with Geneyx API request case for {participant_id}")
        return None


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
    unsorted_variants = []
    for v in variants:
        unsorted_variants.append(v.split('\t'))
    sorted_by_pos = sorted(unsorted_variants, key=lambda x: int(x[1]))
    sorted_by_chrom = sorted(sorted_by_pos, key=lambda x: x[0])
    sorted_variants = list(map(lambda x: '\t'.join(x), sorted_by_chrom))

    return sorted_variants


def pacbio_unify_sv(sv_vcfs):
    """
    Docstring for pacbio_unify_sv

    :param sv_vcfs: Description
    """
    print(f"\tUnifying SVs")
    sv_keys = ["sv_vcf", "cnv", "trgt"]  # skip roh for pacbio
    sv_vcf_header = []
    unified_variants = []
    for key in sv_keys:
        if key not in sv_vcfs:
            print(f"\tCannot unify vcfs, missing {key} VCF")
            return None
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
    return '\n'.join(sv_vcf_header + coordinate_sort_variants(unified_variants)) + '\n'


def sample_uploader(ga_config, s3_client, participant, family, dryrun):
    """
    Upload SNV and SV VCFs to Geneyx
    """
    url_expiration = 604800  # 7 days
    encoding = 'utf-8'

    lrs_manifest_row = participant['manifest']
    participant_id = participant['participant_id']
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

    file_out = f"geneyx_cache/sample_uploader/{participant_id}/"
    if not os.path.exists(file_out):
        os.makedirs(file_out)

    snv_basename = snv_vcf_uri.split('/')[-1]  # If there are multiple, only process the first
    snv_vcf_cache = f"{file_out}/{snv_basename}"
    if os.path.exists(snv_vcf_cache):
        with open(snv_vcf_cache, 'rb') as f:
            snv_vcf_binary = f.read()
    else:
        snv_vcf_binary = aws_calls.get_snv_vcf(s3_client, snv_vcf_uri)
        with open(f"{file_out}/{snv_basename}", 'wb') as f:
            f.write(snv_vcf_binary)

    unify_sv_basename = f"{participant_id}.GRCh38.geneyx.unify.sv.vcf"
    unify_sv_cache = f"{file_out}/{unify_sv_basename}.gz"
    if os.path.exists(unify_sv_cache):
        with gzip.open(unify_sv_cache, 'rt') as f:
            unify_sv_vcf = f.read()
    else:
        sv_vcfs = aws_calls.find_sv_vcfs(s3_client, analysis_out, ambry_id)
        unify_sv_vcf = pacbio_unify_sv(sv_vcfs)
        with bgzf.open(unify_sv_cache, 'wt') as f:
            f.write(unify_sv_vcf)

    files = {  # load complete file contents in bulk
        'snvFile': (
            snv_basename,
            BytesIO(snv_vcf_binary)
        ),
        'svFile': (
            unify_sv_basename,
            BytesIO(bytes(unify_sv_vcf, encoding=encoding))
        ),
    }

    ga_url = f"{ga_config['server']}/api/createSample"

    sample_relation = participant['proband_relationship']
    if sample_relation == "Self":
        sample_relation = "Matched"
    sample_notes = '|'.join(participant['phenotype_description'])
    population_type = ""
    if participant["reported_race"] and participant["reported_ethnicity"]:
        population_type = '|'.join(participant["reported_race"] + [participant["reported_ethnicity"]])

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
    if population_type:
        geneyx_sample["SubjectPopulationType"] = population_type,

    # Save finalized POST request to file
    with open(f"{file_out}/{participant_id}.json", 'wt') as f:
        json.dump(geneyx_sample, f)

    # Send POST request
    if not dryrun:
        print(f"\tGeneyx Request POST CreateSample {participant_id}")
        response = requests.post(ga_url, data=geneyx_sample, files=files)
        if response.json()['Code'] == 'success':
            print(f"\t{response.json()}")
        else:
            print(f"\tCompleted upload of {participant_id} VCFs to Geneyx")
    else:
        print(f"\tCompleted mock upload of {participant_id} VCFs to Geneyx")


def case_maker(ga_config, ga_samples, family_members, dryrun):
    """
    Create Geneyx cases
    """
    ga_url = f"{ga_config['server']}/api/CreateCase"

    associated_samples = []
    for member in family_members:
        participant = family_members[member]
        if member in ga_samples:  # Only include previously uploaded samples
            if participant["proband_relationship"] == "Self":
                proband_id = member
                print(f"\tCreating Geneyx case for proband {member}")
                phenotypes = family_members[member]['phenotypes']
                phenotype_list = ','.join([p["term_id"] for p in phenotypes])
                geneyx_case = {
                    "ApiUserKey": ga_config["apiUserKey"],
                    "ApiUserID": ga_config["apiUserId"],
                    "SerialNumber": proband_id,
                    "Description": '|'.join(participant["phenotype_description"]),
                    "Phenotypes": phenotype_list,  # Comma delimited list of HPO IDs from the Phenotype table
                    "ProtocolId": "LR_seq",  # Currently the only Geneyx protocol for Revio
                    "SubjectId": proband_id,
                    "ProbandSampleId": proband_id,
                }
            else:  # Only add associated samples that exist in Geneyx
                associated_samples.append({
                    "SampleId": member,
                    "Relation": participant["proband_relationship"],
                    "Affected": participant["affected_status"],
                })
        else:
            return None
    geneyx_case["AssociatedSamples"] = associated_samples  # Add associated samples
    file_out = f"geneyx_cache/case_maker/{proband_id}/"
    if not os.path.exists(file_out):
        os.makedirs(file_out)
    with open(f"{file_out}/{proband_id}.json", 'wt') as f:
        json.dump(geneyx_case, f)
    if not dryrun:
        print(f"\tSending POST request for {proband_id}")
        response = requests.post(ga_url, json=geneyx_case)

        if response.json()['Code'] == 'success':
            print(f"\tCompleted creating Geneyx case for {proband_id}")
        else:
            print(f"{response.json()}")
    else:
        print(f"\tCompleted creating mock Geneyx case for {proband_id}")


def update_temp_links(s3_client, ga_config, lrs_manifest_csv, dryrun):
    """
    Update temporary BAM, BAI, and methylation BED file links
    """
    ga_url = f"{ga_config['server']}/api/updateSample"
    url_expiration = 604800  # 7 days

    for row in lrs_manifest_csv:
        participant_id = row['current_id']
        ambry_id = row['ambry_id']
        snv_vcf_uri = row['snv_vcf'].split(';')[0]
        analysis_out = snv_vcf_uri[0:snv_vcf_uri.index('out')]
        bam_uri = row['aligned_bam'].split(';')[0]  # Only process the first bam
        bam_url, bai_url = aws_calls.get_bam_bai_temp_urls(s3_client, analysis_out, bam_uri, url_expiration)
        methyl_bed_url = aws_calls.get_cpg_bed_temp_url(s3_client, analysis_out, ambry_id, url_expiration)
        update_sample = {
            "ApiUserKey": ga_config["apiUserKey"],
            "ApiUserID": ga_config["apiUserId"],
            "SerialNumber": participant_id,
            "BamUrl": bam_url,
            "MethylationUrl": methyl_bed_url,
        }
        file_out = f"geneyx_cache/update_sample/{participant_id}/"
        if not os.path.exists(file_out):
            os.makedirs(file_out)
        with open(f"{file_out}/{participant_id}.json", 'wt') as f:
            json.dump(update_sample, f)
        if not dryrun:
            print(f"\tSending POST request for {participant_id}")
            response = requests.post(ga_url, data=update_sample)

            if response.json()['Code'] == 'success':
                print(f"\tCompleted update of {participant_id} BAM links to Geneyx")
            else:
                print(f"\t{response.json()}")
        else:
            print(f"\tCompleted mock update of {participant_id} BAM links to Geneyx")
