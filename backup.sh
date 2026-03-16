#!/bin/bash

# Backup script for Autoposting database
# Usage: ./backup.sh

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/autoposting_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "📦 Creating database backup..."

# Run pg_dump inside docker container
docker-compose exec -T db pg_dump -U autoposting autoposting > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

echo "✅ Backup created: ${BACKUP_FILE}.gz"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "🧹 Old backups cleaned (keeping last 7 days)"
