#!/bin/bash

# Define config path
CONFIG_PATH=/data/options.json

if [ -f "$CONFIG_PATH" ]; then
    # Try using jq to parse JSON if installed
    if command -v jq >/dev/null 2>&1; then
        USERNAME=$(jq -r '.username // empty' "$CONFIG_PATH" 2>/dev/null)
        PASSWORD=$(jq -r '.password // empty' "$CONFIG_PATH" 2>/dev/null)
    elif command -v python3 >/dev/null 2>&1; then
        # Fallback to python3
        USERNAME=$(python3 -c "import sys, json; print(json.load(sys.stdin).get('username', ''))" < "$CONFIG_PATH" 2>/dev/null)
        PASSWORD=$(python3 -c "import sys, json; print(json.load(sys.stdin).get('password', ''))" < "$CONFIG_PATH" 2>/dev/null)
    else
        # Fallback simplistic grep for simple JSON
        USERNAME=$(grep -Po '"username":\s*"\K[^"]*' "$CONFIG_PATH" 2>/dev/null)
        PASSWORD=$(grep -Po '"password":\s*"\K[^"]*' "$CONFIG_PATH" 2>/dev/null)
    fi

    if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
        if ! id -u obico >/dev/null 2>&1; then
            useradd -m -d /home/obico -s /bin/bash obico
        fi
        echo "obico:$PASSWORD" | chpasswd
    fi
fi

exec "$@"
