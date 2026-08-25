#!/bin/bash

# Automatically confirm the flush operation
echo "yes" | python manage.py flush

# Load data from fixtures
# python manage.py loaddata tests/fixtures/initial.json
# python manage.py loaddata tests/fixtures/test_fixture.json tests/fixtures/hpo_fixture.json
# python manage.py loaddata tests/fixtures/test_fixture_invalid.json
python manage.py loaddata tests/fixtures/test_fixture_valid.json
# python manage.py loaddata config/fixtures/initial.json
# python manage.py loaddata dump.json
# python manage.py loaddata config/fixtures/U09_dump.json

