import os

# Rigid System Directory Mappings
ENGINE_DIR     = os.path.dirname(os.path.abspath(__file__))
BASE_WORKSPACE = os.path.dirname(ENGINE_DIR)

# Inputs Registry (Segregated Media Buckets)
INPUT_FOLDER   = os.path.join(BASE_WORKSPACE, "assets", "images")
VIDEO_FOLDER   = os.path.join(BASE_WORKSPACE, "assets", "videos")
AUDIO_FOLDER   = os.path.join(BASE_WORKSPACE, "assets", "audio")
DEFAULT_AUDIO  = os.path.join(AUDIO_FOLDER, "music.mp3")

# Production Distribution Registry
DIST_DIR             = os.path.join(BASE_WORKSPACE, "dist")
CLIPS_FOLDER         = os.path.join(DIST_DIR, "clips")
MASTERS_FOLDER       = os.path.join(DIST_DIR, "masters")
BACKUP_BASE          = os.path.join(DIST_DIR, "backups")

# Web Server Preview Channel & Metadata Registries
WEB_PREVIEW_DIR      = os.path.join(DIST_DIR, "web_previews")
METADATA_INGEST_CSV  = os.path.join(DIST_DIR, "metadata_ingest.csv")
DISTRIBUTION_HUB     = os.path.join(DIST_DIR, "distribution_hub")
SCHEDULE_LEDGER      = os.path.join(DIST_DIR, "distribution_schedule.txt")

HISTORY_LOG          = os.path.join(DIST_DIR, "history.log")
COMPILATION_MASTER   = os.path.join(MASTERS_FOLDER, "full_compilation_master.mp4")

# Global Video Aspect Ratio Presets
# Global Video Aspect Ratio Presets & Frame Rate
VERTICAL_W, VERTICAL_H     = 1080, 1920
HORIZONTAL_W, HORIZONTAL_H = 1920, 1080
FPS                        = 30

# UI Theme Color Palettes (ANSI Terminal escape codes)
THEMES = {
    "NINJA_ORANGE": {"MAIN": "\033[38;5;208m", "ACCENT": "\033[38;5;214m", "RESET": "\033[0m"},
    "CYBER_PINK":   {"MAIN": "\033[38;5;201m", "ACCENT": "\033[38;5;51m",  "RESET": "\033[0m"},
    "SHADOW_NOIR":  {"MAIN": "\033[38;5;244m", "ACCENT": "\033[38;5;250m", "RESET": "\033[0m"},
    "SAGE_GREEN":   {"MAIN": "\033[38;5;46m",  "ACCENT": "\033[38;5;118m", "RESET": "\033[0m"}
}

VALID_COLORS = ["RED", "BLUE", "GREEN", "YELLOW", "ORANGE", "PURPLE", "WHITE"]
SUPPORTED_EFFECTS = [
    "VINTAGE", "FOG", "GLITCH", "BORDER", "SPLIT", "RAIN", 
    "SHAKE", "LANDSCAPE", "HALATION", "GLOW", "FRINGE", 
    "VIGNETTE", "ANAMORPHIC", "CAPTIONS", "WAVE", "SPEED", "NONE"
]

# ElevenLabs Integration Voice Profile Registry
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default cloned voice fallback ID

# Auto-Initialize Essential Core Workspaces on Import
def initialize_workspace_directories():
    directories = [
        INPUT_FOLDER, VIDEO_FOLDER, AUDIO_FOLDER, 
        CLIPS_FOLDER, MASTERS_FOLDER, BACKUP_BASE, 
        WEB_PREVIEW_DIR, DISTRIBUTION_HUB
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

initialize_workspace_directories()