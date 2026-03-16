"""Detect pitch and BPM from audio using basic-pitch and librosa."""

import librosa
import numpy as np
from basic_pitch.inference import predict

from gp_maker.config import DEFAULT_BPM, MIN_NOTE_AMPLITUDE
from gp_maker.quantizer import DetectedNote


def detect_notes(audio_path: str,
                  min_amplitude: float | None = None) -> list[DetectedNote]:
    """Detect notes from an audio file using basic-pitch.

    Args:
        audio_path: Path to audio file (WAV/MP3).
        min_amplitude: Minimum amplitude threshold. Uses MIN_NOTE_AMPLITUDE if None.

    Returns:
        List of detected notes with timing and pitch info.
    """
    if min_amplitude is None:
        min_amplitude = MIN_NOTE_AMPLITUDE

    model_output, midi_data, note_events = predict(audio_path)

    notes = []
    for start_s, end_s, midi_pitch, amplitude, pitch_bends in note_events:
        if amplitude < min_amplitude:
            continue

        notes.append(DetectedNote(
            start_time=float(start_s),
            end_time=float(end_s),
            midi_pitch=int(round(midi_pitch)),
            amplitude=float(amplitude),
        ))

    return notes


def detect_bpm(audio_path: str) -> float:
    """Detect BPM from audio using librosa.

    Args:
        audio_path: Path to audio file.

    Returns:
        Detected BPM value.
    """
    y, sr = librosa.load(audio_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0])

    if tempo <= 0 or tempo > 300:
        return DEFAULT_BPM

    return round(tempo, 1)
