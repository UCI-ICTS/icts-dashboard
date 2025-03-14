#!/bin/bash

# Set the output file path in the admin directory
OUTPUT_FILE="$(dirname "$(dirname "$(dirname "$(realpath "$0")")")")/admin/SELinux_Full_Snapshot.txt"

# Ensure the admin directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Generate the SELinux snapshot
(
    echo "### SELinux Boolean Settings ###"
    getsebool -a

    echo "### SELinux File Contexts ###"
    semanage fcontext -l

    echo "### Installed SELinux Modules ###"
    semodule -l

    echo "### Recent SELinux Denials ###"
    ausearch -m AVC,USER_AVC -c nginx --raw | audit2allow -M selinux_recent_denials
) > "$OUTPUT_FILE"

echo "✅ SELinux snapshot saved to: $OUTPUT_FILE"
