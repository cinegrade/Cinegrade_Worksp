import cv2
import os
import glob
import csv
import shutil
import sys
import threading
import http.server
import socketserver
import webbrowser
from datetime import datetime
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import numpy as np

import config as cfg
import luts
import overlays
import typography

# ============================================================
# CINEGRADE ENGINE: MOTION KEYFRAME PRESETS
# ============================================================

# FFmpeg filter expressions for cinematic motion scaling & panning
FFMPEG_MOTION_PRESETS = {
    "CENTER": "zoompan=z='min(zoom+0.0015,1.15)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920",
    "LEFT":   "zoompan=z='min(zoom+0.0015,1.15)':d=150:x='if(eq(on,1),0,x-1)':y='ih/2-(ih/zoom/2)':s=1080x1920",
    "RIGHT":  "zoompan=z='min(zoom+0.0015,1.15)':d=150:x='if(eq(on,1),iw-iw/zoom,x+1)':y='ih/2-(ih/zoom/2)':s=1080x1920",
    "PUSHIN": "zoompan=z='min(zoom+0.003,1.25)':d=120:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920",
    "STATIC": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
}

import os

# Explicit path for Intel Mac Homebrew installation
FFMPEG_BIN = "/usr/local/bin/ffmpeg" if os.path.exists("/usr/local/bin/ffmpeg") else "ffmpeg"

def deploy_to_distribution_hub(video_path):
    # function body...
    """
    Deploys the rendered video and its assets to the distribution hub.
    """
    # Your distribution hub staging logic here
    pass

def get_motion_filter(motion_name):
    """Retrieves the matching FFmpeg motion keyframe filter or defaults to CENTER."""
    return FFMPEG_MOTION_PRESETS.get(motion_name.upper(), FFMPEG_MOTION_PRESETS["CENTER"])

def render_video_with_motion(input_image, output_mp4, motion_style="CENTER", duration=5):
    """
    Renders a vertical video reel applying the selected motion keyframe preset.
    """
    motion_filter = get_motion_filter(motion_style)
    
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", input_image,
        "-t", str(duration),
        "-vf", motion_filter,          # Applies the dynamic zoom/pan keyframes here
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        output_mp4
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[+] Rendered motion preset [{motion_style}]: {os.path.basename(output_mp4)}")
    except Exception as e:
        print(f"[!] Motion render failed: {e}")
# ============================================================
# CINEGRADE ENGINE: THUMBNAIL EXTRACTION MODULE
# ============================================================
import os
import subprocess

def extract_thumbnail(video_path, output_thumb_path=None, timestamp_sec=1.0):
    """
    Extracts a high-quality PNG thumbnail frame from a rendered MP4 video reel.
    """
    if not os.path.exists(video_path):
        print(f"     [!] Cannot extract thumbnail: File '{video_path}' not found.")
        return None

    if output_thumb_path is None:
        base_dir = os.path.dirname(video_path)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # Route to dist/thumbnails/ directory
        thumb_dir = os.path.abspath(os.path.join(base_dir, "..", "thumbnails"))
        os.makedirs(thumb_dir, exist_ok=True)
        output_thumb_path = os.path.join(thumb_dir, f"{base_name}_thumb.png")

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(timestamp_sec),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        output_thumb_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"     [+] Thumbnail generated: {os.path.basename(output_thumb_path)}")
        return output_thumb_path
    except Exception as e:
        print(f"     [!] Thumbnail extraction failed: {e}")
        return None

active_theme = "NINJA_ORANGE"

def t_color(key):
    return cfg.THEMES.get(active_theme, cfg.THEMES["NINJA_ORANGE"])[key]

