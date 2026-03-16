"""CLI entry point for GP-Maker."""

import argparse
import shutil
import sys
from pathlib import Path

from gp_maker import __version__
from gp_maker.pipeline import process

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".opus"}


def _check_ffmpeg() -> None:
    """Warn if ffmpeg is not installed (needed for m4a/aac/wma decoding)."""
    if shutil.which("ffmpeg") is None:
        print(
            "Warning: ffmpeg not found. It is required for m4a/aac/wma files.\n"
            "  Install: https://ffmpeg.org/download.html\n"
            "  Ubuntu/Debian: sudo apt install ffmpeg\n"
            "  macOS:         brew install ffmpeg\n"
            "  Windows:       winget install ffmpeg\n",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gp-maker",
        description="Convert audio files to Guitar Pro (.gp5) tablature.",
    )
    parser.add_argument(
        "input",
        help="Input audio file path (MP3, WAV, FLAC, M4A, OGG, etc.)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output .gp5 file path (default: <input_name>.gp5)",
    )
    parser.add_argument(
        "--bpm",
        type=float,
        default=None,
        help="Manual BPM override (auto-detected if not specified)",
    )
    parser.add_argument(
        "--stem",
        choices=["vocals", "guitar"],
        default="vocals",
        help="Which stem to extract and transcribe (default: vocals)",
    )
    parser.add_argument(
        "--no-separate",
        action="store_true",
        help="Skip stem separation (use when input is already an isolated stem)",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Song title for the GP file",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = input_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(
            f"Warning: Unrecognized audio format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            file=sys.stderr,
        )

    # Check ffmpeg for formats that need it
    if ext in {".m4a", ".aac", ".wma", ".opus"}:
        _check_ffmpeg()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.with_suffix(".gp5"))

    # Determine title
    title = args.title or input_path.stem

    print(f"GP-Maker v{__version__}", file=sys.stderr)
    print(f"  Input:  {input_path}", file=sys.stderr)
    print(f"  Output: {output_path}", file=sys.stderr)
    print(f"  Stem:   {args.stem}", file=sys.stderr)
    if args.bpm:
        print(f"  BPM:    {args.bpm}", file=sys.stderr)
    if args.no_separate:
        print(f"  Stem separation: skipped", file=sys.stderr)
    print(file=sys.stderr)

    try:
        process(
            input_path=str(input_path),
            output_path=output_path,
            title=title,
            bpm=args.bpm,
            skip_separation=args.no_separate,
            stem=args.stem,
        )
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
