#!/usr/bin/env python3
# tests/test_apps/test_config_selectors.py

import zipfile
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from metadata.models import Family
from config.selectors import (
    TableValidator, remove_na, multi_value_split, response_status, response_constructor,
    validate_url, generate_tsv, generate_zip, compare_data, bulk_model_retrieve, bulk_retrieve
)

class TableValidatorTests(TestCase):
    """Tests for TableValidator class."""
    
    fixtures = ['tests/fixtures/test_fixture.json']  # Auto-load fixture

    def setUp(self):
        self.validator = TableValidator()

    def test_fixture_loaded(self):
        """Ensure the test fixture data is loaded."""
        self.assertGreater(Family.objects.count(), 0, "Fixture data was not loaded")

    def test_validate_json_valid_case(self):
        """Tests JSON validation with valid input."""
        test_json = {"family_id": "Alice", "consanguinity": "Suspected"}
        self.validator.validate_json(test_json, "family")
        self.assertTrue(self.validator.valid)
        self.assertEqual(self.validator.errors, [])

    def test_validate_json_invalid_case(self):
        """Tests JSON validation with invalid input."""
        test_json = {"family_id": "Alice", "consanguinity": "Nope"}  # invalid enum
        self.validator.validate_json(test_json, "family")

        self.assertFalse(self.validator.valid)
        self.assertGreater(len(self.validator.errors), 0)

    def test_validate_json_missing_schema(self):
        """Tests handling of a missing schema file."""
        self.validator.validate_json({"name": "Alice"}, "invalid file")
        
        self.assertFalse(self.validator.valid)
        self.assertIn("Schema file not found", self.validator.errors[0])

    def test_get_validation_results(self):
        """Tests the get_validation_results method."""
        test_json = {"family_id": "Alice", "consanguinity": "Nope"}  # invalid enum
        self.validator.validate_json(test_json, "family")
        results = self.validator.get_validation_results()
        self.assertFalse(results["valid"])
        self.assertEqual(results["errors"][0]["field"], "Consanguinity")
        self.assertEqual(results["errors"][0]["error"], 
            "'Nope' is not one of ['None suspected', 'Suspected', 'Present', 'Unknown']"
        )

class UtilityFunctionTests(TestCase):
    """Tests for utility functions."""
    fixtures = ['tests/fixtures/test_fixture.json']  # Auto-load fixture

    def test_remove_na(self):
        """Tests that 'NA' values are correctly removed."""
        test_cases = [
            ({"key1": "NA", "key2": "valid"}, {"key2": "valid"}),
            ({"key1": ["NA"], "key2": "something"}, {"key2": "something"}),
            ({"key1": "test", "key2": "NA"}, {"key1": "test"})
        ]
        
        for input_data, expected_output in test_cases:
            self.assertEqual(remove_na(input_data), expected_output)

    def test_multi_value_split(self):
        """Tests multi-value splitting."""
        test_cases = [
            ({"key1": "value1|value2"}, {"key1": ["value1", "value2"]}),
            ({"key1": "single"}, {"key1": "single"}),
            ({"key1": ["existing"]}, {"key1": ["existing"]})
        ]
        
        for input_data, expected_output in test_cases:
            self.assertEqual(multi_value_split(input_data), expected_output)

    def test_response_status(self):
        """Tests response status determination logic."""
        test_cases = [
            (False, False, status.HTTP_400_BAD_REQUEST),
            (False, True, status.HTTP_400_BAD_REQUEST),
            (True, True, status.HTTP_207_MULTI_STATUS),
            (True, False, status.HTTP_200_OK),
        ]
        
        for accepted, rejected, expected_status in test_cases:
            self.assertEqual(response_status(accepted, rejected), expected_status)

    def test_response_constructor(self):
        """Tests constructing standardized API responses."""
        response = response_constructor("123", "success", 200, "All good", {"data": "test"})
        
        self.assertEqual(response["identifier"], "123")
        self.assertEqual(response["request_status"], "success")
        self.assertEqual(response["status_code"], 200)
        self.assertEqual(response["message"], "All good")
        self.assertEqual(response["data"]["data"], "test")

    def test_validate_url(self):
        """Tests URL validation."""
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://test.com/path?query=value"))

        with self.assertRaises(ValidationError):
            validate_url("")
        with self.assertRaises(ValidationError):
            validate_url(None)
        with self.assertRaises(ValidationError):
            validate_url("htp:/invalid-url")
        with self.assertRaises(ValidationError):
            validate_url("just-a-string")

    def test_generate_tsv(self):
        """Tests TSV generation."""
        data = [{"col1": "A", "col2": "B"}, {"col1": "C", "col2": "D"}]
        tsv = generate_tsv(data)
        self.assertIn("col1\tcol2\nA\tB\nC\tD", tsv)

    def test_generate_zip(self):
        """Tests ZIP file generation."""
        files = {"file1.txt": "Hello World", "file2.txt": "Python Testing"}
        zip_buffer = generate_zip(files)
        
        with zipfile.ZipFile(zip_buffer, "r") as zip_file:
            self.assertIn("file1.txt", zip_file.namelist())
            self.assertEqual(zip_file.read("file1.txt").decode(), "Hello World")

    def test_compare_data(self):
        """Tests data comparison function."""
        old_data = {"name": "Alice", "age": 30}
        new_data = {"name": "Alice", "age": 31}
        result = compare_data(old_data, new_data)
        self.assertEqual(result["age"], "30 to 31")


