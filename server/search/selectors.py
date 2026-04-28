#!/usr/bin/env python
# search/selectors.py

import json
import time
import zipfile
from io import BytesIO
import requests
import importlib
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder

from config.selectors import (
    generate_tsv,
    generate_zip,
)

from collections import Counter
from django.apps import apps
from django.db.models import Q, Count
from itertools import chain, groupby

from config.selectors import get_visible_objects

from metadata.models import (
    Analyte,
    Biobank,
    Family,
    GeneticFindings,
    Participant,
    Phenotype,
)

from metadata.services import (
    AnalyteSerializer,
    BiobankSerializer,
    FamilySerializer,
    GeneticFindingsInputSerializer,
    GeneticFindingsOutputSerializer,
    ParticipantOutputSerializer,
    PhenotypeSerializer,
)

from experiments.models import (
    Aligned,
    AlignedDNAShortRead,
    AlignedNanopore,
    AlignedPacBio,
    AlignedRNAShortRead,
    Experiment,
    ExperimentDNAShortRead,
    ExperimentPacBio,
    ExperimentNanopore,
    ExperimentRNAShortRead,
)

from experiments.services import (
    AlignedSerializer,
    AlignedDNAShortReadSerializer,
    AlignedNanoporeSerializer,
    AlignedPacBioSerializer,
    AlignedRNASerializer,
    ExperimentSerializer,
    ExperimentDNAOutputSerializer,
    ExperimentNanoporeSerializer,
    ExperimentPacBioSerializer,
    ExperimentRNAOutputSerializer,
)

from s3.services import fetch_manifest

serializer_mapping ={
    "alignedpacbio": "AlignedPacBioSerializer",
    "experiment": "ExperimentSerializer",
    "aligned": "AlignedSerializer",
    "experimentdnashortread": "ExperimentShortReadSerializer",
    "aligneddnashortread": "AlignedDNAShortReadSerializer",
    "experimentrnashortread": "ExperimentRnaOPutputSerializer",
    "alignedrnashortread": "AlignedRnaSerializer",
    "experimentnanopore":"ExperimentNanoporeSerializer",
    "alignednanopore":"AlignedNanoporeSerializer",
    "experimentpacbio" : "ExperimentPacBioSerializer",
    'family':"FamilySerializer",
    'participant':"ParticipantInputSerializer",
    'phenotype': "PhenotypeSerializer",
    'geneticfindings' : "GeneticFindingsSerializer",
    'analyte': "AnalyteSerializer",
    'biobankentry': "BiobankSerializer",
    'experimentstage': "ExperimentStageSerializer",
}

