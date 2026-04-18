# AxoLexis Post-Install Script v2.0
# Production-ready installer with progress, logging, and retry logic

param(
    [string]$InstallPath = "",
    [string]$PythonDownloadUrl = "https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe",
    [switch]$SkipShortcuts = $false
)

$ErrorActionPreference = "Continue"
$AppName = "AxoLexis"
$MinPythonVersion = [version]"3.10"
$MaxPythonVersion = [version]"3.11"
$PipRetryCount = 3
$global:LogFile = $null
$global:installSuccess = $false

function Write-Log {
    param([string]$Message, [switch]$Error)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    
    if ($global:LogFile) {
        Add-Content -Path $global:LogFile -Value $logEntry -ErrorAction SilentlyContinue
    }
    
    if ($Error) {
        Write-Host $logEntry -ForegroundColor Red
    } else {
        Write-Host $logEntry
    }
}

function Write-Progress-Step {
    param([string]$Step, [string]$Status)
    Write-Host ""
    Write-Host " [STEP $Step] $Status" -ForegroundColor Black -BackgroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
    Write-Log "STEP $Step : $Status"
}

function Initialize-Log {
    param([string]$AppPath)
    
    $logDir = $AppPath
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    $global:LogFile = Join-Path $logDir "install.log"
    
    $header = @"
==============================================
AxoLexis Installation Log
==============================================
Install Path   : $AppPath
Start Time     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Python URL    : $PythonDownloadUrl
"@
    
    Set-Content -Path $global:LogFile -Value $header -ErrorAction SilentlyContinue
    Write-Log "Logger initialized"
}

function Get-PythonPath {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $foundPath = $pythonCmd.Source
        Write-Log "Found Python in PATH: $foundPath"
        return $foundPath
    }
    
    Write-Log "Python not found in PATH, checking common locations..."
    
    $possiblePaths = @(
        "${env:LocalAppData}\Programs\Python\Python310\python.exe",
        "${env:LocalAppData}\Programs\Python\Python39\python.exe",
        "${env:ProgramFiles}\Python310\python.exe",
        "${env:ProgramFiles(x86)}\Python310\python.exe",
        "${env:ProgramFiles}\Python39\python.exe",
        "${env:ProgramFiles(x86)}\Python39\python.exe",
        "${env:APPDATA}\Local\Programs\Python\Python310\python.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            Write-Log "Found Python at: $path"
            return $path
        }
    }
    
    Write-Log "Python not found in any common location"
    return $null
}

function Get-PythonVersion {
    param([string]$PythonPath)
    
    try {
        $versionOutput = & $PythonPath --version 2>&1
        Write-Log "Python version check: $versionOutput"
        
        if ($versionOutput -match "Python (\d+\.\d+)") {
            return [version]$matches[1]
        }
    } catch {
        Write-Log "ERROR: Failed to get Python version: $_" -Error
    }
    return $null
}

function Install-Python {
    param([string]$DownloadUrl, [string]$AppPath)
    
    Write-Log "Starting Python download and installation..."
    
    $tempFile = Join-Path $env:TEMP "axolexis_python_installer.exe"
    
    try {
        Write-Log "Downloading Python from $DownloadUrl"
        
        # Try BITS first as it is more robust for large files
        try {
            Start-BitsTransfer -Source $DownloadUrl -Destination $tempFile -ErrorAction Stop
        } catch {
            Write-Log "BITS transfer failed, falling back to WebClient..."
            $webClient = New-Object System.Net.WebClient
            $webClient.DownloadFile($DownloadUrl, $tempFile)
        }
        
        if (-not (Test-Path $tempFile)) {
            throw "Downloaded file not found"
        }
        
        $fileSize = (Get-Item $tempFile).Length / 1MB
        Write-Log "Downloaded Python installer ($([math]::Round($fileSize, 2)) MB)"
        
    } catch {
        Write-Log "ERROR: Failed to download Python: $_" -Error
        throw "Download failed: $_"
    }
    
    try {
        Write-Log "Installing Python silently..."
        
        $process = Start-Process -FilePath $tempFile -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait -PassThru
        
        if ($process.ExitCode -ne 0) {
            throw "Python installation returned exit code $($process.ExitCode)"
        }
        
        Write-Log "Python installation completed successfully"
        
    } catch {
        Write-Log "ERROR: Python installation failed: $_" -Error
        throw "Installation failed: $_"
    } finally {
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
        }
    }
    
    Start-Sleep -Seconds 5
    
    $pythonPath = Get-PythonPath
    if (-not $pythonPath) {
        throw "Python installation succeeded but Python not found"
    }
    
    $version = Get-PythonVersion -PythonPath $pythonPath
    Write-Log "Python installed: $pythonPath (version $version)"
    
    return $pythonPath
}

