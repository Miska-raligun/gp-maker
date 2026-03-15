"""Main processing pipeline: audio → Guitar Pro tab."""

import sys

from tqdm import tqdm

from gp_maker.config import DEFAULT_BPM, PIPELINE_STEPS
from gp_maker.guitar_mapper import midi_to_guitar
from gp_maker.gp_writer import TabNote, create_gp5
from gp_maker.pitch_detector import detect_bpm, detect_notes
from gp_maker.quantizer import quantize_notes
from gp_maker.separator import separate_vocals


def process(
    input_path: str,
    output_path: str,
    title: str = "Transcribed Tab",
    bpm: float | None = None,
    skip_separation: bool = False,
) -> None:
    """Run the full audio-to-guitar-tab pipeline.

    Args:
        input_path: Path to input audio file.
        output_path: Path for output .gp5 file.
        title: Song title for the GP file.
        bpm: Manual BPM override. Auto-detected if None.
        skip_separation: If True, skip vocal separation (input is already vocals).
    """
    steps = PIPELINE_STEPS if not skip_separation else PIPELINE_STEPS[1:]
    progress = tqdm(total=len(steps), desc="Processing", file=sys.stderr,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}")

    # Step 1: Vocal separation
    if skip_separation:
        audio_path = input_path
    else:
        progress.set_postfix_str(PIPELINE_STEPS[0])
        audio_path = separate_vocals(input_path)
        progress.update(1)

    # Step 2: Pitch detection + BPM
    progress.set_postfix_str("Detecting pitch")
    detected_notes = detect_notes(audio_path)

    if bpm is None:
        bpm = detect_bpm(audio_path)
    progress.update(1)

    print(f"  Detected {len(detected_notes)} notes, BPM: {bpm}", file=sys.stderr)

    # Step 3: Quantize notes
    progress.set_postfix_str("Quantizing notes")
    quantized = quantize_notes(detected_notes, bpm)
    progress.update(1)

    print(f"  Quantized to {len(quantized)} notes", file=sys.stderr)

    # Step 4: Map to guitar fretboard
    progress.set_postfix_str("Mapping to guitar")
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
    progress.update(1)

    # Step 5: Generate GP5 file
    progress.set_postfix_str("Generating GP5 file")
    create_gp5(tab_notes, output_path, title=title, bpm=int(bpm))
    progress.update(1)

    progress.set_postfix_str("Done!")
    progress.close()

    print(f"\nOutput saved to: {output_path}", file=sys.stderr)
