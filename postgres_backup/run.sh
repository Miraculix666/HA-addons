#!/usr/bin/env bashio

PG_HOST=$(bashio::config 'pg_host')
PG_PORT=$(bashio::config 'pg_port')
PG_USER=$(bashio::config 'pg_user')
PG_PASSWORD=$(bashio::config 'pg_password')
PG_DATABASE=$(bashio::config 'pg_database')
BACKUP_DIR=$(bashio::config 'backup_dir')

DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILE="$BACKUP_DIR/ha_db_$DATE.sql.gz"
LATEST_FILE="$BACKUP_DIR/ha_db_latest.sql.gz"

bashio::log.info "Starting database backup from $PG_HOST:$PG_PORT..."

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Perform pg_dump
export PGPASSWORD="$PG_PASSWORD"
if pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" | gzip > "$FILE"; then
    bashio::log.info "Database backup successful: $FILE"
    
    # Create copy as latest
    cp "$FILE" "$LATEST_FILE"
    
    # Keep last 3 days of backups
    find "$BACKUP_DIR" -type f -name "ha_db_*.sql.gz" -mtime +3 -exec rm {} \;
    bashio::log.info "Cleaned up database backups older than 3 days."
else
    bashio::log.error "Database backup failed!"
    exit 1
fi

exit 0
