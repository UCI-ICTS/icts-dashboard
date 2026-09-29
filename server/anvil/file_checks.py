#!/usr/bin/env python
# anvil/file_checks.py

"""
Pre-flight genomic file checks for AnVIL uploads.

These are the Dashboard-side, pre-submission versions of the DCC's file-level
workflows in UW-GAC/gregor-file-checks:

- validate_md5.wdl      -> declared md5sum vs computed file hash
- check_bam_sample.wdl  -> BAM/CRAM @RG SM tags vs experiment_sample_id chain
- check_vcf_samples.wdl -> VCF header samples vs aligned-set sample chain
- check_bucket_paths    -> file resolvability (local analogue)

Each check yields one of three statuses, mirroring the DCC's md5 semantics:

- PASS        the check ran and matched
- FAIL        the check ran and did not match (blocks the upload)
- UNVERIFIED  the check could not run (missing file, missing tooling);
              recorded as a warning, not an error

File access is abstracted behind providers so the same checks run against a
local staging directory (deterministic tests, synthetic demo files) or a real
S3 bucket via the existing s3 app credentials.
"""

import hashlib
from pathlib import Path

try:
    import pysam
except ImportError:  # pragma: no cover - environment without pysam
    pysam = None


PASS = "PASS"
FAIL = "FAIL"
UNVERIFIED = "UNVERIFIED"

# Index-file extension expectations by data-file extension. This is a
# URI-string check, so it runs even when the file itself is unavailable.
# It catches real production dirt such as index URIs ending in .bam.
EXPECTED_INDEX_SUFFIXES = {
    ".cram": (".crai",),
    ".bam": (".bai", ".csi"),
    ".vcf.gz": (".tbi", ".csi"),
}


def strip_uri_bucket(uri: str) -> str:
    """
    Reduce a storage URI to its bucket-relative path.

    'gs://bucket/cram/a.cram' -> 'cram/a.cram'
    's3://bucket/cram/a.cram' -> 'cram/a.cram'
    '/already/local/a.cram'   -> 'already/local/a.cram'
    """

    remainder = uri
    for scheme in ("gs://", "s3://"):
        if remainder.startswith(scheme):
            remainder = remainder[len(scheme):]
            # Drop the bucket segment.
            _bucket, _sep, remainder = remainder.partition("/")
            return remainder

    return remainder.lstrip("/")


class LocalFileProvider:
    """
    Resolve storage URIs against a local staging directory.

    A URI resolves to <root>/<bucket-relative path>, falling back to
    <root>/<basename> so flat staging directories also work.
    """

    name = "local"

    def __init__(self, *, root):
        self.root = Path(root)

    def materialize(self, *, uri: str) -> Path | None:
        """Return a local Path for the URI, or None if unavailable."""

        if not uri:
            return None

        candidates = [
            self.root / strip_uri_bucket(uri),
            self.root / Path(strip_uri_bucket(uri)).name,
        ]

        for candidate in candidates:
            if candidate.is_file():
                return candidate

        return None


class S3FileProvider:
    """
    Resolve storage URIs by downloading from S3 into a staging directory.

    With bucket set, every URI resolves to that bucket at
    key_prefix + bucket-relative path (useful for synthetic-file integration
    tests against a dedicated test prefix). Without it, only s3:// URIs
    resolve, against their own bucket.

    Uses the s3 app's credentialed client with a streaming download, so it
    never loads whole objects into memory.
    """

    name = "s3"

    def __init__(self, *, staging_dir, bucket: str | None = None,
                 key_prefix: str = ""):
        self.staging_dir = Path(staging_dir)
        self.bucket = bucket
        self.key_prefix = key_prefix
        self._client = None

    def _get_client(self):
        if self._client is None:
            from s3.services import get_s3_client

            self._client = get_s3_client()

        return self._client

    def _resolve_object(self, *, uri: str) -> tuple[str, str] | None:
        if self.bucket:
            return self.bucket, self.key_prefix + strip_uri_bucket(uri)

        if uri.startswith("s3://"):
            remainder = uri[len("s3://"):]
            bucket, _sep, key = remainder.partition("/")

            if bucket and key:
                return bucket, key

        return None

    def materialize(self, *, uri: str) -> Path | None:
        """Download the object to the staging dir; return its local Path."""

        resolved = self._resolve_object(uri=uri)

        if resolved is None:
            return None

        bucket, key = resolved
        local_path = self.staging_dir / strip_uri_bucket(uri)

        if local_path.is_file():
            return local_path

        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._get_client().download_file(bucket, key, str(local_path))
        except Exception:
            return None

        return local_path


