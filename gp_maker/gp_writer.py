"""Generate Guitar Pro 5 (.gp5) files from quantized note data."""

from dataclasses import dataclass

import guitarpro

from gp_maker.config import DEFAULT_BPM, DEFAULT_TIME_SIGNATURE, STANDARD_TUNING


@dataclass
class TabNote:
    """A single note ready for tablature output."""
    string: int         # 1-6
    fret: int           # 0-24
    start_beat: float   # beat position (1-based, e.g., 1.0 = first beat)
    duration_value: int  # GP duration: 1=whole, 2=half, 4=quarter, 8=eighth, 16=sixteenth
    velocity: int       # 0-127
    is_rest: bool = False


def create_gp5(notes: list[TabNote], output_path: str, title: str = "Transcribed Tab",
               bpm: int = DEFAULT_BPM) -> None:
    """Create a GP5 file from a list of TabNote objects."""
    song = guitarpro.Song()
    song.title = title
    song.artist = "GP-Maker"
    song.tempo = bpm

    # Configure the default track as acoustic guitar
    track = song.tracks[0]
    track.name = "Vocal Melody"
    track.channel.instrument = 25  # Acoustic Guitar (steel)
    track.strings = [guitarpro.GuitarString(n, v) for n, v in sorted(STANDARD_TUNING.items())]

    beats_per_measure = DEFAULT_TIME_SIGNATURE[0]

    if not notes:
        _write_empty_song(song, output_path)
        return

    # Group notes by measure
    max_beat = max(n.start_beat for n in notes)
    total_measures = int(max_beat // beats_per_measure) + 1

    # Ensure we have enough measure headers
    _ensure_measures(song, track, total_measures)

    # Place notes into measures
    for note in notes:
        measure_idx = int((note.start_beat - 1) // beats_per_measure)
        if measure_idx >= len(track.measures):
            continue

        measure = track.measures[measure_idx]
        voice = measure.voices[0]

        beat = guitarpro.Beat(voice)
        beat.duration.value = note.duration_value

        if note.is_rest:
            beat.status = guitarpro.BeatStatus.rest
        else:
            beat.status = guitarpro.BeatStatus.normal
            gp_note = guitarpro.Note(beat)
            gp_note.string = note.string
            gp_note.value = note.fret
            gp_note.velocity = _velocity_to_gp(note.velocity)
            beat.notes.append(gp_note)

        voice.beats.append(beat)

    # Remove default empty beats from voices that got notes
    _clean_default_beats(track)

    guitarpro.write(song, output_path)


def _ensure_measures(song: guitarpro.Song, track: guitarpro.Track,
                     total_measures: int) -> None:
    """Ensure the song has enough measures."""
    while len(song.measureHeaders) < total_measures:
        header = guitarpro.MeasureHeader()
        header.number = len(song.measureHeaders) + 1
        header.start = song.measureHeaders[-1].start + song.measureHeaders[-1].length
        song.measureHeaders.append(header)

        for t in song.tracks:
            measure = guitarpro.Measure(t, header)
            t.measures.append(measure)


def _clean_default_beats(track: guitarpro.Track) -> None:
    """Remove placeholder beats from voices that have real content."""
    for measure in track.measures:
        for voice in measure.voices:
            if len(voice.beats) > 1:
                # Keep only beats we added (remove the auto-generated one)
                real_beats = [b for b in voice.beats if b.notes or b.status == guitarpro.BeatStatus.rest]
                if real_beats:
                    voice.beats = real_beats


def _write_empty_song(song: guitarpro.Song, output_path: str) -> None:
    """Write a song with no notes."""
    guitarpro.write(song, output_path)


def _velocity_to_gp(velocity: int) -> int:
    """Map 0-127 velocity to Guitar Pro velocity constants."""
    if velocity < 32:
        return guitarpro.Velocities.pianoPianissimo
    elif velocity < 48:
        return guitarpro.Velocities.pianissimo
    elif velocity < 64:
        return guitarpro.Velocities.piano
    elif velocity < 80:
        return guitarpro.Velocities.mezzoForte
    elif velocity < 96:
        return guitarpro.Velocities.forte
    elif velocity < 112:
        return guitarpro.Velocities.fortissimo
    else:
        return guitarpro.Velocities.forteFortissimo
