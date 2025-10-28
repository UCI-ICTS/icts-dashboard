#!/usr/bin/env python
# hpo/selectors.py

from typing import List, Dict
from hpo.models import HPOTerm

def get_hpo_term_by_id(hpo_ids: List[str]) -> List[Dict]:
    """
    Retrieve a list of HPO terms by their ID (e.g., "HP:0001251").
    Returns a list of dict with label, definition, synonyms, release, etc.
    """
    hpo_list = [hpo_id.strip() for hpo_id in hpo_ids if hpo_id and hpo_id.strip()]
    if not hpo_list:
        return []
    
    terms = HPOTerm.objects.filter(hpo_id__in=hpo_list)
    by_id = {term.hpo_id: term for term in terms}
    output = []
    for hpo_id in hpo_list:
        term = by_id.get(hpo_id)
        if not term:
            output.append({"hpo_id": hpo_id, "error": "not found"})
        else:
            output.append({
                "hpo_id": term.hpo_id,
                "label": term.label,
                "definition": term.definition,
                "synonyms": term.synonyms,
                "release": term.release,
                "deprecated": term.deprecated,
            })
    
    return output
