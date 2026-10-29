#!/usr/bin/env python3
"""
Cinegrade A/B Hook Generator
Generates multi-variant caption and hook matrices for platform testing.
"""

import csv
from pathlib import Path

WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
OUTPUT_CSV = WORKSPACE / "dist" / "ab_hooks_matrix.csv"
CLIPS_DIR = WORKSPACE / "dist" / "clips"
ARCHIVE_DIR = WORKSPACE / "dist" / "archive"

HOOK_TEMPLATES = [
    "Most creators don't realize {topic} until it's too late...",
    "Stop scrolling if you want to master {topic} in 10 seconds.",
    "The exact workflow I use for {topic} as a Cinegrade creator."
]

def generate_variants():
    # Gather active clips from clips/ or latest archive if clips is empty
    clips = [p.name for p in CLIPS_DIR.glob("*.mp4")]
    if not clips:
        # Fallback to check most recent archive folder
        latest_archive = sorted(ARCHIVE_DIR.glob("*"))
        if latest_archive:
            clips = [p.name for p in latest_archive[-1].glob("*.mp4")]
    
    if not clips:
        clips = ["graded_live_daemon_test_2026.mp4"]

    variants = []
    for asset_name in clips:
        topic = asset_name.replace("_", " ").replace(".mp4", "")
        for i, template in enumerate(HOOK_TEMPLATES, 1):
            hook = template.format(topic=topic)
            variants.append({
                "Variant": f"Variant {i}",
                "Asset": asset_name,
                "Hook": hook,
                "CallToAction": "Save this workflow and follow @cinegrade.cc"
            })
    
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Variant", "Asset", "Hook", "CallToAction"])
        writer.writeheader()
        writer.writerows(variants)
    print(f"Generated clean A/B hook matrix for {len(clips)} asset(s) -> {OUTPUT_CSV.name}")

if __name__ == "__main__":
    generate_variants()
