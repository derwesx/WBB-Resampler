#!/bin/bash

# Check if Python3 is installed
check_python() {
    if command -v python3 &>/dev/null; then
        echo "Python 3 is already installed."
    else
        echo "Python 3 is not installed. Installing Python 3..."
        install_python
    fi
}

# Download and install Python 3
install_python() {
    PYTHON_VERSION="3.9.7"
    INSTALLER_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-macosx10.9.pkg"
    INSTALLER_PATH="/tmp/python-$PYTHON_VERSION.pkg"

    # Download the Python installer package
    echo "Downloading Python $PYTHON_VERSION installer..."
    curl -o $INSTALLER_PATH $INSTALLER_URL

    if [ $? -eq 0 ]; then
        echo "Python installer downloaded successfully."
    else
        echo "Failed to download Python installer."
        exit 1
    fi

    # Install Python
    echo "Installing Python..."
    sudo installer -pkg $INSTALLER_PATH -target /

    if [ $? -eq 0 ]; then
        echo "Python installed successfully."
    else
        echo "Failed to install Python."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &>/dev/null; then
        echo "pip is already installed."
    else
        echo "pip is not installed. Installing pip..."
        install_pip
    fi
}

# Install pip
install_pip() {
    # Ensure that we use the latest version of pip
    python3 -m ensurepip --upgrade
    python3 -m pip install --upgrade pip

    if [ $? -eq 0 ]; then
        echo "pip installed and upgraded successfully."
    else
        echo "Failed to install pip."
        exit 1
    fi
}

# Install required Python packages
install_requirements() {
    echo "Installing required Python packages..."

    # Install packages using pip from requirements.txt
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

    if [ $? -eq 0 ]; then
        echo "Required Python packages installed successfully."
    else
        echo "Failed to install required Python packages."
        exit 1
    fi
}

# Main installation steps
echo "Starting installation process..."
check_python
check_pip
install_requirements

echo "Installation completed successfully!"