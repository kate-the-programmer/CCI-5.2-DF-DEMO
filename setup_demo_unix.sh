#!/bin/bash

# Script to set up and run DemoGUI-2.0 on Kali Linux
# Exit on error
set -e

echo "====== DemoGUI-2.0 Setup and Run Script ======"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
else
    echo "Python 3 is already installed."
fi

# Navigate to the DemoGUI directory
echo "Navigating to Desktop/DemoGUI-2.0..."
cd ~/Desktop/DemoGUI-2.0 || {
    echo "ERROR: Directory Desktop/DemoGUI-2.0 not found!"
    echo "Please make sure the directory exists and try again."
    exit 1
}

echo "Current directory: $(pwd)"
echo "Contents of directory:"
ls -la

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv || {
        echo "ERROR: Failed to create virtual environment!"
        exit 1
    }
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || {
    echo "ERROR: Failed to activate virtual environment!"
    exit 1
}

# Install required packages
echo "Installing required packages..."
pip install pycryptodome pillow || {
    echo "ERROR: Failed to install required packages!"
    exit 1
}

# Run the application
echo "Running DemoGUI application..."
python3 main.py

# Deactivate virtual environment when the application closes
deactivate

echo "Script execution completed."

