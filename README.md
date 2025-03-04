# File Resampler Application

This application resamples data files in `.wbb` format using a specified resampling method (SWARII). It is designed with a simple GUI to select input and output folders and process files.

## Prerequisites

Before you install the application, make sure you have the following:

- **Python** 3.6 or higher
- **PyQt5** library for the GUI
- **NumPy** for data handling
- **resampling** package for data resampling (or make sure the custom `SWARII` class is installed and accessible)

## Installation

### For Linux/Mac

1. Open the terminal.
2. Clone the repository:
    ```bash
   git clone https://github.com/derwesx/LDM.git
   cd LDM
    ```
3. Run the installation script:

    Linux 
    ```bash
    chmod +x ./install/install_linux.sh
    ./install/install_linux.sh
    ```
    Mac:
    ```bash
    chmod +x ./install/install_mac.sh
    ./install/install_mac.sh
   ```
This will install the required dependencies for running the application.

### For Windows
Open PowerShell or Command Prompt.

Clone the repository:

```powershell
git clone https://github.com/derwesx/LDM.git
cd LDM
```

Run the installation script:
    
```powershell
.\install\install_windows.bat
```

This script will ensure that all dependencies are installed.

## Usage

Once installed, run the application using the following command:

```bash
cd app
python3 main.py
```