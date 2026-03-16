#!/usr/bin/env bash
# GP-Maker one-click startup script for Linux/macOS
# Usage: ./start.sh <audio_file> [options]
# Example: ./start.sh song.mp3 --stem guitar -o output.gp5

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="${VENV_DIR}/bin/python"

# ── Color helpers ──────────────────────────────────────────
info()  { printf "\033[1;34m[INFO]\033[0m  %s\n" "$*"; }
ok()    { printf "\033[1;32m[OK]\033[0m    %s\n" "$*"; }
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
        info "Creating virtual environment..."
        "$SYS_PYTHON" -m venv "$VENV_DIR"
    fi

    # Install / update dependencies
    info "Installing dependencies (this may take a few minutes on first run)..."
    "$PYTHON" -m pip install --upgrade pip -q
    "$PYTHON" -m pip install -r "$SCRIPT_DIR/requirements.txt" -q

    ok "Setup complete."
    echo
}

# ── Main ───────────────────────────────────────────────────
if [ ! -f "$PYTHON" ]; then
    setup
fi

# If no arguments, show help
if [ $# -eq 0 ]; then
    echo "GP-Maker: Convert audio to Guitar Pro tablature"
    echo
    echo "Usage: ./start.sh <audio_file> [options]"
    echo
    echo "Examples:"
    echo "  ./start.sh song.mp3                          # Extract vocals → tab"
    echo "  ./start.sh song.mp3 --stem guitar            # Extract lead guitar → tab"
    echo "  ./start.sh song.mp3 --stem guitar -o out.gp5 # Custom output path"
    echo "  ./start.sh guitar.wav --no-separate           # Pre-isolated audio"
    echo "  ./start.sh song.mp3 --bpm 140 --title 'My Song'"
    echo
    echo "Options:"
    "$PYTHON" -m gp_maker --help 2>/dev/null | tail -n +3
    exit 0
fi

# Check if deps need install (venv exists but maybe incomplete)
if ! "$PYTHON" -c "import gp_maker" &>/dev/null; then
    setup
fi

exec "$PYTHON" -m gp_maker "$@"
