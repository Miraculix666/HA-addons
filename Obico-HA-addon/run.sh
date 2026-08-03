#!/bin/bash
set -euo pipefail

if [ -f /data/options.json ]; then
    USERNAME=$(python3 -c "import sys, json; print(json.load(open('/data/options.json')).get('username', ''))" 2>/dev/null || true)
    PASSWORD=$(python3 -c "import sys, json; print(json.load(open('/data/options.json')).get('password', ''))" 2>/dev/null || true)

    if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
        if ! id "obico" >/dev/null 2>&1; then
            useradd -m -d /home/obico -s /bin/bash obico
        fi
        echo "obico:${PASSWORD}" | chpasswd
    fi
fi

exec obico server
