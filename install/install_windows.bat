@echo off

:: Check if pip is installed
python -m ensurepip --upgrade

:: Install PyQt5 and other dependencies
echo Installing required Python packages...
python -m pip install -r requirements.txt

echo Installation complete for Windows!
pause