function Validate-Python {
    param([string]$PythonPath)
    
    Write-Log "Validating Python installation..."
    
    if (-not (Test-Path $PythonPath)) {
        throw "Python executable not found at $PythonPath"
    }
    
    $version = Get-PythonVersion -PythonPath $PythonPath
    if (-not $version) {
        throw "Cannot determine Python version"
    }
    
    if ($version -lt $MinPythonVersion) {
        throw "Python version $version is below minimum required $MinPythonVersion"
    }
    
    if ($version -gt $MaxPythonVersion) {
        throw "Python version $version is above maximum supported $MaxPythonVersion"
    }
    
    try {
        $testResult = & $PythonPath -c "print('OK')" 2>&1
        if ($testResult -ne "OK") {
            throw "Python test execution failed"
        }
    } catch {
        throw "Python validation failed: $_"
    }
    
    Write-Log "Python validation passed (version $version)"
    return $version
}

function New-AppVirtualEnvironment {
    param([string]$AppPath, [string]$PythonPath)
    
    $venvPath = Join-Path $AppPath "venv"
    
    if (Test-Path $venvPath) {
        Write-Log "Removing existing virtual environment..."
        Remove-Item $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-Log "Creating virtual environment at $venvPath"
    
    try {
        # Check if python exists
        if (-not (Test-Path $PythonPath)) {
             throw "Python not found at $PythonPath"
        }

        # Create venv with more verbose error if it fails
        $createResult = & $PythonPath -m venv $venvPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            $err = $createResult -join " "
            throw "venv creation failed: $err"
        }
        
        if (-not (Test-Path $venvPath)) {
            throw "venv directory not created"
        }
        
        $pipPath = Join-Path $venvPath "Scripts\pip.exe"
        if (-not (Test-Path $pipPath)) {
            throw "pip not found in virtual environment"
        }
        
        Write-Log "Virtual environment created successfully"
        return $venvPath
        
    } catch {
        Write-Log "ERROR: Failed to create virtual environment: $_" -Error
        throw
    }
}

function Install-Dependencies {
    param(
        [string]$VenvPath,
        [string]$RequirementsFile,
        [string]$WheelCachePath = ""
    )
    
    $pipPath = Join-Path $VenvPath "Scripts\pip.exe"
    $pythonPath = Join-Path $VenvPath "Scripts\python.exe"
    
    Write-Log "Installing dependencies from $RequirementsFile"
    
    $retryCount = 0
    $success = $false
    
    while (-not $success -and $retryCount -lt $PipRetryCount) {
        $retryCount++
        Write-Log "Pip install attempt $retryCount of $PipRetryCount"
        
        try {
            Write-Log "Upgrading pip using python -m pip..."
            $upgradeResult = & $pythonPath -m pip install --upgrade pip 2>&1
            Write-Log "Pip upgrade: $upgradeResult"
            
            $installArgs = @("-m", "pip", "install", "-r", $RequirementsFile, "--no-warn-script-location")
            
            if ($WheelCachePath -and (Test-Path $WheelCachePath)) {
                $installArgs += "--find-links"
                $installArgs += $WheelCachePath
                Write-Log "Using wheel cache: $WheelCachePath"
            }
            
            Write-Log "Running: python $($installArgs -join ' ')"
            
            # Run directly to show progress bar to user
            & $pythonPath @installArgs
            
            if ($LASTEXITCODE -eq 0) {
                $success = $true
                Write-Log "Dependencies installed successfully on attempt $retryCount"
            } else {
                Write-Log "Pip install returned exit code $LASTEXITCODE"
            }
            
        } catch {
            Write-Log "ERROR on pip install attempt $retryCount`: $_" -Error
        }
        
        if (-not $success -and $retryCount -lt $PipRetryCount) {
            $waitTime = $retryCount * 10
            Write-Log "Waiting $waitTime seconds before retry..."
            Start-Sleep -Seconds $waitTime
        }
    }
    
    if (-not $success) {
        throw "Failed to install dependencies after $PipRetryCount attempts"
    }
    
    Write-Log "Validating installed packages..."
    
    try {
        $listOutput = & $pipPath list 2>&1
        $packageCount = ($listOutput | Select-String "^-").Count
        Write-Log "Installed $packageCount packages"
        
        $criticalPackages = @("PyQt6", "torch", "numpy")
        foreach ($pkg in $CriticalPackages) {
            if ($listOutput -match $pkg) {
                Write-Log "  [OK] $pkg"
            } else {
                Write-Log "  [WARN] $pkg not found in list" -Error
            }
        }
        
    } catch {
        Write-Log "WARNING: Could not validate packages: $_"
    }
    
    return $true
}

