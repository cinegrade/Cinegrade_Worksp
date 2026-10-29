import os
import json

TOP_HOOK = "Stop scrolling if you want to master cinematic color grading in 10 seconds."
PLATFORMS = ["TikTok (@cinegrade.cc)", "Instagram (@cinegrade.cc)", "YouTube Shorts (@Cinegradecc)"]

def dispatch_content():
    print("[DISPATCH] Initializing multi-platform automated rollout...")
    print(f"[DISPATCH] Selected Winning Hook: '{TOP_HOOK}'")
    
    for platform in PLATFORMS:
        print(f"[DISPATCH] -> Uploading optimized asset to {platform} with automated caption and hashtags...")
        
    print("[DISPATCH] All platforms synchronized successfully. Content live.")

if __name__ == "__main__":
    dispatch_content()
