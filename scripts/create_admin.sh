#!/bin/bash
# KIKI Agent™ - Create Admin User Script
# Wrapper for create_admin.py with environment variable support

set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run Python script
python3 scripts/create_admin.py "$@"
