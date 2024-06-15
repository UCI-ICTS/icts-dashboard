import os
from django.test import TestCase
from django.utils import timezone
from config.selectors import TableValidator
from django.conf import settings


# models test
class TableValidatorTest(TestCase):
    """ """

    example_family = {
        "family_id": "PMGRC-11111",
        "consanguinity_detail": "NA",
        "family_history_detail": "syndrome",
        "consanguinity": "None suspected",
        "pedigree_file_detail": "NA",
        "pedigree_file": "NA",
    }

    def test_validator_initialization(self):
        validator = TableValidator()
        expected_base_path = os.path.join(settings.BASE_DIR, "utilities/json_schemas/")

        self.assertEqual(validator.base_path, expected_base_path)
        self.assertFalse(validator.valid)
        self.assertEqual(validator.errors, [])

    def test_validation(self):
        validator = TableValidator()
        validator.validate_json(json_object=self.example_family, table_name="family")
        results = validator.get_validation_results()
        self.assertTrue(results["valid"])
