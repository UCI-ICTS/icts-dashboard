#!/usr/bin/env python
# utilities/safe_loader.py

import json
from django.core.serializers import deserialize
from django.db import IntegrityError

input_file = "/Users/hadleyking/Desktop/biobank_dump25.06.12.json"

with open(input_file, "r") as f:
    objects = list(deserialize("json", f))
failed_imports = []
for i, obj in enumerate(objects, start=1):
    try:
        obj.save()
        print(f"✅ Saved object #{i} — {obj.object._meta.label} (pk: {obj.object.pk})")
    except IntegrityError as e:
        failed_imports.append({"object": obj, "error": e})
        continue

print("\n\n")

for index, fail in enumerate(failed_imports):
    obj = fail["object"]
    err = fail["error"]
    print(f"\n❌ FAILED at object #{index}")
    print(f"Model: {obj.object._meta.label}")
    print(f"PK: {obj.object.pk}")
    print("ERROR:", err)
