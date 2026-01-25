@echo off
echo Checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Failed to install dependencies. 
    echo Please check your internet connection or install manually.
    echo.
    pause
)

echo Starting Apple Audio Converter...
python main.py