class BulkModelRetrieveTestCase(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def setUp(self):
        """Retrieve existing families from the fixture instead of creating duplicates."""
        self.family_1 = Family.objects.get(family_id="GREGoR_test-001")
        self.family_2 = Family.objects.get(family_id="GREGoR_test-002")


    def test_bulk_model_retrieve_valid_ids(self):
        """Tests retrieving objects using valid IDs."""
        result = bulk_model_retrieve(
            [
                {"family_id": "GREGoR_test-001"},
                {"family_id": "GREGoR_test-002"}
            ], Family, "family_id")

        self.assertIn("GREGoR_test-001", result)
        self.assertIn("GREGoR_test-002", result)
        self.assertEqual(result["GREGoR_test-001"], self.family_1)
        self.assertEqual(result["GREGoR_test-002"], self.family_2)
    
    def test_bulk_model_retrieve_invalid_ids(self):
        """Tests retrieving objects with non-existent IDs."""
        result = bulk_model_retrieve(
            [{"family_id": "GREGoR_test-999"}], Family, "family_id")
        self.assertEqual(result, {})
    
    def test_bulk_model_retrieve_empty_list(self):
        """Tests retrieving objects with an empty ID list."""
        result = bulk_model_retrieve([], Family, "family_id")
        self.assertEqual(result, {})
    
    def test_bulk_model_retrieve_invalid_field(self):
        """Tests retrieving objects with an invalid field name."""
        result = bulk_model_retrieve(
            [{"family_id": "GREGoR_test-001"}], Family, "invalid_field")
        self.assertIn("error", result)

        
class BulkRetrieveTestCase(TestCase):
    fixtures = ['tests/fixtures/test_fixture.json']

    def test_bulk_retrieve_valid_ids(self):
        """Tests retrieving objects using valid IDs."""
        result = bulk_retrieve(Family, ["GREGoR_test-001", "GREGoR_test-002"], "family_id")

        self.assertIn("GREGoR_test-001", result)
        self.assertIn("GREGoR_test-002", result)
        self.assertEqual(result["GREGoR_test-001"]["family_id"], "GREGoR_test-001")
        self.assertEqual(result["GREGoR_test-002"]["family_id"], "GREGoR_test-002")
    
    def test_bulk_retrieve_invalid_ids(self):
        """Tests retrieving objects with non-existent IDs."""
        result = bulk_retrieve(Family, ["GREGoR_test-999"], "family_id")
        self.assertEqual(result, {})
    
    def test_bulk_retrieve_empty_list(self):
        """Tests retrieving objects with an empty ID list."""
        result = bulk_retrieve(Family, [], "family_id")
        self.assertEqual(result, {})
    
    def test_bulk_retrieve_invalid_field(self):
        """Tests retrieving objects with an invalid field name."""
        result = bulk_retrieve(Family, ["GREGoR_test-001"], "invalid_field")
        self.assertIn("error", result)
