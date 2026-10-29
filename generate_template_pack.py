#!/usr/bin/env python3
import subprocess
import sys

# Define the 5 template keyframes with individual prompts and visual styles
prompts = [
    ("Cinematic Camera Lens", "TEAL_ORANGE"),
    ("Craft Desk", "TEAL_ORANGE"),
    ("Dog in Motion", "CYBERPUNK"),
    ("Light Through Window", "CINEMATIC_PURPLE"),
    ("Portrait of a Girl", "TEAL_ORANGE")
]

print("=== Starting Batch Keyframe Generation for 'Cinegrade First AI Template' ===")

for prompt, style in prompts:
    print(f"\n[+] Generating asset for prompt: '{prompt}' (Style: {style})")
    subprocess.run(["python3", "engine/image_generator.py", prompt, style], check=True)

print("\n=== Generation Complete! Running Full Render Pipeline ===")
subprocess.run(["./run_pipeline.sh"], check=True)
