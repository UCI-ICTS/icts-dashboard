#!/bin/bash

# Automatically confirm the flush operation
echo "yes" | python manage.py flush

# Load data from fixtures
python manage.py loaddata config/fixtures/local_data.json
