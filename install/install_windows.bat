@echo off

:: Check for Python3
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found! Please install Python and ensure it is added to your PATH.
    exit /b
)

:: Check if pip is installed
python -m ensurepip --upgrade

:: Install PyQt5 and other dependencies
echo Installing required Python packages...
pip install -r requirements.txt

echo Installation complete for Windows!
pause
