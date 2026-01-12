#!/usr/bin/env python3
# metadata/servces.py

import re
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from rest_framework import serializers
from config.selectors import (
    remove_na,
    response_constructor,
    compare_data,
    TableValidator,
)
from metadata.models import (
    Analyte,
    GeneticFindings,
    Participant,
    Family,
    Phenotype,
    InternalProjectId,
    PmidId,
    TwinId,
    Biobank,
)

from experiments.models import Experiment, Aligned

from metadata.selectors import (
    participant_parser,
    genetic_findings_parser,
    phenotype_parser,
    biobank_parser,
)

from submodels.models import (
    ReportedRace,
    VariantType,
    VariantInheritance,
    ConditionInheritance,
    GREGoRVariantClassification,
    GeneDiseaseValidity,
    DiscoveryMethod
)


class GeneticFindingsInputSerializer(serializers.ModelSerializer):
    """
    Validate fields for GeneticFindings
    """

    additional_family_members_with_variant = serializers.PrimaryKeyRelatedField(
        queryset=Participant.objects.all(), many=True, required=False
    )

    experiment_id = serializers.JSONField(required=False)
    variant_type = serializers.JSONField(required=False)
    gene_of_interest = serializers.JSONField(required=False)
    condition_inheritance = serializers.JSONField(required=False)
    method_of_discovery = serializers.JSONField(required=False)

    class Meta:
        model = GeneticFindings
        fields = "__all__"

    def _partial_helper(self, attrs):
        """
        For partial updates, combine existing instance values with incoming attrs.
        For creates, this just returns attrs.
        """
        if not self.instance:
            return dict(attrs)

        combined = { }
        for name in self.fields.keys():
            combined[name] = getattr(self.instance, name, None)
        combined.update(attrs)
        return combined


    def validate(self, attrs):
        data = self._partial_helper(attrs)
        errors = {}

        valid_variant_types = [choice[0] for choice in VariantType.choices]
        valid_condition_inheritance = [choice[0] for choice in ConditionInheritance.choices]
        valid_GREGoR_variant_classification = [choice[0] for choice in GREGoRVariantClassification.choices]
        valid_gene_disease_validity = [choice[0] for choice in  GeneDiseaseValidity.choices]
        valid_method_of_discovery = [choice[0] for choice in  DiscoveryMethod.choices]

        variant_types = set(data.get("variant_type") or [])
        experiment_ids = set(data.get("experiment_id" or []))

        if not isinstance(data.get("variant_type"), list):
            errors.setdefault("variant_type", []).append("variant_types must be a list")
        if not isinstance(data.get("experiment_id"), list):
            errors.setdefault("experiment_id", []).append("experiment_id must be a list")

        missing_experiment_ids = [e for e in experiment_ids if not Experiment.objects.filter(pk=e).exists()]
        if missing_experiment_ids:
            errors.setdefault("experiment_id", []).append(
                f"experiment_id not found: {', '.join(map(str, missing_experiment_ids))}"
            )

        bad_variant_types = [x for x in variant_types if x not in valid_variant_types]
        if bad_variant_types:
            errors.setdefault("variant_types", []).append(
                f" invalid variant_type {bad_variant_types}. Must be one of {', '.join(sorted(valid_variant_types))}"
            )

        # Required ref/alt for SNV/INDEL/RE
        if variant_types & {"SNV", "INDEL", "RE"}:
            if not data.get("ref"):
                errors.setdefault("ref", []).append(
                    "ref is required for SNV/INDEL/RE"
                )
            if not data.get("alt"):
                errors.setdefault("alt", []).append(
                    "alt is required for SNV/INDEL/RE"
                )
        # Require gene_of_interest for small variants
        if variant_types & {"SNV", "INDEL", "RE"} and not (data.get("gene_of_interest")):
            errors.setdefault("gene_of_interest", []).append(
                "gene_of_interest is required for SNV/INDEL/RE"
            )

        # candidate/known phenotype logic
        gene_known_for_phenotype = (data.get("gene_known_for_phenotype") or "").strip().lower()
        phenotype_contribution = data.get("phenotype_contribution") or ""
        if gene_known_for_phenotype == "candidate" and phenotype_contribution != "Uncertain":
            errors.setdefault("phenotype_contribution", []).append(
                "If 'gene_known_for_phenotype' is 'Candidate, 'phenotype_contribution' must be 'Uncertain'"
            )

        if gene_known_for_phenotype == "known":
            # require known_condition_name
            if not (data.get("known_condition_name") or "").strip():
                errors.setdefault("known_condition_name", []).append(
                    "known_condition_name is required for a known gene/phenotype."
                )

            # condition_id must be `OMIM:` or `MONDO:`
            condition_id = (data.get("condition_id") or "").strip()

            if condition_id and not re.match(r"^(OMIM|MONDO):\S+$", condition_id):
                errors.setdefault("condition_id", []).append(f"{condition_id} must be OMIM:... or MONDO:...")

            # if known gene_known_for_phenotype then valid_condition_inheritance is required
            condition_inheritance = data.get("condition_inheritance")
            if not condition_inheritance:
                errors.setdefault("condition_inheritance", []).append(
                    "If `gene_known_for_phenotype` is known then condition_inheritance is required and cannot be empty"
                )
            else:
                bad_condition_inheritance = [v for v in (data["condition_inheritance"] or []) if v not in valid_condition_inheritance]
                if bad_condition_inheritance:
                    errors.setdefault("condition_inheritance", []).append(
                        f"invalid: {bad_condition_inheritance} (valid: {', '.join(sorted(valid_condition_inheritance))})"
                    )
            # if known gene_known_for_phenotype then valid_GREGoR_variant_classification is required
            GREGoR_variant_classification = data.get("GREGoR_variant_classification")
            if not GREGoR_variant_classification:
                errors.setdefault("GREGoR_variant_classification", []).append(
                    "If `gene_known_for_phenotype` is known then GREGoR_variant_classification is required and cannot be empty"
                )
            if data.get("GREGoR_variant_classification") and data["GREGoR_variant_classification"] not in valid_GREGoR_variant_classification:
                errors.setdefault("GREGoR_variant_classification", []).append(
                    f"invalid (valid: {', '.join(sorted(valid_GREGoR_variant_classification))})"
                )

            # if known gene_known_for_phenotype then gene_disease_validity is required
            gene_disease_validity = data.get("gene_disease_validity")
            if not gene_disease_validity:
                errors.setdefault("gene_disease_validity", []).append(
                    "If `gene_known_for_phenotype` is known then gene_disease_validity is required and cannot be empty"
                )
            if data.get("gene_disease_validity") and data["gene_disease_validity"] not in valid_gene_disease_validity:
                errors.setdefault("gene_disease_validity", []).append(
                    f"invalid (valid: {', '.join(sorted(valid_gene_disease_validity))})"
                )

        # check for linked_variant existance
        linked_variant = data.get("linked_variant")
        if linked_variant and not GeneticFindings.objects.filter(pk=linked_variant).exists():
            errors.setdefault("linked_variant", []).append(
                f"'linked_variant' {linked_variant} does not match any 'genetic_findings_id'"
            )

        # partial_contribution_explained terms must be valid HPO in phenotype table
        partial_contribution_explained = data.get("partial_contribution_explained") or []
        if partial_contribution_explained and isinstance(partial_contribution_explained, list):
            missing = [p for p in partial_contribution_explained if not Phenotype.objects.filter(term_id=p).exists()]
            if missing:
                errors.setdefault("partial_contribution_explained", []).append(
                    f"unknown HPO terms: {', '.join(missing)}"
                )
        # method_of_discovery should be a list
        method_of_discovery = data.get("method_of_discovery")
        if method_of_discovery:
            if not isinstance(method_of_discovery, list):
                errors.setdefault("method_of_discovery", []).append("method_of_discovery must be a list")
            bad_method_of_discovery = [x for x in method_of_discovery if x not in valid_method_of_discovery]
            if bad_method_of_discovery:
                f"invalid: {bad_method_of_discovery} (valid: {', '.join(sorted(valid_method_of_discovery))})"

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


    def create(self, validated_data):
        """
        Create a new GeneticFindings instance using the validated data
        """
        additional_family_members = validated_data.pop(
            "additional_family_members_with_variant", []
        )
        genetic_findings_instance = GeneticFindings.objects.create(**validated_data)
        if additional_family_members:
            genetic_findings_instance.additional_family_members_with_variant.set(
                additional_family_members
            )
        genetic_findings_instance.save()
        return genetic_findings_instance


    def update(self, instance, validated_data):
        """
        Update each attribute of the instance with validated data
        """
        additional_family_members = validated_data.pop(
            "additional_family_members_with_variant", []
        )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if additional_family_members:
            instance.additional_family_members_with_variant.clear()
            instance.additional_family_members_with_variant.set(
                additional_family_members
            )
        instance.save()

        return instance


