<#
.SYNOPSIS
    setup_autostart.ps1 — Configures Windows Task Scheduler to auto-start
    the IoT Shield Live Detector on Windows logon with elevated privileges.
.DESCRIPTION
    Creates or updates a scheduled task named 'IoT Shield Detector'.
    The task runs 'start_detector.bat' from the current project directory,
    restarts if it exits unexpectedly, and runs with highest privileges
    required by Scapy packet capture.
#>

[CmdletBinding()]
param()

$taskName = "IoT Shield Detector"
$projectDir = $PSScriptRoot
$batPath = Join-Path -Path $projectDir -ChildPath "start_detector.bat"

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "   IoT Shield -- Windows Auto-Start Configuration" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Project Directory : $projectDir"
Write-Host "[*] Launcher Script   : $batPath"

# 1. Verify launcher script exists
if (-not (Test-Path -Path $batPath)) {
    Write-Error "[ERROR] Could not find '$batPath'. Make sure setup_autostart.ps1 is in the project root."
    exit 1
}

# 2. Check for Administrator privileges
$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principalCheck = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
$isAdmin = $principalCheck.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "[ELEVATION REQUIRED] Creating an elevated Scheduled Task requires Administrator privileges."
    Write-Host ""
    Write-Host "Attempting to launch elevated PowerShell to complete task registration..." -ForegroundColor Yellow
    
    $scriptPath = $MyInvocation.MyCommand.Definition
    try {
        Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
        Write-Host "[*] Elevated installer launched. Please approve the UAC prompt." -ForegroundColor Green
        exit 0
    } catch {
        Write-Error "[!] Elevation prompt declined or failed: $_"
        Write-Host "Please manually open PowerShell as Administrator and run:"
        Write-Host "  powershell -ExecutionPolicy Bypass -File `"$scriptPath`"" -ForegroundColor Yellow
        exit 1
    }
}

# 3. Define Task Components
try {
    # Action: Run start_detector.bat via cmd.exe in the project directory
    $action = New-ScheduledTaskAction `
        -Execute "cmd.exe" `
        -Argument "/c `"`"$batPath`"`"" `
        -WorkingDirectory $projectDir

    # Trigger: At user logon
    $trigger = New-ScheduledTaskTrigger -AtLogOn

    # Principal: Run with highest privileges (needed for Scapy raw sockets)
    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType Interactive `
        -RunLevel Highest

    # Settings: Restart on unexpected exit, allow running on battery, no execution timeout
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -ExecutionTimeLimit (New-TimeSpan -Days 0) `
        -Priority 5

    # 4. Register Scheduled Task
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "IoT Shield Live Network Threat Detector (Scapy + ML inference + Firebase sync)" `
        -Force | Out-Null

    Write-Host ""
    Write-Host "[SUCCESS] Task '$taskName' successfully registered!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor White
    Write-Host "  - Name        : $taskName"
    Write-Host "  - Trigger     : On user logon ($env:USERNAME)"
    Write-Host "  - Privileges  : Highest (Administrator for Npcap/Scapy)"
    Write-Host "  - Script      : $batPath"
    Write-Host "  - Working Dir : $projectDir"
    Write-Host "  - Resilience  : Auto-restart up to 3 times if exited unexpectedly"
    Write-Host ""
    Write-Host "To remove this task at any time, run: .\remove_autostart.ps1" -ForegroundColor Gray
    Write-Host "==============================================================" -ForegroundColor Cyan
} catch {
    Write-Error "[ERROR] Failed to register scheduled task: $_"
    exit 1
}
