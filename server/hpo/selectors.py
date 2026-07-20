#!/usr/bin/env python
# hpo/selectors.py

from collections.abc import Iterable
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, Q, QuerySet
from django.db.models.functions import Greatest
from typing import List, Dict
from hpo.models import HPOTerm, HPOEdge
from metadata.models import Phenotype, Participant

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


def lookup_hpo_terms(search_text: str, limit: int = 25) -> QuerySet:
    """
    Return active HPO terms ranked by similarity to the supplied search text.

    Exact HPO-ID matches are supported, while label and synonym matches are
    ranked using PostgreSQL trigram similarity.
    """
    search_text = search_text.strip()

    if not search_text:
        return HPOTerm.objects.none()

    if search_text.upper().startswith("HP:"):
        return HPOTerm.objects.filter(
            hpo_id__iexact=search_text,
            deprecated=False,
        )

    return (
        HPOTerm.objects
        .filter(deprecated=False)
        .annotate(
            label_score=TrigramSimilarity(
                "label_normalized",
                search_text.lower(),
            ),
            synonym_score=TrigramSimilarity(
                "synonyms_concat",
                search_text,
            ),
        )
        .annotate(
            similarity=Greatest(
                F("label_score"),
                F("synonym_score"),
            )
        )
        .filter(
            Q(label__icontains=search_text)
            | Q(synonyms_concat__icontains=search_text)
            | Q(similarity__gte=0.15)
        )
        .order_by("-similarity", "label")[:limit]
    )


def get_hpo_descendant_ids(
    root_ids: list[str],
    include_roots: bool = True,
) -> set[str]:
    """
    Return all HPO term IDs descended from one or more root HPO terms.

    The traversal continues until no additional child terms are found.

    Args:
        root_ids:
            HPO term IDs to use as the starting points.

        include_roots:
            Include the supplied root IDs in the returned set.

    Returns:
        A set containing the descendant HPO term IDs.
    """
    roots = set(root_ids)
    descendants = set(roots) if include_roots else set()
    current_level = set(roots)

    while current_level:
        child_ids = set(
            HPOEdge.objects.filter(
                parent_id__in=current_level
            ).values_list(
                "child_id",
                flat=True,
            )
        )

        new_child_ids = child_ids - descendants

        if not new_child_ids:
            break

        descendants.update(new_child_ids)
        current_level = new_child_ids

    return descendants


def get_participants_by_hpo_terms(
    hpo_term_ids: Iterable[str],
    *,
    present_only: bool = True,
) -> QuerySet[Participant]:
    """
    Return distinct participants with phenotype records matching any of the
    supplied HPO term IDs.

    Args:
        hpo_term_ids:
            One or more HPO identifiers, such as ``HP:0001251``.

        present_only:
            When True, only phenotype records whose presence is ``Present``
            are included.

    Returns:
        A distinct Participant queryset. Returning a queryset allows callers
        to add further filters for age, solve status, enrollment status, or
        related analysis records.

    Raises:
        ValueError:
            If no nonblank HPO term IDs are supplied.
    """
    term_ids = {
        str(term_id).strip()
        for term_id in hpo_term_ids
        if term_id and str(term_id).strip()
    }

    if not term_ids:
        raise ValueError("At least one HPO term ID is required.")

    phenotype_filters = {
        "term_id__in": term_ids,
    }

    if present_only:
        phenotype_filters["presence"] = "Present"

    participant_ids = (
        Phenotype.objects
        .filter(**phenotype_filters)
        .values_list("participant_id_id", flat=True)
        .distinct()
    )

    return (
        Participant.objects
        .filter(participant_id__in=participant_ids)
        .distinct()
    )


def phenotype_cohort_summary(participants: QuerySet) -> dict:
    """
    """
    return {
        "total_enrolled": participants.count(),
        "adult_at_enrollment": participants.filter(
            age_at_enrollment__gte=18
        ).count(),
        "solved": participants.filter(
            solve_status="Solved"
        ).count(),
        "analyzed": "See LR-GS data sheet",
    }


def resolve_hpo_inputs(
    inputs: Iterable[str],
) -> tuple[set[str], list[dict]]:
    """
    Resolve a mixture of HPO IDs and text labels into HPO term IDs.

    Exact HPO IDs are resolved directly. Text inputs use the highest-ranked
    result returned by ``lookup_hpo_terms``.

    Returns:
        A tuple containing:

        - the set of resolved HPO IDs;
        - resolution details for each submitted input.
    """
    resolved_ids = set()
    resolutions = []

    for raw_value in inputs:
        value = str(raw_value).strip()

        if not value:
            continue

        if value.upper().startswith("HP:"):
            term = (
                HPOTerm.objects
                .filter(
                    hpo_id__iexact=value,
                    deprecated=False,
                )
                .first()
            )
        else:
            term = lookup_hpo_terms(value, limit=1).first()

        if term is None:
            resolutions.append({
                "input": value,
                "resolved": False,
                "hpo_id": None,
                "label": None,
            })
            continue

        resolved_ids.add(term.hpo_id)

        resolutions.append({
            "input": value,
            "resolved": True,
            "hpo_id": term.hpo_id,
            "label": term.label,
        })

    return resolved_ids, resolutions