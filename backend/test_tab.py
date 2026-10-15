import numpy as np

import tab


def bass_line(midis, sr=tab.SR, lead=0.5, step=0.25):
    """Plucked-ish tones (6 harmonics, decaying) every `step` seconds, plus a click track on the beat."""
    t = np.arange(int(sr * (step - 0.01))) / sr
    y = np.zeros(int(sr * (lead + len(midis) * step + 1)))
    for i, m in enumerate(midis):
        f = 440 * 2 ** ((m - 69) / 12)
        s = int(sr * (lead + i * step))
        y[s : s + len(t)] += sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 7)) * np.exp(-t * 6) * 0.3
    mix = y.copy()
    click = np.sin(2 * np.pi * 60 * t[:500]) * np.exp(-t[:500] * 40)
    for b in np.arange(lead, len(y) / sr - 0.2, 2 * step):
        mix[int(b * sr) : int(b * sr) + 500] += click
    return y, mix


def test_transcribe_synthetic_line():
    line = [28, 33, 38, 43, 48, 42, 28, 28] * 2  # E A D G C F# E E in eighths at 120 BPM
    bass, mix = bass_line(line)
    notes = tab.detect_notes(bass, tab.SR)
    assert [m for _, m in notes] == line
    assert np.allclose([t for t, _ in notes], 0.5 + 0.25 * np.arange(len(line)), atol=0.04)

    text = tab.render(notes, tab.beat_grid(mix, tab.SR, len(mix) / tab.SR))
    rows = {r[0]: r for r in text.splitlines() if r[:2] in ("G|", "D|", "A|", "E|")}
    played = [(s, fret) for s in "GDAE" for fret in rows[s][2:].replace("|", "").split("-") if fret]
    assert sorted(played) == sorted([("E", "0"), ("A", "0"), ("D", "0"), ("G", "0"), ("G", "5"), ("D", "4"), ("E", "0"), ("E", "0")] * 2)


def test_place():
    assert tab.place(28, 0) == (3, 0)  # low E open
    assert tab.place(48, 0) == (0, 5)  # C3: G string 5th fret, not D 10
    assert tab.place(48, 12) == (1, 10)  # ...unless the hand is already up there
    assert tab.place(16, 0) == (3, 0)  # below the bass's range: up an octave
