#!/usr/bin/env python3
"""
Cinegrade Pipeline Notification Hook
Sends a macOS system notification via AppleScript when distribution completes.
"""

import subprocess
import sys

def send_notification(title, message):
    escaped_title = title.replace('"', '\\"')
    escaped_message = message.replace('"', '\\"')
    applescript = f'display notification "{escaped_message}" with title "{escaped_title}" sound name "Glass"'
    subprocess.run(["osascript", "-e", applescript])

if __name__ == "__main__":
    asset_name = sys.argv[1] if len(sys.argv) > 1 else "Asset"
    send_notification("Cinegrade Pipeline", f"Successfully distributed and archived {asset_name}!")
