#!/bin/bash
# Backup Samba AD DC avec rotation des N derniers backups

BACKUP_DIR="/opt/samba-backups"
LOG_FILE="/var/log/samba-backup.log"
KEEP=5   # nombre de backups à conserver
ADMIN_PASS='Samba@bogosy2026!'
DC="dc01.lab.local"

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

log() { echo "[$(timestamp)] $*" | tee -a "$LOG_FILE"; }

log "=== Début du backup Samba AD ==="

# Crée le répertoire si nécessaire
mkdir -p "$BACKUP_DIR"

# Lance le backup
if samba-tool domain backup online \
    --server="$DC" \
    --targetdir="$BACKUP_DIR" \
    -U "Administrator%${ADMIN_PASS}" >> "$LOG_FILE" 2>&1; then
    log "OK : backup réussi"
else
    log "ERREUR : le backup a échoué"
    exit 1
fi

# Rotation : supprime les anciens backups si on dépasse KEEP
BACKUP_COUNT=$(find "$BACKUP_DIR" -maxdepth 1 -name "*.tar.bz2" 2>/dev/null | wc -l)
if [[ $BACKUP_COUNT -gt $KEEP ]]; then
    log "Rotation : $BACKUP_COUNT backups trouvés, conservation des $KEEP plus récents"
    find "$BACKUP_DIR" -maxdepth 1 -name "*.tar.bz2" -printf "%T@ %p\n" | sort -rn | tail -n +$((KEEP + 1)) | cut -d' ' -f2- | while read -r old; do
        rm -f "$old"
        log "Supprimé : $old"
    done
fi

log "Backups présents : $(find "$BACKUP_DIR" -maxdepth 1 -name "*.tar.bz2" | wc -l)"
log "=== Fin du backup ==="