function Create-Shortcuts {
    param([string]$AppPath)
    
    if ($SkipShortcuts) {
        Write-Log "Skipping shortcut creation (flag set)"
        return
    }
    
    Write-Log "Creating shortcuts..."
    
    $exePath = Join-Path $AppPath "AxoLexis.exe"
    if (-not (Test-Path $exePath)) {
        Write-Log "WARNING: AxoLexis.exe not found at $exePath"
    }
    
    $desktop = [Environment]::GetFolderPath("Desktop")
    $startMenu = [Environment]::GetFolderPath("StartMenu")
    
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        
        if ($desktop) {
            $desktopShortcut = $WshShell.CreateShortcut("$desktop\AxoLexis.lnk")
            $desktopShortcut.TargetPath = $exePath
            $desktopShortcut.IconLocation = (Join-Path $AppPath "app_icon.ico")
            $desktopShortcut.WorkingDirectory = $AppPath
            $desktopShortcut.Description = "AxoLexis Intelligent Training System"
            $desktopShortcut.Save()
            Write-Log "Created desktop shortcut"
        }
        
        $programsPath = Join-Path $startMenu "Programs\AxoLexis"
        if (-not (Test-Path $programsPath)) {
            New-Item -ItemType Directory -Path $programsPath -Force | Out-Null
        }
        
        $startMenuShortcut = $WshShell.CreateShortcut("$programsPath\AxoLexis.lnk")
        $startMenuShortcut.TargetPath = $exePath
        $startMenuShortcut.IconLocation = (Join-Path $AppPath "app_icon.ico")
        $startMenuShortcut.WorkingDirectory = $AppPath
        $startMenuShortcut.Description = "AxoLexis Intelligent Training System"
        $startMenuShortcut.Save()
        Write-Log "Created Start Menu shortcut"
        
        $uninstallShortcut = $WshShell.CreateShortcut("$programsPath\Uninstall AxoLexis.lnk")
        $uninstallShortcut.TargetPath = (Join-Path $AppPath "Uninstall.exe")
        $uninstallShortcut.WorkingDirectory = $AppPath
        $uninstallShortcut.Description = "Uninstall AxoLexis"
        $uninstallShortcut.Save()
        Write-Log "Created uninstall shortcut"
        
    } catch {
        Write-Log "ERROR: Failed to create shortcuts: $_" -Error
    }
}

function Add-WindowsRegistry {
    param([string]$AppPath)
    
    Write-Log "Adding Windows registry entries..."
    
    try {
        $uninstallKey = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\AxoLexis"
        
        if (-not (Test-Path $uninstallKey)) {
            New-Item -Path $uninstallKey -Force | Out-Null
        }
        
        Set-ItemProperty -Path $uninstallKey -Name "DisplayName" -Value "AxoLexis"
        Set-ItemProperty -Path $uninstallKey -Name "DisplayVersion" -Value "1.0.0"
        Set-ItemProperty -Path $uninstallKey -Name "Publisher" -Value "AxoLexis Labs"
        Set-ItemProperty -Path $uninstallKey -Name "InstallLocation" -Value $AppPath
        Set-ItemProperty -Path $uninstallKey -Name "DisplayIcon" -Value (Join-Path $AppPath "AxoLexis.exe")
        Set-ItemProperty -Path $uninstallKey -Name "NoModify" -Value 1 -Type DWord
        Set-ItemProperty -Path $uninstallKey -Name "NoRepair" -Value 1 -Type DWord
        Set-ItemProperty -Path $uninstallKey -Name "EstimatedSize" -Value 0 -Type DWord
        
        Write-Log "Registry entries added"
        
    } catch {
        Write-Log "WARNING: Could not add registry entries: $_"
    }
}

