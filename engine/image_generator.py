#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
ASSETS_IMAGES_DIR = WORKSPACE / "assets" / "images"

# Default prompt config if none is passed via CLI
DEFAULT_PROMPT = "CYBERPUNK NEON CITY"
DEFAULT_STYLE = "TEAL_ORANGE"

def generate_cinematic_assets(prompt=DEFAULT_PROMPT, style=DEFAULT_STYLE):
    ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sanitize prompt for filename
    file_tag = prompt.lower().replace(" ", "_")
    target_image = ASSETS_IMAGES_DIR / f"{file_tag}_keyframe.png"
    
    print(f"Initializing automated cinematic image generator with prompt: '{prompt}'...")
    
    width, height = 1080, 1920
    
    # Style palette selection based on prompt intent
    if "cyberpunk" in prompt.lower() or style == "TEAL_ORANGE":
        bg_color = "#0B132B"
        border_color1 = "#FF5722"  # Neon Orange
        border_color2 = "#00E5FF"  # Neon Cyan
        gradient_base = (11, 19, 43)
    elif "monochrome" in prompt.lower() or "noir" in prompt.lower():
        bg_color = "#121212"
        border_color1 = "#FFFFFF"
        border_color2 = "#777777"
        gradient_base = (20, 20, 20)
    else:
        bg_color = "#1A002C"  # Vaporwave / Cinematic Purple
        border_color1 = "#E040FB"
        border_color2 = "#00E5FF"
        gradient_base = (26, 0, 44)
        
    image = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # Render background gradient
    for y in range(height):
        r = int(gradient_base[0] + (y / height) * 30)
        g = int(gradient_base[1] + (y / height) * 40)
        b = int(gradient_base[2] + (y / height) * 80)
        draw.line([(0, y), (width, y)], fill=(min(r, 255), min(g, 255), min(b, 255)))
        
    # Render prompt box overlay
    draw.rectangle([80, 700, width - 80, 1220], outline=border_color1, width=8)
    draw.rectangle([100, 720, width - 100, 1200], outline=border_color2, width=4)
    
    # Render dynamic text prompt on asset
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 55)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 36)
    except IOError:
        font_large = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.text((130, 850), "CINEGRADE PROMPT:", fill="#00E5FF", font=font_sub)
    draw.text((130, 930), prompt.upper(), fill="#FFFFFF", font=font_large)
    draw.text((130, 1050), f"STYLE: {style}", fill="#FF5722", font=font_sub)
    
    image.save(target_image)
    print(f"[+] Keyframe generated successfully: {target_image.name}")

if __name__ == "__main__":
    # Allow prompt input via CLI arguments (e.g., python3 image_generator.py "Tokyo Night" "VAPORWAVE")
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT
    user_style = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STYLE
    generate_cinematic_assets(user_prompt, user_style)
