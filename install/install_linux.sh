#!/bin/bash

# Update apt package list
echo "Updating apt package list..."
sudo apt update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-dev build-essential libqt5gui5 libqt5core5a libqt5widgets5

# Install necessary Python libraries via pip
echo "Installing required Python packages..."
pip3 install -r requirements.txt

echo "Installation complete for Linux (Debian-based)!"
