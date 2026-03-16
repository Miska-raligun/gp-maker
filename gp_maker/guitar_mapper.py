"""Map MIDI pitch values to guitar string/fret positions."""

from gp_maker.config import STANDARD_TUNING, GUITAR_MIN_MIDI, GUITAR_MAX_MIDI, MAX_FRET


def midi_to_guitar(midi_pitch: int) -> tuple[int, int]:
    """Convert a MIDI pitch to (string_number, fret_number).

    Chooses the most comfortable position on the fretboard.
    Returns (string, fret) where string is 1-6 and fret is 0-24.
    """
    midi_pitch = clamp_to_guitar_range(midi_pitch)

    candidates = []
    for string_num, open_pitch in STANDARD_TUNING.items():
        fret = midi_pitch - open_pitch
        if 0 <= fret <= MAX_FRET:
            candidates.append((string_num, fret))

    if not candidates:
        # Fallback: shouldn't happen after clamping, but just in case
        return (1, 0)

    # Prefer: lower fret positions (0-12), then middle strings (3,4,2,5,1,6)
    string_preference = {3: 0, 4: 1, 2: 2, 5: 3, 1: 4, 6: 5}
    candidates.sort(key=lambda sf: (
        0 if sf[1] <= 12 else 1,  # prefer frets 0-12
        sf[1],                     # then lower frets
        string_preference.get(sf[0], 6),  # then middle strings
    ))

    return candidates[0]


def clamp_to_guitar_range(midi_pitch: int) -> int:
    """Shift a MIDI pitch by octaves until it falls within guitar range."""
    while midi_pitch < GUITAR_MIN_MIDI:
        midi_pitch += 12
    while midi_pitch > GUITAR_MAX_MIDI:
        midi_pitch -= 12
    return midi_pitch


def map_chord(midi_pitches: list[int]) -> list[tuple[int, int]]:
    """Map multiple simultaneous MIDI notes to guitar positions without string conflicts.

    Strategy: sort notes low-to-high, assign to strings low (6) to high (1),
    using greedy allocation to avoid placing two notes on the same string.

    Args:
        midi_pitches: List of MIDI pitch values (simultaneous notes).

    Returns:
        List of (string, fret) tuples. Notes that cannot be placed are dropped.
    """
    if not midi_pitches:
        return []

    # Single note: use standard mapping
    if len(midi_pitches) == 1:
        return [midi_to_guitar(midi_pitches[0])]

    # Sort low to high
    sorted_pitches = sorted(midi_pitches)
    used_strings = set()
    result = []

    for pitch in sorted_pitches:
        pitch = clamp_to_guitar_range(pitch)

        # Find all valid positions, prefer lower strings for lower notes
        candidates = []
        for string_num, open_pitch in STANDARD_TUNING.items():
            fret = pitch - open_pitch
            if 0 <= fret <= MAX_FRET and string_num not in used_strings:
                candidates.append((string_num, fret))

        if not candidates:
            continue

        # Prefer: higher string number (lower pitch string) first, then lower fret
        candidates.sort(key=lambda sf: (-sf[0], sf[1]))
        chosen = candidates[0]
        used_strings.add(chosen[0])
        result.append(chosen)

    return result


def midi_to_note_name(midi_pitch: int) -> str:
    """Convert MIDI pitch to note name (e.g., 60 → 'C4')."""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_pitch // 12) - 1
    note = note_names[midi_pitch % 12]
    return f"{note}{octave}"