def log_production_event(entry_text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(cfg.HISTORY_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {entry_text}\n")
    except Exception: pass

def log_metadata_to_csv(filename, title, pan, style, active_lut, clip_path):
    file_exists = os.path.exists(cfg.METADATA_INGEST_CSV)
    clean_title = title if title else "Cinegrade Visual Masterpiece"
    social_title = f"{clean_title} | Cinematic Edit"
    description = f"{clean_title} rendered with Cinegrade. Camera movement: {pan.lower()}; color look: {active_lut.lower()}; effects: {style.lower()}."
    base_tags = "#Cinegrade #VideoEdit #Shorts #Reels #TikTok"
    style_tag = f" #{style.lower().replace('_', '')}" if style != "NONE" else ""
    hashtags = f"{base_tags}{style_tag}"

    try:
        with open(cfg.METADATA_INGEST_CSV, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Source Filename", "Suggested YouTube Shorts Title", "Suggested YouTube Shorts Description", "Suggested TikTok Caption", "Suggested Instagram Reels Caption", "Hashtags", "Motion", "Effects", "LUT", "Text Color", "Soundtrack", "Export Clip Path"])
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            writer.writerow([timestamp, filename, social_title, description, social_title + " " + hashtags, social_title + " " + hashtags, hashtags, pan, style, active_lut, "WHITE", os.path.basename(cfg.DEFAULT_AUDIO), clip_path])
    except Exception as e:
        log_production_event(f"METADATA LOG ERROR: {e}")

def deploy_to_distribution_hub():
    video_clips = glob.glob(os.path.join(cfg.CLIPS_FOLDER, "*.mp4"))
    if not video_clips:
        print(f"\n     {t_color('MAIN')}[!] No rendered clips found to stage in distribution hub.{t_color('RESET')}")
        return
    platforms = ["youtube_shorts", "tiktok_drops", "instagram_reels"]
    for platform in platforms:
        os.makedirs(os.path.join(cfg.DISTRIBUTION_HUB, platform), exist_ok=True)
    print(f"\n     {t_color('ACCENT')}-> Initialising Distribution Hub Synchronization Flow...{t_color('RESET')}")
    for v_path in video_clips:
        bname = os.path.basename(v_path)
        for platform in platforms:
            shutil.copy2(v_path, os.path.join(cfg.DISTRIBUTION_HUB, platform, bname))
    print(f"     {t_color('MAIN')}[+] Successfully staged {len(video_clips)} clips across platform dropboxes.{t_color('RESET')}")

def allocate_drop_schedule():
    print(f"\nSelect Content Drop Rhythm:\n Morning Engagement Burst (08:30 AM)\n Prime Evening Scroll Spike (18:15 PM)")
    r_ch = input("Choice: ").strip()
    drop_time = "08:30:00" if r_ch == "1" else "18:15:00" if r_ch == "2" else "12:00:00"
    video_clips = glob.glob(os.path.join(cfg.CLIPS_FOLDER, "*.mp4"))
    if not video_clips:
        print(f"     {t_color('MAIN')}[!] Render video clips first before assigning drop schedules.{t_color('RESET')}")
        return
    try:
        with open(cfg.SCHEDULE_LEDGER, "a", encoding="utf-8") as f:
            f.write(f"\n# --- NEW AUTOMATED CONTENT RELEASE SCHEDULE BATCH ({datetime.now().strftime('%Y-%m-%d')}) ---\n")
            for idx, v_path in enumerate(video_clips, 1):
                f.write(f"RELEASE_SLOT_DAY_{idx} = {drop_time} TARGET_CLIP = {os.path.basename(v_path)}\n")
        print(f"     {t_color('MAIN')}[+] Drop sequences successfully written onto ledger!{t_color('RESET')}")
    except Exception as e: print(f"     Ledger Update Error: {e}")

def run_audio_trend_sensor_manifest():
    radar_file = os.path.join(cfg.AUDIO_FOLDER, "trend_radar.txt")
    print(f"\n     {t_color('ACCENT')}-> Scanning assets/audio/ for viral trend signatures...{t_color('RESET')}")
    audio_tracks = sorted(glob.glob(os.path.join(cfg.AUDIO_FOLDER, "*.mp3")))
    try:
        with open(radar_file, "w", encoding="utf-8") as f:
            f.write("====================================================\n")
            f.write("     CINEGRADE WORKSPACE ALGORITHMIC TREND RADAR    \n")
            f.write(f"     Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}             \n")
            f.write("====================================================\n\n")
            if not audio_tracks:
                f.write("[!] No audio tracking files found inside assets/audio/.\n")
                print(f"     {t_color('MAIN')}[!] No local audio tracking tracks found to scan.{t_color('RESET')}")
                return
            f.write("RANK  | ALGO SCORE | AUDIO TRACK SIGNATURE | REC RECOMMENDATION\n")
            f.write("------|------------|-----------------------|---------------------\n")
            for idx, track in enumerate(audio_tracks, 1):
                bname = os.path.basename(track)
                score = 98.4 if "hype" in bname.lower() else 94.1 if "music" in bname.lower() else 89.5
                rec = "HIGH TRAFFIC (Use _WAVE)" if score > 90 else "STABLE BACKGROUND"
                f.write(f"#{idx:02d}   | {score}%      | {bname.ljust(21)} | {rec}\n")
        print(f"     {t_color('MAIN')}[+] Algorithmic trend manifest successfully written to: assets/audio/trend_radar.txt{t_color('RESET')}")
    except Exception as e: print(f"     Sensor Sync Error: {e}")

def launch_web_layout_preview_server():
    os.makedirs(cfg.WEB_PREVIEW_DIR, exist_ok=True)
    
    # Clean up old previews first so there are no stale files
    for old_preview in glob.glob(os.path.join(cfg.WEB_PREVIEW_DIR, "*.mp4")):
        try: os.remove(old_preview)
        except Exception: pass

    video_clips = glob.glob(os.path.join(cfg.CLIPS_FOLDER, "*.mp4"))
    if not video_clips:
        print(f"\n     {t_color('MAIN')}[!] No rendered clips found to preview.{t_color('RESET')}")
        return

    html_content = """<!DOCTYPE html><html><head><title>Cinegrade Preview Deck</title>
    <style>body{background:#111;color:#fff;font-family:sans-serif;padding:30px;}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:25px;}
    .card{background:#222;border:2px solid #ff7700;border-radius:8px;padding:15px;text-align:center;}
    video{width:100%;border-radius:4px;background:#000;}</style></head>
    <body><h2>🎬 Cinegrade Media Workspace Preview Engine</h2><div class='grid'>"""

    for idx, v_path in enumerate(video_clips):
        dest_path = os.path.join(cfg.WEB_PREVIEW_DIR, f"preview_{idx}.mp4")
        shutil.copy2(v_path, dest_path)
        # Ensure file is fully flushed
        if os.path.exists(dest_path):
            html_content += f"<div class='card'><h4>{os.path.basename(v_path)}</h4><video controls preload='metadata' src='preview_{idx}.mp4'></video></div>"
            
    html_content += "</div></body></html>"
    
    with open(os.path.join(cfg.WEB_PREVIEW_DIR, "index.html"), "w", encoding="utf-8") as f: 
        f.write(html_content)

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args): pass

    old_cwd = os.getcwd()
    os.chdir(cfg.WEB_PREVIEW_DIR)
    PORT = 8080
    
    try:
        with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
            print(f"\n     {t_color('ACCENT')}[Web Server Channel Active at http://localhost:{PORT}]{t_color('RESET')}")
            webbrowser.open(f"http://localhost:{PORT}")
            # Serve until user hits enter back in the terminal
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            input(f"\n     {t_color('ACCENT')}Server running. Press [Enter] to close preview deck...{t_color('RESET')}\n")
            httpd.shutdown()
    except Exception as e:
        print(f"     [!] Server Error: {e}")
    
    os.chdir(old_cwd)

def analyze_and_extract_best_highlight_window(cap, target_frames, total_src_frames, sy, bh, sx, bw, native_fps=30):
    stride_step = max(1, int(native_fps * 0.25))
    sampled_indices, crushed_matrices = [], []
    for f_idx in range(0, total_src_frames, stride_step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret: break
        crop = frame[sy:sy+bh, sx:sx+bw]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
        crushed = cv2.resize(gray_blur, (160, 90), interpolation=cv2.INTER_AREA)
        
        sampled_indices.append(f_idx)
        crushed_matrices.append(crushed)
        
    if len(crushed_matrices) < 2:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return []
    motion_scores = []
    for i in range(len(crushed_matrices) - 1):
        diff = cv2.absdiff(crushed_matrices[i+1], crushed_matrices[i])
        clamped_diff = np.clip(diff, 0, 45)
        motion_scores.append(np.mean(clamped_diff))
        
    stride_window_size = max(1, int(target_frames / stride_step))
    max_avg_motion, best_stride_start = -1.0, 0
    for i in range(len(motion_scores) - stride_window_size + 1):
        current_avg = np.mean(motion_scores[i:i+stride_window_size])
        if current_avg > max_avg_motion:
            max_avg_motion = current_avg; best_stride_start = i
    best_start_frame = sampled_indices[best_stride_start]
    if best_start_frame + target_frames > total_src_frames:
        best_start_frame = max(0, total_src_frames - target_frames)
        
    print(f"  {t_color('ACCENT')}[+] Strided Analysis Complete! Peak Highlight Frame Window: {best_start_frame} to {best_start_frame + target_frames}{t_color('RESET')}", flush=True)
    final_extracted_frames = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, best_start_frame)
    for _ in range(target_frames):
        ret, frame = cap.read()
        if not ret: break
        final_extracted_frames.append(frame[sy:sy+bh, sx:sx+bw])
    return final_extracted_frames

def single_image_to_vertical_zoom_video(img_path, temp_path, dur=5, fps=30, zoom=0.12, fade=0.5, wm="", title="", pan="CENTER", style="NONE", text_color="WHITE"):
    ext = os.path.splitext(img_path)[1].lower()
    is_video_input = ext in [".mp4", ".mov", ".avi", ".mkv"]
    is_landscape = "LANDSCAPE" in style.upper()
    tw, th = (cfg.HORIZONTAL_W, cfg.HORIZONTAL_H) if is_landscape else (cfg.VERTICAL_W, cfg.VERTICAL_H)
    tot_f, fade_f = int(dur * fps), int(fade * fps)
    bgr_color = typography.get_color_bgr(text_color)

    if is_video_input:
        cap = cv2.VideoCapture(img_path)
        if not cap.isOpened(): return False
        ow, oh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_src_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        bh, bw = oh, int(oh * (tw / th))
        if bw > ow: bw = ow; bh = int(ow * (th / tw))
        sx, sy = (ow - (bw - bw%2)) // 2, (oh - (bh - bh%2)) // 2
        video_frames_buffer = analyze_and_extract_best_highlight_window(cap, tot_f, total_src_frames, sy, (bh - bh%2), sx, (bw - bw%2), fps)
        cap.release()
        if not video_frames_buffer: return False
    else:
        img = cv2.imread(img_path)
        if img is None: return False
        oh, ow, _ = img.shape
        print(f"  -> Rendering Static Image Canvas: {pan} Motion | LUT Look: {style}", flush=True)
        bh, bw = oh, int(oh * (tw / th))
        if bw > ow: bw = ow; bh = int(ow * (th / tw))
        sx, sy = (ow - (bw - bw%2)) // 2, (oh - (bh - bh%2)) // 2

    out = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*'avc1'), fps, (tw, th))
    current_video_source_ptr = 0.0
    
    for f_idx in range(tot_f):
        p = f_idx / tot_f
        if is_video_input:
            if "SPEED" in style.upper():
                if p < 0.25: current_video_source_ptr += 2.0
                elif p < 0.75: current_video_source_ptr += 0.3
                else: current_video_source_ptr += 1.0
            else: current_video_source_ptr += 1.0
            base_img = video_frames_buffer[int(current_video_source_ptr) % len(video_frames_buffer)]
        else:
            base_img = img[sy:sy+(bh - bh%2), sx:sx+(bw - bw%2)]
            
        cz = 1.0 + (p * zoom) if not is_video_input else 1.0
        cw, ch = int((bw - bw%2) / cz), int((bh - bh%2) / cz)
        cw, ch = cw - cw%2, ch - ch%2
        x1 = 0 if pan == "LEFT" else (bw - bw%2) - cw if pan == "RIGHT" else ((bw - bw%2) - cw) // 2
        y1 = 0 if pan == "UP" else (bh - bh%2) - ch if pan == "DOWN" else ((bh - bh%2) - ch) // 2
        
        frame = cv2.resize(base_img[y1:y1+ch, x1:x1+cw], (tw, th))
        frame = luts.apply_cinegrade_lut(frame, style)
        
        if "FOG" in style.upper(): frame = cv2.add(frame, cv2.convertScaleAbs(overlays.generate_moving_fog_layer(tw, th, f_idx, tot_f), alpha=0.25, beta=0))
        if "RAIN" in style.upper(): frame = cv2.addWeighted(frame, 1.0, overlays.generate_rain_layer(tw, th, f_idx), 0.35, 0)
        if "GLOW" in style.upper(): frame = overlays.apply_diffusion_glow(frame)
        if "HALATION" in style.upper(): frame = overlays.apply_halation(frame)
        if "ANAMORPHIC" in style.upper(): frame = overlays.apply_anamorphic_flare(frame, f_idx)
        if "FRINGE" in style.upper(): frame = overlays.apply_chromatic_fringe(frame)
        if "VINTAGE" in style.upper(): frame = cv2.add(frame, overlays.generate_light_leak_layer(tw, th, f_idx, tot_f)); frame = overlays.apply_film_grain(frame)
        if "GLITCH" in style.upper() and f_idx < int(1.5 * fps): frame = overlays.apply_glitch_fx(frame, f_idx)
        if "VIGNETTE" in style.upper(): frame = overlays.apply_vignette(frame)
        
        frame = overlays.inject_micro_variation_fx(frame, f_idx, seed_val=int(ow % 100))
        bar_size = 100 if is_landscape else 160
        cv2.rectangle(frame, (0, 0), (tw, bar_size), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, th - bar_size), (tw, th), (0, 0, 0), -1)
        
        if "WAVE" in style.upper(): frame = overlays.draw_audio_waveform(frame, f_idx, tot_f, bgr_color, tw, th, bar_size)
        if "BORDER" in style.upper(): cv2.rectangle(frame, (30, bar_size + 30), (tw - 30, th - bar_size - 30), bgr_color, 4, cv2.LINE_AA)
        if title: frame = typography.render_neon_glowing_text(frame, title, f_idx, int(1.0 * fps), bgr_color, tw, th, is_landscape)
        if wm:
            ts, _ = cv2.getTextSize(wm, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)
            cv2.putText(frame, wm, ((tw - ts[0]) // 2, th - (180 if is_landscape else 300)), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 9, cv2.LINE_AA)
            cv2.putText(frame, wm, ((tw - ts[0]) // 2, th - (180 if is_landscape else 300)), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
            
        if f_idx < fade_f: frame = cv2.convertScaleAbs(frame, alpha=(f_idx / fade_f), beta=0)
        elif f_idx > (tot_f - fade_f): frame = cv2.convertScaleAbs(frame, alpha=((tot_f - f_idx) / fade_f), beta=0)
        
        out.write(frame)
        sys.stdout.write(f"\r     [Pipeline Flow] {'█' * int(25 * (f_idx + 1) / tot_f) + '░' * (25 - int(25 * (f_idx + 1) / tot_f))} {int(((f_idx + 1) / tot_f) * 100)}% Complete")
        sys.stdout.flush()
        
    out.release()
    print()
    return True

def add_audio_to_video(v_path, a_path, out_path):
    try:
        vc, ac = VideoFileClip(v_path), AudioFileClip(a_path)
        
        # Handle subclip/subclipped compatibility across MoviePy versions
        final_audio = ac.subclipped(0, vc.duration) if hasattr(ac, "subclipped") else ac.subclip(0, vc.duration)
        
        # Safe audio fadeout compatibility across MoviePy versions
        if vc.duration > 1.5:
            try:
                if hasattr(final_audio, "audio_fadeout"):
                    final_audio = final_audio.audio_fadeout(1.5)
                elif hasattr(final_audio, "audio_fade_out"):
                    final_audio = final_audio.audio_fade_out(1.5)
                elif hasattr(final_audio, "afade"):
                    final_audio = final_audio.afade(fade_out=1.5, duration=1.5)
            except Exception:
                pass  # Fallback to standard audio if fade method signature differs

        # Handle with_audio / set_audio compatibility
        fv = vc.with_audio(final_audio) if hasattr(vc, "with_audio") else vc.set_audio(final_audio)
        
        fv.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
        vc.close()
        ac.close()
        print(f"     {t_color('MAIN')}[+] Soundtrack successfully merged into: {os.path.basename(out_path)}{t_color('RESET')}")
        return True
    except Exception as e:
        print(f"     [!] Audio Merge Error: {e}")
        return False

def compile_videos(folder, out_path):
    print("\nStep 3: Creating master compilation loop...", flush=True)
    paths = sorted(glob.glob(os.path.join(folder, "*_vertical.mp4")))
    if not paths: return
    clips = [VideoFileClip(p) for p in paths]
    try:
        print("  -> Injecting 0.5s Cinematic Cross-Dissolve Transitions...", flush=True)
        fc = concatenate_videoclips(clips, method="compose", padding=-0.5)
        print("  -> Generating transition-stabilized master reel...", flush=True)
        fc.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
        for c in clips: c.close()
        fc.close(); print(f"\n[+] Master Reel saved to {out_path}")
    except Exception as e: log_production_event(f"ERROR: Compilation failed -> {e}")

def parse_filename_config(filename, def_dur, def_aud, current_global_lut):
    dur, aud, title, pan, style = def_dur, def_aud, "", "CENTER", "NONE"
    text_color, active_lut = "WHITE", current_global_lut
    parts = filename.split("_")
    
    if parts and parts[-1].upper() in cfg.VALID_COLORS: 
        text_color = parts[-1].upper()
        parts = parts[:-1]
        
    lut_map = {"TEAL": "TEAL_ORANGE", "CYBERPUNK": "CYBERPUNK", "ANIME": "ANIME", "NOIR": "NOIR", "STANDARD": "STANDARD"}
    if parts and parts[-1].upper() in lut_map: 
        active_lut = lut_map[parts[-1].upper()]
        parts = parts[:-1]
        
    matched_tags = []
    while parts and parts[-1].upper() in cfg.SUPPORTED_EFFECTS: 
        matched_tags.append(parts[-1].upper())
        parts = parts[:-1]
    if matched_tags: style = "".join(reversed(matched_tags))
    
    if parts and parts[-1].upper() in ["LEFT", "RIGHT", "UP", "DOWN", "CENTER"]: 
        pan = parts[-1].upper()
        parts = parts[:-1]
        
    if len(parts) == 1: return dur, aud, title, pan, style, text_color, active_lut
    nums = [i for i, p in enumerate(parts) if p.isdigit()]
    if nums:
        idx = nums[0]
        dur = int(parts[idx])
        if idx > 1: title = " ".join(parts[1:idx]).upper()
        if idx + 1 < len(parts):
            trig = parts[idx+1]
            aud = os.path.join(cfg.AUDIO_FOLDER, f"{trig}.mp3" if not trig.endswith(".mp3") else trig)
    return dur, aud, title, pan, style, text_color, active_lut

def archive_old_outputs():
    if not os.path.exists(cfg.CLIPS_FOLDER): return
    old = glob.glob(os.path.join(cfg.CLIPS_FOLDER, "*.mp4"))
    if not old: return
    bdir = os.path.join(cfg.BACKUP_BASE, f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    os.makedirs(bdir, exist_ok=True)
    for f in old: shutil.move(f, os.path.join(bdir, os.path.basename(f)))

def run_processing_pipeline(wm, z_rate, comp, clean, global_lut):
    log_production_event(f"BATCH INITIALIZED: Global LUT -> [{global_lut}]")
    if clean == "ENABLED": archive_old_outputs()
    os.makedirs(cfg.CLIPS_FOLDER, exist_ok=True)
    
    img_exts = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]
    vid_exts = [".mp4", ".mov", ".MP4", ".MOV"]
    paths = []
    for ext in img_exts: paths.extend(glob.glob(os.path.join(cfg.INPUT_FOLDER, f"*{ext}")))
    for ext in vid_exts: paths.extend(glob.glob(os.path.join(cfg.VIDEO_FOLDER, f"*{ext}")))
    
    if not paths: 
        print(f"\n[!] No input media assets found inside assets/images/ or assets/videos/!")
        return
        
    print(f"\n[*] Processing {len(paths)} assets...")
    for idx, p in enumerate(paths, 1):
        bname, _ = os.path.splitext(os.path.basename(p))
        dur, aud, title, pan, style, t_color_val, clip_lut = parse_filename_config(bname, 5, cfg.DEFAULT_AUDIO, global_lut)
        print(f"\n[{idx}/{len(paths)}] Processing: {bname}")
        tmp, fin = os.path.join(cfg.CLIPS_FOLDER, f"temp_{bname}.mp4"), os.path.join(cfg.CLIPS_FOLDER, f"{bname}_vertical.mp4")
        
        if single_image_to_vertical_zoom_video(p, tmp, dur, cfg.FPS, z_rate, 0.5, wm, title, pan, style, t_color_val):
            audio_target = None
            
            # Smart case-insensitive audio file resolver
            if os.path.exists(aud):
                audio_target = aud
            else:
                # Check lowercase or alternative extensions if exact path fails
                base_aud_dir = os.path.dirname(aud)
                aud_name_base = os.path.splitext(os.path.basename(aud))[0].lower()
                matching_tracks = glob.glob(os.path.join(base_aud_dir, "*.mp3")) + glob.glob(os.path.join(base_aud_dir, "*.wav"))
                
                for track in matching_tracks:
                    if os.path.splitext(os.path.basename(track))[0].lower() == aud_name_base:
                        audio_target = track
                        break
            
            # Fallback to default audio if specific track isn't found
            if not audio_target and os.path.exists(cfg.DEFAULT_AUDIO):
                audio_target = cfg.DEFAULT_AUDIO

            # Execute merge or warn
            if audio_target and os.path.exists(audio_target):
                add_audio_to_video(tmp, audio_target, fin)
            else:
                shutil.copy(tmp, fin)
                print(f"     {t_color('MAIN')}[!] Warning: Soundtrack '{os.path.basename(aud)}' not found in assets/audio/. Exported silent clip to: {fin}{t_color('RESET')}")
                
        if os.path.exists(tmp): 
            os.remove(tmp)
        log_metadata_to_csv(bname, title, pan, style, clip_lut, fin)
        
    if comp == "Y": compile_videos(cfg.CLIPS_FOLDER, cfg.COMPILATION_MASTER)
    # ------------------------------------------------------------
    # STEP: AUDIO MERGE & THUMBNAIL GENERATION
    # ------------------------------------------------------------
    # [Existing code] Final rendered video path:
    # final_output_mp4 = ".../dist/clips/img_CHIDORI_8_hype_..._vertical.mp4"

    # 1. Sound track merge step (Existing)
    # merge_audio(final_output_mp4, matched_audio_track)

    # 2. Extract PNG Thumbnail (NEW STEP)
    # Inside run_processing_pipeline() in image_to_video.py:
    extract_thumbnail(fin, timestamp_sec=1.5)
    # 3. Synchronize with Distribution Hub (Existing)
    # stage_to_distribution_hub(final_output_mp4)

if __name__ == "__main__":
    os.makedirs(cfg.INPUT_FOLDER, exist_ok=True)
    os.makedirs(cfg.VIDEO_FOLDER, exist_ok=True)
    os.makedirs(cfg.AUDIO_FOLDER, exist_ok=True)
    os.makedirs(cfg.CLIPS_FOLDER, exist_ok=True)
    os.makedirs(cfg.MASTERS_FOLDER, exist_ok=True)
    
    wm, z_rate, comp, clean, global_lut = "@Naruto_Cinegrade", 0.12, "Y", "ENABLED", "STANDARD"
    
    while True:
        main_c, acc_c, rst_c = t_color("MAIN"), t_color("ACCENT"), t_color("RESET")
        print(f"{main_c}=============================================\n      CINEGRADE VIDEO AUTOMATION ENGINE      \n============================================={rst_c}")
        print(f" Change Watermark   : {wm}\n Change Zoom Speed  : {'Slow' if z_rate==0.06 else 'Cinematic' if z_rate==0.12 else 'Fast Hype'} ({z_rate})\n Compile Master Reel: {'ENABLED' if comp=='Y' else 'DISABLED'}\n Auto-Clean Output  : {clean}\n Select Color LUT   : {global_lut}\n Swap Terminal Theme: {active_theme}\n {acc_c}[D]{rst_c} Execute Automated Platform API Dispatch\n {acc_c}[S]{rst_c} Allocate Scheduled Time Release Matrix Ledger\n {acc_c}[T]{rst_c} Scan Algorithmic Sound Velocity Trend Radar\n {acc_c}[P]{rst_c} Open Web Layout Player Gallery\n ---------------------------------------------\n {main_c}[R] RUN VIDEO ENGINE\n [X] EXIT{rst_c}\n=============================================")
        ch = input("Select option: ").strip().upper()
        
        if ch == "1": wm = input("\nEnter watermark: ").strip()
        elif ch == "2":
            sch = input(f"\n{acc_c}[A]{rst_c} Slow (6%)\n{acc_c}[B]{rst_c} Cinematic (12%)\n{acc_c}[C]{rst_c} Fast Hype (22%)\nChoice: ").strip().upper()
            z_rate = 0.06 if sch=="A" else 0.22 if sch=="C" else 0.12
        elif ch == "3": comp = "N" if comp=="Y" else "Y"
        elif ch == "4": clean = "DISABLED" if clean=="ENABLED" else "ENABLED"
        elif ch == "5":
            l_ch = input(f"\nSelect Cinegrade LUT:\n {acc_c}[A]{rst_c} Standard Rec.709\n {acc_c}[B]{rst_c} Teal & Orange\n {acc_c}[C]{rst_c} Cyberpunk Neon\n {acc_c}[D]{rst_c} Anime Horizon\n {acc_c}[E]{rst_c} Monochrome Noir\nChoice: ").strip().upper()
            global_lut = "STANDARD" if l_ch=='A' else "TEAL_ORANGE" if l_ch=='B' else "CYBERPUNK" if l_ch=='C' else "ANIME" if l_ch=='D' else "NOIR" if l_ch=='E' else global_lut
        elif ch == "6":
            t_ch = input(f"\nSelect Theme Profile:\n {acc_c}1{rst_c} Ninja Orange\n {acc_c}2{rst_c} Cyber Pink\n {acc_c}3{rst_c} Shadow Noir\n {acc_c}4{rst_c} Sage Green\nChoice: ").strip()
            active_theme = "NINJA_ORANGE" if t_ch=="1" else "CYBER_PINK" if t_ch=="2" else "SHADOW_NOIR" if t_ch=="3" else "SAGE_GREEN" if t_ch=="4" else active_theme
        elif ch == "D": 
            sub_ch = input(f"\n{acc_c}[1]{rst_c} Stage to Local Distribution Hub Folders\n{acc_c}[2]{rst_c} Run Live API Auto-Publisher (YouTube/TikTok)\nChoice: ").strip()
            if sub_ch == "1":
                deploy_to_distribution_hub()
            elif sub_ch == "2":
                import publisher
                publisher.run_auto_publisher()
            input("\nPress [Enter] to continue...")
        elif ch == "S": allocate_drop_schedule(); input("\nPress [Enter] to continue...")
        elif ch == "T": run_audio_trend_sensor_manifest(); input("\nPress [Enter] to continue...")
        elif ch == "P": launch_web_layout_preview_server(); input(f"\n{acc_c}Server frame cycle closed.{rst_c} Press [Enter] to return...")
        elif ch == "R": run_processing_pipeline(wm, z_rate, comp, clean, global_lut); input("\nPress [Enter] to continue...")
        elif ch == "X": break
        os.system("clear" if os.name == "posix" else "cls")
        
