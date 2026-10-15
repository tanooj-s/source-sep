"""Turn a separated bass stem into ASCII tab for a 4-string bass in standard tuning."""

import itertools
import math

import librosa
import numpy as np
import scipy.signal

SR = 11025  # bass lives well under 1 kHz, and pyin is the slow step
FRAME = 1024  # ~93 ms, long enough for two periods of low B
HOP = 128  # ~12 ms
MIN_NOTE_FRAMES = 5  # ~60 ms; shorter pitch runs are pyin jitter
SNAP_FRAMES = 6  # ~70 ms: pyin + median filter smear pitch changes by about this much
MIN_RMS = 0.005  # ~-46 dBFS; quieter frames are bleed or silence, not bass
STRINGS = [("G", 43), ("D", 38), ("A", 33), ("E", 28)]  # MIDI of open strings, top tab line first
MAX_FRET = 20
SLOTS_PER_BEAT = 4  # 16th-note grid
BEATS_PER_BAR = 4
BARS_PER_LINE = 4


def detect_notes(y, sr):
    """Return [(seconds, midi)] note starts for a monophonic bass line."""
    f0, voiced, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("B0"), fmax=librosa.note_to_hz("E4"), sr=sr, frame_length=FRAME, hop_length=HOP
    )
    rms = librosa.feature.rms(y=y, frame_length=FRAME, hop_length=HOP)[0]
    voiced &= rms > max(MIN_RMS, rms.max() / 30)  # also drop bleed 30 dB under the loudest note
    midi = np.where(voiced, np.round(librosa.hz_to_midi(np.nan_to_num(f0, nan=1.0))), 0)
    midi = scipy.signal.medfilt(midi, 5)
    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=HOP)
    notes, frame = [], 0
    for pitch, run in itertools.groupby(midi):
        start, frame = frame, frame + len(list(run))
        if pitch == 0 or frame - start < MIN_NOTE_FRAMES:
            continue
        # pyin's window smears run edges by up to half a frame, so snap the start to the nearest onset
        near = onsets[np.abs(onsets - start) <= SNAP_FRAMES]
        first = near[np.argmin(np.abs(near - start))] if len(near) else start
        # later onsets inside a steady pitch are repeated notes
        starts = [first] + [o for o in onsets if first + SNAP_FRAMES < o < frame - MIN_NOTE_FRAMES]
        notes += [(librosa.frames_to_time(s, sr=sr, hop_length=HOP), int(pitch)) for s in starts]
    return notes


def beat_grid(mix, sr, duration):
    """Beat times covering the whole track, with a bar starting on the first detected beat."""
    _, beats = librosa.beat.beat_track(y=mix, sr=sr, hop_length=HOP, units="time")  # default hop skews tempo a few %
    if len(beats) < 2:
        beats = np.array([0.0, 0.5])  # no pulse found: fall back to 120 BPM
    period = np.median(np.diff(beats))
    # ponytail: assumes 4/4 with the first detected beat as a downbeat; a downbeat tracker would fix bar lines
    pre = math.ceil(beats[0] / period / BEATS_PER_BAR) * BEATS_PER_BAR
    post = math.ceil((duration - beats[-1]) / period) + 1
    return np.concatenate([beats[0] - period * np.arange(pre, 0, -1), beats, beats[-1] + period * np.arange(1, post)])


def place(midi, hand):
    """Pick (string index, fret) for a pitch, staying near the fretting hand; open strings are free."""
    while midi < STRINGS[-1][1]:
        midi += 12
    while midi > STRINGS[0][1] + MAX_FRET:
        midi -= 12
    options = [(i, midi - open_) for i, (_, open_) in enumerate(STRINGS) if 0 <= midi - open_ <= MAX_FRET]
    # ponytail: greedy per note; a Viterbi pass over the whole line would plan shifts better
    return min(options, key=lambda o: (0 if o[1] == 0 else abs(o[1] - hand), o[1]))


def render(notes, beats):
    """ASCII tab, one column per 16th note, BARS_PER_LINE bars per system."""
    beat_index = np.arange(len(beats))
    slots, hand = {}, 0
    for t, midi in notes:
        slot = round(float(np.interp(t, beats, beat_index)) * SLOTS_PER_BEAT)
        if slot not in slots:  # two notes in one 16th: keep the first
            slots[slot] = place(midi, hand)
            hand = slots[slot][1] or hand

    slots_per_bar = SLOTS_PER_BEAT * BEATS_PER_BAR
    n_bars = (len(beats) - 1) // BEATS_PER_BAR
    bpm = 60 / np.median(np.diff(beats))
    out = [f"Bass tab - standard tuning (E A D G), ~{bpm:.0f} BPM, 4/4 assumed", ""]
    if not notes:
        return "\n".join(out + ["No bass notes detected."])
    for first in range(0, n_bars, BARS_PER_LINE):
        start = max(0.0, beats[first * BEATS_PER_BAR])
        out.append(f"Bar {first + 1}  ({int(start // 60)}:{int(start % 60):02d})")
        rows = [name + "|" for name, _ in STRINGS]
        for bar in range(first, min(first + BARS_PER_LINE, n_bars)):
            for slot in range(bar * slots_per_bar, (bar + 1) * slots_per_bar):
                string, fret = slots.get(slot, (None, ""))
                width = len(str(fret)) + 1
                rows = [row + (str(fret) if i == string else "").ljust(width, "-") for i, row in enumerate(rows)]
            rows = [row + "|" for row in rows]
        out += rows + [""]
    return "\n".join(out)


def transcribe(bass_path, mix_path):
    bass, _ = librosa.load(bass_path, sr=SR, mono=True)
    mix, _ = librosa.load(mix_path, sr=SR, mono=True)
    return render(detect_notes(bass, SR), beat_grid(mix, SR, len(mix) / SR))
