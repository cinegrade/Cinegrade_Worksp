#!/bin/bash
WORKSPACE="$HOME/Desktop/Cinegrade_Worksp"
cd "$WORKSPACE" || exit 1

echo "=== 1. Generating Cinematic Images ==="
python3 engine/image_generator.py

echo "=== 2. Running Batch Render ==="
python3 engine/batch_render.py

echo "=== 3. Running Auto-Stage ==="
python3 engine/auto_stage.py

echo "=== 4. Generating Content Schedule ==="
python3 engine/content_scheduler.py

echo "=== 5. Executing Workspace Backup ==="
./backup_workspace.sh

echo "=== Pipeline Complete ==="
