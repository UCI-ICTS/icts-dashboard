#!/usr/bin/env python3
# tests/test_db_integrity/test_linkage.py

import json
from collections import defaultdict
from django.core.management import call_command
from django.test import TestCase
from io import StringIO
from typing import Dict, Any
from metadata.models import Participant, Biobank, Analyte
from experiments.models import (
    Experiment,
    Aligned,
    ExperimentDNAShortRead,
    ExperimentPacBio,
    ExperimentNanopore,
    ExperimentRNAShortRead,
    AlignedDNAShortRead,
    AlignedPacBio,
    AlignedNanopore,
    AlignedRNAShortRead,
)


model_map = {
    "experiment_dna_short_read": ExperimentDNAShortRead,
    "experiment_pac_bio": ExperimentPacBio,
    "experiment_nanopore": ExperimentNanopore,
    "experiment_rna_short_read": ExperimentRNAShortRead,
    "aligned_dna_short_read": AlignedDNAShortRead,
    "aligned_nanopore": AlignedNanopore,
    "aligned_pac_bio": AlignedPacBio,
    "aligned_rna_short_read": AlignedRNAShortRead,
}


class BioBanklTests(TestCase):
    #     # fixtures = ['tests/fixtures/test_fixture.json']
    fixtures = ["dump.json"]

    def test_run_biobank_qc_traceability(self) -> Dict[str, Any]:
        """
        Run QC to trace Biobank entries through Analyte → Experiment → Aligned
        and report consistency of participant_id linkage across models.

        Returns:
            Dict[str, Any]: A nested dictionary of traceability results per biobank entry.
        """
        report = defaultdict(dict)

        for biobank in Biobank.objects.all():
            biobank_id = biobank.biobank_id
            participant_id = biobank.participant_id_id
            result = {
                "participant_id": participant_id,
                "analytes": [],
                "experiments": [],
                "alignments": [],
                "issues": [],
            }

            # Step 1: Check analytes
            for analyte in biobank.child_analytes.all():
                result["analytes"].append(analyte.analyte_id)
                if analyte.participant_id_id != participant_id:
                    result["issues"].append(
                        f"Analyte {analyte.analyte_id} has mismatched participant_id: {analyte.participant_id_id}"
                    )

            # Step 2: Check experiments
            for exp in biobank.experiments.all():
                result["experiments"].append(exp.experiment_id)
                if exp.participant_id_id != participant_id:
                    result["issues"].append(
                        f"Experiment {exp.experiment_id} has mismatched participant_id: {exp.participant_id}"
                    )

            # Step 3: Check alignments
            for aln in biobank.alignments.all():
                result["alignments"].append(aln.aligned_id)
                if aln.participant_id_id != participant_id:
                    result["issues"].append(
                        f"Alignment {aln.aligned_id} has mismatched participant_id: {aln.participant_id}"
                    )
            if result["issues"] != []:
                report[biobank_id] = result

        with open("tests/results/biobank_qc_output.json", "w") as f:
            json.dump(report, f, indent=4)
        print(len(report))
        return dict(report)


