@echo off
setlocal
cd /d "%~dp0"
echo [*] Running IoT Shield Auto-Start Setup...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_autostart.ps1"
pause
