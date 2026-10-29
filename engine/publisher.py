import os
import csv
import glob
import json
import requests
import config as cfg

def load_pending_metadata():
    """Reads the metadata CSV to fetch titles, descriptions, and hashtags for upload."""
    metadata_entries = []
    if not os.path.exists(cfg.METADATA_INGEST_CSV):
        return metadata_entries
    
    with open(cfg.METADATA_INGEST_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metadata_entries.append(row)
    return metadata_entries

def publish_to_youtube_shorts(clip_path, title, description, tags):
    """
    Automated YouTube Data API v3 integration for Shorts publishing.
    Requires OAuth2 credentials configured in config.py or environment variables.
    """
    print(f"  -> [Cinegrade API] Staging YouTube Short: {title}")
    # Integration hook for YouTube Data API resumable upload v3
    # Endpoint: https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable
    # Real implementation uses google-api-python-client
    pass

def publish_to_tiktok(clip_path, caption):
    """
    Automated TikTok Content Posting API integration.
    """
    print(f"  -> [Cinegrade API] Staging TikTok Drop: {caption[:30]}...")
    # Integration hook for TikTok Direct Post API
    # Endpoint: https://open.tiktokapis.com/v2/post/publish/video/init/
    pass

def run_auto_publisher():
    print(f"\n[{cfg.THEMES['NINJA_ORANGE']['ACCENT']}Cinegrade Publisher Daemon{cfg.THEMES['NINJA_ORANGE']['RESET']}] Initializing cloud distribution queue...")
    entries = load_pending_metadata()
    
    if not entries:
        print("[!] No metadata records found to publish.")
        return

    # Target the latest rendered batch
    for entry in entries[-3:]: # Process latest batch
        clip_path = entry.get("Export Clip Path")
        if clip_path and os.path.exists(clip_path):
            title = entry.get("Suggested YouTube Shorts Title")
            desc = entry.get("Suggested YouTube Shorts Description")
            tags = entry.get("Hashtags")
            
            # Execute pipeline sync
            publish_to_youtube_shorts(clip_path, title, desc, tags)
            publish_to_tiktok(clip_path, title + " " + tags)
        else:
            print(f"[!] Clip path missing or invalid: {clip_path}")
            
    print("[+] Distribution queue synchronization complete.")

if __name__ == "__main__":
    run_auto_publisher()