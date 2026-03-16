"""Configuration constants for GP-Maker."""

# Standard guitar tuning (string number → MIDI note value)
# String 1 (highest) = E4 (64), String 6 (lowest) = E2 (40)
STANDARD_TUNING = {
    1: 64,  # E4
    2: 59,  # B3
    3: 55,  # G3
    4: 50,  # D3
    5: 45,  # A2
    6: 40,  # E2
}

# Guitar range in MIDI notes
GUITAR_MIN_MIDI = 40   # E2 (6th string open)
GUITAR_MAX_MIDI = 88   # E6 (1st string, 24th fret)
MAX_FRET = 24

# Default BPM when detection fails
DEFAULT_BPM = 120

# Time signature (beats per measure, beat value)
DEFAULT_TIME_SIGNATURE = (4, 4)

# Quantization: smallest note value (16 = sixteenth note)
QUANTIZE_RESOLUTION = 16

# Minimum note duration in seconds to keep (filter noise)
MIN_NOTE_DURATION_S = 0.03  # 30ms

# Minimum amplitude from basic-pitch to consider a note valid
MIN_NOTE_AMPLITUDE = 0.3

# Lower threshold for guitar (harmonics and overtones are quieter)
MIN_NOTE_AMPLITUDE_GUITAR = 0.2

# Demucs 6-stem model (has dedicated guitar stem)
DEMUCS_6S_MODEL = "htdemucs_6s"

# Maximum simultaneous notes in a chord (one per string)
MAX_CHORD_NOTES = 6

# Pipeline step names for progress display
PIPELINE_STEPS = [
    "Separating stem",
    "Detecting pitch",
    "Quantizing notes",
    "Mapping to guitar",
    "Generating GP5 file",
]
