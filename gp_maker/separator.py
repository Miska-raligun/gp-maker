"""Separate audio stems (vocals, guitar, etc.) using Demucs."""

import os
import tempfile
from pathlib import Path

from gp_maker.config import DEMUCS_6S_MODEL


def separate_stem(audio_path: str, stem: str = "vocals",
                  output_dir: str | None = None) -> str:
    """Separate a specific stem from an audio file using Demucs.

    Args:
        audio_path: Path to input audio file.
        stem: Which stem to extract ("vocals" or "guitar").
        output_dir: Directory for separated output. Uses temp dir if None.

    Returns:
        Path to the separated stem WAV file.
    """
    import demucs.separate

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="gp_maker_")

    audio_name = Path(audio_path).stem

    if stem == "guitar":
        # Use 6-stem model which has a dedicated guitar output
        demucs.separate.main([
            "-n", DEMUCS_6S_MODEL,
            "--out", output_dir,
            audio_path,
        ])
        stem_filename = "guitar.wav"
        model_dir = DEMUCS_6S_MODEL
    else:
        # Vocal mode: use htdemucs with two-stem separation
        demucs.separate.main([
            "--two-stems", "vocals",
            "-n", "htdemucs",
            "--out", output_dir,
            audio_path,
        ])
        stem_filename = "vocals.wav"
        model_dir = "htdemucs"

    # Find the output file
    # Demucs outputs to: output_dir/<model>/<filename_without_ext>/<stem>.wav
    stem_path = os.path.join(output_dir, model_dir, audio_name, stem_filename)

    if not os.path.exists(stem_path):
        # Try alternative path patterns
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f == stem_filename:
                    return os.path.join(root, f)
        raise FileNotFoundError(
            f"Demucs separation completed but {stem_filename} not found in {output_dir}"
        )

    return stem_path


def separate_vocals(audio_path: str, output_dir: str | None = None) -> str:
    """Separate vocals from an audio file. Backward-compatible wrapper."""
    return separate_stem(audio_path, stem="vocals", output_dir=output_dir)
