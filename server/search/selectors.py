#!/usr/bin/env python
# search/selectors.py

import importlib
from django.apps import apps

from config.selectors import (
    generate_tsv,
    generate_zip,
)

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

