#!/bin/bash
# KIKI Agent™ Periodic Cleanup Script
# Cleans Docker, Python/Go cache, and old logs. Safe for production use.
# Logs actions to /var/log/kiki_cleanup.log or ./logs/cleanup.log if /var/log not writable.

set -euo pipefail

LOGFILE="/var/log/kiki_cleanup.log"
if [ ! -w "/var/log" ]; then
  LOGFILE="$(pwd)/logs/cleanup.log"
  mkdir -p "$(pwd)/logs"
fi

echo "[KIKI CLEANUP] $(date) Starting cleanup..." | tee -a "$LOGFILE"

# 1. Docker: Remove unused images, containers, volumes (safe, does not stop running containers)
docker system prune -a -f --volumes | tee -a "$LOGFILE"

# 2. Python: Remove __pycache__ and .pyc files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 3. Go: Clean build and module cache
go clean -cache -modcache 2>/dev/null || true

# 4. Remove old log files (older than 14 days)
find ./logs -type f -name "*.txt" -mtime +14 -delete 2>/dev/null || true

# 5. Disk usage summary
df -h / | tee -a "$LOGFILE"

echo "[KIKI CLEANUP] $(date) Cleanup complete." | tee -a "$LOGFILE"
