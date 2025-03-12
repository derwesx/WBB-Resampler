
REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install required packages from requirements.txt
echo Installing required packages...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required Python packages.
    exit /b 1
) else (
    echo Required Python packages installed successfully.
)

echo Installation completed successfully!

pause