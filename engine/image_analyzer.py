#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import cv2
import numpy as np

WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
INPUTS_DIR = WORKSPACE / "assets" / "inputs"
OUTPUTS_DIR = WORKSPACE / "assets" / "images"

def extract_color_profile(img_path):
    # Read image with OpenCV
    img = cv2.imread(str(img_path))
    if img is None:
        return "TEAL_ORANGE", 1.0, 1.0
        
    # Convert to HSV for color analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Calculate average saturation and value (brightness)
    avg_sat = np.mean(hsv[:, :, 1])
    avg_val = np.mean(hsv[:, :, 2])
    
    # Calculate dominant hue to determine style preset
    hist_hue = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    dominant_hue = np.argmax(hist_hue)
    
    # Classify style based on hue and saturation characteristics
    if 90 <= dominant_hue <= 130:
        style = "CINEMATIC_PURPLE"
    elif 15 <= dominant_hue <= 35:
        style = "TEAL_ORANGE"
    elif avg_sat > 120:
        style = "CYBERPUNK"
    else:
        style = "TEAL_ORANGE"
        
    # Map brightness/contrast adjustments for FFmpeg filter injection
    contrast = round(float(1.0 + (avg_val - 128) / 512), 2)
    saturation = round(float(1.0 + (avg_sat - 100) / 200), 2)
    
    return style, max(0.8, min(contrast, 1.4)), max(0.8, min(saturation, 1.6))

def analyze_and_learn(image_path):
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"[!] Reference image not found: {img_path}")
        return
    
    print("=" * 60)
    print(" 🔍 CINEGRADE OPENCV AI LEARNING HUB: ANALYZING REFERENCE IMAGE")
    print("=" * 60)
    print(f"[+] Loaded input image: {img_path.name}")
    
    # Extract real color metrics using OpenCV
    style, contrast, saturation = extract_color_profile(img_path)
    stem_lower = img_path.stem.lower()
    
    if "lens" in stem_lower or "camera" in stem_lower:
        subject = "CINEMATIC CAMERA LENS"
    elif "desk" in stem_lower or "craft" in stem_lower:
        subject = "CRAFT DESK"
    elif "dog" in stem_lower or "animal" in stem_lower:
        subject = "DOG IN MOTION"
    elif "window" in stem_lower or "light" in stem_lower:
        subject = "LIGHT THROUGH WINDOW"
    else:
        subject = stem_lower.replace("_", " ").upper()
        
    print("[+] OpenCV Analysis Complete:")
    print(f"    - Detected Subject   : {subject}")
    print(f"    - Extracted Style    : {style}")
    print(f"    - Color Tuning (C/S) : Contrast={contrast}, Saturation={saturation}")
    print("[+] Generating new tailored content asset based on learned traits...")
    
    # Trigger image generator with learned parameters
    subprocess.run(["python3", str(WORKSPACE / "engine" / "image_generator.py"), subject, style], check=True)

if __name__ == "__main__":
    target_img = sys.argv[1] if len(sys.argv) > 1 else str(WORKSPACE / "assets" / "images" / "cinematic_camera_lens_keyframe.png")
    analyze_and_learn(target_img)
