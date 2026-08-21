#!/usr/bin/env python
# utilities/json_schema_maker.py

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen


__version__ = "0.2"
__status__ = "TEST"

DEFAULT_MODEL_URL = (
    "https://raw.githubusercontent.com/UW-GAC/gregor_data_models/"
    "main/GREGoR_data_model.json"
)
BUNDLE_FORMAT_VERSION = 1

DATA_TYPE_MAP = {
    "string": "string",
    "date": "string",
    "integer": "integer",
    "float": "number",
    "boolean": "boolean",
    "object": "object",
    "array": "array",
    "enumeration": "string",
}


def usr_args() -> argparse.Namespace:
    """Parse command-line arguments for schema bundle generation."""

    parser = argparse.ArgumentParser(
        prog="json_schema_maker",
        description=(
            "Generate a versioned GREGoR schema bundle from the canonical "
            "data model JSON."
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    parser.add_argument(
        "-i",
        "--input",
        default=DEFAULT_MODEL_URL,
        help="Canonical GREGoR data model JSON path or URL.",
    )
    parser.add_argument(
        "-o",
        "--output-root",
        default="utilities/json_schemas",
        help=(
            "Parent directory for versioned bundles. The model version is "
            "appended automatically (for example, <root>/v1.12)."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing bundle for the same model version.",
    )

    return parser.parse_args()


def _sha256(data: bytes) -> str:
    """Return the SHA-256 digest of bytes."""

    return hashlib.sha256(data).hexdigest()


def _json_bytes(data: dict) -> bytes:
    """Serialize generated JSON deterministically."""

    return (json.dumps(data, indent=4, sort_keys=True) + "\n").encode("utf-8")


def _read_model_source(source: str) -> tuple[dict, bytes, str]:
    """Read a canonical model from a local path or HTTP(S) URL."""

    parsed = urlparse(source)

    if parsed.scheme in ("http", "https"):
        with urlopen(source, timeout=30) as response:
            raw_model = response.read()
        source_name = source
    else:
        source_path = Path(source)
        raw_model = source_path.read_bytes()
        source_name = source_path.name

    return json.loads(raw_model), raw_model, source_name


def _validate_model(model: dict) -> str:
    """Validate the minimum canonical-model structure and return its version."""

    version = str(model.get("version", "")).removeprefix("v")
    tables = model.get("tables")

    if not version:
        raise ValueError("GREGoR data model is missing a version.")

    if not isinstance(tables, list) or not tables:
        raise ValueError("GREGoR data model must contain a non-empty tables list.")

    table_names = [table.get("table") for table in tables]

    if any(not table_name for table_name in table_names):
        raise ValueError("Every GREGoR data model table must have a name.")

    if len(table_names) != len(set(table_names)):
        raise ValueError("GREGoR data model contains duplicate table names.")

    for table in tables:
        columns = table.get("columns", [])
        column_names = [column.get("column") for column in columns]

        if any(not column_name for column_name in column_names):
            raise ValueError(
                f"Table {table['table']} contains a column without a name."
            )

        if len(column_names) != len(set(column_names)):
            raise ValueError(f"Table {table['table']} contains duplicate column names.")

    return version


def convert_column(column: dict) -> dict:
    """
    Convert one canonical model column into a JSON Schema property.

    Standard JSON Schema keywords drive row validation. GREGoR relational and
    workflow metadata are retained as ``x-*`` annotations so each
    generated schema remains self-describing without changing Draft 7
    validation behavior.
    """

    data_type = column.get("data_type", "string").lower()
    json_type = DATA_TYPE_MAP.get(data_type, "string")
    value_schema = {"type": json_type}

    if "enumerations" in column:
        enumerations = column["enumerations"]
        value_schema["enum"] = (
            enumerations if isinstance(enumerations, list) else [enumerations]
        )

    description = column.get("description", "")
    notes = column.get("notes")

    if notes:
        description = (
            f"{description}\n\nNotes: {notes}" if description else f"Notes: {notes}"
        )

    if description:
        value_schema["description"] = description

    if "examples" in column:
        examples = column["examples"]
        value_schema["examples"] = (
            examples if isinstance(examples, list) else [examples]
        )

    if column.get("is_bucket_path") is True:
        value_schema["pattern"] = r"^(https?|gs|s3):\/\/.+$"

    if column.get("multi_value_delimiter") == "|":
        property_schema = {"type": "array", "items": value_schema}
    else:
        property_schema = value_schema

    if column.get("is_bucket_path") is True:
        property_schema["x-is_bucket_path"] = True

    if column.get("primary_key") is True:
        property_schema["x-primary-key"] = True

    if column.get("references"):
        property_schema["x-references"] = column["references"]

    required = column.get("required")

    if isinstance(required, str) and required.startswith("CONDITIONAL"):
        property_schema["x-required-condition"] = required

    return property_schema


def _table_schema(*, table: dict, model_version: str) -> dict:
    """Create one Draft 7 JSON Schema from a canonical table definition."""

    table_name = table["table"]
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"urn:gregor:data-model:{model_version}:{table_name}",
        "title": table_name,
        "version": model_version,
        "type": "object",
        "required": [],
        "definitions": {},
        "properties": {},
    }

    if table.get("required") is not None:
        schema["x-table-required"] = table["required"]

    for column in table.get("columns", []):
        if column.get("required") is True:
            schema["required"].append(column["column"])

        schema["properties"][column["column"]] = convert_column(column)

    return schema


def build_schema_bundle(
    *,
    source: str,
    output_root: str | Path,
    force: bool = False,
) -> Path:
    """
    Build a complete, versioned GREGoR schema bundle.

    The bundle contains the exact canonical input as ``GREGoR_data_model.json``, one
    generated Draft 7 schema per table, and a deterministic manifest containing
    source and generated-file hashes. The target version is derived from the
    model; callers cannot accidentally write version 1.12 rules into v1.11.
    """

    model, raw_model, source_name = _read_model_source(source)
    model_version = _validate_model(model)

    output_root = Path(output_root).resolve()
    bundle_path = output_root / f"v{model_version}"

    if bundle_path.exists() and not force:
        raise FileExistsError(
            f"Schema bundle already exists: {bundle_path}. Use --force to replace it."
        )

    output_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=f".v{model_version}-",
        dir=output_root,
    ) as temporary_directory:
        temporary_path = Path(temporary_directory)
        (temporary_path / "GREGoR_data_model.json").write_bytes(raw_model)

        schema_hashes = {}

        for table in model["tables"]:
            schema_name = f"{table['table']}.json"
            schema_data = _json_bytes(
                _table_schema(table=table, model_version=model_version)
            )
            (temporary_path / schema_name).write_bytes(schema_data)
            schema_hashes[schema_name] = _sha256(schema_data)

        manifest = {
            "bundle_format_version": BUNDLE_FORMAT_VERSION,
            "generator": {
                "name": "icts-dashboard-json-schema-maker",
                "version": __version__,
            },
            "gregor_model_version": model_version,
            "source": source_name,
            "source_sha256": _sha256(raw_model),
            "table_count": len(model["tables"]),
            "schemas": schema_hashes,
        }
        (temporary_path / "schema_manifest.json").write_bytes(_json_bytes(manifest))

        if bundle_path.exists():
            shutil.rmtree(bundle_path)

        os.replace(temporary_path, bundle_path)

    return bundle_path


def main() -> None:
    """Generate a versioned schema bundle from command-line options."""

    options = usr_args()
    bundle_path = build_schema_bundle(
        source=options.input,
        output_root=options.output_root,
        force=options.force,
    )
    print(bundle_path)


if __name__ == "__main__":
    main()
