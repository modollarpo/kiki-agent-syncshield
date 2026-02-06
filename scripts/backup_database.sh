#!/bin/bash
# Database Backup Script for KIKI Agent™
#
# Automated PostgreSQL backups with compression and rotation.
# Supports local backups and optional S3/MinIO upload.

set -e

# ============================================================================
# Configuration
# ============================================================================

BACKUP_DIR="${KIKI_BACKUP_DIR:-/var/backups/kiki}"
RETENTION_DAYS="${KIKI_BACKUP_RETENTION:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="kiki_backup_${TIMESTAMP}.sql.gz"

# Database configuration (from environment or defaults)
DB_HOST="${KIKI_DB_HOST:-localhost}"
DB_PORT="${KIKI_DB_PORT:-5432}"
DB_USER="${KIKI_DB_USER:-kiki}"
DB_NAME="${KIKI_DB_NAME:-kiki_db}"
DB_PASSWORD="${KIKI_DB_PASSWORD:-kiki_pass}"

# S3/MinIO configuration (optional)
S3_ENABLED="${KIKI_BACKUP_S3_ENABLED:-false}"
S3_BUCKET="${KIKI_BACKUP_S3_BUCKET:-kiki-backups}"
S3_ENDPOINT="${KIKI_BACKUP_S3_ENDPOINT:-}"
S3_ACCESS_KEY="${KIKI_BACKUP_S3_ACCESS_KEY:-}"
S3_SECRET_KEY="${KIKI_BACKUP_S3_SECRET_KEY:-}"

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

# Check if pg_dump is installed
if ! command -v pg_dump &> /dev/null; then
    error "pg_dump not found. Install PostgreSQL client tools."
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# ============================================================================
# Backup Database
# ============================================================================

log "Starting database backup..."
log "Database: $DB_NAME @ $DB_HOST:$DB_PORT"
log "Backup file: $BACKUP_DIR/$BACKUP_FILE"

# Export password for pg_dump
export PGPASSWORD="$DB_PASSWORD"

# Perform backup with compression
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --format=plain \
    --no-owner \
    --no-acl \
    --verbose \
    | gzip > "$BACKUP_DIR/$BACKUP_FILE"; then
    log "✓ Backup completed successfully"
    
    # Get backup size
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    log "Backup size: $BACKUP_SIZE"
else
    error "Backup failed!"
    exit 1
fi

# Unset password
unset PGPASSWORD

# ============================================================================
# Upload to S3/MinIO (Optional)
# ============================================================================

if [ "$S3_ENABLED" = "true" ]; then
    log "Uploading backup to S3/MinIO..."
    
    if command -v aws &> /dev/null; then
        # Configure AWS CLI
        export AWS_ACCESS_KEY_ID="$S3_ACCESS_KEY"
        export AWS_SECRET_ACCESS_KEY="$S3_SECRET_KEY"
        
        # Upload to S3
        if [ -n "$S3_ENDPOINT" ]; then
            # MinIO or custom S3 endpoint
            aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" \
                "s3://$S3_BUCKET/$BACKUP_FILE" \
                --endpoint-url "$S3_ENDPOINT"
        else
            # AWS S3
            aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" \
                "s3://$S3_BUCKET/$BACKUP_FILE"
        fi
        
        if [ $? -eq 0 ]; then
            log "✓ Backup uploaded to S3"
        else
            error "S3 upload failed!"
        fi
        
        # Cleanup AWS credentials
        unset AWS_ACCESS_KEY_ID
        unset AWS_SECRET_ACCESS_KEY
    else
        error "aws-cli not installed. Skipping S3 upload."
    fi
fi

# ============================================================================
# Cleanup Old Backups
# ============================================================================

log "Cleaning up old backups (retention: $RETENTION_DAYS days)..."

# Delete local backups older than retention period
find "$BACKUP_DIR" -name "kiki_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# Count remaining backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "kiki_backup_*.sql.gz" -type f | wc -l)
log "Local backups retained: $BACKUP_COUNT"

# Cleanup old S3 backups (if enabled)
if [ "$S3_ENABLED" = "true" ] && command -v aws &> /dev/null; then
    export AWS_ACCESS_KEY_ID="$S3_ACCESS_KEY"
    export AWS_SECRET_ACCESS_KEY="$S3_SECRET_KEY"
    
    # Calculate cutoff date
    CUTOFF_DATE=$(date -d "$RETENTION_DAYS days ago" +%Y%m%d)
    
    # List and delete old backups from S3
    if [ -n "$S3_ENDPOINT" ]; then
        aws s3 ls "s3://$S3_BUCKET/" --endpoint-url "$S3_ENDPOINT" \
            | awk '{print $4}' \
            | grep "kiki_backup_" \
            | while read file; do
                FILE_DATE=$(echo "$file" | grep -oP '\d{8}' | head -1)
                if [ "$FILE_DATE" -lt "$CUTOFF_DATE" ]; then
                    aws s3 rm "s3://$S3_BUCKET/$file" --endpoint-url "$S3_ENDPOINT"
                    log "Deleted old S3 backup: $file"
                fi
            done
    else
        aws s3 ls "s3://$S3_BUCKET/" \
            | awk '{print $4}' \
            | grep "kiki_backup_" \
            | while read file; do
                FILE_DATE=$(echo "$file" | grep -oP '\d{8}' | head -1)
                if [ "$FILE_DATE" -lt "$CUTOFF_DATE" ]; then
                    aws s3 rm "s3://$S3_BUCKET/$file"
                    log "Deleted old S3 backup: $file"
                fi
            done
    fi
    
    unset AWS_ACCESS_KEY_ID
    unset AWS_SECRET_ACCESS_KEY
fi

# ============================================================================
# Summary
# ============================================================================

log "=================================================="
log "Backup Summary:"
log "  File: $BACKUP_FILE"
log "  Size: $BACKUP_SIZE"
log "  Location: $BACKUP_DIR"
if [ "$S3_ENABLED" = "true" ]; then
    log "  S3 Bucket: $S3_BUCKET"
fi
log "  Retention: $RETENTION_DAYS days"
log "  Backups retained: $BACKUP_COUNT"
log "=================================================="
log "✓ Backup completed successfully!"
