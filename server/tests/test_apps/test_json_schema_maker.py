#!/usr/bin/env python
# tests/test_apps/test_json_schema_maker.py

import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from utilities.json_schema_maker import build_schema_bundle


TEST_MODEL = {
    "name": "GREGoR Data Model",
    "version": "1.12",
    "tables": [
        {
            "table": "family",
            "required": True,
            "columns": [
                {
                    "column": "family_id",
                    "primary_key": True,
                    "required": True,
                    "data_type": "string",
                },
                {
                    "column": "consanguinity",
                    "required": True,
                    "data_type": "enumeration",
                    "enumerations": ["None suspected", "Present"],
                },
            ],
        },
        {
            "table": "participant",
            "required": True,
            "columns": [
                {
                    "column": "participant_id",
                    "primary_key": True,
                    "required": True,
                    "data_type": "string",
                },
                {
                    "column": "family_id",
                    "required": True,
                    "data_type": "string",
                    "references": "> family.family_id",
                },
                {
                    "column": "reported_race",
                    "data_type": "enumeration",
                    "enumerations": ["White", "Asian"],
                    "multi_value_delimiter": "|",
                },
                {
                    "column": "missing_variant_details",
                    "data_type": "string",
                    "required": "CONDITIONAL (missing_variant_case = 'Yes')",
                },
            ],
        },
    ],
}


class JsonSchemaBundleTests(SimpleTestCase):
    def _write_model(self, directory: str) -> Path:
        model_path = Path(directory) / "GREGoR_data_model.json"
        model_path.write_text(json.dumps(TEST_MODEL, indent=2), encoding="utf-8")
        return model_path

    @staticmethod
    def _bundle_files(bundle_path: Path) -> dict[str, bytes]:
        return {path.name: path.read_bytes() for path in sorted(bundle_path.iterdir())}

    def test_build_schema_bundle_derives_version_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = self._write_model(temp_dir)
            output_root = Path(temp_dir) / "schemas"

            bundle_path = build_schema_bundle(
                source=str(model_path),
                output_root=output_root,
            )

            self.assertEqual(bundle_path, (output_root / "v1.12").resolve())

            self.assertEqual(
                (bundle_path / "GREGoR_data_model.json").read_bytes(),
                model_path.read_bytes(),
            )
            self.assertTrue((bundle_path / "family.json").exists())
            self.assertTrue((bundle_path / "participant.json").exists())

            manifest = json.loads(
                (bundle_path / "schema_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["gregor_model_version"], "1.12")
            self.assertEqual(manifest["table_count"], 2)
            self.assertEqual(
                set(manifest["schemas"]),
                {"family.json", "participant.json"},
            )

    def test_generated_schema_retains_relational_annotations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = self._write_model(temp_dir)
            bundle_path = build_schema_bundle(
                source=str(model_path),
                output_root=Path(temp_dir) / "schemas",
            )

            participant = json.loads(
                (bundle_path / "participant.json").read_text(encoding="utf-8")
            )

            self.assertEqual(
                participant["$id"],
                "urn:gregor:data-model:1.12:participant",
            )
            self.assertTrue(participant["x-table-required"])
            self.assertTrue(
                participant["properties"]["participant_id"]["x-primary-key"]
            )
            self.assertEqual(
                participant["properties"]["family_id"]["x-references"],
                "> family.family_id",
            )
            self.assertEqual(
                participant["properties"]["reported_race"]["type"],
                "array",
            )
            self.assertEqual(
                participant["properties"]["reported_race"]["items"]["enum"],
                ["White", "Asian"],
            )
            self.assertEqual(
                participant["properties"]["missing_variant_details"][
                    "x-required-condition"
                ],
                "CONDITIONAL (missing_variant_case = 'Yes')",
            )

    def test_generated_bundle_is_deterministic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = self._write_model(temp_dir)

            first_bundle = build_schema_bundle(
                source=str(model_path),
                output_root=Path(temp_dir) / "first",
            )
            second_bundle = build_schema_bundle(
                source=str(model_path),
                output_root=Path(temp_dir) / "second",
            )

            self.assertEqual(
                self._bundle_files(first_bundle),
                self._bundle_files(second_bundle),
            )

    def test_existing_bundle_requires_force_to_replace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = self._write_model(temp_dir)
            output_root = Path(temp_dir) / "schemas"
            bundle_path = build_schema_bundle(
                source=str(model_path),
                output_root=output_root,
            )
            stale_file = bundle_path / "stale.json"
            stale_file.write_text("stale", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                build_schema_bundle(
                    source=str(model_path),
                    output_root=output_root,
                )

            replaced_path = build_schema_bundle(
                source=str(model_path),
                output_root=output_root,
                force=True,
            )

            self.assertEqual(replaced_path, bundle_path)
            self.assertFalse(stale_file.exists())

    def test_invalid_model_is_rejected_before_writing_bundle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "GREGoR_data_model.json"
            model_path.write_text(
                json.dumps({"version": "1.12", "tables": []}),
                encoding="utf-8",
            )
            output_root = Path(temp_dir) / "schemas"

            with self.assertRaisesMessage(ValueError, "non-empty tables list"):
                build_schema_bundle(
                    source=str(model_path),
                    output_root=output_root,
                )

            self.assertFalse((output_root / "v1.12").exists())