class AnalyteTests(TestCase):
    fixtures = ["dump.json"]

    def test_run_analyte_qc_traceability(self) -> Dict[str, Any]:
        """
        Run QC to trace Analyte entries through Experiment → Aligned,
        reporting consistency of participant_id linkage across models.
        """
        report = defaultdict(dict)
        all_analytes = Analyte.objects.all()
        warning_count = 0
        error_count = 0
        analyte_count = len(all_analytes)
        for analyte in all_analytes:
            analyte_id = analyte.analyte_id
            participant_id = analyte.participant_id_id
            result = {
                "participant_id": participant_id,
                "experiments": [],
                "alignments": [],
                "warnings": [],
                "errors": [],
            }

            for exp_table, exp_model in model_map.items():
                if not exp_table.startswith("experiment_"):
                    continue

                experiments = exp_model.objects.filter(analyte_id=analyte)
                for exp in experiments:
                    exp_id_field = f"{exp_table}_id"
                    exp_id = getattr(exp, exp_id_field, None)
                    if not exp_id:
                        result["errors"].append(
                            f"Missing experiment ID on {exp_table} object"
                        )
                        continue

                    result["experiments"].append(exp_id)

                    if participant_id not in exp_id:
                        result["warnings"].append(
                            f"Experiment {exp_id} (table {exp_table}) has mismatched ID (does not contain participant_id)."
                        )

                    # Only lookup alignments for the matching experiment type
                    aligned_table = exp_table.replace("experiment", "aligned")
                    aln_model = model_map.get(aligned_table)
                    aln_fk_field = f"{exp_table}_id"

                    if aln_model:
                        try:
                            alignments = aln_model.objects.filter(**{aln_fk_field: exp})
                        except Exception as e:
                            result["errors"].append(
                                f"Failed lookup in {aligned_table} for {exp_id}: {str(e)}"
                            )
                            continue

                        for aln in alignments:
                            aln_id_field = f"{aligned_table}_id"
                            aln_id = getattr(aln, aln_id_field, None)
                            if not aln_id:
                                result["errors"].append(
                                    f"Missing aligned ID on {aligned_table} object linked to {exp_id}"
                                )
                                continue

                            result["alignments"].append(aln_id)

                            if participant_id not in aln_id:
                                result["warnings"].append(
                                    f"Alignment ID {aln_id} does not include participant_id {participant_id}"
                                )
                    else:
                        result["errors"].append(
                            f"No aligned model found for experiment table {exp_table}"
                        )

            if result["errors"] or result["warnings"]:
                report[analyte_id] = result
                warning_count += len(result["warnings"])
                error_count += len(result["errors"])

        with open("tests/results/analyte_qc_output.json", "w") as f:
            json.dump(report, f, indent=4)

        print(f"\nWARNINGS: {warning_count}")
        print(f"ERRORS: {error_count}")
        print(f"for {len(report)} objects out of {analyte_count} analytes")
        return dict(report)


class ExperimentTests(TestCase):
    fixtures = ["dump.json"]

    experiment_model_map = {
        "dna_short_read": {
            "experiment_model": ExperimentDNAShortRead,
            "alegnment_model": AlignedDNAShortRead,
            "exp_fk": "experiment_dna_short_read_id",
            "aln_fk": "aligned_dna_short_read_id",
        },
        "rna_short_read": {
            "experiment_model": ExperimentRNAShortRead,
            "alegnment_model": AlignedRNAShortRead,
            "exp_fk": "experiment_rna_short_read_id",
            "aln_fk": "aligned_rna_short_read_id",
        },
        "nanopore": {
            "experiment_model": ExperimentNanopore,
            "alegnment_model": AlignedNanopore,
            "exp_fk": "experiment_nanopore_id",
            "aln_fk": "aligned_nanopore_id",
        },
        "pac_bio": {
            "experiment_model": ExperimentPacBio,
            "alegnment_model": AlignedPacBio,
            "exp_fk": "experiment_pac_bio_id",
            "aln_fk": "aligned_pac_bio_id",
        },
    }

    def test_run_experiment_qc_traceability(self) -> Dict[str, Any]:
        report = defaultdict(dict)
        warning_count = 0
        error_count = 0

        for exp_type, conf in self.experiment_model_map.items():
            exp_model = conf["experiment_model"]
            aln_model = conf["alegnment_model"]
            exp_fk_field = conf["exp_fk"]
            aln_id_field = conf["aln_fk"]

            for exp in exp_model.objects.all():
                exp_id = getattr(exp, exp_fk_field, None)
                analyte = getattr(exp, "analyte_id", None)
                participant_id = analyte.participant_id_id if analyte else "UNKNOWN"

                result = {
                    "participant_id": participant_id,
                    "analyte_id": getattr(analyte, "analyte_id", None),
                    "experiment_id": exp_id,
                    "alignments": [],
                    "warnings": [],
                    "errors": [],
                }

                if not exp_id:
                    result["errors"].append("Missing experiment ID.")
                    continue

                if participant_id not in exp_id:
                    result["warnings"].append(
                        f"Experiment {exp_id} does not include participant_id {participant_id}"
                    )

                if not analyte:
                    result["errors"].append(f"Missing analyte for experiment {exp_id}")
                elif analyte.participant_id_id != participant_id:
                    result["errors"].append(
                        f"Analyte {analyte.analyte_id} has mismatched participant_id: {analyte.participant_id_id}"
                    )

                try:
                    alignments = aln_model.objects.filter(**{exp_fk_field: exp})
                    for aln in alignments:
                        aln_id = getattr(aln, aln_id_field, None)
                        result["alignments"].append(aln_id)

                        if participant_id not in aln_id:
                            result["warnings"].append(
                                f"Alignment {aln_id} does not include participant_id {participant_id}"
                            )
                except Exception as e:
                    result["errors"].append(
                        f"Failed to query alignments for {exp_id}: {str(e)}"
                    )

                if result["errors"] or result["warnings"]:
                    report[exp_id] = result
                    warning_count += len(result["warnings"])
                    error_count += len(result["errors"])

        with open("tests/results/experiment_qc_output.json", "w") as f:
            json.dump(report, f, indent=4)

        print(f"\nWARNINGS: {warning_count}")
        print(f"ERRORS: {error_count}")
        print(f"Total flagged experiments: {len(report)}")
        return dict(report)


