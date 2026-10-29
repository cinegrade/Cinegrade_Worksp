#!/bin/bash
cd /Users/Naruto/Cinegrade_Worksp
exec /Users/Naruto/Cinegrade_Worksp/.venv/bin/python daemon.py >> logs/pipeline_stdout.log 2>> logs/pipeline_stderr.log
