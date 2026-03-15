"""Separate vocals from audio using Demucs."""

import os
import tempfile
from pathlib import Path


def separate_vocals(audio_path: str, output_dir: str | None = None) -> str:
    """Separate vocals from an audio file using Demucs.

    Args:
        audio_path: Path to input audio file.
        output_dir: Directory for separated output. Uses temp dir if None.

    Returns:
        Path to the separated vocals WAV file.
    """
    import demucs.separate

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="gp_maker_")

    # Run demucs with two-stem mode (vocals + accompaniment)
    demucs.separate.main([
        "--two-stems", "vocals",
        "-n", "htdemucs",
        "--out", output_dir,
        audio_path,
    ])

    # Find the vocals output file
    # Demucs outputs to: output_dir/htdemucs/<filename_without_ext>/vocals.wav
    audio_name = Path(audio_path).stem
    vocals_path = os.path.join(output_dir, "htdemucs", audio_name, "vocals.wav")

    if not os.path.exists(vocals_path):
        # Try alternative path patterns
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f == "vocals.wav":
                    return os.path.join(root, f)
        raise FileNotFoundError(
            f"Demucs vocal separation completed but vocals.wav not found in {output_dir}"
        )

    return vocals_path
