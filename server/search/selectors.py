#!/usr/bin/env python
# search/selectors.py

import importlib
from django.apps import apps

from config.selectors import (
    compare_data,
    generate_tsv,
    generate_zip,
    response_constructor,
    remove_na,
    TableValidator
)

from metadata.services import (
    AnalyteSerializer,
    GeneticFindingsSerializer,
    ParticipantInputSerializer,
    ParticipantOutputSerializer,
    FamilySerializer,
    PhenotypeSerializer,
    get_or_create_sub_models,
)

from metadata.selectors import (
    participant_parser,
    genetic_findings_parser
)

from experiments.services import (
    AlignedDNAShortReadSerializer,
    AlignedNanoporeSerializer,
    AlignedPacBioSerializer,
    AlignedRnaSerializer,
    ExperimentShortReadSerializer,
    ExperimentRnaSerializer,
    ExperimentNanoporeSerializer,
    ExperimentPacBioSerializer,
    ExperimentSerializer
)
from experiments.selectors import (
    parse_short_read,
    parse_nanopore,
    parse_pac_bio,
    parse_rna,
    parse_short_read_aligned,
    parse_rna_aligned,
    parse_pac_bio_aligned,
    parse_nanopore_aligned
)

serializer_mapping ={
    "alignedpacbio": "AlignedPacBioSerializer",
    "experiment": "ExperimentSerializer",
    "aligned": "AlignedSerializer",
    "experimentdnashortread": "ExperimentShortReadSerializer",
    "aligneddnashortread": "AlignedDNAShortReadSerializer",
    "experimentrnashortread": "ExperimentRnaSerializer",
    "alignedrnashortread": "AlignedRnaSerializer",
    "experimentnanopore":"ExperimentNanoporeSerializer",
    "alignednanopore":"AlignedNanoporeSerializer",
    "experimentpacbio" : "ExperimentPacBioSerializer",
    'family':"FamilySerializer",
    'participant':"ParticipantInputSerializer",
    'phenotype': "PhenotypeSerializer",
    'geneticfindings' : "GeneticFindingsSerializer",
    'analyte': "AnalyteSerializer"
}
def get_anvil_tables():
    files = {}
    metadata_list = ['family', 'participant', 'phenotype', 'geneticfindings', 'analyte']
    experiments_list = ['experiment', 'aligned', 'experimentdnashortread', 'aligneddnashortread', 'experimentrnashortread', 'alignedrnashortread', 'experimentnanopore', 'alignednanopore', 'experimentpacbio', 'alignedpacbio']
    experiments_models = apps.all_models['experiments']
    experiments_serializer_module = importlib.import_module('experiments.services')
    metadata_serializer_module = importlib.import_module('metadata.services')
    metadata_models = apps.all_models['metadata']
    for key in experiments_models.keys():
        if key in experiments_list:
            try:
                SerializerClass = getattr(experiments_serializer_module, serializer_mapping[key], None)
                queryset = experiments_models[key].objects.all()
                serializer = SerializerClass(queryset, many=True)
                serialized_data = serializer.data
                tsv_content = generate_tsv(serialized_data)     
                files[f"{key.lower()}.tsv"]  = tsv_content
            except KeyError as error:
                print(error)
    for key in metadata_models.keys():
        if key in metadata_list:
            try:
                SerializerClass = getattr(metadata_serializer_module, serializer_mapping[key], None)
                queryset = metadata_models[key].objects.all()
                serializer = SerializerClass(queryset, many=True)
                serialized_data = serializer.data
                tsv_content = generate_tsv(serialized_data)     
                files[f"{key.lower()}.tsv"]  = tsv_content
            except KeyError as error:
                print(error)
            
    zip_buffer = generate_zip(files)

    return zip_buffer

