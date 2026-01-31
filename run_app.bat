@echo off
echo ===================================
echo   Apple Ringtone Converter Loader
echo ===================================
echo checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Failed to install dependencies.
    pause
)

echo Starting Desktop App...
python desktop_app.py