function Test-AppLaunch {
    param([string]$AppPath)
    
    Write-Log "Testing application launch..."
    
    $exePath = Join-Path $AppPath "AxoLexis.exe"
    
    if (-not (Test-Path $exePath)) {
        Write-Log "ERROR: AxoLexis.exe not found" -Error
        return $false
    }
    
    try {
        $testProcess = Start-Process -FilePath $exePath -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        if ($testProcess.HasExited) {
            if ($testProcess.ExitCode -ne 0) {
                Write-Log "App exited with code $($testProcess.ExitCode)" -Error
                return $false
            }
        } else {
            Write-Log "App launched successfully (PID: $($testProcess.Id))"
            Stop-Process -Id $testProcess.Id -Force -ErrorAction SilentlyContinue
            return $true
        }
        
    } catch {
        Write-Log "ERROR: App launch test failed: $_" -Error
    }
    
    return $false
}

function Complete-Installation {
    param(
        [string]$AppPath,
        [bool]$Success,
        [string]$ErrorMessage = ""
    )
    
    $endTime = Get-Date
    
    $footer = @"

==============================================
Installation Summary
==============================================
Status          : $(if ($Success) { "SUCCESS" } else { "FAILED" })
End Time       : $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))
Error Message  : $ErrorMessage
Install Path   : $AppPath
"@
    
    if ($global:LogFile) {
        Add-Content -Path $global:LogFile -Value $footer
    }
    
    Write-Host ""
    if ($Success) {
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "         INSTALLATION COMPLETED SUCCESSFULLY" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host " AxoLexis has been installed to:" -ForegroundColor Green
        Write-Host "   $AppPath" -ForegroundColor White
        Write-Host ""
        Write-Host " This window will close automatically in 5 seconds..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
    } else {
        Write-Host "============================================================" -ForegroundColor Red
        Write-Host "                  INSTALLATION FAILED" -ForegroundColor Red
        Write-Host "============================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host " Error: $ErrorMessage" -ForegroundColor Red
        Write-Host ""
        Write-Host " Check log file for details: $global:LogFile" -ForegroundColor Yellow
        Write-Host ""
        Write-Host " Press any key to close this window and exit Setup..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
    $global:installSuccess = $Success
}

function Main {
    $ErrorMessage = ""
    
    try {
        if ([string]::IsNullOrEmpty($InstallPath)) {
            $InstallPath = Split-Path $MyInvocation.MyCommand.Path -Parent
        }
        
        Initialize-Log -AppPath $InstallPath
        
        Write-Log "=============================================="
        Write-Log "Starting AxoLexis Post-Install Configuration"
        Write-Log "=============================================="
        
        $requirementsFile = Join-Path $InstallPath "requirements.txt"
        if (-not (Test-Path $requirementsFile)) {
            throw "requirements.txt not found at $requirementsFile"
        }
        
        $pythonPath = Get-PythonPath
        $needsInstall = $true

        if ($pythonPath) {
            $pythonVersion = Get-PythonVersion -PythonPath $pythonPath
            if ($pythonVersion -and $pythonVersion -ge $MinPythonVersion -and $pythonVersion -le $MaxPythonVersion) {
                Write-Progress-Step "1/4" "Checking Python Environment"
                Write-Log "Using existing Python $pythonVersion at $pythonPath"
                $needsInstall = $false
            }
        }

        if ($needsInstall) {
            Write-Progress-Step "1/4" "Installing Python $MinPythonVersion"
            $pythonPath = Install-Python -DownloadUrl $PythonDownloadUrl -AppPath $InstallPath
        }

        Validate-Python -PythonPath $pythonPath | Out-Null
        
        Write-Progress-Step "2/4" "Creating Virtual Environment (VENV)"
        $venvPath = New-AppVirtualEnvironment -AppPath $InstallPath -PythonPath $pythonPath
        
        $wheelCache = Join-Path $InstallPath "wheel_cache"
        if (-not (Test-Path $wheelCache)) { $wheelCache = "" }
        
        Write-Progress-Step "3/4" "Installing AI Libraries & Dependencies (May take several minutes)"
        Install-Dependencies -VenvPath $venvPath -RequirementsFile $requirementsFile -WheelCachePath $wheelCache
        
        Write-Progress-Step "4/4" "Finalizing System Configuration"
        Create-Shortcuts -AppPath $InstallPath
        
        Add-WindowsRegistry -AppPath $InstallPath
        
        Complete-Installation -AppPath $InstallPath -Success $true
        
        exit 0
        
    } catch {
        $ErrorMessage = $_.Exception.Message
        Write-Log "FATAL ERROR: $ErrorMessage" -Error
        Write-Log "Stack trace: $($_.ScriptStackTrace)"
        
        Complete-Installation -AppPath $InstallPath -Success $false -ErrorMessage $ErrorMessage
        
        exit 1
    }
}

Main