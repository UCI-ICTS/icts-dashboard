#!/usr/bin/env python3
# experiments/selectors.py

"""Experiments Selectors
"""

from experiments.models import Experiment, ExperimentDNAShortRead


def get_experiment(experiment_id: str) -> Experiment:
    """Retrieve an experiment instance by its ID or return None if not found."""
    try:
        experiment_instance = Experiment.objects.get(experiment_id=experiment_id)
        return experiment_instance
    except Experiment.DoesNotExist:
        return None
    

def get_experiment_dna_short_read(experiment_dna_short_read_id: str) -> ExperimentDNAShortRead:
    """Retrieve an experiment instance by its ID or return None if not found."""
    try:
        experiment_dna_short_read_instance = ExperimentDNAShortRead.objects.get(experiment_dna_short_read_id=experiment_dna_short_read_id)
        return experiment_dna_short_read_instance
    except ExperimentDNAShortRead.DoesNotExist:
        return None
