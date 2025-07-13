#!/bin/bash

# NakenChat AI Bot Startup Script

echo "Starting NakenChat AI Bot..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

# Check if config exists
if [ ! -f "config.yaml" ]; then
    echo "Error: config.yaml not found"
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip3 install -r requirements.txt

# Start the bot
echo "Starting bot..."
python3 main.py 