@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: IoT Shield - Safe Process Stopper
:: Stops only IoT Shield detector, simulator, and dashboard processes
:: ============================================================================

title IoT Shield - Stopping Services
color 0E

echo ======================================================================
echo    IoT Shield -- Stopping Running Processes
echo ======================================================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$patterns = @('step4_dashboard\.py', 'step5_live\.py', 'step5_simulate\.py');" ^
    "$found = 0;" ^
    "$processes = Get-CimInstance Win32_Process | Where-Object { $cmd = $_.CommandLine; if ($cmd) { foreach ($pat in $patterns) { if ($cmd -match $pat) { return $true } } } return $false };" ^
    "if ($processes) {" ^
    "    foreach ($p in $processes) {" ^
    "        Write-Host ('[STOPPING] PID ' + $p.ProcessId + ': ' + $p.Name) -ForegroundColor Yellow;" ^
    "        try { Stop-Process -Id $p.ProcessId -Force; Write-Host ('[OK] Stopped PID ' + $p.ProcessId) -ForegroundColor Green; $found++ } catch { Write-Host ('[!] Could not stop PID ' + $p.ProcessId + ': ' + $_.Exception.Message) -ForegroundColor Red }" ^
    "    }" ^
    "    Write-Host ('`n[SUCCESS] Terminated ' + $found + ' IoT Shield process(es).') -ForegroundColor Green;" ^
    "} else {" ^
    "    Write-Host '[INFO] No running IoT Shield processes found.' -ForegroundColor Cyan;" ^
    "}"

echo.
echo Done.
ping -n 3 127.0.0.1 >nul