class GeneticFindingsOutputSerializer(serializers.ModelSerializer):
    """
    Docstring for GeneticFindingsOutputSerializer
    """
    # declare JSON fields explicitly (no encoder kw)
    experiment_id = serializers.ListField(child=serializers.CharField(), default=list)
    variant_type = serializers.ListField(
        child=serializers.ChoiceField(choices=VariantType.choices),
        default=list
    )
    gene_of_interest = serializers.ListField(child=serializers.CharField(), default=list, allow_null=True)
    condition_inheritance = serializers.ListField(child=serializers.CharField(), default=list, allow_empty=True)
    method_of_discovery = serializers.ListField(child=serializers.CharField(), default=list, allow_empty=True)

    # ManyToMany: read-only on the output serializer
    additional_family_members_with_variant = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = GeneticFindings
        fields = "__all__"


class AnalyteSerializer(serializers.ModelSerializer):
    """
    Docstring for AnalyteSerializer
    """

    class Meta:
        model = Analyte
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Analyte instance using the validated data"""

        # participant_instance = validated_data["participant_id"]
        # if "age_at_collection" in validated_data:
        #     try:
        #         participant_instance.age_at_enrollment == validated_data["age_at_collection"]
        #     except:
        #         raise ValueError

        analyte_instance = Analyte.objects.create(**validated_data)
        return analyte_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BiobankSerializer(serializers.ModelSerializer):
    """
    Serializer for the Biobank model.
    Handles full serialization and deserialization of nested ManyToMany and ForeignKey fields.
    """

    participant_id = serializers.SlugRelatedField(
        slug_field="participant_id",
        queryset=Participant.objects.all(),
    )
    child_analytes = serializers.SlugRelatedField(
        many=True,
        slug_field="analyte_id",
        queryset=Analyte.objects.all(),
        required=False,
    )
    experiments = serializers.SlugRelatedField(
        many=True,
        slug_field="experiment_id",  # Fully-qualified ID like "experiment_dna_short_read.UCI_GREGoR_..."
        queryset=Experiment.objects.all(),
        required=False,
    )
    alignments = serializers.SlugRelatedField(
        many=True,
        slug_field="aligned_id",  # Fully-qualified
        queryset=Aligned.objects.all(),
        required=False,
    )

    class Meta:
        model = Biobank
        fields = "__all__"


class PhenotypeSerializer(serializers.ModelSerializer):
    """
    Docstring for PhenotypeSerializer
    """
    class Meta:
        model = Phenotype
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Phenotype instance using the validated data"""
        phenotype = Phenotype.objects.create(**validated_data)
        return phenotype

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()
        return instance