def create_or_update(table_name: str, identifier: str, model_instance, datum: dict):
    """
    Create or update a model instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create or update.
        identifier (str): The unique identifier for the model instance.
        model_instance: The existing model instance to update, or None to create 
            a new instance.
        datum (dict): The data to create or update the model instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """

    
    table_serializers = {
        "participant": {
            "input_serializer": ParticipantInputSerializer,
            "output_serializer": ParticipantOutputSerializer,
            "parsed_data": lambda datum: participant_parser(participant=datum)
        },
        "family":{
            "input_serializer": FamilySerializer,
            "output_serializer": FamilySerializer
        },
        "genetic_findings": {
            "input_serializer": GeneticFindingsSerializer,
            "output_serializer": GeneticFindingsSerializer,
            "parsed_data": lambda datum: genetic_findings_parser(genetic_findings=datum)
        },
        "analyte": {
            "input_serializer": AnalyteSerializer,
            "output_serializer": AnalyteSerializer
        },
        "phenotype": {
            "input_serializer": PhenotypeSerializer,
            "output_serializer": PhenotypeSerializer
        },
        "experiment_dna_short_read": {
            "input_serializer": ExperimentShortReadSerializer,
            "output_serializer": ExperimentShortReadSerializer,
            "parsed_data": lambda datum: parse_short_read(short_read=datum)
        },
        "experiment_nanopore": {
            "input_serializer": ExperimentNanoporeSerializer,
            "output_serializer": ExperimentNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore(nanopore=datum)
        },
        "experiment_pac_bio": {
            "input_serializer": ExperimentPacBioSerializer,
            "output_serializer": ExperimentPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio(pac_bio_datum=datum)
        },
        "experiment_rna_short_read": {
            "input_serializer": ExperimentRnaSerializer,
            "output_serializer": ExperimentRnaSerializer#,
            # "parsed_data": lambda datum: parse_rna(rna_datum=datum)
        },
        "aligned_dna_short_read": {
            "input_serializer": AlignedDNAShortReadSerializer,
            "output_serializer": AlignedDNAShortReadSerializer,
            "parsed_data": lambda datum: parse_short_read_aligned(short_read_aligned=datum)
        },
        "aligned_nanopore": {
            "input_serializer": AlignedNanoporeSerializer,
            "output_serializer": AlignedNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore_aligned(nanopore_aligned=datum)
        },
        "aligned_pac_bio": {
            "input_serializer": AlignedPacBioSerializer,
            "output_serializer": AlignedPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio_aligned(pac_bio_aligned=datum)
        },
        "aligned_rna_short_read": {
            "input_serializer": AlignedRnaSerializer,
            "output_serializer": AlignedRnaSerializer,
            "parsed_data": lambda datum: parse_rna_aligned(rna_aligned=datum)
        }
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
        changes = compare_data(
            old_data=model_output_serializer(model_instance).data,
            new_data=datum
        ) if model_instance else {identifier:"CREATED"}
        #create needed submodules before serialization
        if table_name == "participant":
            datum = get_or_create_sub_models(datum=datum) 
        serializer = model_input_serializer(model_instance, data=datum)

        if serializer.is_valid():
            updated_instance = serializer.save()
            if not changes:
                return response_constructor(
                    identifier=identifier,
                    request_status="SUCCESS",
                    code=200,
                    message=f"{table_name} {identifier} had no changes.",
                    data={
                        "updates": None,
                        "instance": model_output_serializer(updated_instance).data
                    }
                ), "accepted_request"

            return response_constructor(
                identifier=identifier,
                request_status="UPDATED" if model_instance else "CREATED",
                code=200 if model_instance else 201,
                message=(
                    f"{table_name} {identifier} updated." if model_instance 
                    else f"{table_name} {identifier} created."
                ),
                data={
                    "updates": changes,
                    "instance": model_output_serializer(updated_instance).data
                }
            ), "accepted_request"
            
        else:
            error_data = [
                {item: serializer.errors[item]}
                for item in serializer.errors
            ]
            return response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=error_data,
            ), "rejected_request"
        
    else:
        return response_constructor(
            identifier=identifier,
            request_status="BAD REQUEST",
            code=400,
            data=results["errors"],
        ), "rejected_request"
