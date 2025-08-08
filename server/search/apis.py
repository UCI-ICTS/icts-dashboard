#!/usr/bin/env python
# search/apis.py

from collections import Counter, defaultdict
from django.apps import apps
from django.db.models import Q, Count
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from itertools import chain, groupby
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from search.selectors import get_anvil_tables
from rest_framework_simplejwt.authentication import JWTAuthentication

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
    GeneticFindingsSerializer,
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


class GetAllTablesAPI(APIView):
    """"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="get_tables",
        responses={
            200: "Submission successfull",
            400: "Bad request",
        },
        tags=["Search"],
    )
    def get(self, request):
        response_data = []
        try:
            # Metadata Models
            serialized_participants = ParticipantOutputSerializer(
                Participant.objects.all(), many=True
            )
            serialized_families = FamilySerializer(Family.objects.all(), many=True)
            serialized_analytes = AnalyteSerializer(Analyte.objects.all(), many=True)
            serialized_phenotypes = PhenotypeSerializer(
                Phenotype.objects.all(), many=True
            )
            serialized_genetic_findings = GeneticFindingsSerializer(
                GeneticFindings.objects.all(), many=True
            )
            serialized_biobank_entries = BiobankSerializer(
                Biobank.objects.all(), many=True
            )

            # Experiment Models
            serialized_aligned_experiments = AlignedSerializer(
                Aligned.objects.all(), many=True
            )
            serialized_aligned_dna = AlignedDNAShortReadSerializer(
                AlignedDNAShortRead.objects.all(), many=True
            )
            serialized_aligned_nanopore = AlignedNanoporeSerializer(
                AlignedNanopore.objects.all(), many=True
            )
            serialized_aligned_pacbio = AlignedPacBioSerializer(
                AlignedPacBio.objects.all(), many=True
            )
            serialized_aligned_rna = AlignedRNASerializer(
                AlignedRNAShortRead.objects.all(), many=True
            )
            serialized_experiments = ExperimentSerializer(
                Experiment.objects.all(), many=True
            )
            serialized_dna = ExperimentDNAOutputSerializer(
                ExperimentDNAShortRead.objects.all(), many=True
            )
            serialized_nanopore = ExperimentNanoporeSerializer(
                ExperimentNanopore.objects.all(), many=True
            )
            serialized_pacbio = ExperimentPacBioSerializer(
                ExperimentPacBio.objects.all(), many=True
            )
            serialized_rna = ExperimentRNAOutputSerializer(
                ExperimentRNAShortRead.objects.all(), many=True
            )

            serilized_return_data = {
                # Metadata Tables
                "participants": serialized_participants.data,
                "families": serialized_families.data,
                "genetic_findings": serialized_genetic_findings.data,
                "analytes": serialized_analytes.data,
                "phenotypes": serialized_phenotypes.data,
                "biobank_entries": serialized_biobank_entries.data,
                # Experiment Tables
                "experiments": serialized_experiments.data,
                "experiment_dna_short_read": serialized_dna.data,
                "experiment_nanopore": serialized_nanopore.data,
                "experiment_pac_bio": serialized_pacbio.data,
                "experiment_rna_short_read": serialized_rna.data,
                # Aligned tables
                "aligned": serialized_aligned_experiments.data,
                "aligned_dna_short_read": serialized_aligned_dna.data,
                "aligned_nanopore": serialized_aligned_nanopore.data,
                "aligned_pac_bio": serialized_aligned_pacbio.data,
                "aligned_rna_short_read": serialized_aligned_rna.data,
            }
            return Response(status=status.HTTP_200_OK, data=serilized_return_data)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class SummaryAPI(APIView):
    
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_id="summary",
        responses={
            200: "Submission successfull",
            400: "Bad request",
        },
        tags=["Search"],
    )


    def get(self, request):
        try:
            # Basic counts
            participants = Participant.objects.all()
            families = Family.objects.count()
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

            # --- Family relationship grouping ---
            participants_sorted = sorted(participants, key=lambda x: x.family_id_id)

            # Keep track of which families appear in participants
            family_ids_with_participants = set()

            # Define mapping from role sets to category
            FAMILY_CATEGORIES = ["Trio+", "Trio", "Maternal Dyads", "Paternal Dyads", "Singletons", "Other"]
            # Initialize counts for all categories
            kindrid = {category: 0 for category in FAMILY_CATEGORIES}
            kindred_count = 0
            for family_id, members_iter in groupby(participants_sorted, key=lambda x: x.family_id_id):
                family_ids_with_participants.add(family_id)
                roles = {m.proband_relationship for m in members_iter}  # set of roles in this family

                # Determine category based on presence of proband (Self), Mother, and Father
                if {"Self", "Mother", "Father"}.issubset(roles):
                    # Family includes proband and both parents
                    if len(roles) > 3:
                        kindrid["Trio+"] += 1  # There are other roles in addition to the trio
                    else:
                        kindrid["Trio"] += 1   # Exactly Self, Mother, Father
                elif roles == {"Self", "Mother"}:
                    kindrid["Maternal Dyads"] += 1
                elif roles == {"Self", "Father"}:
                    kindrid["Paternal Dyads"] += 1
                elif roles == {"Self"}:
                    kindrid["Singletons"] += 1
                else:
                    kindrid["Other"] += 1
                    print(f'{family_id}: {roles}')
                kindred_count += 1
            print(kindred_count)
            all_family_ids = set(Family.objects.values_list("family_id", flat=True))
            family_ids_without_participants = all_family_ids - family_ids_with_participants
            families = families - len(family_ids_without_participants)

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
                "kindrid": kindrid,
            }

            return Response(status=status.HTTP_200_OK, data=response)

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GetExperimentDNAShortReadTableAPI(APIView):
    """"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="get_experiment_dna_short_read_table",
        responses={
            200: "Submission successfull",
            400: "Bad request",
        },
        tags=["Search"],
    )
    def get(self, request):
        response_data = []
        try:
            serialized_experiment_dna_short_reads = ExperimentShortReadSerializer(
                ExperimentDNAShortRead.objects.all(), many=True
            )

            serilized_return_data = {
                "experiment_dna_short_reads": serialized_experiment_dna_short_reads.data
            }
            return Response(status=status.HTTP_200_OK, data=serilized_return_data)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class DownloadTablesAPI(APIView):
    """AnVIL upload table generation."""

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_id="get_anvil_tables",
        responses={
            200: "Submission successfull",
            400: "Bad request",
        },
        tags=["Search"],
    )
    def get(self, request):
        zip_buffer = get_anvil_tables()

        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="data.zip"'

        return response


class SearchTablesAPI(APIView):
    """"""

    permission_classes = [AllowAny]
    model_name_param = openapi.Parameter(
        "model_name",
        openapi.IN_PATH,
        description="Name of the model to query",
        type=openapi.TYPE_STRING,
    )
    slow_client_param = openapi.Parameter(
        "slowClient",
        openapi.IN_QUERY,
        description="Flag to indicate slow client handling",
        type=openapi.TYPE_BOOLEAN,
        required=False,
    )

    @swagger_auto_schema(
        manual_parameters=[model_name_param, slow_client_param],
        responses={200: "JSON response of model data"},
        auto_schema=None,
    )
    def get(self, request, model_name):
        try:
            model = apps.get_model("metadata", model_name)
        except LookupError:
            return Response(
                {"error": "Model not found."}, status=status.HTTP_404_NOT_FOUND
            )

        query_params = request.query_params
        filter_kwargs = {k: v for k, v in query_params.items() if hasattr(model, k)}

        queryset = model.objects.filter(**filter_kwargs)
        data = chain(queryset.values())

        return Response(data)