class FamilySerializer(serializers.ModelSerializer):
    """
    Docstring for FamilySerializer
    """

    class Meta:
        model = Family
        fields = "__all__"

    def create(self, validated_data):
        """Create an new instance of the model with validated data"""
        family_id = validated_data.get("family_id")
        family, created = Family.objects.get_or_create(
            family_id=family_id, defaults=validated_data
        )
        return family

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ParticipantOutputSerializer(serializers.ModelSerializer):
    """
    Docstring for ParticipantOutputSerializer
    """
    class Meta:
        model = Participant
        fields = "__all__"


class ParticipantInputSerializer(serializers.ModelSerializer):
    """
    Docstring for ParticipantInputSerializer
    """
    prior_testing = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of prior testing entries",
    )

    internal_project_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="An identifier used by GREGoR research centers to identify a set of participants for their internal tracking",
    )

    pmid_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Case specific PubMed IDs if applicable",
    )

    twin_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Participant IDs for twins, triplets, etc.",
    )

    reported_race = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Participant race if available.",
    )

    class Meta:
        model = Participant
        fields = "__all__"

    def create(self, validated_data):
        internal_project_id = validated_data.pop("internal_project_id", [])
        pmid_id = validated_data.pop("pmid_id", [])
        twin_id = validated_data.pop("twin_id", [])
        reported_race = validated_data.pop("reported_race", [])

        try:
            with transaction.atomic():
                participant = Participant.objects.create(**validated_data)
                if internal_project_id:
                    self._set_relationship(
                        participant,
                        InternalProjectId,
                        internal_project_id,
                        "internal_project_id",
                    )
                if pmid_id:
                    self._set_relationship(participant, PmidId, pmid_id, "pmid_id")
                if twin_id:
                    self._set_relationship(participant, TwinId, twin_id, "twin_id")
                if reported_race:
                    self._set_relationship(
                        participant, ReportedRace, reported_race, "reported_race"
                    )
                participant.save()
        except IntegrityError as error:
            raise serializers.ValidationError(error)

        return participant

    def update(self, instance, validated_data):
        internal_project_id = validated_data.pop("internal_project_id", [])
        pmid_id = validated_data.pop("pmid_id", [])
        twin_id = validated_data.pop("twin_id", [])
        reported_race = validated_data.pop("reported_race", [])

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            self._set_relationship(
                instance, InternalProjectId, internal_project_id, "internal_project_id"
            )
            self._set_relationship(instance, PmidId, pmid_id, "pmid_id")
            self._set_relationship(instance, TwinId, twin_id, "twin_id")
            self._set_relationship(
                instance, ReportedRace, reported_race, "reported_race"
            )

        return instance

    def _set_relationship(self, instance, model, ids, related_name):
        # Setting ManyToMany relations
        # print(instance, model, ids, related_name)  # Debugging
        try:
            manager = getattr(instance, related_name)
            if model == ReportedRace:  # Special handling for ReportedRace
                manager.set(model.objects.filter(description__in=ids))
            else:
                manager.set(model.objects.filter(pk__in=ids))
        except Exception as e:
            print(f"Error setting relationship: {e}")
            raise


