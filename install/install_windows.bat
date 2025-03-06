@echo off

:: Check if Python is already installed
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo Python is already installed.
    goto :install_dependencies
)

:: Download and install Python
echo Downloading Python installer...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe', '%TEMP%\python-installer.exe')"[1]

echo Installing Python...
%TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0[6]

:: Refresh environment variables
setx PATH "%PATH%" >nul

:install_dependencies
:: Check if pip is installed
python -m ensurepip --upgrade

:: Install PyQt5 and other dependencies
echo Installing required Python packages...
pip install -r requirements.txt

echo Installation complete for Windows!
pause
