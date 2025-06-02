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

# Loop through each TSV file in the directory
for FILE in "$DIR"/*.tsv; do
    # Check if any .tsv files exist
    if [ ! -e "$FILE" ]; then
        echo "No .tsv files found in '$DIR'."
        exit 1
    fi

    echo "Processing file: $FILE"
    python utilities/data_converter.py -t "$FILE" -n "$(basename ${FILE%.tsv})"

    # Check if the command was successful
    if [ $? -ne 0 ]; then
        echo "Error processing $FILE"
    else
        echo "Successfully processed $FILE"
    fi
done

echo "All .tsv files processed."