table_serializers = {
    # Metadata Tables
    "participant": {
        "model": Participant,
        "output_serializer": ParticipantOutputSerializer,
        "queryset": lambda: Participant.objects.all()
            .select_related("family_id")
            .prefetch_related(
                "internal_project_id",
                "pmid_id",
                "twin_id",
                "reported_race",
            ),
    },
    "family": {
        "model": Family,
        "input_serializer": FamilySerializer,
        "output_serializer": FamilySerializer,
    },
    "genetic_findings": {
        "model": GeneticFindings,
        "input_serializer": GeneticFindingsInputSerializer,
        "output_serializer": GeneticFindingsOutputSerializer,
    },
    "analyte": {
        "model": Analyte,
        "input_serializer": AnalyteSerializer,
        "output_serializer": AnalyteSerializer,
    },
    "phenotype": {
        "model": Phenotype,
        "input_serializer": PhenotypeSerializer,
        "output_serializer": PhenotypeSerializer,
        "queryset": lambda: Phenotype.objects.all()
            .select_related("participant_id")
    },
    "biobank": {
        "model": Biobank,
        "input_serializer": BiobankSerializer,
        "output_serializer": BiobankSerializer,
        "queryset": lambda: Biobank.objects.all()
            .select_related("participant_id")
            .prefetch_related("child_analytes", "experiments", "alignments"),
    },
    # Experiment Tables
    "experiment": {
        "model": Experiment,
        "input_serializer": ExperimentSerializer,
        "output_serializer": ExperimentSerializer,
    },
    "experiment_dna_short_read": {
        "model": ExperimentDNAShortRead,
        "output_serializer": ExperimentDNAOutputSerializer,
    },
    "experiment_nanopore": {
        "model": ExperimentNanopore,
        "input_serializer": ExperimentNanoporeSerializer,
        "output_serializer": ExperimentNanoporeSerializer,
    },
    "experiment_pac_bio": {
        "model": ExperimentPacBio,
        "input_serializer": ExperimentPacBioSerializer,
        "output_serializer": ExperimentPacBioSerializer,
    },
    "experiment_rna_short_read": {
        "model": ExperimentRNAShortRead,
        "output_serializer": ExperimentRNAOutputSerializer,
    },
    "aligned_dna_short_read": {
        "model": AlignedDNAShortRead,
        "input_serializer": AlignedDNAShortReadSerializer,
        "output_serializer": AlignedDNAShortReadSerializer,
    },
    # Aligned tables
    "aligned": {
        "model": Aligned, 
        "input_serializer": AlignedSerializer,
        "output_serializer": AlignedSerializer,
    },
    "aligned_nanopore": {
        "model": AlignedNanopore,
        "input_serializer": AlignedNanoporeSerializer,
        "output_serializer": AlignedNanoporeSerializer,
    },
    "aligned_pac_bio": {
        "model": AlignedPacBio,
        "input_serializer": AlignedPacBioSerializer,
        "output_serializer": AlignedPacBioSerializer,
    },
    "aligned_rna_short_read": {
        "model": AlignedRNAShortRead,
        "input_serializer": AlignedRNASerializer,
        "output_serializer": AlignedRNASerializer,
    },
}


def serialize_table(name, queryset, serializer_class): 
    start = time.perf_counter()
    count = queryset.count()
    serialized = serializer_class(queryset, many=True)
    data = serialized.data

    size_bytes = len(json.dumps(data, cls=DjangoJSONEncoder).encode("utf-8"))
    elapsed = time.perf_counter() - start
    return {
        "name": name,
        "count": count,
        "size_mb": round(size_bytes / 1024 / 1024, 2),
        "seconds": elapsed,
        "data": data,
    }


def get_all_tables():
    manifest = []
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for name, values in table_serializers.items():
            try:
                queryset_factory = values.get("queryset")

                if queryset_factory:
                    queryset = queryset_factory()
                else:
                    queryset = values["model"].objects.all()

                result = serialize_table(
                    name,
                    queryset=queryset,
                    serializer_class=values["output_serializer"]
                )
                data = result.pop("data")
                manifest.append(result)
                
                payload = json.dumps(
                    data,
                    cls=DjangoJSONEncoder,
                    indent=2
                )
                
                zip_file.writestr(f"{name}.json", payload)

            except Exception as error:
                manifest.append({
                    "name": name,
                    "error": str(error)
                })
        zip_file.writestr("manifest.json", json.dumps(manifest, cls=DjangoJSONEncoder))
    zip_buffer.seek(0)

    return zip_buffer


