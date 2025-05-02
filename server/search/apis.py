#!/usr/bin/env python
# search/apis.py

from django.apps import apps
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from itertools import chain
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from search.selectors import get_anvil_tables
from rest_framework_simplejwt.authentication import JWTAuthentication
from metadata.models import (
    Participant,
    Family,
    GeneticFindings,
    Phenotype,
    Analyte,
    Biobank,
    ExperimentStage,
)

from metadata.services import (
    ParticipantInputSerializer,
    ParticipantOutputSerializer,
    FamilySerializer,
    GeneticFindingsSerializer,
    AnalyteSerializer,
    PhenotypeSerializer,
    BiobankSerializer,
    ExperimentStageSerializer,
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
    ExperimentRNAShortRead
)

from experiments.services import (
    AlignedSerializer,
    AlignedDNAShortReadSerializer,
    AlignedNanoporeSerializer,
    AlignedPacBioSerializer,
    AlignedRnaSerializer,
    ExperimentSerializer,
    ExperimentShortReadSerializer,
    ExperimentNanoporeSerializer,
    ExperimentPacBioSerializer,
    ExperimentRnaOutputSerializer
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
            serialized_participants = ParticipantOutputSerializer(Participant.objects.all(), many=True)
            serialized_families = FamilySerializer(Family.objects.all(), many=True)
            serialized_analytes = AnalyteSerializer(Analyte.objects.all(), many=True)
            serialized_phenotypes = PhenotypeSerializer(Phenotype.objects.all(), many=True)
            serialized_genetic_findings = GeneticFindingsSerializer(GeneticFindings.objects.all(), many=True)
            serialized_biobank_entries = BiobankSerializer(Biobank.objects.all(), many=True)
            serialized_experiment_stages = ExperimentStageSerializer(ExperimentStage.objects.all(), many=True)

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
            serialized_aligned_rna = AlignedRnaSerializer(
                AlignedRNAShortRead.objects.all(), many=True
            )
            serialized_experiments = ExperimentSerializer(Experiment.objects.all(), many=True)
            serialized_dna = ExperimentShortReadSerializer(ExperimentDNAShortRead.objects.all(), many=True)
            serialized_nanopore = ExperimentNanoporeSerializer(ExperimentNanopore.objects.all(), many=True)
            serialized_pacbio = ExperimentPacBioSerializer(ExperimentPacBio.objects.all(), many=True)
            serialized_rna = ExperimentRnaOutputSerializer(ExperimentRNAShortRead.objects.all(), many=True)


            serilized_return_data = {
                # Metadata Tables
                'participants': serialized_participants.data,
                'families': serialized_families.data,
                'genetic_findings': serialized_genetic_findings.data,
                'analytes': serialized_analytes.data,
                'phenotypes': serialized_phenotypes.data,
                'biobank_entries': serialized_biobank_entries.data,
                'experiment_stages': serialized_experiment_stages.data,
                # Experiment Tables
                'experiments': serialized_experiments.data,
                'experiment_dna_short_read' : serialized_dna.data,
                'experiment_nanopore': serialized_nanopore.data,
                'experiment_pac_bio': serialized_pacbio.data,
                'experiment_rna_short_read': serialized_rna.data,
                # Aligned tables
                'aligned': serialized_aligned_experiments.data,
                'aligned_dna_short_read': serialized_aligned_dna.data,
                'aligned_nanopore': serialized_aligned_nanopore.data,
                'aligned_pac_bio': serialized_aligned_pacbio.data,
                'aligned_rna_short_read': serialized_aligned_rna.data
            }
            # time.sleep(5)
            return Response(status=status.HTTP_200_OK, data=serilized_return_data)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class DounlaodTablesAPI(APIView):
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

        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="data.zip"'

        return response


class SearchTablesAPI(APIView):
    """ """

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
        auto_schema=None
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
