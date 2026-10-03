@echo off
setlocal
cd /d "%~dp0"
echo [*] Removing IoT Shield Auto-Start Task...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0remove_autostart.ps1"
pause
