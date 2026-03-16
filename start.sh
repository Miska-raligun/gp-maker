#!/usr/bin/env bash
# GP-Maker one-click startup script for Linux/macOS
# Usage: ./start.sh <audio_file> [options]
# Example: ./start.sh song.mp3 --stem guitar -o output.gp5

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

# pip mirror (comment out to use default PyPI)
PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"
PIP_MIRROR_ARGS="-i $PIP_INDEX --trusted-host pypi.tuna.tsinghua.edu.cn"

# ── Color helpers ──────────────────────────────────────────
info()  { printf "\033[1;34m[INFO]\033[0m  %s\n" "$*"; }
ok()    { printf "\033[1;32m[OK]\033[0m    %s\n" "$*"; }
warn()  { printf "\033[1;33m[WARN]\033[0m  %s\n" "$*"; }
err()   { printf "\033[1;31m[ERROR]\033[0m %s\n" "$*" >&2; }

# ── Find a usable Python >= 3.10 ──────────────────────────
find_python() {
    for cmd in python3.12 python3.11 python3.10 python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver="$("$cmd" -c 'import sys; print(sys.version_info[:2]>=(3,10))' 2>/dev/null)"
            if [ "$ver" = "True" ]; then
                echo "$cmd"
                return
            fi
        fi
    done
    return 1
}

# ── Check if key deps are installed ────────────────────────
deps_ok() {
    "$PYTHON" -c "import demucs; import basic_pitch; import guitarpro; import librosa" 2>/dev/null
}

# ── Setup virtual environment and install deps ─────────────
setup() {
    info "Setting up GP-Maker..."

    # Find Python
    SYS_PYTHON="$(find_python)" || {
        err "Python 3.10+ is required but not found."
        err "Please install Python from https://www.python.org/downloads/"
        exit 1
    }
    info "Using Python: $SYS_PYTHON ($($SYS_PYTHON --version))"

    # Create venv if missing
    if [ ! -d "$VENV_DIR" ]; then
        info "Creating virtual environment in .venv/ ..."
        "$SYS_PYTHON" -m venv "$VENV_DIR"
    fi

    # Upgrade pip
    info "Upgrading pip..."
    "$PYTHON" -m pip install --upgrade pip $PIP_MIRROR_ARGS 2>&1 | tail -1

    # Install dependencies
    info "Installing dependencies (first run may take several minutes)..."
    info "Using mirror: $PIP_INDEX"
    "$PIP" install -r "$SCRIPT_DIR/requirements.txt" $PIP_MIRROR_ARGS
    if [ $? -ne 0 ]; then
        err "Failed to install dependencies. Check errors above."
        exit 1
    fi

    # Check ffmpeg (needed for m4a/aac/wma)
    if ! command -v ffmpeg &>/dev/null; then
        echo
        warn "ffmpeg not found. It is needed for m4a/aac/wma files."
        warn "Install: sudo apt install ffmpeg  (or: brew install ffmpeg)"
    fi

    ok "Setup complete."
    echo
}

# ── If no arguments, show help ─────────────────────────────
if [ $# -eq 0 ]; then
    echo "GP-Maker: Convert audio to Guitar Pro tablature"
    echo
    echo "Usage: ./start.sh <audio_file> [options]"
    echo
    echo "Examples:"
    echo "  ./start.sh song.mp3                          # Extract vocals → tab"
    echo "  ./start.sh song.mp3 --stem guitar            # Extract lead guitar → tab"
    echo "  ./start.sh song.mp3 --stem guitar -o out.gp5 # Custom output path"
    echo "  ./start.sh song.m4a --stem guitar             # Apple Music m4a file"
    echo "  ./start.sh guitar.wav --no-separate           # Pre-isolated audio"
    echo "  ./start.sh song.mp3 --bpm 140 --title 'My Song'"
    echo
    echo "Commands:"
    echo "  ./start.sh --setup    Install/update dependencies only"
    echo
    if [ -f "$PYTHON" ]; then
        echo "Options:"
        "$PYTHON" -m gp_maker --help 2>/dev/null | tail -n +3
    fi
    exit 0
fi

# ── Setup-only mode ────────────────────────────────────────
if [ "$1" = "--setup" ]; then
    setup
    exit 0
fi

# ── Auto-setup: create venv if missing ─────────────────────
if [ ! -f "$PYTHON" ]; then
    setup
fi

# ── Auto-setup: install deps if missing ────────────────────
if ! deps_ok; then
    warn "Dependencies not found, running setup..."
    setup
fi

# ── Run GP-Maker ───────────────────────────────────────────
cd "$SCRIPT_DIR"
exec "$PYTHON" -m gp_maker "$@"
