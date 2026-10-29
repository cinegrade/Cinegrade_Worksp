#!/bin/zsh

# ============================================================
# CINEGRADE WORKSPACE AUTO-BACKUP SCRIPT
# ============================================================
LOG_DIR="$HOME/Desktop/Cinegrade_Worksp/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/backup.log"

# Inside your backup commands, redirect to $LOG_FILE:
echo "$(date): Starting backup..." >> "$LOG_FILE"

WORKSPACE_DIR="$HOME/Desktop/Cinegrade_Worksp"
BACKUP_DEST="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Cinegrade_Backups"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
ARCHIVE_NAME="Cinegrade_Backup_$TIMESTAMP.tar.gz"

# Ensure backup destination directory exists in iCloud Drive
mkdir -p "$BACKUP_DEST"

echo "============================================================"
echo " 📦 CINEGRADE WORKSPACE BACKUP STARTED"
echo " Time: $(date)"
echo "============================================================"

# Create compressed archive excluding heavy rendered clips and git folder
tar --exclude='dist/clips/*.mp4' \
    --exclude='.git' \
    -czf "$BACKUP_DEST/$ARCHIVE_NAME" \
    -C "$HOME/Desktop" "Cinegrade_Worksp"

if [ $? -eq 0 ]; then
    echo ""
    echo "[+] Backup successfully created and saved to iCloud:"
    echo "    -> $BACKUP_DEST/$ARCHIVE_NAME"
else
    echo ""
    echo "[!] Backup failed."
    exit 1
fi