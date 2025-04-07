#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Create a log file
LOG_FILE="leetlogger.log"
echo "Starting LeetLogger at $(date)" > "$LOG_FILE"
echo "Current directory: $(pwd)" >> "$LOG_FILE"
echo "Python version: $(python --version)" >> "$LOG_FILE"

# Check if we have all required files
echo "Checking for required files:" >> "$LOG_FILE"
ls -la >> "$LOG_FILE"

# Try to run the application
echo "Starting main application..." >> "$LOG_FILE"
python main.py >> "$LOG_FILE" 2>&1

echo "Script ended at $(date)" >> "$LOG_FILE" 