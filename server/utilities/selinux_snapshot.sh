#!/bin/bash

# Set the default output directory and file path
OUTPUT_DIR="/var/www/backups/config"
OUTPUT_FILE="$OUTPUT_DIR/SELinux_Full_Snapshot.txt"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Generate the SELinux snapshot
(
    echo "### SELinux Boolean Settings ###"
    getsebool -a

    echo -e "\n### SELinux File Contexts ###"
    semanage fcontext -l

    echo -e "\n### Installed SELinux Modules ###"
    semodule -l

    echo -e "\n### Recent SELinux Denials (nginx-related) ###"
    ausearch -m AVC,USER_AVC -c nginx --raw | audit2allow -M selinux_recent_denials 2>/dev/null || echo "No recent denials found."
) > "$OUTPUT_FILE"

echo "✅ SELinux snapshot saved to: $OUTPUT_FILE"