def get_or_create_sub_models(datum: dict) -> dict:
    """
    Create or retrieve related model instances based on the provided data.

    This function processes the `datum` dictionary to handle the creation or retrieval
    of related model instances. It updates the `datum` dictionary with the primary keys
    of the related instances.

    Args:
        datum (dict): A dictionary containing the data for the main model and its related models.

    Returns:
        dict: The updated `datum` dictionary with primary keys of the related instances.
    """
    # Define how to handle creation of related objects
    mapping = {
        "family_id": (Family, "family_id"),
        "internal_project_id": (InternalProjectId, "internal_project_id"),
        "pmid_id": (PmidId, "pmid_id"),
        "twin_id": (TwinId, "twin_id"),
    }
    for key, (model, field_name) in mapping.items():
        if isinstance(datum.get(key), list):  # Handles list fields differently
            objects = []
            for item in datum[key]:
                obj, created = model.objects.get_or_create(**{field_name: item})
                objects.append(obj.pk)
            datum[key] = objects
        else:
            if datum.get(key):
                obj, created = model.objects.get_or_create(**{field_name: datum[key]})
                datum[key] = obj.pk
    return datum


def create_metadata(table_name: str, identifier: str, datum: dict):
    """
    Create a new model instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create.
        identifier (str): The unique identifier for the model instance.
        datum (dict): The data to create the model instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "participant": {
            "input_serializer": ParticipantInputSerializer,
            "output_serializer": ParticipantOutputSerializer,
            "parsed_data": lambda datum: participant_parser(participant=datum),
        },
        "family": {
            "input_serializer": FamilySerializer,
            "output_serializer": FamilySerializer,
        },
        "genetic_findings": {
            "input_serializer": GeneticFindingsInputSerializer,
            "output_serializer": GeneticFindingsOutputSerializer,
            "parsed_data": lambda datum: genetic_findings_parser(
                genetic_findings=datum
            ),
        },
        "analyte": {
            "input_serializer": AnalyteSerializer,
            "output_serializer": AnalyteSerializer,
        },
        "phenotype": {
            "input_serializer": PhenotypeSerializer,
            "output_serializer": PhenotypeSerializer,
            "parsed_data": lambda datum: phenotype_parser(phenotype=datum),
        },
        "biobank": {
            "input_serializer": BiobankSerializer,
            "output_serializer": BiobankSerializer,
            "parsed_data": lambda datum: biobank_parser(biobank=datum),
        },
    }

    model_input_serializer = table_serializers[table_name]["input_serializer"]
    model_output_serializer = table_serializers[table_name]["output_serializer"]

    if "parsed_data" in table_serializers[table_name]:
        datum = remove_na(table_serializers[table_name]["parsed_data"](datum))
    else:
        datum = remove_na(datum=datum)

    table_validator = TableValidator()
    table_validator.validate_json(json_object=datum, table_name=table_name)
    results = table_validator.get_validation_results()
    if results["valid"]:
        serializer = model_input_serializer(data=datum)
        if serializer.is_valid():
            new_instance = serializer.save()
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="CREATED",
                    code=201,
                    message=f"{table_name} {identifier} created.",
                    data={"instance": model_output_serializer(new_instance).data},
                ),
                "accepted_request",
            )
        else:
            error_data = [{item: serializer.errors[item]} for item in serializer.errors]
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="BAD REQUEST",
                    code=400,
                    data=error_data,
                ),
                "rejected_request",
            )
    else:
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=results["errors"],
            ),
            "rejected_request",
        )


def update_metadata_entry(
    table_name: str, identifier: str, model_instance, datum: dict):
    """
    Update an existing model instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to update.
        identifier (str): The unique identifier for the model instance.
        model_instance: The existing model instance to update.
        datum (dict): The data to update the model instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "participant": {
            "input_serializer": ParticipantInputSerializer,
            "output_serializer": ParticipantOutputSerializer,
            "parsed_data": lambda datum: participant_parser(participant=datum),
        },
        "family": {
            "input_serializer": FamilySerializer,
            "output_serializer": FamilySerializer,
        },
        "genetic_findings": {
            "input_serializer": GeneticFindingsInputSerializer,
            "output_serializer": GeneticFindingsOutputSerializer,
            "parsed_data": lambda datum: genetic_findings_parser(
                genetic_findings=datum
            ),
        },
        "analyte": {
            "input_serializer": AnalyteSerializer,
            "output_serializer": AnalyteSerializer,
        },
        "phenotype": {
            "input_serializer": PhenotypeSerializer,
            "output_serializer": PhenotypeSerializer,
            "parsed_data": lambda datum: phenotype_parser(phenotype=datum),
        },
        "biobank": {
            "input_serializer": BiobankSerializer,
            "output_serializer": BiobankSerializer,
            "parsed_data": lambda datum: biobank_parser(biobank=datum),
        },
    }

    serializers = table_serializers.get(table_name)
    if not serializers:
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=f"Unsupported table: {table_name}",
            ),
            "rejected_request",
        )

    if "parsed_data" in table_serializers[table_name]:
        datum = table_serializers[table_name]["parsed_data"](datum)

    with transaction.atomic():
        input_serializer = serializers["input_serializer"]
        output_serializer = serializers["output_serializer"]
        changes = compare_data(
            old_data=output_serializer(model_instance).data,
            new_data=datum,
        )

        serializer = input_serializer(model_instance, data=datum, partial=True)

        if serializer.is_valid():
            updated_instance = serializer.save()
            message = (
                f"{table_name} {identifier} updated."
                if changes
                else f"{table_name} {identifier} had no changes."
            )
            status_label = "UPDATED" if changes else "NO CHANGE"
            code = 200 if changes else 204
            return (
                response_constructor(
                    identifier=identifier,
                    request_status=status_label,
                    code=code,
                    message=message,
                    data={
                        "updates": changes or None,
                        "instance": output_serializer(updated_instance).data,
                    },
                ),
                "accepted_request",
            )
        else:
            error_data = [{item: serializer.errors[item]} for item in serializer.errors]
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="BAD REQUEST",
                    code=400,
                    data=error_data,
                ),
                "rejected_request",
            )


