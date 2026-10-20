@echo off
setlocal enabledelayedexpansion

echo ===============================================================
echo         TeraBox Search Bot -- Windows Quick Launcher
echo ===============================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to your Windows PATH!
    echo Please install Python 3.10 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: 2. Check for .env file
if not exist .env (
    if exist .env.example (
        echo [INFO] No .env file found. Creating from .env.example...
        copy .env.example .env >nul
        echo [ACTION REQUIRED] Please open .env in Notepad and paste your TELEGRAM_BOT_TOKEN
        echo                   and ADMIN_TELEGRAM_ID before starting the bot.
        echo.
        notepad .env
    ) else (
        echo [WARNING] Neither .env nor .env.example was found.
    )
)

:: 3. Setup Virtual Environment
if not exist venv (
    echo [INFO] Creating Python virtual environment (venv)...
    python -m venv venv
    if errorlevel 1 (
        echo [WARNING] Could not create virtual environment. Running with global Python.
        goto RUN_GLOBAL
    )
)

:: 4. Activate venv and install dependencies
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing / updating required libraries from requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] Pip install encountered issues. Will attempt running with standalone fallback.
)

:: 5. Launch bot
echo [INFO] Starting TeraBox Search Bot...
python main.py
goto END

:RUN_GLOBAL
python main.py

:END
if errorlevel 1 (
    echo.
    echo [INFO] Bot exited. Press any key to close this window.
    pause
)
