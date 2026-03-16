# GP-Maker

Audio-to-Guitar-Pro tablature converter.

## Project Structure

```
gp_maker/
  cli.py              # CLI entry point (argparse)
  pipeline.py          # Main processing orchestrator
  separator.py         # Demucs stem separation (vocals/guitar)
  pitch_detector.py    # basic-pitch note detection + librosa BPM
  quantizer.py         # Note quantization to beat grid (supports chords)
  guitar_mapper.py     # MIDI → (string, fret) mapping (supports chords)
  gp_writer.py         # GP5 file generation via pyguitarpro
  config.py            # Configuration constants
```

## Running

```bash
# Via startup script (auto-installs deps)
./start.sh <audio_file> [options]

# Direct
python -m gp_maker <audio_file> [options]
```

## Key CLI Flags

- `--stem vocals` (default): extract vocals, monophonic tab
- `--stem guitar`: extract lead guitar via htdemucs_6s, polyphonic with chords
- `--no-separate`: skip Demucs separation (input is already isolated)
- `--bpm <N>`: manual BPM override
- `-o <path>`: output .gp5 path

## Testing

No test framework yet. Manual validation:
```bash
python -m gp_maker test.mp3 --stem guitar -o test.gp5
# Open test.gp5 in TuxGuitar / Guitar Pro
```

## Dependencies

See `requirements.txt`. Key: demucs, basic-pitch, librosa, pyguitarpro, torch.
