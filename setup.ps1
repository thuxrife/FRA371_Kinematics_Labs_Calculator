# Setup FRA371 Kinematics Labs (Lab 3 synced) for Windows (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Setting up FRA371 Kinematics Labs (Lab 3)" -ForegroundColor Cyan
Write-Host " (Windows PowerShell - Python 3.11-3.13)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Select Python 3.13 (recommended for Lab 3), falling back to 3.12 / 3.11
$pythonArgs = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($ver in @("-3.13", "-3.12", "-3.11")) {
        try {
            $verOut = & py $ver --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonArgs = @("py", $ver)
                Write-Host "[OK] Using $verOut" -ForegroundColor Green
                break
            }
        } catch {}
    }
}

if (-not $pythonArgs) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $verOut = & python --version 2>&1
        Write-Host "[WARN] Python 3.13 not found via 'py'. Falling back to: $verOut" -ForegroundColor Yellow
        $pythonArgs = @("python")
    } else {
        Write-Host "[ERROR] Python 3.11-3.13 not found. Install via: winget install Python.Python.3.13" -ForegroundColor Red
        exit 1
    }
}

# Create .venv if it doesn't exist
if (-not (Test-Path -Path ".venv")) {
    Write-Host "[INFO] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    if ($pythonArgs.Length -eq 2) {
        & $pythonArgs[0] $pythonArgs[1] -m venv .venv
    } else {
        & $pythonArgs[0] -m venv .venv
    }
} else {
    Write-Host "[INFO] Existing .venv found." -ForegroundColor Yellow
}

# Python executable inside .venv
$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"

# Upgrade pip
Write-Host "[INFO] Upgrading pip..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip

# Install pinned Lab 3 dependencies + symbolic tools
Write-Host "[INFO] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install -r requirements.txt

# Apply Windows drive-path patch to swift
Write-Host "[INFO] Running fix_swift.py..." -ForegroundColor Yellow
& $venvPython fix_swift.py

# Quick verification check
Write-Host "[INFO] Verifying Robot.URDF_read, Swift, and SymPy..." -ForegroundColor Yellow
& $venvPython -c "import roboticstoolbox as rtb, swift, sympy; from roboticstoolbox.robot.Robot import Robot; assert hasattr(Robot, 'URDF_read'); print('[OK] All Lab 3 imports verified!')"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " Setup complete!" -ForegroundColor Green
Write-Host " Activate anytime: .venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host " Select kernel '.venv' in Lab_Calculator.ipynb or Lab 3 notebooks" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
