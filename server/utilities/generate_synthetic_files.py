#!/usr/bin/env python
# utilities/generate_synthetic_files.py

"""Regenerate the persistent genomic files used by test_fixture_valid.json."""

import hashlib
import json
import shutil
from pathlib import Path

import pysam


CONTIG = "chr1"
REFERENCE = "ACGTACGTGGCCTTAA" * 8
READ_LENGTH = 10

ALIGNMENT_TABLES = {
    "aligneddnashortread": {
        "file": "aligned_dna_short_read_file",
        "index": "aligned_dna_short_read_index_file",
        "experiment_fk": "experiment_dna_short_read_id",
        "experiment_model": "experimentdnashortread",
    },
    "alignedrnashortread": {
        "file": "aligned_rna_short_read_file",
        "index": "aligned_rna_short_read_index_file",
        "experiment_fk": "experiment_rna_short_read_id",
        "experiment_model": "experimentrnashortread",
    },
    "alignednanopore": {
        "file": "aligned_nanopore_file",
        "index": "aligned_nanopore_index_file",
        "experiment_fk": "experiment_nanopore_id",
        "experiment_model": "experimentnanopore",
    },
    "alignedpacbio": {
        "file": "aligned_pac_bio_file",
        "index": "aligned_pac_bio_index_file",
        "experiment_fk": "experiment_pac_bio_id",
        "experiment_model": "experimentpacbio",
    },
}

VCF_TABLES = {
    "calledvariantsdnashortread": {
        "file": "called_variants_dna_file",
        "set_fk": "aligned_dna_short_read_set_id",
        "set_model": "aligneddnashortreadset",
        "members": "aligned_dna_short_read_id",
        "aligned_model": "aligneddnashortread",
        "experiment_fk": "experiment_dna_short_read_id",
        "experiment_model": "experimentdnashortread",
    },
    "calledvariantsnanopore": {
        "file": "called_variants_dna_file",
        "set_fk": "aligned_nanopore_set_id",
        "set_model": "alignednanoporeset",
        "members": "aligned_nanopore_id",
        "aligned_model": "alignednanopore",
        "experiment_fk": "experiment_nanopore_id",
        "experiment_model": "experimentnanopore",
    },
    "calledvariantspacbio": {
        "file": "called_variants_dna_file",
        "set_fk": "aligned_pac_bio_set_id",
        "set_model": "alignedpacbioset",
        "members": "aligned_pac_bio_id",
        "aligned_model": "alignedpacbio",
        "experiment_fk": "experiment_pac_bio_id",
        "experiment_model": "experimentpacbio",
    },
}


def relative_uri_path(uri: str) -> Path:
    if uri.startswith(("gs://", "s3://")):
        return Path(uri.split("/", 3)[3])
    return Path(uri.lstrip("/"))


def file_md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_offset(key: str, modulo: int) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % modulo


def write_reference(root: Path) -> Path:
    path = root / "_reference" / "synthetic.fa"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f">{CONTIG}\n{REFERENCE}\n", encoding="utf-8")
    pysam.faidx(str(path))
    return path


