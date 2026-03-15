# GP Maker - Audio to Guitar Tab

## Overview
Convert MP3 audio files to Guitar Pro (.gp5) tab files by extracting the vocal melody and mapping it to single-note guitar notation.

## Pipeline

```
MP3 → Vocal Separation (demucs) → Pitch Detection (crepe) → Note Quantization → Guitar Fret Mapping → GP5 File
```

## Tech Stack
- Python 3.10+
- `demucs` - vocal/instrument separation
- `crepe` - neural pitch detection
- `librosa` - audio analysis, beat detection
- `pyguitarpro` - GP file generation

## Project Structure
```
gp-maker/
├── requirements.txt
├── main.py              # CLI entry point
├── gp_maker/
│   ├── __init__.py
│   ├── separator.py     # Vocal separation (demucs)
│   ├── pitch.py         # Pitch detection (crepe)
│   ├── quantize.py      # Note/rhythm quantization
│   ├── guitar_map.py    # Pitch → guitar fret mapping
│   └── gp_writer.py     # GP file generation (pyguitarpro)
```

## Key Design Decisions
- Standard tuning EADGBE
- Single-note melody only (no chords)
- 4/4 time signature with auto BPM detection
- Prefer lower fret positions, minimize string jumps
- Ignore low-confidence pitch frames
