#!/usr/bin/env python3
# tests/test_clases/test_selectors.py

import pytest
import json
import zipfile
from unittest.mock import patch, MagicMock
from config.selectors import (
    TableValidator, remove_na, multi_value_split, response_status, response_constructor,
    validate_url, generate_tsv, generate_zip, compare_data, bulk_retrieve
)
from django.core.exceptions import ValidationError
from rest_framework import status

@pytest.fixture
def mock_schema_file(tmpdir):
    """Creates a temporary JSON schema file for testing."""
    schema_path = tmpdir.join("test_schema.json")
    schema_content = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    schema_path.write(json.dumps(schema_content))
    return str(schema_path)

@pytest.fixture
def validator():
    """Returns an instance of TableValidator."""
    return TableValidator()

### TableValidator Class Tests ###
def test_validate_json_valid_case(validator, mock_schema_file, tmpdir):
    """Tests JSON validation with valid input."""
    validator.base_path = tmpdir  # Override base path to mock schema location
    test_json = {"name": "Alice", "age": 25}
    
    validator.validate_json(test_json, "test_schema")
    
    assert validator.valid is True
    assert validator.errors == []

def test_validate_json_invalid_case(validator, mock_schema_file, tmpdir):
    """Tests JSON validation with invalid input."""
    validator.base_path = tmpdir  # Override base path to mock schema location
    test_json = {"age": 25}  # Missing "name"

    validator.validate_json(test_json, "test_schema")

    assert validator.valid is False
    assert len(validator.errors) > 0

def test_validate_json_missing_schema(validator):
    """Tests handling of a missing schema file."""
    validator.validate_json({"name": "Alice"}, "non_existent_schema")

    assert validator.valid is False
    assert "Schema file not found" in validator.errors[0]

def test_get_validation_results(validator):
    """Tests the get_validation_results method."""
    validator.valid = False
    validator.errors = ["['name']: is required"]

    results = validator.get_validation_results()
    
    assert results["valid"] is False
    assert results["errors"][0]["field"] == "Name"
    assert results["errors"][0]["error"] == "is required"

### Utility Function Tests ###
@pytest.mark.parametrize("input_data, expected_output", [
    ({"key1": "NA", "key2": "valid"}, {"key2": "valid"}),
    ({"key1": ["NA"], "key2": "something"}, {"key2": "something"}),
    ({"key1": "test", "key2": "NA"}, {"key1": "test"})
])
def test_remove_na(input_data, expected_output):
    """Tests that 'NA' values are correctly removed."""
    assert remove_na(input_data) == expected_output

@pytest.mark.parametrize("input_data, expected_output", [
    ({"key1": "value1|value2"}, {"key1": ["value1", "value2"]}),
    ({"key1": "single"}, {"key1": "single"}),
    ({"key1": ["existing"]}, {"key1": ["existing"]})
])
def test_multi_value_split(input_data, expected_output):
    """Tests multi-value splitting."""
    assert multi_value_split(input_data) == expected_output

@pytest.mark.parametrize("accepted, rejected, expected_status", [
    (False, False, status.HTTP_400_BAD_REQUEST),
    (False, True, status.HTTP_400_BAD_REQUEST),
    (True, True, status.HTTP_207_MULTI_STATUS),
    (True, False, status.HTTP_200_OK),
])
def test_response_status(accepted, rejected, expected_status):
    """Tests response status determination logic."""
    assert response_status(accepted, rejected) == expected_status

def test_response_constructor():
    """Tests constructing standardized API responses."""
    response = response_constructor("123", "success", 200, "All good", {"data": "test"})
    
    assert response["identifier"] == "123"
    assert response["request_status"] == "success"
    assert response["status_code"] == 200
    assert response["message"] == "All good"
    assert response["data"]["data"] == "test"

def test_validate_url_valid():
    """Tests valid URLs."""
    assert validate_url("https://example.com") is True
    assert validate_url("http://test.com/path?query=value") is True

def test_validate_url_invalid():
    """Tests invalid URLs."""
    with pytest.raises(ValidationError, match="Invalid URL: URL must be a non-empty string."):
        validate_url("")
    
    with pytest.raises(ValidationError, match="Invalid URL: URL must be a non-empty string."):
        validate_url(None)

    with pytest.raises(ValidationError, match="is not a valid URL"):
        validate_url("htp:/invalid-url")  # Invalid scheme

    with pytest.raises(ValidationError, match="is not a valid URL"):
        validate_url("just-a-string")  # Not a valid URL

def test_generate_tsv():
    """Tests TSV generation."""
    data = [{"col1": "A", "col2": "B"}, {"col1": "C", "col2": "D"}]
    tsv = generate_tsv(data)
    
    assert "col1\tcol2\nA\tB\nC\tD" in tsv

def test_generate_zip():
    """Tests ZIP file generation."""
    files = {"file1.txt": "Hello World", "file2.txt": "Python Testing"}
    zip_buffer = generate_zip(files)

    with zipfile.ZipFile(zip_buffer, "r") as zip_file:
        assert "file1.txt" in zip_file.namelist()
        assert zip_file.read("file1.txt").decode() == "Hello World"

def test_compare_data():
    """Tests data comparison function."""
    old_data = {"name": "Alice", "age": 30}
    new_data = {"name": "Alice", "age": 31}

    result = compare_data(old_data, new_data)
    
    assert result["age"] == "30 to 31"

@patch("config.selectors.bulk_retrieve")
def test_bulk_retrieve(mock_bulk_retrieve):
    """Tests bulk retrieve with mocked database."""
    mock_bulk_retrieve.return_value = {"1": "Test Object"}

    result = bulk_retrieve([{"id": "1"}], MagicMock(), "id")

    assert result == {"1": "Test Object"}