def write_alignment(
    *,
    path: Path,
    index_path: Path,
    sample: str,
    reference_path: Path,
    key: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_cram = path.suffix == ".cram"
    mode = "wc" if is_cram else "wb"
    header = {
        "HD": {"VN": "1.6", "SO": "coordinate"},
        "SQ": [{"SN": CONTIG, "LN": len(REFERENCE)}],
        "RG": [{"ID": "rg1", "SM": sample}],
        "CO": [f"synthetic fixture for {key}"],
    }
    start = stable_offset(key, len(REFERENCE) - READ_LENGTH)

    with pysam.AlignmentFile(
        str(path),
        mode,
        header=header,
        reference_filename=str(reference_path),
    ) as output:
        read = pysam.AlignedSegment(output.header)
        read.query_name = f"synthetic-{stable_offset(key, 1_000_000)}"
        read.query_sequence = REFERENCE[start:start + READ_LENGTH]
        read.flag = 0
        read.reference_id = 0
        read.reference_start = start
        read.mapping_quality = 60
        read.cigar = [(0, READ_LENGTH)]
        read.query_qualities = pysam.qualitystring_to_array("I" * READ_LENGTH)
        read.set_tag("RG", "rg1")
        output.write(read)

    pysam.index(str(path))
    generated_index = Path(str(path) + (".crai" if is_cram else ".bai"))
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if generated_index != index_path:
        shutil.move(generated_index, index_path)


def write_vcf(*, path: Path, samples: list[str], key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = pysam.VariantHeader()
    header.add_line(f"##contig=<ID={CONTIG},length={len(REFERENCE)}>")
    header.add_line(
        '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">'
    )
    header.add_line(f"##synthetic_source={key}")
    for sample in samples:
        header.add_sample(sample)

    start = stable_offset(key, len(REFERENCE) - 2)
    ref = REFERENCE[start]
    alt = "A" if ref != "A" else "G"

    with pysam.VariantFile(str(path), "wz", header=header) as output:
        record = output.new_record(
            contig=CONTIG,
            start=start,
            stop=start + 1,
            alleles=(ref, alt),
        )
        for sample in samples:
            record.samples[sample]["GT"] = (0, 1)
        output.write(record)

    pysam.tabix_index(str(path), preset="vcf", force=True)


def generate_fixture_files(*, fixture_path: Path, output_root: Path) -> dict:
    rows = json.loads(fixture_path.read_text(encoding="utf-8"))
    by_model = {}
    for row in rows:
        model = row["model"].split(".", 1)[-1]
        by_model.setdefault(model, {})[str(row["pk"])] = row["fields"]

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)
    reference_path = write_reference(output_root)

    generated = 0
    md5_updates = 0

    for model, config in ALIGNMENT_TABLES.items():
        for pk, fields in by_model.get(model, {}).items():
            file_path = output_root / relative_uri_path(fields[config["file"]])
            index_path = output_root / relative_uri_path(fields[config["index"]])
            experiment = by_model[config["experiment_model"]][
                str(fields[config["experiment_fk"]])
            ]
            write_alignment(
                path=file_path,
                index_path=index_path,
                sample=experiment["experiment_sample_id"],
                reference_path=reference_path,
                key=f"{model}:{pk}",
            )
            fields["md5sum"] = file_md5(file_path)
            generated += 1
            md5_updates += 1

    for model, config in VCF_TABLES.items():
        for pk, fields in by_model.get(model, {}).items():
            aligned_set = by_model[config["set_model"]][
                str(fields[config["set_fk"]])
            ]
            samples = []
            for aligned_pk in aligned_set[config["members"]]:
                aligned = by_model[config["aligned_model"]][str(aligned_pk)]
                experiment = by_model[config["experiment_model"]][
                    str(aligned[config["experiment_fk"]])
                ]
                sample = experiment["experiment_sample_id"]
                if sample not in samples:
                    samples.append(sample)

            file_path = output_root / relative_uri_path(fields[config["file"]])
            write_vcf(path=file_path, samples=samples, key=f"{model}:{pk}")
            fields["md5sum"] = file_md5(file_path)
            generated += 1
            md5_updates += 1

    # Remove the generation-only reference; CRAM headers remain readable
    # without it, which is all validate-files needs.
    shutil.rmtree(output_root / "_reference")
    fixture_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    index_count = sum(
        1
        for path in output_root.rglob("*")
        if path.suffix in {".crai", ".bai", ".tbi", ".csi"}
    )
    return {
        "data_file_count": generated,
        "index_file_count": index_count,
        "md5_update_count": md5_updates,
    }


if __name__ == "__main__":
    server_root = Path(__file__).resolve().parents[1]
    result = generate_fixture_files(
        fixture_path=server_root / "tests/fixtures/test_fixture_valid.json",
        output_root=server_root / "tests/fixtures/files",
    )
    print(
        f"Generated {result['data_file_count']} data files, "
        f"{result['index_file_count']} indexes, and updated "
        f"{result['md5_update_count']} MD5 values."
    )
