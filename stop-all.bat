@echo off
echo Stopping IoT Cloud Platform...
taskkill /FI "WINDOWTITLE eq Mosquitto*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Flask Backend*" /F >nul 2>&1
echo All services stopped.
pause