def families_by_type(participants_sorted:Participant)-> dict:
    """Family relationship grouping"""
    families = Family.objects.count()

    # Families that appear in participants
    family_ids_with_participants = set()

    # Define mapping from role sets to category
    FAMILY_CATEGORIES = ["Trio+", "Trio", "Maternal Dyads", "Paternal Dyads", "Singletons", "Other"]
    # Initialize counts for all categories
    family_types = {category: 0 for category in FAMILY_CATEGORIES}
    family_types_count = 0

    for family_id, members_iter in groupby(participants_sorted, key=lambda x: x.family_id_id):
        family_ids_with_participants.add(family_id)
        roles = {m.proband_relationship for m in members_iter}  # set of roles in this family

        # Determine category based on presence of proband (Self), Mother, and Father
        if {"Self", "Mother", "Father"}.issubset(roles):
            # Family includes proband and both parents
            if len(roles) > 3:
                family_types["Trio+"] += 1  # There are other roles in addition to the trio
            else:
                family_types["Trio"] += 1   # Exactly Self, Mother, Father
        elif roles == {"Self", "Mother"}:
            family_types["Maternal Dyads"] += 1
        elif roles == {"Self", "Father"}:
            family_types["Paternal Dyads"] += 1
        elif roles == {"Self"}:
            family_types["Singletons"] += 1
        else:
            family_types["Other"] += 1

        family_types_count += 1

    all_family_ids = set(Family.objects.values_list("family_id", flat=True))
    family_ids_without_participants = all_family_ids - family_ids_with_participants
    families = families - len(family_ids_without_participants)

    return family_types, families


def get_summary_stats():
    # Basic counts
    participants = Participant.objects.all()
    analytes = Analyte.objects.all()
    aligned = Aligned.objects.count()
    biobank = Biobank.objects.all()
    experiments = Experiment.objects.all()
    findings = GeneticFindings.objects.all()

    # --- Solve status for probands only ---
    probands = participants.filter(proband_relationship="Self")
    solve_status_counts = (
        probands.values("solve_status")
        .annotate(count=Count("solve_status"))
        .order_by()
    )
    solve_status = {entry["solve_status"]: entry["count"] for entry in solve_status_counts}

    # --- Biobank status ---
    biobank_status = dict(Counter(biobank.values_list("status", flat=True)))

    # --- Ontology Terms ---
    ontology_terms = dict()
    ontology_terms_sorted = dict(
        sorted(Counter(Phenotype.objects.all().
                values_list("term_id",
                flat=True)).items(),
                key=lambda item: item[1],
                reverse=True
        )[:10]
    )

    for ont in ontology_terms_sorted:
        term = requests.get(f'https://ontology.jax.org/api/hp/terms/{ont}')
        count = ontology_terms_sorted[ont]
        ontology_terms_sorted[ont] = {
            "count": count,
            "name": json.loads(term.text)['name']
        }

    # --- Proband reported reace ---
    proband_reported_reace = dict(Counter(probands.values_list("reported_race", flat=True)))

    # --- Analyte counts ---
    analyte_biosample = dict(Counter(analytes.values_list("primary_biosample", flat=True)))
    analyte_type = dict(Counter(analytes.values_list("analyte_type", flat=True)))

    # --- Genetic findings phenotype_contribution ---
    findings_contribution = dict(Counter(findings.values_list("phenotype_contribution", flat=True)))

    # --- Sequencing vs Aligned comparison ---
    def group_by_table_name(qs):
        values = qs.values_list("table_name", flat=True)
        return dict(Counter(v.replace("experiment_", "").replace("aligned_", "").capitalize() for v in values))

    experiment_counts = group_by_table_name(experiments)
    aligned_counts = group_by_table_name(Aligned.objects.all())

    # Delta comparison
    labels = set(experiment_counts) | set(aligned_counts)
    sequencing_vs_alignment = [
        {
            "label": label,
            "experiments": experiment_counts.get(label, 0),
            "alignments": aligned_counts.get(label, 0),
            "delta": experiment_counts.get(label, 0) - aligned_counts.get(label, 0),
        }
        for label in sorted(labels)
    ]
    # --- Experiment category buckets per participant ---
    # Map experiments to three sets of participant_ids
    sr_participants = set(
        experiments.filter(table_name="experiment_dna_short_read")
        .values_list("participant_id", flat=True)
    )
    lr_participants = set(
        experiments.filter(table_name__in=["experiment_nanopore", "experiment_pac_bio"])
        .values_list("participant_id", flat=True)
    )
    rna_participants = set(
        experiments.filter(table_name="experiment_rna_short_read")
        .values_list("participant_id", flat=True)
    )

    all_exp_participants = sr_participants | lr_participants | rna_participants

    EXPERIMENT_CATEGORIES = ["ALL", "LRxSR", "LRxRNA", "SRxRNA", "LR", "SR", "RNA"]
    experiment_buckets = {k: 0 for k in EXPERIMENT_CATEGORIES}

    # (Optional) keep a per-participant label if you want to display later
    participant_experiment_category = {}

    for pid in all_exp_participants:
        has_sr = pid in sr_participants
        has_lr = pid in lr_participants
        has_rna = pid in rna_participants

        if has_lr and has_sr and has_rna:
            bucket = "ALL"
        elif has_lr and has_sr:
            bucket = "LRxSR"
        elif has_lr and has_rna:
            bucket = "LRxRNA"
        elif has_sr and has_rna:
            bucket = "SRxRNA"
        elif has_lr:
            bucket = "LR"
        elif has_sr:
            bucket = "SR"
        else:
            bucket = "RNA"  # only RNA
        experiment_buckets[bucket] += 1

        try:
            participant_experiment_category[bucket].append(pid)
        except KeyError as exp:
            participant_experiment_category[bucket] = [pid]

    pediatric_probands = {
        "pediatric_count": len(probands.filter(age_at_enrollment__lt=18)),
        "non_pediatric_count": len(probands.filter(age_at_enrollment__gte=18))
    }
    participants_sorted = sorted(participants, key=lambda x: x.family_id_id)
    family_types, families = families_by_type(participants_sorted)

    lr_participants_sorted = sorted(
        Participant.objects.filter(
            pk__in=lr_participants),
        key=lambda x: x.family_id_id
    )
    lr_family_types, _ = families_by_type(lr_participants_sorted)
    # import pdb; pdb.set_trace()
    response = {
        "participants": participants.count(),
        "families": families,
        "analytes": analytes.count(),
        "aligned": aligned,
        "biobank": biobank.count(),
        "probands": probands.count(),
        "findings": findings.count(),
        "solve_status_counts": solve_status,
        "biobank_status_counts": biobank_status,
        "analyte_biosample_counts": analyte_biosample,
        "analyte_type_counts": analyte_type,
        "findings_contribution": findings_contribution,
        "sequencing_vs_alignment": sequencing_vs_alignment,
        "family_types": family_types,
        "experiment_category_counts": experiment_buckets,
        "pediatric_probands": pediatric_probands,
        "lr_family_types":lr_family_types,
        "proband_reported_reace": proband_reported_reace,
        "ontology_terms": ontology_terms_sorted
        # "participant_experiment_category": participant_experiment_category,
    }

    return response


