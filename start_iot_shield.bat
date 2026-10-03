@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: IoT Shield - Complete System Launcher (Dashboard + Live Detector)
:: ============================================================================

title IoT Shield Launcher
color 0B

echo ======================================================================
echo    IoT Shield -- Real-Time Network Threat Detection System
echo ======================================================================
echo.

:: 1. Navigate to script directory (handles paths with spaces safely)
cd /d "%~dp0"
set "PROJECT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
echo [*] Project directory: "%PROJECT_DIR%"

:: 2. Activate Conda environment 'iotfinal' if available, or fall back to system Python
set "PYTHON_EXE="

:: Try standard conda in PATH
where conda >nul 2>nul
if %errorlevel% equ 0 (
    echo [*] Found conda in PATH. Activating 'iotfinal'...
    call conda activate iotfinal >nul 2>nul
)

:: Try standard Anaconda / Miniconda install locations
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
    echo [!] 'iotfinal' conda env not directly detected in PATH.
    echo [*] Checking for available Python with installed packages...
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
    echo Please install Python 3.11 or create the 'iotfinal' Conda environment.
    echo.
    pause
    exit /b 1
)

:: 4. Verify project scripts exist
if not exist "step4_dashboard.py" (
    color 0C
    echo [ERROR] Could not find 'step4_dashboard.py' in "%PROJECT_DIR%".
    pause
    exit /b 1
)
if not exist "step5_live.py" (
    color 0C
    echo [ERROR] Could not find 'step5_live.py' in "%PROJECT_DIR%".
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo  Starting Components:
echo    1. Live Network Packet Detector (Scapy + ML Ensemble) in a new window
echo    2. Streamlit Web Dashboard in this window
echo ======================================================================
echo.

:: 5. Launch Live Detector in a new, dedicated terminal window
echo [*] Spawning Live Detector window...
start "IoT Shield - Live Packet Detector" cmd /k "title IoT Shield Live Detector && cd /d ""%PROJECT_DIR%"" && (where conda >nul 2>nul && call conda activate iotfinal 2>nul) && echo ====================================================== && echo   IoT Shield Live Detection Sensor && echo   Capturing LAN packets ^& syncing to Firebase... && echo ====================================================== && python step5_live.py --reset"

:: 6. Short pause to allow detector initialization
ping -n 3 127.0.0.1 >nul

:: 7. Launch Streamlit Dashboard in the current terminal window
echo [*] Starting Streamlit Dashboard...
echo [*] Access the dashboard in your browser at: http://localhost:8501
echo.
python -m streamlit run step4_dashboard.py

pause
