import cv2
import html
import math
import re
import numpy as np


def get_color_bgr(color_name):
    colors = {
        "RED": (0, 0, 255), 
        "BLUE": (255, 0, 0), 
        "GREEN": (0, 255, 0), 
        "YELLOW": (0, 255, 255), 
        "ORANGE": (0, 140, 255), 
        "PURPLE": (211, 0, 148), 
        "WHITE": (255, 255, 255)
    }
    return colors.get(color_name.upper(), (255, 255, 255))


def render_neon_glowing_text(
    frame,
    title,
    f_idx,
    text_fade_frames,
    bgr_color,
    tw,
    th,
    is_landscape=False,
    shake=False,
):
    font = cv2.FONT_HERSHEY_SIMPLEX
    glow_layer = np.zeros_like(frame)
    font_scale = 1.6 if is_landscape else 2.2
    thickness = 4 if is_landscape else 5
    
    ts, _ = cv2.getTextSize(title, font, font_scale, thickness)
    if ts[0] > tw - 80:
        font_scale *= (tw - 80) / ts[0]
        ts, _ = cv2.getTextSize(title, font, font_scale, thickness)
        
    tx = (tw - ts[0]) // 2
    
    # Adaptive Safe Zone Alignment mapping
    ty = int(th * 0.25) if is_landscape else 500
    if shake:
        tx += round(3 * math.sin(f_idx * 0.8))
        ty += round(3 * math.cos(f_idx * 0.8))
    
    cv2.putText(glow_layer, title, (tx, ty), font, font_scale, bgr_color, 20, cv2.LINE_AA)
    glow_blur = cv2.GaussianBlur(glow_layer, (25, 25), 0)
    frame = cv2.addWeighted(glow_blur, 0.6, frame, 1.0, 0)
    
    text_core = frame.copy()
    cv2.putText(text_core, title, (tx, ty), font, font_scale, (0, 0, 0), 8, cv2.LINE_AA)
    cv2.putText(text_core, title, (tx, ty), font, font_scale, (255, 255, 255), 3, cv2.LINE_AA)
    
    alpha = f_idx / text_fade_frames if f_idx < text_fade_frames else 1.0
    return cv2.addWeighted(text_core, alpha, frame, 1.0 - alpha, 0)


_SRT_TIMING = re.compile(
    r"^\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*"
    r"(\d{2}:\d{2}:\d{2}[,.]\d{3})(?:\s+.*)?$"
)


def _srt_timestamp_seconds(timestamp):
    hours, minutes, remainder = timestamp.replace(",", ".").split(":")
    seconds, milliseconds = remainder.split(".")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000
    )


def load_srt_captions(srt_path):
    with open(srt_path, encoding="utf-8-sig") as subtitle_file:
        content = subtitle_file.read()

    cues = []
    for cue_number, block in enumerate(re.split(r"\n\s*\n", content.strip()), 1):
        lines = block.splitlines()
        timing_line_index = 1 if lines and lines[0].strip().isdigit() else 0
        if timing_line_index >= len(lines):
            raise ValueError(f"Subtitle cue {cue_number} is missing its timing line.")
        timing = _SRT_TIMING.match(lines[timing_line_index])
        if timing is None:
            raise ValueError(f"Subtitle cue {cue_number} has invalid SRT timing.")

        start = _srt_timestamp_seconds(timing.group(1))
        end = _srt_timestamp_seconds(timing.group(2))
        text = "\n".join(lines[timing_line_index + 1:]).strip()
        text = re.sub(r"<[^>]*>", "", html.unescape(text))
        if end <= start:
            raise ValueError(f"Subtitle cue {cue_number} ends before it starts.")
        if text:
            cues.append((start, end, text))
    return cues


def render_caption(frame, text, tw, th, is_landscape=False):
    if not text.strip():
        return frame

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.78 if is_landscape else 0.9
    thickness = 2
    max_text_width = int(tw * 0.88)
    lines = []
    
    for source_line in text.splitlines():
        words = source_line.split()
        if not words:
            lines.append("")
            continue
        current_line = words[0]
        for word in words[1:]:
            candidate = f"{current_line} {word}"
            text_size, _ = cv2.getTextSize(candidate, font, font_scale, thickness)
            if text_size[0] <= max_text_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

    line_metrics = [cv2.getTextSize(line, font, font_scale, thickness) for line in lines]
    line_height = max((height for _, height in line_metrics), default=0) + 12
    padding_x, padding_y = 28, 14
    box_width = min(
        max((width for (width, _), _ in line_metrics), default=0) + 2 * padding_x,
        tw - 24,
    )
    box_height = len(lines) * line_height + 2 * padding_y
    bottom_margin = 170 if is_landscape else 340
    box_bottom = min(th - bottom_margin, th - 1)
    box_top = max(0, box_bottom - box_height)
    box_left = (tw - box_width) // 2
    box_right = box_left + box_width

    panel = frame.copy()
    cv2.rectangle(panel, (box_left, box_top), (box_right, box_bottom), (0, 0, 0), -1)
    frame = cv2.addWeighted(panel, 0.68, frame, 0.32, 0)

    text_y = box_top + padding_y + line_height - 10
    for line, (text_size, _) in zip(lines, line_metrics):
        text_x = (tw - text_size[0]) // 2
        cv2.putText(frame, line, (text_x, text_y), font, font_scale, (0, 0, 0), 5, cv2.LINE_AA)
        cv2.putText(frame, line, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        text_y += line_height
    return frame