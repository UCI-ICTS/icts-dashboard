#!/usr/bin/env python3

from datetime import date
import json
import requests

# TODO: Modify this to match new endpoint
def get_all_tables(token):
    """Get tables and return if valid"""
    url = "https://genomics.icts.uci.edu/api/search/get_all_tables/"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, verify=False)
    if response.ok:

        return response.json()


def sanitize_tables(tables):
    """Convert output to a form django loaddata can accept"""
    models = {
            "participants": "metadata.participant",
            "families": "metadata.family",
            "genetic_findings": "metadata.geneticfindings",
            "analytes": "metadata.analyte",
            "phenotypes": "metadata.phenotype",
            "biobank_entries": "metadata.biobank",
            "experiments": "experiments.experiment",
            "experiment_dna_short_read": "experiments.experimentdnashortread",
            "experiment_nanopore": "experiments.experimentnanopore",
            "experiment_pac_bio": "experiments.experimentpacbio",
            "experiment_rna_short_read": "experiments.experimentrnashortread",
            "aligned": "experiments.aligned",
            "aligned_dna_short_read": "experiments.aligneddnashortread",
            "aligned_nanopore": "experiments.alignednanopore",
            "aligned_pac_bio": "experiments.alignedpacbio",
            "aligned_rna_short_read": "experiments.alignedrnashortread",
            }

    remap_pks = {
            "geneticfindings_id": "genetic_findings_id",
            "experimentdnashortread_id": "experiment_dna_short_read_id",
            "experimentnanopore_id": "experiment_nanopore_id",
            "experimentpacbio_id": "experiment_pac_bio_id",
            "experimentrnashortread_id": "experiment_rna_short_read_id",
            "aligneddnashortread_id": "aligned_dna_short_read_id",
            "alignednanopore_id": "aligned_nanopore_id",
            "alignedpacbio_id": "aligned_pac_bio_id",
            "alignedrnashortread_id": "aligned_rna_short_read_id",
            }

    library_prep_type = [
            "stranded poly-A pulldown",
            "stranded total RNA",
            "rRNA depletion",
            "globin depletion",
            "custom",
            ]

    experiment_type = [
            "single-end",
            "paired-end",
            "targeted",
            "untargeted",
            ]

    sub_models = [
        {
          "model": "submodels.reportedrace",
          "pk": "American Indian or Alaska Native",
          "fields": {
            "description": "American Indian or Alaska Native"
          }
        },
        {
          "model": "submodels.reportedrace",
          "pk": "Asian",
          "fields": {
            "description": "Asian"
          }
        },
        {
          "model": "submodels.reportedrace",
          "pk": "Black or African American",
          "fields": {
            "description": "Black or African American"
          }
        },
        {
          "model": "submodels.reportedrace",
          "pk": "Middle Eastern or North African",
          "fields": {
            "description": "Middle Eastern or North African"
          }
        },
        {
          "model": "submodels.reportedrace",
          "pk": "Native Hawaiian or Other Pacific Islander",
          "fields": {
            "description": "Native Hawaiian or Other Pacific Islander"
          }
        },
        {
          "model": "submodels.reportedrace",
          "pk": "White",
          "fields": {
            "description": "White"
          }
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Arnold Palmer Hospital For Children",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Arnold Palmer Hospital for Children, FL",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Ataxia Cohort",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Atrium Health Wake Forest Baptist Hospital",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "CHOC",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "CNH",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Cousin Of Proband",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Deceased Diagnosed Prenatally",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Expecting Twins Both Look Healthy So Far Apr 2024 21 Wks",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "MTC Study",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "MTCStudy",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "NIH Referral",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Orlando Health Arnold Palmer Genetics Referral",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Private Health Management",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Stepfather",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Twin brother",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "UCI",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "UCI referral",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "University of Arizona/Banner",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "University Of Illinois At Chicago",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "UT Aorta Study",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "UTAortaStudy",
          "fields": {}
        },
        {
          "model": "submodels.internalprojectid",
          "pk": "Vanderbilt",
          "fields": {}
        },
        {
          "model": "submodels.twinid",
          "pk": "0",
          "fields": {}
        },
        {
          "model": "submodels.twinid",
          "pk": "PMGRC-494-494-0",
          "fields": {}
        },
        {
          "model": "submodels.twinid",
          "pk": "PMGRC-495-494-3",
          "fields": {}
        },
        {
          "model": "submodels.twinid",
          "pk": "PMGRC-1147-1147-0",
          "fields": {}
        },
        {
          "model": "submodels.twinid",
          "pk": "PMGRC-1148-1147-3",
          "fields": {}
        },
    ]

    sanitized_tables = list()
    for table in tables:
        for entry in tables[table]:  # List of entries per table
            [app, model] = models[table].split('.')
            pk_name = f"{model}_id"
            if pk_name in remap_pks:
                pk_name = remap_pks[pk_name]
            pk_value = entry[pk_name]
            del entry[pk_name]
            if pk_name == "experiment_rna_short_read_id":
                for lpt in entry["library_prep_type"]:
                    lpt_index = entry["library_prep_type"].index(lpt)
                    entry["library_prep_type"][lpt_index] = library_prep_type.index(lpt)
                for et in entry["experiment_type"]:
                    et_index = entry["experiment_type"].index(et)
                    entry["experiment_type"][et_index] = experiment_type.index(et)
            sanitized_tables.append({
                'model': models[table],
                'pk': pk_value,
                'fields': entry,  # after removing the pk
                })
    sanitized_tables.extend(sub_models)
    return sanitized_tables


if __name__ == '__main__':
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY1NjY0NjQ0LCJpYXQiOjE3NjU1NzgyNDQsImp0aSI6IjA5ODZlMDJiMzY3YzQ3MmQ4MzdmZDI2ZTc1ODI3OGQ4IiwidXNlcl9pZCI6OCwiZmlyc3RfbmFtZSI6Ikl2YW4iLCJsYXN0X25hbWUiOiJEZSBEaW9zIiwidXNlcm5hbWUiOiJpZGVkaW9zIiwiZW1haWwiOiJpZGVkaW9zQHVjaS5lZHUiLCJpc19zdGFmZiI6dHJ1ZSwiaXNfc3VwZXJ1c2VyIjp0cnVlfQ.YCJP-U0SzwKkog2NzmlXvx3QcZtFHhTLhgzvXDjaa24"
    tables = get_all_tables(token)
    if tables:
        sanitized_tables = sanitize_tables(tables)
        output = f"{date.today()}_all_tables.json"
        with open(output, 'wt') as f:
            json.dump(sanitized_tables, f, indent=4)