class AlignmentTests(TestCase):
    fixtures = ["dump.json"]

    alignment_model_map = {
        "dna_short_read": {
            "experiment_model": ExperimentDNAShortRead,
            "alignment_model": AlignedDNAShortRead,
            "exp_fk": "experiment_dna_short_read_id",
            "aln_fk": "aligned_dna_short_read_id",
        },
        "rna_short_read": {
            "experiment_model": ExperimentRNAShortRead,
            "alignment_model": AlignedRNAShortRead,
            "exp_fk": "experiment_rna_short_read_id",
            "aln_fk": "aligned_rna_short_read_id",
        },
        "nanopore": {
            "experiment_model": ExperimentNanopore,
            "alignment_model": AlignedNanopore,
            "exp_fk": "experiment_nanopore_id",
            "aln_fk": "aligned_nanopore_id",
        },
        "pac_bio": {
            "experiment_model": ExperimentPacBio,
            "alignment_model": AlignedPacBio,
            "exp_fk": "experiment_pac_bio_id",
            "aln_fk": "aligned_pac_bio_id",
        },
    }

    def test_run_alignment_qc_traceability(self) -> Dict[str, Any]:
        report = defaultdict(dict)
        warning_count = 0
        error_count = 0

        for aln_type, conf in self.alignment_model_map.items():
            aln_model = conf["alignment_model"]
            exp_model = conf["experiment_model"]
            exp_fk_field = conf["exp_fk"]
            aln_id_field = conf["aln_fk"]

            for aln in aln_model.objects.all():
                aln_id = getattr(aln, aln_id_field, None)
                exp = getattr(aln, exp_fk_field, None)
                analyte = getattr(exp, "analyte_id", None) if exp else None
                participant_id = analyte.participant_id_id if analyte else "UNKNOWN"

                result = {
                    "participant_id": participant_id,
                    "analyte_id": getattr(analyte, "analyte_id", None),
                    "experiment_id": getattr(exp, exp_fk_field, None) if exp else None,
                    "alignment_id": aln_id,
                    "warnings": [],
                    "errors": [],
                }

                if not aln_id:
                    result["errors"].append("Missing alignment ID.")
                    continue

                if not exp:
                    result["errors"].append(
                        f"Missing experiment for alignment {aln_id}"
                    )
                elif participant_id not in aln_id:
                    result["warnings"].append(
                        f"Alignment {aln_id} does not include participant_id {participant_id}"
                    )

                if not analyte:
                    result["errors"].append(f"Missing analyte for alignment {aln_id}")
                elif analyte.participant_id_id != participant_id:
                    result["errors"].append(
                        f"Analyte {analyte.analyte_id} has mismatched participant_id: {analyte.participant_id_id}"
                    )

                if result["errors"] or result["warnings"]:
                    import pdb

                    pdb.set_trace()
                    report[aln_id] = result
                    warning_count += len(result["warnings"])
                    error_count += len(result["errors"])

        with open("tests/results/alignment_qc_output.json", "w") as f:
            json.dump(report, f, indent=4)

        print(f"\nWARNINGS: {warning_count}")
        print(f"ERRORS: {error_count}")
        print(f"Total flagged alignments: {len(report)}")
        return dict(report)

    def test_run_cross_traceability_qc(self) -> Dict[str, Any]:
        report = defaultdict(dict)
        pass_checks = 0
        warnings = 0
        errors = 0

        for aln_type, conf in self.alignment_model_map.items():
            aln_model = conf["alignment_model"]
            print(aln_type)
            exp_fk = conf["exp_fk"]
            aln_id_field = conf["aln_fk"]

            for aln in aln_model.objects.all():
                exp = getattr(aln, exp_fk, None)
                analyte = getattr(exp, "analyte_id", None)

                result = {
                    "model": aln_type,
                    "alignment_id": getattr(aln, aln_id_field, None),
                    "experiment_id": None,
                    "analyte": None,
                    "biobank": [],
                    "warnings": [],
                    "errors": [],
                }

                if not exp:
                    result["errors"].append(
                        f"Missing experiment for alignment {result['alignment_id']}"
                    )
                    continue
                else:
                    result["experiment_id"] = exp.pk

                if not analyte:
                    result["errors"].append(
                        f"Missing analyte for experiment {getattr(exp, exp_fk)}"
                    )
                    continue
                else:
                    result["analyte_id"] = analyte.pk

                biobanks = analyte.biobank_set.all()
                result["alt_biobank"] = [bio.pk for bio in biobanks]
                if not biobanks:
                    result["errors"].append(
                        f"Analyte {analyte.analyte_id} not linked to any Biobank"
                    )
                    alternates = Biobank.objects.filter(
                        participant_id=analyte.participant_id
                    )

                    for alternate in alternates:
                        if (
                            not alternate.experiments.all()
                            and not alternate.alignments.all()
                        ):
                            result["warnings"].append(
                                f"Analyte {analyte.analyte_id} may be linked to Biobank {alternate.biobank_id}"
                            )
                    # else:
                    # import pdb; pdb.set_trace()
                # Consistency check
                participant_ids = [
                    getattr(aln, "participant_id_id", None),
                    getattr(exp.analyte_id, "participant_id_id", None),
                    getattr(analyte, "participant_id_id", None),
                ]
                if biobanks:
                    participant_ids.append(biobanks[0].participant_id_id)

                if len(set(pid for pid in participant_ids if pid)) > 1:
                    result["errors"].append(
                        f"Inconsistent participant_ids: {participant_ids}"
                    )

                if result["errors"] or result["warnings"]:
                    report[result["alignment_id"]] = result
                    warnings += len(result["warnings"])
                    errors += len(result["errors"])
                else:
                    pass_checks += 1

        with open("tests/results/cross_traceability_qc_output.json", "w") as f:
            json.dump(report, f, indent=4)

        print(f"\nCROSS TRACEABILITY WARNINGS: {warnings}")
        print(f"CROSS TRACEABILITY ERRORS: {errors}")
        print(f"Total flagged alignments: {len(report)}")
        print(f"Passed: {pass_checks}")
        return dict(report)


def dump_test_data(self, file_name: str = "test_results.json") -> None:
    out = StringIO()
    call_command("dumpdata", "--exclude", "contenttypes", "--indent", "2", stdout=out)
    with open(file_name, "w") as f:
        f.write(out.getvalue())