def delete_metadata(table_name: str, identifier: str, id_field: str = "id"):
    """
    Delete an existing model instance based on the provided identifier.

    Args:
        table_name (str): The name of the table (model) to delete from.
        identifier (str): The unique identifier of the model instance.
        id_field (str): The field used as an identifier (default is "id").

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    model_mapping = {
        "participant": Participant,
        "family": Family,
        "genetic_findings": GeneticFindings,
        "analyte": Analyte,
        "phenotype": Phenotype,
        "biobank": Biobank,
    }

    model_class = model_mapping.get(table_name)
    if not model_class:
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=f"Invalid table name: {table_name}",
            ),
            "rejected_request",
        )

    try:
        instance = model_class.objects.filter(**{id_field: identifier}).first()
        if instance:
            instance.delete()
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="DELETED",
                    code=200,
                    data=f"{table_name} {identifier} deleted successfully.",
                ),
                "accepted_request",
            )
        else:
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="NOT FOUND",
                    code=404,
                    data=f"{table_name} {identifier} not found.",
                ),
                "rejected_request",
            )

    except Exception as error:
        return (
            response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ),
            "rejected_request",
        )


# def validate_biobank_traceability(biobank):
#     """
#     Check that all experiments and alignments linked to a biobank sample
#     are also traceable via analyte → experiment → aligned.

