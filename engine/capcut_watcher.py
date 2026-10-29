#!/usr/bin/env python3
"""
Cinegrade CapCut Auto-Ingest Watcher
Monitors CapCut exports folder and stages completed video assets into dist/clips/.
"""

import time
import shutil
from pathlib import Path

WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
CAPCUT_EXPORTS = Path.home() / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft" # Adjust default if needed
DEST_CLIPS = WORKSPACE / "dist" / "clips"

DEST_CLIPS.mkdir(parents=True, exist_ok=True)

def watch_capcut_exports():
    print("Watching CapCut export directory for new renders...")
    seen = {p.name for p in DEST_CLIPS.glob("*.mp4")}
    
    # Generic fallback watcher for desktop movies folder if CapCut custom path varies
    target_dir = Path.home() / "Movies"
    
    while True:
        try:
            for mp4 in target_dir.glob("*.mp4"):
                if mp4.name not in seen:
                    time.sleep(1.0) # Ensure write completion
                    dest_path = DEST_CLIPS / mp4.name
                    shutil.copy2(str(mp4), str(dest_path))
                    seen.add(mp4.name)
                    print(f"Staged CapCut render into pipeline: {mp4.name}")
            time.sleep(5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Watcher error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    watch_capcut_exports()