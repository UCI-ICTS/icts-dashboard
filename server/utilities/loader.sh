#!/bin/bash
#
# process_tsv.sh
#
# This script processes all `.tsv` files in a specified directory by running
# them through the `data_converter.py` Python script.
#
# Usage:
#   ./process_tsv.sh <directory_path>
#
# Arguments:
#   <directory_path>  The path to the directory containing TSV files.
#
# Description:
#   - Ensures that a directory path is provided as an argument.
#   - Checks if the specified directory exists.
#   - Iterates through all `.tsv` files in the directory.
#   - Runs `python utilities/data_converter.py -t <file>` on each `.tsv` file.
#   - Reports success or failure for each processed file.
#
# Exit Codes:
#   - 1: No directory provided, directory does not exist, or no `.tsv` files found.
#   - 0: Script completes successfully.
#

# Ensure a directory is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <directory_path>"
    exit 1
fi

# Assign input argument to a variable
DIR="$1"

# Check if the directory exists
if [ ! -d "$DIR" ]; then
    echo "Error: Directory '$DIR' does not exist."
    exit 1
fi

# Loop through each TSV file in the directory in the correct order
declare -a TABLE_ORDER=(
    "family"
    "participant"
    "phenotype"
    "genetic_findings"
    "analyte"
    "experiment_dna_short_read"
    "experiment_rna_short_read"
    "experiment_pac_bio"
    "experiment_nanopore"
    "aligned_dna_short_read"
    "aligned_rna_short_read"
    "aligned_pac_bio"
    "aligned_nanopore"
    "biobank"
)
for TABLE in "${TABLE_ORDER[@]}"; do
    # Check if any table.tsv files exist
    FILE="${DIR}/${TABLE}.tsv"
    if [ ! -e "$FILE" ]; then
        echo "'$FILE' not found in '$DIR'."
        continue
    fi

    echo "Processing file: $FILE"
    python utilities/data_converter.py -t "$FILE" -n "$TABLE"

    # Check if the command was successful
    if [ $? -ne 0 ]; then
        echo "Error processing $FILE"
    else
        echo "Successfully processed $FILE"
    fi
done

echo "All .tsv files processed."
