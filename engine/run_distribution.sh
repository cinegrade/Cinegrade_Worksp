#!/bin/zsh
set -e

WORKSPACE_DIR="$HOME/Desktop/Cinegrade_Worksp"
cd "$WORKSPACE_DIR"
PYTHON_BIN="$WORKSPACE_DIR/.venv/bin/python"

echo "=== [1/5] Running Social Distribution ==="
"$PYTHON_BIN" engine/social_distribute.py

echo "=== [2/5] Generating A/B Hook Matrix ==="
"$PYTHON_BIN" engine/ab_hook_tester.py

echo "=== [3/5] Syncing Archive to iCloud Drive ==="
"$PYTHON_BIN" engine/backup.py

echo "=== [4/5] Sending Webhook Notification ==="
"$PYTHON_BIN" engine/webhook_notifier.py "Cinegrade Pipeline" "Distribution, A/B testing, and cloud sync completed successfully."

echo "=== [5/5] Archiving Processed Clips ==="
ARCHIVE_DIR="dist/archive/$(date +%Y-%m)"
mkdir -p "$ARCHIVE_DIR"
setopt +o nomatch
for p in dist/clips/*.mp4; do
    if [ -f "$p" ]; then
        mv "$p" "$ARCHIVE_DIR/"
    fi
done
unsetopt nomatch

echo "=== Pipeline Lifecycle Completed Successfully ==="
