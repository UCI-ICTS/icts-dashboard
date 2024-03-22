#!/usr/bin/env python3

"""Metadata Selectors
"""

from metadata.models import (
    InternalProjectId,
    PriorTesting,
    PmidId
    )

def get_sub_models(datum:dict)-> dict:
    """Get Submodles
    
    Selector to get or create objects that are part of the participant sheet
    """ 

    pmid_ids, prior_testings, internal_projects, pmid_id = [], [], []

    for item in datum['internal_project_id']:
        project_id, created = InternalProjectId.objects.get_or_create(
            internal_project_id=item
        )
        internal_projects.append(project_id.pk)

    for item in datum['prior_testing']:
        prior_testing, created = PriorTesting.objects.get_or_create(
            prior_testing=item
        )
        prior_testings.append(prior_testing.pk)
    
    for item in datum['pmid_id']:
        pmid_id, created = PriorTesting.objects.get_or_create(
            pmid_id=item
        )
        pmid_ids.append(pmid_id.pk)

    datum['internal_project_id'] = internal_projects
    datum['prior_testing'] = prior_testing
    datum['pmid_id'] = pmid_ids
    return datum
    