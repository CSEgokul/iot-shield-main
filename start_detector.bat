@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: IoT Shield - Dedicated Live Detector Launcher (For Streamlit Cloud Deployments)
:: Runs only the local Scapy packet sniffer + ML inference + Firebase sync
:: ============================================================================

title IoT Shield - Live Network Detector
color 0A

echo ======================================================================
echo    IoT Shield -- Live Network Detector
echo    (Local Sensor Node - Streams detections to Firebase)
echo ======================================================================
echo.

:: 1. Navigate to script directory
cd /d "%~dp0"
set "PROJECT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
echo [*] Project directory: "%PROJECT_DIR%"

:: 2. Activate Conda environment 'iotfinal' if available
where conda >nul 2>nul
if %errorlevel% equ 0 (
    call conda activate iotfinal >nul 2>nul
)

if "%CONDA_DEFAULT_ENV%" neq "iotfinal" (
    for %%P in (
        "%USERPROFILE%\miniconda3"
        "%USERPROFILE%\anaconda3"
        "C:\ProgramData\miniconda3"
        "C:\ProgramData\anaconda3"
        "C:\miniconda3"
        "C:\anaconda3"
    ) do (
        if exist "%%~fP\condabin\conda.bat" (
            call "%%~fP\condabin\conda.bat" activate iotfinal >nul 2>nul
            if "!CONDA_DEFAULT_ENV!"=="iotfinal" goto :env_found
        )
        if exist "%%~fP\Scripts\activate.bat" (
            call "%%~fP\Scripts\activate.bat" iotfinal >nul 2>nul
            if "!CONDA_DEFAULT_ENV!"=="iotfinal" goto :env_found
        )
    )
)

:env_found
if "%CONDA_DEFAULT_ENV%"=="iotfinal" (
    echo [OK] Active Conda environment: iotfinal
) else (
    if exist "%USERPROFILE%\miniconda3\python.exe" (
        set "PATH=%USERPROFILE%\miniconda3;%USERPROFILE%\miniconda3\Scripts;!PATH!"
        echo [OK] Using Python from %USERPROFILE%\miniconda3
    )
)

:: 3. Verify Python availability
where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python was not found in PATH or standard Conda directories.
    pause
    exit /b 1
)

:: 4. Verify step5_live.py exists
if not exist "step5_live.py" (
    color 0C
    echo [ERROR] Could not find 'step5_live.py' in "%PROJECT_DIR%".
    pause
    exit /b 1
)

:: 5. Elevation / Admin check advisory
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [NOTE] Running in standard user mode.
    echo        If Scapy packet capture fails with PermissionError,
    echo        right-click this file and select 'Run as administrator'.
    echo.
) else (
    echo [OK] Running with Administrator privileges.
    echo.
)

:: 6. Launch step5_live.py
echo [*] Starting live packet capture and threat detection...
echo [*] Live alerts will stream to Firebase and your Cloud Dashboard.
echo [*] Press Ctrl+C at any time to stop.
echo ======================================================================
echo.

python step5_live.py --reset

echo.
echo ======================================================================
echo [*] Detector process stopped.
echo ======================================================================
pause
