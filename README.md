# GP-Maker

Audio to Guitar Pro tablature converter. Extracts vocals or lead guitar from audio files and generates `.gp5` Guitar Pro tabs.

## Features

- **Vocal extraction**: Isolate vocals from a mix and transcribe to guitar tab
- **Lead guitar extraction**: Isolate guitar using Demucs 6-stem model (`htdemucs_6s`)
- **Chord support**: Polyphonic transcription with chord-aware fretboard mapping
- **Auto BPM detection**: Tempo detection via librosa, with manual override
- **One-click scripts**: `start.sh` / `start.bat` handle venv and deps automatically

## Quick Start

### Linux / macOS

```bash
chmod +x start.sh

# Extract lead guitar
./start.sh song.mp3 --stem guitar

# Extract vocals (default)
./start.sh song.mp3

# Custom output + BPM
./start.sh song.mp3 --stem guitar -o my_tab.gp5 --bpm 140
```

### Windows

```cmd
REM Extract lead guitar
start.bat song.mp3 --stem guitar

REM Extract vocals (default)
start.bat song.mp3

REM Install dependencies only
start.bat --setup
```

### Manual (pip)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m gp_maker song.mp3 --stem guitar -o output.gp5
```

## CLI Reference

```
usage: gp-maker [-h] [-o OUTPUT] [--bpm BPM] [--stem {vocals,guitar}]
                [--no-separate] [--title TITLE] [-v]
                input

Convert audio files to Guitar Pro (.gp5) tablature.

positional arguments:
  input                 Input audio file path (MP3, WAV, FLAC, M4A, OGG, etc.)

options:
  -o, --output          Output .gp5 file path (default: <input_name>.gp5)
  --bpm BPM             Manual BPM override (auto-detected if not specified)
  --stem {vocals,guitar}
                        Which stem to extract and transcribe (default: vocals)
  --no-separate         Skip stem separation (input is already an isolated stem)
  --title TITLE         Song title for the GP file
  -v, --version         Show version
```

## Processing Pipeline

```
Audio file (MP3/WAV/FLAC/M4A/OGG/...)
    |
    v
[1] Stem Separation (Demucs)
    - vocals: htdemucs (2-stem mode)
    - guitar: htdemucs_6s (6-stem, dedicated guitar output)
    |
    v
[2] Pitch Detection (basic-pitch)
    - Polyphonic note detection
    - Amplitude filtering
    |
    v
[3] Note Quantization
    - Snap to 16th-note grid
    - Chord grouping (guitar mode)
    |
    v
[4] Fretboard Mapping
    - MIDI → (string, fret) assignment
    - Chord-aware: no two notes on same string
    - Range clamping with octave shift
    |
    v
[5] GP5 Generation (pyguitarpro)
    - Multi-note beats for chords
    - 4/4 time signature
    - Velocity dynamics
    |
    v
Output: .gp5 file
```

## Examples

```bash
# Full song → lead guitar tab
python -m gp_maker song.mp3 --stem guitar -o guitar_tab.gp5

# Full song → vocal melody tab
python -m gp_maker song.mp3 -o vocal_tab.gp5

# Pre-isolated guitar audio (skip separation)
python -m gp_maker guitar_only.wav --stem guitar --no-separate

# Apple Music m4a file → lead guitar tab
python -m gp_maker song.m4a --stem guitar -o guitar_tab.gp5

# Override tempo and title
python -m gp_maker song.mp3 --stem guitar --bpm 120 --title "Hotel California"
```

## Output Format

Generates `.gp5` (Guitar Pro 5) files, compatible with:
- Guitar Pro 5, 6, 7, 8
- TuxGuitar (free, open-source)
- MuseScore

## Dependencies

| Package | Purpose |
|---------|---------|
| `demucs` | Audio stem separation (Meta) |
| `basic-pitch` | Polyphonic pitch detection (Spotify) |
| `librosa` | BPM detection |
| `pyguitarpro` | GP5 file generation |
| `torch` | Deep learning backend |
| `tqdm` | Progress display |

## Supported Audio Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| MP3 | `.mp3` | Works out of the box |
| WAV | `.wav` | Works out of the box |
| FLAC | `.flac` | Works out of the box |
| M4A/AAC | `.m4a`, `.aac` | Requires ffmpeg |
| OGG | `.ogg` | Works out of the box |
| WMA | `.wma` | Requires ffmpeg |
| Opus | `.opus` | Requires ffmpeg |

For m4a/aac/wma/opus files, install ffmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install ffmpeg
```

## Requirements

- Python 3.10+
- ffmpeg (for m4a/aac/wma formats; startup scripts will warn if missing)
- ~4GB disk space (for ML models on first run)
- GPU optional (CPU works, but slower for Demucs separation)

## Claude Code Skill

This project includes a Claude Code skill at `.claude/skills/gp-maker.md`. To use it as an agent tool:

```
/gp-maker song.mp3 --stem guitar
```

## License

See [LICENSE](LICENSE) for details.
