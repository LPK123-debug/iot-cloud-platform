@echo off
chcp 65001 >nul
title IoT Cloud Platform
echo =============================================
echo    IoT Cloud Platform - One Click Start
echo =============================================
echo.

:: Start Mosquitto
echo [1/3] Starting Mosquitto...
start "Mosquitto" /min cmd /c "C:\Program Files\mosquitto\mosquitto.exe" -c C:\iot-cloud-platform\mosquitto\mosquitto.conf -v
timeout /t 2 >nul

:: Start Flask Backend
echo [2/3] Starting Flask Backend...
start "Flask Backend" cmd /k "cd /d C:\iot-cloud-platform\server && call venv\Scripts\activate.bat && python app.py"
timeout /t 3 >nul

echo [3/3] Done!
echo.
echo =============================================
echo  Services Running:
echo    Mosquitto:  Port 1883
echo    Dashboard:  http://127.0.0.1:5000
echo    Health:     http://127.0.0.1:5000/api/health
echo =============================================
echo.
echo Close this window to keep services running.
echo To stop all: close Mosquitto and Flask Backend windows.
echo.
pause