#!/bin/bash
# Simple script to activate the Python virtual environment
# Usage: source activate_venv.sh

if [ -d "venv" ]; then
    echo "Activating Python virtual environment..."
    source venv/bin/activate
    echo "Virtual environment activated. Python and pip are now isolated."
    echo "Python path: $(which python)"
    echo "Pip path: $(which pip)"
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated."
fi