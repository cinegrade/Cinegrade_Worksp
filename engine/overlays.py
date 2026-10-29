import cv2
import math
import numpy as np

def generate_moving_fog_layer(tw, th, f_idx, tot_f):
    """Generates an organic procedural rolling fog/smoke overlay layer."""
    fog = np.zeros((th, tw, 3), dtype=np.uint8)
    progress = f_idx / max(tot_f, 1)
    
    # Create soft drifting gradient clouds using sine waves
    for y in range(0, th, 15):
        alpha_val = int(35 + 25 * np.sin((y * 0.02) + (progress * 6.28)))
        cv2.rectangle(fog, (0, y), (tw, y + 15), (200, 210, 220), -1)
        
    return cv2.GaussianBlur(fog, (99, 99), 0)

def generate_rain_layer(tw, th, f_idx):
    """Generates procedural diagonal rain streaks across the frame."""
    rain_layer = np.zeros((th, tw, 3), dtype=np.uint8)
    np.random.seed(f_idx)
    
    for _ in range(35):
        x = np.random.randint(0, tw)
        y = np.random.randint(0, th)
        length = np.random.randint(20, 50)
        cv2.line(rain_layer, (x, y), (x - 8, y + length), (220, 220, 220), 1, cv2.LINE_AA)
        
    return rain_layer

def apply_diffusion_glow(frame):
    """Applies a dreamy cinematic bloom/diffusion glow effect."""
    blur = cv2.GaussianBlur(frame, (31, 31), 0)
    return cv2.addWeighted(frame, 0.75, blur, 0.25, 0)

def apply_halation(frame):
    """Simulates red-channel film halation around high-contrast highlights."""
    b, g, r = cv2.split(frame)
    r_blur = cv2.GaussianBlur(r, (41, 41), 0)
    r_combined = cv2.addWeighted(r, 0.85, r_blur, 0.15, 0)
    return cv2.merge([b, g, r_combined])

def apply_anamorphic_flare(frame, f_idx):
    """Renders a streak anamorphic lens flare horizontally across the frame."""
    h, w, _ = frame.shape
    flare = np.zeros_like(frame)
    center_y = h // 3
    
    # Pulsing horizontal beam
    intensity = int(180 + 75 * math.sin(f_idx * 0.1))
    cv2.line(flare, (0, center_y), (w, center_y), (255, 180, 100), 2, cv2.LINE_AA)
    flare_blur = cv2.GaussianBlur(flare, (0, 99), 0)
    
    return cv2.addWeighted(frame, 1.0, flare_blur, 0.35, 0)

def apply_chromatic_fringe(frame):
    """Splits RGB channels slightly at the corners for vintage camera lens chromatic aberration."""
    h, w, _ = frame.shape
    b, g, r = cv2.split(frame)
    
    # Shift red channel right and blue channel left
    M_right = np.float32([[1, 0, 2], [0, 1, 0]])
    M_left = np.float32([[1, 0, -2], [0, 1, 0]])
    
    r_shifted = cv2.warpAffine(r, M_right, (w, h))
    b_shifted = cv2.warpAffine(b, M_left, (w, h))
    
    return cv2.merge([b_shifted, g, r_shifted])

def generate_light_leak_layer(tw, th, f_idx, tot_f):
    """Generates warm vintage light leaks pulsing across the corner."""
    leak = np.zeros((th, tw, 3), dtype=np.uint8)
    p = f_idx / max(tot_f, 1)
    intensity = int(120 * abs(math.sin(p * 3.14)))
    
    cv2.circle(leak, (tw, 0), int(tw * 0.7), (0, 100, 255), -1)
    return cv2.GaussianBlur(leak, (151, 151), 0)

def apply_film_grain(frame):
    """Adds subtle high-frequency monochromatic noise to simulate 35mm film stock."""
    h, w, c = frame.shape
    noise = np.random.normal(0, 12, (h, w, c)).astype(np.uint8)
    return cv2.add(frame, noise)

def apply_glitch_fx(frame, f_idx):
    """Injected digital data-moshing / RGB shift glitch artifact for intro frames."""
    h, w, _ = frame.shape
    glitched = frame.copy()
    
    # Slice random horizontal band and shift it
    if f_idx % 3 == 0:
        y1 = (f_idx * 37) % (h - 40)
        y2 = y1 + np.random.randint(10, 40)
        shift = np.random.randint(-25, 25)
        glitched[y1:y2, :] = np.roll(glitched[y1:y2, :], shift, axis=1)
        
    return glitched

def apply_vignette(frame):
    """Darkens the border edges to naturally draw focus to the center."""
    h, w, _ = frame.shape
    X_axis = cv2.getGaussianKernel(w, w / 1.5)
    Y_axis = cv2.getGaussianKernel(h, h / 1.5)
    kernel = Y_axis * X_axis.T
    mask = kernel / kernel.max()
    
    vignette = np.copy(frame)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * mask
        
    return vignette

def draw_audio_waveform(frame, f_idx, tot_f, bgr_color, tw, th, bar_size):
    """Renders a dynamic live audio frequency visualizer wave inside the lower container bar."""
    center_y = th - (bar_size // 2)
    num_bars = 48
    step = tw // num_bars
    
    for i in range(num_bars):
        x = i * step + 15
        # Modulate height dynamically based on frame progression and seed frequency
        amplitude = int((bar_size * 0.35) * abs(math.sin((f_idx * 0.2) + (i * 0.4))))
        cv2.line(frame, (x, center_y - amplitude), (x, center_y + amplitude), bgr_color, 4, cv2.LINE_AA)
        
    return frame

def inject_micro_variation_fx(frame, frame_idx, seed_val=42):
    """Injects unnoticeable sub-pixel matrix variations to bypass platform reuse flags."""
    np.random.seed(frame_idx + seed_val)
    h, w, c = frame.shape
    
    # 1. Subtle peripheral vignette shift (0.5% variation)
    vignette_shift = 1.0 - (np.random.rand() * 0.005)
    
    # 2. Inject a single micro-noise row at the very bottom border pixel line
    # This alters the absolute binary hash signature of the video file cleanly
    frame[h-1, :, :] = np.clip(frame[h-1, :, :].astype(np.int16) + np.random.randint(-1, 2, (w, c)), 0, 255).astype(np.uint8)
    
    return cv2.convertScaleAbs(frame, alpha=vignette_shift, beta=0)