#     Args:
#         biobank (Biobank): The biobank sample to validate.

#     Returns:
#         dict: A status summary with errors, if any.
#     """
#     errors = []

#     analyte_ids = {a.analyte_id for a in biobank.child_analytes.all()}
#     experiment_ids = {e.experiment_id for e in biobank.experiments.all()}
#     alignment_ids = {a.aligned_id for a in biobank.alignments.all()}

#     for exp in biobank.experiments.all():
#         analyte_match = getattr(exp, "analyte", None)
#         if analyte_match and analyte_match.analyte_id not in analyte_ids:
#             errors.append(f"Experiment {exp.experiment_id} links to unknown analyte {analyte_match.analyte_id}")

#     for aln in biobank.alignments.all():
#         experiment_match = getattr(aln, "experiment", None)
#         if experiment_match and experiment_match.experiment_id not in experiment_ids:
#             errors.append(f"Alignment {aln.aligned_id} links to unknown experiment {experiment_match.experiment_id}")

#     return {
#         "biobank_id": biobank.biobank_id,
#         "status": "valid" if not errors else "invalid",
#         "errors": errors
#     }


# def repair_biobank_links(biobank):
#     """
#     Attempt to reconstruct relationships for a Biobank sample:
#     - link Analytes (by biobank or ID pattern)
#     - link Experiments via Analyte
#     - link Alignments via Experiment
#     """
#     result = {"biobank_id": biobank.biobank_id, "linked": {}, "errors": []}

#     try:
#         # 1. Link Analytes
#         analytes = Analyte.objects.filter(analyte_id__icontains=biobank.participant_id_id)
#         if analytes:
#             biobank.child_analytes.set(analytes)
#             import pdb; pdb.set_trace()
#             result["linked"]["analytes"] = [a.analyte_id for a in analytes]
#         else:
#             result["errors"].append("No matching analytes")

#         # 2. Link Experiments via Analyte
#         experiments = Experiment.objects.filter(analyte__in=analytes)
#         if experiments:
#             biobank.experiments.set(experiments)
#             result["linked"]["experiments"] = [e.experiment_id for e in experiments]
#         else:
#             result["errors"].append("No experiments found for analytes")

#         # 3. Link Alignments via Experiment
#         alignments = Aligned.objects.filter(experiment__in=experiments)
#         if alignments:
#             biobank.alignments.set(alignments)
#             result["linked"]["alignments"] = [a.aligned_id for a in alignments]
#         else:
#             result["errors"].append("No alignments found for experiments")

#         biobank.save()

#     except Exception as e:
#         result["errors"].append(str(e))

#     result["status"] = "complete" if not result["errors"] else "partial"
#     return result