def compute_file_md5(*, path) -> str:
    """Stream-hash a file, returning the hex md5 digest."""

    digest = hashlib.md5()

    with open(path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def read_alignment_sm_tags(*, path) -> list[str] | None:
    """
    Return the distinct @RG SM values from a BAM/CRAM header.

    Header reads never require the CRAM reference. Returns None when pysam
    is unavailable or the header cannot be parsed.
    """

    if pysam is None:
        return None

    mode = "rc" if str(path).endswith(".cram") else "rb"

    try:
        with pysam.AlignmentFile(str(path), mode, check_sq=False) as file_handle:
            read_groups = file_handle.header.to_dict().get("RG", [])
    except (OSError, ValueError):
        return None

    samples = []

    for read_group in read_groups:
        sample = read_group.get("SM")

        if sample is not None and sample not in samples:
            samples.append(sample)

    return samples


def read_vcf_samples(*, path) -> list[str] | None:
    """Return the sample IDs from a VCF header, or None if unreadable."""

    if pysam is None:
        return None

    try:
        with pysam.VariantFile(str(path)) as file_handle:
            return list(file_handle.header.samples)
    except (OSError, ValueError):
        return None


def check_index_uri(*, file_uri: str, index_uri: str) -> dict | None:
    """
    Check that an index URI has a plausible extension for its data file.

    This is the string-only half of the DCC's file checks: it needs no file
    access, so it always produces PASS or FAIL when both URIs are present.
    Returns None when the data file's extension has no expectation.
    """

    if not file_uri or not index_uri:
        return None

    expected_suffixes = None

    for file_suffix, index_suffixes in EXPECTED_INDEX_SUFFIXES.items():
        if file_uri.endswith(file_suffix):
            expected_suffixes = index_suffixes
            break

    if expected_suffixes is None:
        return None

    matched = any(
        index_uri.endswith(suffix)
        for suffix in expected_suffixes
    )

    return {
        "check": "index_extension",
        "status": PASS if matched else FAIL,
        "detail": (
            None
            if matched
            else (
                f"index '{Path(index_uri).name}' does not end with "
                f"{' or '.join(expected_suffixes)} expected for "
                f"'{Path(file_uri).name}'"
            )
        ),
    }


def check_file_md5(*, local_path, declared_md5: str) -> dict:
    """Compare a declared md5sum with the file's computed hash."""

    if local_path is None:
        return {
            "check": "md5",
            "status": UNVERIFIED,
            "detail": "file not available to hash",
        }

    if not declared_md5:
        return {
            "check": "md5",
            "status": UNVERIFIED,
            "detail": "no declared md5sum to compare",
        }

    computed = compute_file_md5(path=local_path)

    if computed == declared_md5.lower():
        return {"check": "md5", "status": PASS, "detail": None}

    return {
        "check": "md5",
        "status": FAIL,
        "detail": (
            f"declared md5 {declared_md5} != computed {computed}"
        ),
    }


def check_alignment_samples(*, local_path, expected_samples: list[str]) -> dict:
    """Compare BAM/CRAM @RG SM tags with the expected sample set."""

    if local_path is None:
        return {
            "check": "alignment_sample",
            "status": UNVERIFIED,
            "detail": "file not available to read header",
        }

    file_samples = read_alignment_sm_tags(path=local_path)

    if file_samples is None:
        return {
            "check": "alignment_sample",
            "status": UNVERIFIED,
            "detail": "alignment header unreadable (pysam unavailable "
                      "or file malformed)",
        }

    if set(file_samples) == set(expected_samples):
        return {"check": "alignment_sample", "status": PASS, "detail": None}

    return {
        "check": "alignment_sample",
        "status": FAIL,
        "detail": (
            f"header SM tags {sorted(file_samples)} != expected "
            f"{sorted(expected_samples)}"
        ),
    }


def check_vcf_sample_set(*, local_path, expected_samples: list[str]) -> dict:
    """Compare VCF header samples with the expected aligned-set chain."""

    if local_path is None:
        return {
            "check": "vcf_samples",
            "status": UNVERIFIED,
            "detail": "file not available to read header",
        }

    file_samples = read_vcf_samples(path=local_path)

    if file_samples is None:
        return {
            "check": "vcf_samples",
            "status": UNVERIFIED,
            "detail": "VCF header unreadable (pysam unavailable "
                      "or file malformed)",
        }

    if set(file_samples) == set(expected_samples):
        return {"check": "vcf_samples", "status": PASS, "detail": None}

    return {
        "check": "vcf_samples",
        "status": FAIL,
        "detail": (
            f"VCF samples {sorted(file_samples)} != expected "
            f"{sorted(expected_samples)}"
        ),
    }
