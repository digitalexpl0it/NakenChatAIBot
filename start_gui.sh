#!/bin/bash

# NakenChat AI Bot GUI Startup Script

echo "Starting NakenChat AI Bot GUI..."
if [ -f venv/bin/python ]; then
    venv/bin/python gui.py
else
    echo "Virtual environment not found! Please run ./install_ubuntu.sh first."
    exit 1
fi 