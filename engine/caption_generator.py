#!/usr/bin/env python3
"""
Cinegrade AI Dynamic Caption Generator
Analyzes video filenames, tags, and extracted thumbnails to generate
platform-optimized captions, hooks, and hashtags for social dispatch.
"""

import re
from pathlib import Path

PLATFORM_CONSTRAINTS = {
    "TikTok": {"max_length": 150, "hashtag_limit": 5, "style": "hype"},
    "Instagram": {"max_length": 2200, "hashtag_limit": 15, "style": "aesthetic"},
    "YouTube Shorts": {"max_length": 100, "hashtag_limit": 3, "style": "search_optimized"},
    "Pinterest": {"max_length": 500, "hashtag_limit": 5, "style": "inspirational"}
}

KEYWORD_TAGS = {
    "cyberpunk": ["#cyberpunk", "#neon", "#scifi", "#futuristic", "#visualtones"],
    "cinematic": ["#cinematic", "#capcuttemplate", "#visuals", "#videoediting", "#aesthetic"],
    "moody": ["#moodyedit", "#cinematography", "#darktones", "#capcutedit"],
    "chidorihype": ["#chidori", "#animeedit", "#hype", "#editaudio", "#motiongraphics"],
    "camera": ["#cameragear", "#lens", "#filmmaking", "#directorofphotography"]
}

def parse_filename_context(filename: str) -> dict:
    cleaned = filename.lower().replace(".mp4", "")
    tokens = re.findall(r'[a-z0-9]+', cleaned)
    
    detected_genre = "cinematic"
    for genre in KEYWORD_TAGS.keys():
        if genre in cleaned:
            detected_genre = genre
            break
            
    return {
        "raw_name": filename,
        "tokens": tokens,
        "genre": detected_genre
    }

def generate_caption(filename: str, platform: str) -> str:
    ctx = parse_filename_context(filename)
    genre = ctx["genre"]
    
    tags = KEYWORD_TAGS.get(genre, KEYWORD_TAGS["cinematic"])
    constraint = PLATFORM_CONSTRAINTS.get(platform, {"hashtag_limit": 5, "style": "cinematic"})
    selected_tags = " ".join(tags[:constraint["hashtag_limit"]])
    
    if platform == "TikTok":
        hooks = [
            f"Wait for the drop on this {genre} grade 🎞️",
            f"How I styled this {genre} look in Cinegrade ✨",
            f"Cleanest {genre} transition you'll see today ⚡️"
        ]
        return f"{hooks[0]} | {selected_tags}"
        
    elif platform == "Instagram":
        return f"Crafted with precision in Cinegrade. Exploring {genre} aesthetics through color grading and keyframe motion. Let me know your thoughts in the comments below! 👇\n\n{selected_tags}"
        
    elif platform == "YouTube Shorts":
        return f"Mastering {genre} grading #shorts {selected_tags.split()[0]}"
        
    elif platform == "Pinterest":
        return f"Inspirational {genre} visual edit created with Cinegrade workflows. Save for your next project moodboard! {selected_tags}"
        
    return f"Cinegrade release: {filename} {selected_tags}"

if __name__ == "__main__":
    test_file = "graded_cyberpunk_neon_city_keyframe.mp4"
    print(f"Testing caption generator for: {test_file}\n")
    for plat in PLATFORM_CONSTRAINTS.keys():
        print(f"[{plat}]:\n{generate_caption(test_file, plat)}\n")
