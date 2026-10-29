import cv2
import numpy as np


def apply_cinegrade_lut(frame, look_name):
    look = look_name.upper()
    if look == "STANDARD":
        return frame

    img = frame.astype(np.float32) / 255.0
    blue, green, red = cv2.split(img)
    
    if look == "TEAL_ORANGE":
        red = np.where(red > 0.5, red + (1.0 - red) * 0.15, red * 0.9)
        blue = np.where(blue < 0.5, blue + (0.5 - blue) * 0.15, blue * 0.85)
        green = green * 0.95
        graded = cv2.merge([blue, green, red])
    elif look == "CYBERPUNK":
        red = np.clip(red * 1.2, 0, 1)
        blue = np.clip(blue * 1.4, 0, 1)
        green = np.clip(green * 0.7, 0, 1)
        graded = cv2.merge([blue, green, red])
    elif look == "ANIME":
        red = np.clip(red * 1.15, 0, 1)
        green = np.clip(green * 1.15, 0, 1)
        blue = np.clip(blue * 1.05, 0, 1)
        graded = cv2.merge([blue, green, red])
        return (np.clip(graded * 1.1, 0, 1) * 255.0).astype(np.uint8)
    elif look == "NOIR":
        gray = np.clip(
            (blue * 0.114 + green * 0.587 + red * 0.299 - 0.5) * 1.3 + 0.5,
            0,
            1,
        )
        graded = cv2.merge([gray, gray, gray])
        return (graded * 255.0).astype(np.uint8)
    else:
        graded = cv2.merge([blue, green, red])

    return (np.clip(graded, 0, 1) * 255.0).astype(np.uint8)