def get_family_detail(participant_id: str, superuser: bool = False) -> list[dict]:
    """
    Return full family detail for a participant's family.
    """
    family_detail = []
    s3_manifest = fetch_manifest("icts-dashboard-analysis-files")
    root_participant = Participant.objects.get(pk=participant_id)

    participants = get_visible_objects(
        model=Participant,
        superuser=superuser,
    ).filter(family_id=root_participant.family_id)

    for participant in participants:
        serialized_participant = ParticipantOutputSerializer(participant)

        serialized_biobanks = BiobankSerializer(
            get_visible_objects(
                Biobank,
                superuser=superuser,
                participant_id=participant
            ),
            many=True,
        )

        serialized_phenotypes = PhenotypeSerializer(
            get_visible_objects(
                Phenotype,
                superuser=superuser,
                participant_id=participant
            ),
            many=True,
        )

        serialized_genetic_findings = GeneticFindingsOutputSerializer(
            get_visible_objects(
                GeneticFindings,
                superuser=superuser,
                participant_id=participant
            ),
            many=True,
        )

        # Sequencing
        experiments = Experiment.objects.filter(participant_id=participant)
        serialized_sequencing = []

        for exp in experiments:
            model = table_serializers[exp.table_name]["model"]
            serializer = table_serializers[exp.table_name]["output_serializer"]

            sequence = serializer(model.objects.get(pk=exp.id_in_table)).data
            sequence["table_type"] = exp.table_name
            serialized_sequencing.append(sequence)

        # Alignments
        aligned = Aligned.objects.filter(participant_id=participant)
        serialized_alignments = []
        serialized_reports = []
        for aln in aligned:
            model = table_serializers[aln.table_name]["model"]
            serializer = table_serializers[aln.table_name]["output_serializer"]

            alignment = serializer(model.objects.get(pk=aln.id_in_table)).data
            alignment["table_type"] = aln.table_name
            for report in s3_manifest:
                if report["source_analysis_file"]["table_identifier"] == aln.aligned_id:
                    serialized_reports.append(report)
            
            
            serialized_alignments.append(alignment)
            print(serialized_reports)

        
        # for aln in serialized_alignments:
        #     for report in TEST_MANIFEST:
        #         if report["source_analysis_file"]["table_identifier"] == aln.aligned_id:
        #             print(report)
        #     # if aln["alignment_id"]
    
        family_detail.append({
            "participant": serialized_participant.data,
            "proband_relationship": participant.proband_relationship,
            "family_id": participant.family_id_id,
            "biobank": serialized_biobanks.data,
            "phenotypes": serialized_phenotypes.data,
            "genetic_findings": serialized_genetic_findings.data,
            "sequencing": serialized_sequencing,
            "alignments": serialized_alignments,
            "reports": serialized_reports
        })

    return family_detail


