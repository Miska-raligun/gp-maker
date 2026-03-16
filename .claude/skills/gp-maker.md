---
name: gp-maker
description: Convert audio files (MP3, WAV, FLAC) to Guitar Pro (.gp5) tablature. Extracts lead guitar or vocals from a mix and generates playable guitar tabs with chord support.
user_invocable: true
---

# GP-Maker Skill

Convert audio files to Guitar Pro tablature by extracting and transcribing instrument stems.

## Usage

The user provides an audio file path and optionally specifies which stem to extract.

### Arguments

The skill accepts the same arguments as the CLI:

- First argument: path to audio file (required)
- `--stem guitar` or `--stem vocals`: which stem to extract (default: vocals)
- `-o <path>`: output .gp5 file path
- `--bpm <number>`: manual BPM override
- `--no-separate`: skip stem separation (input is already isolated)
- `--title <name>`: song title for the GP file

### Examples

```
/gp-maker song.mp3 --stem guitar
/gp-maker song.mp3 --stem guitar -o my_tab.gp5
/gp-maker vocals.wav --no-separate
/gp-maker song.mp3 --bpm 140 --title "My Song"
```

## Instructions

When this skill is invoked:

1. **Parse the arguments** from `$ARGUMENTS`. The first positional argument is the audio file path. All remaining arguments are CLI flags.

2. **Validate the input file** exists. If not, tell the user and stop.

3. **Ensure dependencies are installed**. Run:
   ```bash
   cd /home/user/gp-maker
   if [ ! -f .venv/bin/python ]; then
     python3 -m venv .venv
     .venv/bin/pip install -r requirements.txt -q
   fi
   ```

4. **Run the pipeline**:
   ```bash
   cd /home/user/gp-maker
   .venv/bin/python -m gp_maker $ARGUMENTS
   ```

5. **Report the result** to the user:
   - On success: tell them the output file path and suggest opening it in Guitar Pro or TuxGuitar
   - On failure: show the error message and suggest common fixes:
     - "No notes detected" → try lowering `--bpm` or check audio quality
     - "File not found" → verify the audio file path
     - Import errors → run `./start.sh --setup` or `pip install -r requirements.txt`

## Supported Modes

| Mode | Flag | Demucs Model | Description |
|------|------|-------------|-------------|
| Vocals | `--stem vocals` (default) | `htdemucs` | Extract vocal melody, monophonic tab |
| Guitar | `--stem guitar` | `htdemucs_6s` | Extract lead guitar, polyphonic with chords |

## Notes

- First run downloads ML models (~1-2GB). This is normal and only happens once.
- Processing takes 1-5 minutes depending on audio length and hardware.
- GPU (CUDA) accelerates Demucs separation significantly but is not required.
- Output `.gp5` files are compatible with Guitar Pro 5/6/7/8, TuxGuitar, and MuseScore.
