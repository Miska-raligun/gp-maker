"""Main processing pipeline: audio → Guitar Pro tab."""

import sys
from itertools import groupby

from tqdm import tqdm

from gp_maker.config import (
    DEFAULT_BPM,
    MIN_NOTE_AMPLITUDE,
    MIN_NOTE_AMPLITUDE_GUITAR,
    PIPELINE_STEPS,
)
from gp_maker.guitar_mapper import map_chord, midi_to_guitar
from gp_maker.gp_writer import TabNote, create_gp5
from gp_maker.pitch_detector import detect_bpm, detect_notes
from gp_maker.quantizer import quantize_notes
from gp_maker.separator import separate_stem


def process(
    input_path: str,
    output_path: str,
    title: str = "Transcribed Tab",
    bpm: float | None = None,
    skip_separation: bool = False,
    stem: str = "vocals",
) -> None:
    """Run the full audio-to-guitar-tab pipeline.

    Args:
        input_path: Path to input audio file.
        output_path: Path for output .gp5 file.
        title: Song title for the GP file.
        bpm: Manual BPM override. Auto-detected if None.
        skip_separation: If True, skip stem separation.
        stem: Which stem to extract ("vocals" or "guitar").
    """
    is_guitar = stem == "guitar"
    steps = PIPELINE_STEPS if not skip_separation else PIPELINE_STEPS[1:]
    progress = tqdm(total=len(steps), desc="Processing", file=sys.stderr,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}")

    # Step 1: Stem separation
    if skip_separation:
        audio_path = input_path
    else:
        step_name = f"Separating {stem}"
        progress.set_postfix_str(step_name)
        audio_path = separate_stem(input_path, stem=stem)
        progress.update(1)

    # Step 2: Pitch detection + BPM
    progress.set_postfix_str("Detecting pitch")
    amplitude_threshold = MIN_NOTE_AMPLITUDE_GUITAR if is_guitar else MIN_NOTE_AMPLITUDE
    detected_notes = detect_notes(audio_path, min_amplitude=amplitude_threshold)

    if bpm is None:
        bpm = detect_bpm(audio_path)
    progress.update(1)

    print(f"  Detected {len(detected_notes)} notes, BPM: {bpm}", file=sys.stderr)

    # Step 3: Quantize notes
    progress.set_postfix_str("Quantizing notes")
    quantized = quantize_notes(detected_notes, bpm, allow_polyphony=is_guitar)
    progress.update(1)

    print(f"  Quantized to {len(quantized)} notes", file=sys.stderr)

    # Step 4: Map to guitar fretboard
    progress.set_postfix_str("Mapping to guitar")
    if is_guitar:
        tab_notes = _map_polyphonic(quantized)
    else:
        tab_notes = _map_monophonic(quantized)
    progress.update(1)

    # Step 5: Generate GP5 file
    progress.set_postfix_str("Generating GP5 file")
    track_name = "Lead Guitar" if is_guitar else "Vocal Melody"
    instrument = 27 if is_guitar else 25  # Electric clean vs Acoustic steel
    create_gp5(tab_notes, output_path, title=title, bpm=int(bpm),
               track_name=track_name, instrument=instrument)
    progress.update(1)

    progress.set_postfix_str("Done!")
    progress.close()

    print(f"\nOutput saved to: {output_path}", file=sys.stderr)


def _map_monophonic(quantized):
    """Map single notes to fretboard (original vocal mode)."""
    tab_notes = []
    for qn in quantized:
        string, fret = midi_to_guitar(qn.midi_pitch)
        tab_notes.append(TabNote(
            string=string,
            fret=fret,
            start_beat=qn.start_beat,
            duration_value=qn.duration_value,
            velocity=qn.velocity,
            is_rest=qn.is_rest,
        ))
    return tab_notes


def _map_polyphonic(quantized):
    """Map chord groups to fretboard (guitar mode)."""
    tab_notes = []

    # Group quantized notes by start_beat
    for beat, group in groupby(quantized, key=lambda n: round(n.start_beat, 2)):
        group_list = list(group)

        if len(group_list) == 1:
            qn = group_list[0]
            string, fret = midi_to_guitar(qn.midi_pitch)
            tab_notes.append(TabNote(
                string=string,
                fret=fret,
                start_beat=qn.start_beat,
                duration_value=qn.duration_value,
                velocity=qn.velocity,
                is_rest=qn.is_rest,
            ))
        else:
            # Chord: map all pitches together to avoid string conflicts
            pitches = [qn.midi_pitch for qn in group_list]
            positions = map_chord(pitches)
            # Use duration/velocity from the loudest note in the group
            ref = max(group_list, key=lambda n: n.velocity)
            for string, fret in positions:
                tab_notes.append(TabNote(
                    string=string,
                    fret=fret,
                    start_beat=ref.start_beat,
                    duration_value=ref.duration_value,
                    velocity=ref.velocity,
                    is_rest=False,
                ))

    return tab_notes
