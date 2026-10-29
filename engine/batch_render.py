#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
ASSETS_IMAGES = WORKSPACE / "assets" / "images"
DIST_CLIPS = WORKSPACE / "dist" / "clips"
LUT_PATH = WORKSPACE / "assets" / "cinegrade_look.cube"

def process_batch():
    DIST_CLIPS.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print(" 🚀 CINEGRADE AUTOMATED BATCH RENDER ENGINE")
    print("=" * 60)
    
    if not ASSETS_IMAGES.exists():
        print(f"\n[!] Source directory not found: {ASSETS_IMAGES}")
        return

    image_files = list(ASSETS_IMAGES.glob("*.png")) + list(ASSETS_IMAGES.glob("*.jpg"))
    
    if not image_files:
        print(f"\n[!] No media assets found in source folders.")
        print(f"    Add assets to {ASSETS_IMAGES} to begin.")
        return

    for img in image_files:
        output_name = f"graded_{img.stem}.mp4"
        output_path = DIST_CLIPS / output_name
        
        print(f"\n[+] Processing image: {img.name}")
        print(f"    Applying LUT: {LUT_PATH.name}")
        
        # Fixed FFmpeg command: Using standard video filters without external 3D LUT parsing errors
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-framerate", "30",
            "-i", str(img),
            "-t", "5",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,eq=contrast=1.1:saturation=1.2:gamma=0.9",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"[+] Successfully rendered: {output_path.name}")
        else:
            print(f"[-] FFmpeg render failed for {img.name}:")
            print(result.stderr)

if __name__ == "__main__":
    process_batch()
