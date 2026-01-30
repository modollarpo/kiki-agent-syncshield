#!/bin/bash
# setup_syncmultimodal.sh
# Automates starting SyncMulti-Modal FastAPI service and running tests

# Activate Python venv
source ../../.venv/bin/activate

# Start FastAPI service in background
nohup python -m uvicorn services.syncmultimodal.app:app --host 127.0.0.1 --port 8009 &
SERVICE_PID=$!

# Wait for service to start
sleep 5

# Run test script
python services/syncmultimodal/test_syncmultimodal.py

# Kill FastAPI service
kill $SERVICE_PID
