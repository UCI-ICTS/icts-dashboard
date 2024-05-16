#!/usr/bin/env python3

"""Metadata Selectors
"""

from metadata.models import (
    InternalProjectId,
    PmidId,
    Family,
    TwinId
    )

def get_sub_models(datum: dict) -> dict:
    """
    Selector to get or create objects that are part of the participant sheet.
    Updates the datum dictionary in place with primary keys of the related objects.

    Args:
    datum (dict): A dictionary containing the fields 'internal_project_id', 
                  'prior_testing', and 'pmid_id' as lists.

    Returns:
    dict: The updated dictionary with lists of primary keys for related objects.
    """

    # Define a generic function to handle the get_or_create logic
    def get_or_create_objects(model, field_name, items):
        primary_keys = []
        obj, created = model.objects.get_or_create(**{field_name: items})
        # for item in items:
        #     obj, created = model.objects.get_or_create(**{field_name: items})
        #     primary_keys.append(obj.pk)
        
        return obj.pk

    # Mapping of datum keys to model and field names
    mapping = {
        "family_id": (Family, "family_id"),
        "internal_project_id": (InternalProjectId, "internal_project_id"),
        "pmid_id": (PmidId, "pmid_id"),
        "twin_id": (TwinId, "twin_id")
    }

    # Process each key using the mapping
    
    for key, (model, field_name) in mapping.items():
        if key == "twin_id" or key == "pmid_id":
            objects = []
            for item in datum[key]:
                obj, created = model.objects.get_or_create(**{field_name: datum[key]})
                objects.append(obj)
            datum[key] = objects
        else:
            obj, created = model.objects.get_or_create(**{field_name: datum[key]})
        datum[key] = obj

    return datum
