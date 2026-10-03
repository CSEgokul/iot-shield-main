@echo off
setlocal
cd /d "%~dp0"

echo ======================================================================
echo    IoT Shield -- Push to GitHub (CSEgokul/iot-shield-main)
echo ======================================================================
echo.
echo [*] Pushing branch 'main' to:
echo     https://github.com/CSEgokul/iot-shield-main.git
echo.
echo [*] If a browser window opens, sign in with your 'CSEgokul' GitHub account.
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo [SUCCESS] Successfully pushed to https://github.com/CSEgokul/iot-shield-main!
    echo ======================================================================
) else (
    echo.
    echo ======================================================================
    echo [NOTE] If permission was denied because Windows used your previous account:
    echo        1. Open Windows Credential Manager (Start -> 'Credential Manager')
    echo        2. Select 'Windows Credentials'
    echo        3. Find 'git:https://github.com' and click 'Remove'
    echo        4. Re-run this file to sign in with your CSEgokul account.
    echo ======================================================================
)

echo.
pause
