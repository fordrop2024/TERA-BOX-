# ===============================================================
# TeraBox Search Bot -- PowerShell Launcher (Windows 10/11)
# ===============================================================
# Run in PowerShell: .\start_bot.ps1
# If script execution is blocked on Windows, run once:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# ===============================================================

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "         TeraBox Search Bot -- Windows PowerShell Launcher     " -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verify Python Installation
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python was not found in your system PATH!" -ForegroundColor Red
    Write-Host "Please download Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Be sure to check 'Add Python to PATH' in the installer." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    Exit 1
}

$pyVersion = (& python --version 2>&1)
Write-Host "[OK] Detected: $pyVersion" -ForegroundColor Green

# 2. Check for .env Configuration
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "[INFO] Creating .env from .env.example template..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "[ACTION REQUIRED] Opening .env in Notepad. Set TELEGRAM_BOT_TOKEN and ADMIN_TELEGRAM_ID!" -ForegroundColor Magenta
        Start-Process notepad.exe ".env" -Wait
    }
}

# 3. Create Virtual Environment if not present
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating Python virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

# 4. Activate venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "[WARNING] Virtual environment activation script not found, proceeding with global Python..." -ForegroundColor Yellow
}

# 5. Install Dependencies
if (Test-Path "requirements.txt") {
    Write-Host "[INFO] Verifying Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
}

# 6. Run Self-Test Suite First (Safety Check)
Write-Host "`n[INFO] Running self-test suite..." -ForegroundColor Cyan
python run_tests.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Self-test reported warnings, but launching bot..." -ForegroundColor Yellow
}

# 7. Start the Telegram Bot
Write-Host "`n[INFO] Starting TeraBox Search Bot..." -ForegroundColor Green
Write-Host "Press Ctrl+C at any time in this terminal to stop the bot.`n" -ForegroundColor DarkGray

python main.py