def get_case_queue(participant_id:str) -> dict:
    """
    Only collect families with completed PacBio alignments
    """
    case_queue = []
    analysis_ready = {}
    participants = Participant.objects.filter(family_id=Participant.objects.get(pk=participant_id).family_id)  # Get related participants

    for participant in participants:
        serialized_participant = ParticipantOutputSerializer(participant)
        analytes = Analyte.objects.filter(participant_id=participant)
        dna_analytes = []
        pac_bio_sequencing = []
        pac_bio_alignments = []

        for analyte in analytes:
            if analyte.analyte_type != "DNA":
                continue
            dna_analytes.append(analyte.analyte_id)
            pac_bio_experiment = ExperimentPacBio.objects.filter(analyte_id=analyte)  # each analyte should have one experiment
            if not pac_bio_experiment:
                continue
            pac_bio_sequencing.append(pac_bio_experiment[0].experiment_pac_bio_id)
            pac_bio_alignment = AlignedPacBio.objects.filter(experiment_pac_bio_id=pac_bio_experiment[0])
            if not pac_bio_alignment:
                continue
            pac_bio_alignments.append(pac_bio_alignment[0].aligned_pac_bio_id)
            analysis_ready[participant.participant_id] = True  # avoid adding duplicates

        serialized_biobanks = BiobankSerializer(Biobank.objects.filter(child_analytes__in=dna_analytes), many=True)
        serialized_analytes = AnalyteSerializer(Analyte.objects.filter(pk__in=dna_analytes), many=True)
        serialized_sequencing = ExperimentPacBioSerializer(ExperimentPacBio.objects.filter(pk__in=pac_bio_sequencing), many=True)
        serialized_alignments = AlignedPacBioSerializer(AlignedPacBio.objects.filter(pk__in=pac_bio_alignments), many=True)

        items = {
            "participant": serialized_participant.data,
            "proband_relationship": participant.proband_relationship,
            "family_id": participant.family_id_id,
            "family_size": len(participants),
            "biobank": serialized_biobanks.data,
            "analytes": serialized_analytes.data,
            "sequencing": serialized_sequencing.data,
            "alignments": serialized_alignments.data,
            }
        case_queue.append(items)

    for p in case_queue:
        if len(analysis_ready) == p["family_size"]:
            p["cohort_analysis"] = "ready"
        else:
            p["cohort_analysis"] = "incomplete"

    return case_queue
