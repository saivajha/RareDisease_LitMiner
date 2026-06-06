#!/bin/bash
# Backup PostgreSQL and Qdrant data to ./backups/
set -e
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Backing up PostgreSQL..."
docker compose exec -T postgres pg_dump -U postgres litminer > "$BACKUP_DIR/postgres.sql"

echo "Backing up Qdrant snapshot..."
curl -s -X POST "http://localhost:6333/collections/literature_chunks/snapshots" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('name',''))" \
  | xargs -I{} curl -s "http://localhost:6333/collections/literature_chunks/snapshots/{}" \
  -o "$BACKUP_DIR/qdrant_snapshot.snapshot" 2>/dev/null || echo "Qdrant snapshot skipped (collection may be empty)"

echo "Backup complete: $BACKUP_DIR"
