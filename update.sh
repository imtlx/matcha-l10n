#!/bin/sh

if command -v python >/dev/null 2>&1; then
    PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    echo "Error: Python not found"
    exit 1
fi

"$PYTHON" ./csv_to_json.py || exit 1

git add .
git commit -m "update $(date '+%Y-%m-%d %H:%M:%S')"
git push

