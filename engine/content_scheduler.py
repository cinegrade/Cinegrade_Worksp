import os
import csv
import glob
import time
import subprocess
from datetime import datetime, timedelta
import config as cfg

# Resolve workspace root dynamically relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = getattr(cfg, "BASE_DIR", os.path.abspath(os.path.join(SCRIPT_DIR, "..")))

POSSIBLE_LEDGER_PATHS = [
    os.path.join(WORKSPACE_DIR, "engine", "metadata_ingest.csv"),
    os.path.join(WORKSPACE_DIR, "metadata_ingest.csv")
]

CLIPS_DIR = os.path.join(WORKSPACE_DIR, "dist", "clips")
THUMBS_DIR = os.path.join(WORKSPACE_DIR, "dist", "thumbnails")
LOG_OUTPUT_PATH = os.path.join(WORKSPACE_DIR, "latest_release_manifest.txt")

POSTING_SLOTS = ["12:00", "18:00", "20:30"]

def parse_filename_metadata(filepath):
    """Fallback parser: extracts metadata directly from rendered clip filenames."""
    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]
    parts = name_no_ext.split("_")
    
    title = parts[1] if len(parts) > 1 else "CINEMATIC_REEL"
    lut = parts[4] if len(parts) > 4 else "CINEMATIC"
    motion = parts[3] if len(parts) > 3 else "CENTER"
    
    return {
        "Title": title,
        "LUT": lut,
        "Motion": motion,
        "FilePath": filepath
    }

def find_matching_thumbnail(filepath):
    """Locates matching PNG thumbnail frame in dist/thumbnails/."""
    basename_no_ext = os.path.splitext(os.path.basename(filepath))[0]
    expected_thumb = os.path.join(THUMBS_DIR, f"{basename_no_ext}_thumb.png")
    
    if os.path.exists(expected_thumb):
        return expected_thumb
    return "No thumbnail generated"

def calculate_drop_schedule(total_items, start_date=None, clips_per_day=1):
    if start_date is None:
        start_date = datetime.now() + timedelta(days=1)
    
    schedule = []
    current_date = start_date

    for i in range(total_items):
        slot_time = POSTING_SLOTS[i % len(POSTING_SLOTS)]
        date_str = current_date.strftime("%A, %b %d, %Y")
        schedule.append(f"{date_str} @ {slot_time}")
        
        if (i + 1) % clips_per_day == 0:
            current_date += timedelta(days=1)
            
    return schedule

def export_to_apple_notes(title, content):
    """Creates or updates a note in Apple Notes using osascript."""
    html_content = content.replace("\n", "<br>")
    
    applescript = f'''
    tell application "Notes"
        activate
        if not (exists account "iCloud") then
            set defaultAccount to first account
        else
            set defaultAccount to account "iCloud"
        end if
        
        make new note at folder "Notes" of defaultAccount with properties {{name:"{title}", body:"<h1>{title}</h1><br>{html_content}"}}
    end tell
    '''
    
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
        print("\n[+] Successfully exported manifest with thumbnails to Apple Notes!")
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Failed to write to Apple Notes: {e}")

def generate_social_manifest():
    print("=" * 60)
    print(" 📅 CINEGRADE CONTENT RELEASE & CALENDAR LEDGER")
    print(f" Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    rows = []
    ledger_file = next((p for p in POSSIBLE_LEDGER_PATHS if os.path.exists(p)), None)

    if ledger_file:
        with open(ledger_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

    if not rows:
        print("\n[*] CSV ledger not found. Scanning dist/clips/ for rendered master files...")
        rendered_clips = sorted(glob.glob(os.path.join(CLIPS_DIR, "*.mp4")))
        for clip in rendered_clips:
            rows.append(parse_filename_metadata(clip))

    if not rows:
        print(f"\n[!] No master clips or metadata records found.")
        print(f"    Add assets and run 'python3 batch_render.py' first.")
        return

    drop_schedule = calculate_drop_schedule(len(rows), clips_per_day=1)

    log_lines = []
    log_lines.append(f"CINEGRADE RELEASE MANIFEST & SCHEDULE | {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append("------------------------------------------------------------\n")

    print(f"\n[+] Processing {len(rows)} recorded master asset(s)...\n")

    for i, clip in enumerate(rows, 1):
        title = clip.get("Title", "Untitled")
        lut = clip.get("LUT", "CINEMATIC")
        pan = clip.get("Motion", "CENTER")
        filepath = clip.get("FilePath", "")
        filename = os.path.basename(filepath) if filepath else f"Clip_{i}"
        scheduled_slot = drop_schedule[i - 1]
        
        # Resolve Thumbnail Path
        thumb_path = find_matching_thumbnail(filepath)

        caption = (
            f"⚡️ {title} // Cinematic Edit\n"
            f"Graded with {lut} look | Motion: {pan}\n\n"
            f"#cinegrade #capcuttemplate #cinematicedit #visuals #videoediting #aesthetic"
        )

        entry = (
            f"[{i}] Asset: {filename}\n"
            f"    Scheduled Drop : 🗓️ {scheduled_slot}\n"
            f"    Thumbnail Asset: 🖼️ {thumb_path}\n"
            f"    Title Tag      : {title}\n"
            f"    Style/LUT      : {lut} ({pan} Pan)\n"
            f"    Caption:\n{caption}\n"
            f"------------------------------------------------------------"
        )
        log_lines.append(entry)
        print(entry)

    full_manifest_text = "\n".join(log_lines)

    # Write text log
    with open(LOG_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(full_manifest_text)

    # Sync to Apple Notes
    note_title = f"Cinegrade Schedule - {time.strftime('%b %d, %Y')}"
    export_to_apple_notes(note_title, full_manifest_text)

if __name__ == "__main__":
    generate_social_manifest()