#!/usr/bin/env python3
"""""Analyte combination
one off script to combine the ANViL and UCI local analyte lists
"""

import json

thing1 = "/Users/hadleyking/GitHub/UCI-GREGoR/GREGor_dashboard/server/utilities/anvil_json/AnVIL_GREGoR_CNH_I_U06_GRU_analyte.json"
thing2 = "/Users/hadleyking/GitHub/UCI-GREGoR/GREGor_dashboard/server/utilities/anvil_json/2024.11.14_PMGRC_analytes.json"

combined_data = []
captured_analytes = []
with open(thing1) as anvil:
    anvil_data = json.load(anvil)
with open(thing2) as local:
    local_data = json.load(local)

for datum in anvil_data:
    participant_id = datum["participant_id"]
    datum["internal_analyte_id"] = []
    for participant in local_data:
        if participant_id == participant["participant_id"]:
            captured_analytes.append(participant["analyte_id"])
            datum["internal_analyte_id"].append(participant["analyte_id"])
    combined_data.append(datum)

for datum in local_data:
    if datum["analyte_id"] not in captured_analytes:
        datum["internal_analyte_id"] = []
        combined_data.append(datum)
# import pdb; pdb.set_trace()
print(json.dumps(combined_data, indent=4))