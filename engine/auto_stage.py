#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

# Define workspace paths
WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
SRC_DIR = WORKSPACE / "dist" / "clips"
HUB_DIR = WORKSPACE / "distribution_hub"

# Define platform destination mappings based on keywords or default distribution
PLATFORMS = {
    "tiktok": HUB_DIR / "tiktok",
    "instagram": HUB_DIR / "instagram_reels",
    "youtube": HUB_DIR / "youtube_shorts"
}

def stage_clips():
    if not SRC_DIR.exists():
        print(f"Source directory not found: {SRC_DIR}")
        return

    # Ensure hub and subfolders exist
    for folder in PLATFORMS.values():
        folder.mkdir(parents=True, exist_ok=True)

    staged_count = 0
    for file_path in SRC_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".mp4":
            filename = file_path.name.lower()
            
            # Determine target platform folder (default to TikTok/Shorts if generic)
            target_folder = HUB_DIR / "tiktok" # default fallback
            if "insta" in filename or "reel" in filename:
                target_folder = PLATFORMS["instagram"]
            elif "yt" in filename or "tube" in filename or "short" in filename:
                target_folder = PLATFORMS["youtube"]

            dest_path = target_folder / file_path.name
            if not dest_path.exists():
                shutil.copy2(file_path, dest_path)
                print(f"Staged: {file_path.name} -> {target_folder.name}/")
                staged_count += 1
            else:
                print(f"Skipped (already exists): {file_path.name}")

    print(f"Auto-staging complete. {staged_count} new file(s) staged.")

if __name__ == "__main__":
    stage_clips()