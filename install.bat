@echo off
echo ========================================
echo User Behavior Anomaly Detection System
echo Installation Script
echo ========================================
echo.

echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install flask flask-cors pandas numpy scikit-learn werkzeug jinja2 markupsafe itsdangerous click blinker

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please try installing manually: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\images" mkdir static\images

echo.
echo Installation completed successfully!
echo.
echo To start the application, run:
echo   python app.py
echo.
echo Or use the startup script:
echo   python run.py
echo.
echo The web interface will be available at:
echo   http://localhost:5000
echo.
pause 