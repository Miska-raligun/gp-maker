"""Quantize detected notes to musical grid positions and durations."""

from dataclasses import dataclass

from gp_maker.config import (
    DEFAULT_BPM,
    MIN_NOTE_DURATION_S,
    QUANTIZE_RESOLUTION,
)


@dataclass
class DetectedNote:
    """A note detected from audio."""
    start_time: float   # seconds
    end_time: float     # seconds
    midi_pitch: int     # 0-127
    amplitude: float    # 0.0-1.0


@dataclass
class QuantizedNote:
    """A note quantized to beat grid."""
    midi_pitch: int
    start_beat: float    # 1-based beat position
    duration_value: int  # GP duration: 1=whole, 2=half, 4=quarter, 8=eighth, 16=sixteenth
    velocity: int        # 0-127
    is_rest: bool = False


def quantize_notes(notes: list[DetectedNote], bpm: float) -> list[QuantizedNote]:
    """Quantize detected notes to the beat grid.

    Args:
        notes: List of detected notes with timestamps.
        bpm: Beats per minute.

    Returns:
        List of quantized notes aligned to the beat grid.
    """
    if not notes:
        return []

    beat_duration = 60.0 / bpm  # seconds per beat
    grid_size = beat_duration / (QUANTIZE_RESOLUTION / 4)  # seconds per grid unit

    result = []
    for note in notes:
        duration_s = note.end_time - note.start_time
        if duration_s < MIN_NOTE_DURATION_S:
            continue

        # Snap start time to nearest grid position
        grid_pos = round(note.start_time / grid_size)
        start_beat = (grid_pos * grid_size) / beat_duration + 1  # 1-based

        # Determine duration value from note length
        duration_beats = duration_s / beat_duration
        duration_value = _beats_to_duration_value(duration_beats)

        # Map amplitude to velocity (0-127)
        velocity = min(127, max(30, int(note.amplitude * 127)))

        result.append(QuantizedNote(
            midi_pitch=note.midi_pitch,
            start_beat=start_beat,
            duration_value=duration_value,
            velocity=velocity,
        ))

    # Sort by start position and remove overlaps
    result.sort(key=lambda n: n.start_beat)
    result = _remove_overlaps(result, bpm)

    return result


def _beats_to_duration_value(duration_beats: float) -> int:
    """Convert duration in beats to GP duration value.

    GP duration values: 1=whole (4 beats), 2=half (2 beats),
    4=quarter (1 beat), 8=eighth (0.5 beats), 16=sixteenth (0.25 beats).
    """
    if duration_beats >= 3.0:
        return 1   # whole note
    elif duration_beats >= 1.5:
        return 2   # half note
    elif duration_beats >= 0.75:
        return 4   # quarter note
    elif duration_beats >= 0.375:
        return 8   # eighth note
    else:
        return 16  # sixteenth note


def _remove_overlaps(notes: list[QuantizedNote], bpm: float) -> list[QuantizedNote]:
    """Remove overlapping notes, keeping the louder one."""
    if len(notes) <= 1:
        return notes

    beat_duration = 60.0 / bpm
    result = [notes[0]]

    for note in notes[1:]:
        prev = result[-1]
        prev_end = prev.start_beat + _duration_value_to_beats(prev.duration_value)

        # If this note starts before previous ends, it's an overlap
        if note.start_beat < prev_end - 0.01:
            # Keep the louder one
            if note.velocity > prev.velocity:
                result[-1] = note
        else:
            result.append(note)

    return result


def _duration_value_to_beats(duration_value: int) -> float:
    """Convert GP duration value back to beats."""
    mapping = {1: 4.0, 2: 2.0, 4: 1.0, 8: 0.5, 16: 0.25}
    return mapping.get(duration_value, 1.0)
