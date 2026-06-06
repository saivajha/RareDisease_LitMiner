#!/bin/bash
# Restore PostgreSQL from a backup
# Usage: ./scripts/restore.sh ./backups/20240101_120000
set -e
BACKUP_DIR="${1:?Usage: $0 <backup_dir>}"

echo "Restoring PostgreSQL from $BACKUP_DIR/postgres.sql..."
docker compose exec -T postgres psql -U postgres -d litminer < "$BACKUP_DIR/postgres.sql"
echo "Restore complete."
