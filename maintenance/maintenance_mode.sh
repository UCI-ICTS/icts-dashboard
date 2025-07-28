#!/bin/bash

FLAG_FILE="/Users/hadleyking/GitHub/UCI-ICTS/icts-dashboard/maintenance/maintenance.flag"

if [ -f "$FLAG_FILE" ]; then
    echo "🔓 Disabling maintenance mode..."
    rm "$FLAG_FILE"
else
    echo "🚧 Enabling maintenance mode..."
    touch "$FLAG_FILE"
fi
