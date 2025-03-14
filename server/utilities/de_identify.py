import json

# Example usage:
# input_json = "input.json"   # Replace with your actual input JSON file
# output_json = "output.json" # Replace with the desired output filename
# deidentify_json(input_json, output_json)

# print(f"De-identified JSON saved to {output_json}")

input_json = "/Users/hadleyking/Downloads/test_data.json"
output_json = "/Users/hadleyking/Downloads/de_identified.json"
# Mapping from original values (column 1) to de-identified values (column 2)
deid_map = {
    "PMGRC-178": "GREGoR_test-001",
    "PMGRC-178-178-0": "GREGoR_test-001-001-0",
    "PMGRC-179-178-2": "GREGoR_test-002-001-2",
    "PMGRC-180-178-1": "GREGoR_test-003-001-1",
    "LS4268810": "LS4268810",
    "LS4268811": "LS4268811",
    "LS4268812": "LS4268812",
    "LS4716288": "LS4716288",
    "LS4716300": "LS4716300",
    "LS4716312": "LS4716312",
    "UCI001-178_RNA": "UCI001-001_RNA",
    "PMGRC-178-178-0_LS4268812_SQ6044": "GREGoR_test-001-001-0_LS4268812_DW44",
    "PMGRC-179-178-2_LS4268811_SQ6043": "GREGoR_test-001-001-0_LS4268811_DW43",
    "PMGRC-180-178-1_LS4268810_SQ6042": "GREGoR_test-001-001-0_LS4268810_DW42",
    "10_73792184_PMGRC-178-178-0": "10_73792184_GREGoR_test-001-001-0",
    "2_6849938_PMGRC-178-178-0": "2_6849938_GREGoR_test-001-001-0",
    "2_6865407_PMGRC-178-178-0": "2_6865407_GREGoR_test-001-001-0",
    "5_98899555_PMGRC-178-178-0": "5_98899555_GREGoR_test-001-001-0",
    "CNH_I_UCI001-178_RNA": "GREGoR_test-001-001-0_RNA"
}

# Function to replace values in JSON
def deidentify_json(input_file, output_file):
    with open(input_file, "r") as file:
        data = json.load(file)

    def replace_values(obj):
        if isinstance(obj, dict):
            return {key: replace_values(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [replace_values(item) for item in obj]
        elif isinstance(obj, str) and obj in deid_map:
            return deid_map[obj]
        return obj

    # Apply the replacement
    deidentified_data = replace_values(data)

    # Save to new JSON file
    with open(output_file, "w") as file:
        json.dump(deidentified_data, file, indent=4)

if __name__ == "__main__":
    deidentify_json(
        input_file=input_json,
        output_file=output_json
    )