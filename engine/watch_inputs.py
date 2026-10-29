#!/usr/bin/env python3
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WORKSPACE = Path.home() / "Desktop" / "Cinegrade_Worksp"
INPUTS_DIR = WORKSPACE / "assets" / "inputs"
VALID_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

class InputImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in VALID_EXTS:
            print(f"\n[⚡️] New reference image detected: {file_path.name}")
            print("[+] Triggering Cinegrade AI Learning Hub & Pipeline...")
            
            # Step 1: Run OpenCV analyzer on new image
            analyzer_script = WORKSPACE / "engine" / "image_analyzer.py"
            subprocess.run(["python3", str(analyzer_script), str(file_path)], check=False)
            
            # Step 2: Execute full pipeline script
            pipeline_script = WORKSPACE / "run_pipeline.sh"
            subprocess.run([str(pipeline_script)], cwd=str(WORKSPACE), check=False)

def start_watcher():
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    event_handler = InputImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INPUTS_DIR), recursive=False)
    
    print("=" * 60)
    print(" 👁️ CINEGRADE AUTOMATED INPUT WATCHER RUNNING")
    print(f" Listening for new reference images in: {INPUTS_DIR}")
    print(" Press Ctrl+C to stop.")
    print("=" * 60)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[!] Watcher service stopped.")
    observer.join()

if __name__ == "__main__":
    start_watcher()
