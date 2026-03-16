@echo off
REM GP-Maker one-click startup script for Windows
REM Usage: start.bat <audio_file> [options]
REM Example: start.bat song.mp3 --stem guitar -o output.gp5

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "PIP=%VENV_DIR%\Scripts\pip.exe"

REM pip mirror (comment out to use default PyPI)
set "PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple"
set "PIP_MIRROR_ARGS=-i %PIP_INDEX% --trusted-host pypi.tuna.tsinghua.edu.cn"

REM ── Show help if no arguments ────────────────────────────
if "%~1"=="" (
    echo GP-Maker: Convert audio to Guitar Pro tablature
    echo.
    echo Usage: start.bat ^<audio_file^> [options]
    echo.
    echo Examples:
    echo   start.bat song.mp3                          # Extract vocals -^> tab
    echo   start.bat song.mp3 --stem guitar            # Extract lead guitar -^> tab
    echo   start.bat song.mp3 --stem guitar -o out.gp5 # Custom output path
    echo   start.bat song.m4a --stem guitar             # Apple Music m4a file
    echo   start.bat guitar.wav --no-separate           # Pre-isolated audio
    echo   start.bat song.mp3 --bpm 140 --title "My Song"
    echo.
    echo Commands:
    echo   start.bat --setup    Install/update dependencies only
    exit /b 0
)

REM ── Setup-only mode ──────────────────────────────────────
if "%~1"=="--setup" (
    call :setup
    exit /b !errorlevel!
)

REM ── Auto-setup if venv missing ───────────────────────────
if not exist "%PYTHON%" (
    echo [INFO]  Virtual environment not found, running setup...
    call :setup
    if !errorlevel! neq 0 exit /b 1
)

REM ── Auto-setup if deps missing ───────────────────────────
"%PYTHON%" -c "import demucs; import basic_pitch; import guitarpro; import librosa" >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARN]  Dependencies not found, running setup...
    call :setup
    if !errorlevel! neq 0 exit /b 1
)

REM ── Run GP-Maker ─────────────────────────────────────────
cd /d "%SCRIPT_DIR%"
"%PYTHON%" -m gp_maker %*
exit /b %errorlevel%

REM ══════════════════════════════════════════════════════════
:setup
echo [INFO]  Setting up GP-Maker...

REM Find Python
set "SYS_PYTHON="
for %%P in (python3 python py) do (
    where %%P >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%V in ('%%P -c "import sys; print(sys.version_info[:2]>=(3,10))" 2^>nul') do (
            if "%%V"=="True" (
                set "SYS_PYTHON=%%P"
                goto :found_python
            )
        )
    )
)

echo [ERROR] Python 3.10+ is required but not found.
echo [ERROR] Please install Python from https://www.python.org/downloads/
echo [ERROR] Make sure to check "Add Python to PATH" during installation.
exit /b 1

:found_python
for /f "tokens=*" %%V in ('!SYS_PYTHON! --version') do echo [INFO]  Using: %%V

REM Create venv if missing
if not exist "%VENV_DIR%" (
    echo [INFO]  Creating virtual environment in .venv\ ...
    !SYS_PYTHON! -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

REM Upgrade pip
echo [INFO]  Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip %PIP_MIRROR_ARGS%
if !errorlevel! neq 0 (
    echo [ERROR] Failed to upgrade pip.
    exit /b 1
)

REM Install dependencies
echo [INFO]  Installing dependencies (first run may take several minutes)...
echo [INFO]  Using mirror: %PIP_INDEX%
"%PIP%" install -r "%SCRIPT_DIR%requirements.txt" %PIP_MIRROR_ARGS%
if !errorlevel! neq 0 (
    echo [ERROR] Failed to install dependencies. Check errors above.
    exit /b 1
)

REM Check ffmpeg
where ffmpeg >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo [WARN]  ffmpeg not found. It is needed for m4a/aac/wma files.
    echo [WARN]  Install: winget install ffmpeg
)

echo [OK]    Setup complete.
echo.
exit /b 0
