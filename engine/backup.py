#!/usr/bin/env python3
"""
Cinegrade Cloud Backup & Sync Verification
Mirrors dist/archive/ and manifests to iCloud Drive.
"""

import shutil
from pathlib import Path

WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
ARCHIVE_DIR = WORKSPACE / "dist" / "archive"
ICLOUD_BACKUP = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Cinegrade_Backups"

def sync_to_cloud():
    ICLOUD_BACKUP.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_DIR.exists():
        print("No archive directory found to sync.")
        return
    
    for item in ARCHIVE_DIR.iterdir():
        dest = ICLOUD_BACKUP / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
    print(f"Successfully synced Cinegrade archive state to iCloud Drive: {ICLOUD_BACKUP}")

if __name__ == "__main__":
    sync_to_cloud()