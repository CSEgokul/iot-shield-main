@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: IoT Shield - Simulation Mode Launcher (Dashboard + Traffic Simulator)
:: ============================================================================

title IoT Shield Simulation Launcher
color 0B

echo ======================================================================
echo    IoT Shield -- Simulation Mode Launcher
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

:: 4. Verify project scripts exist
if not exist "step4_dashboard.py" (
    color 0C
    echo [ERROR] Could not find 'step4_dashboard.py'.
    pause
    exit /b 1
)
if not exist "step5_simulate.py" (
    color 0C
    echo [ERROR] Could not find 'step5_simulate.py'.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo  Starting Simulation:
echo    1. Traffic Flow Simulator (step5_simulate.py --reset) in a new window
echo    2. Streamlit Web Dashboard in this window
echo ======================================================================
echo.

:: 5. Launch Traffic Simulator in a new window
echo [*] Spawning Traffic Simulator window...
start "IoT Shield - Traffic Simulator" cmd /k "title IoT Shield Traffic Simulator && cd /d ""%PROJECT_DIR%"" && (where conda >nul 2>nul && call conda activate iotfinal 2>nul) && echo ====================================================== && echo   IoT Shield Traffic Simulator && echo   Replaying flows from combined.csv ^& pushing alerts... && echo ====================================================== && python step5_simulate.py --reset --speed 2"

:: 6. Short pause
ping -n 3 127.0.0.1 >nul

:: 7. Launch Streamlit Dashboard
echo [*] Starting Streamlit Dashboard...
echo [*] Open in browser: http://localhost:8501
echo.
python -m streamlit run step4_dashboard.py

pause
