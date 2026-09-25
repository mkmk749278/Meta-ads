#!/usr/bin/env python3
"""Synthesize an ad's soundtrack from the cue list inside its HTML.

An ad opts in with a <script type="application/json" id="soundtrack"> block:

    {"bpm": 120, "music_until": 12500, "end": 18000,
     "sfx": [[0, "impact"], [60, "ding"], [9000, "toggle"], ...]}

Everything is generated here from sine waves and seeded noise: no samples, no
library music, nothing to license. It is deterministic, so the same HTML gives
the same WAV every time, and the beat grid is the one the ad's visuals cut on
(runtime.js times are ms, 120 BPM = one beat every 500ms).

The mix: four-on-the-floor kick, off-beat hats, a sidechained bass + pad on an
Am-F-C-G loop until `music_until`; then only the pad rings out under the end
card, so the disclaimer is not fighting a beat.

    python tools/soundtrack.py ads/hero-auto-trade out/hero.wav
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(360)


def env(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / decay)


def lowpass(x: np.ndarray, cutoff: float | np.ndarray) -> np.ndarray:
    """One-pole low-pass; cutoff may vary per sample."""
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def highpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    return x - lowpass(x, cutoff)


def tone(freq: float | np.ndarray, n: int) -> np.ndarray:
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def noise(n: int) -> np.ndarray:
    return rng.uniform(-1, 1, n)


# ---------------------------------------------------------------- instruments
def kick() -> np.ndarray:
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.045)
    click = highpass(noise(n), 3000) * env(n, 0.0005, 0.004) * 0.4
    return tone(f, n) * env(n, 0.001, 0.16) + click


def hat() -> np.ndarray:
    n = int(0.06 * SR)
    return highpass(noise(n), 7000) * env(n, 0.0005, 0.018) * 0.5


def impact() -> np.ndarray:
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    boom = tone(38 + 60 * np.exp(-t / 0.08), n) * env(n, 0.001, 0.45)
    crash = lowpass(noise(n), 5000) * env(n, 0.001, 0.25) * 0.35
    return (boom + crash) * 0.9


def whoosh() -> np.ndarray:
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    cut = 400 + 6000 * np.sin(np.pi * t / t[-1])
    return lowpass(noise(n), cut) * np.sin(np.pi * t / t[-1]) ** 2 * 0.7


def riser1() -> np.ndarray:
    """1s noise sweep that ends on the next cut."""
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    cut = 200 + 9000 * (t / t[-1]) ** 2
    sweep = tone(300 + 900 * (t / t[-1]) ** 2, n) * 0.15
    return (lowpass(noise(n), cut) * 0.5 + sweep) * (t / t[-1]) ** 2


def ding() -> np.ndarray:
    n = int(0.9 * SR)
    a = tone(1318.5, n) * env(n, 0.002, 0.30)
    b = np.zeros(n)
    off = int(0.11 * SR)
    b[off:] = tone(1975.5, n - off) * env(n - off, 0.002, 0.40)
    return (a + b) * 0.35


def buzz() -> np.ndarray:
    """Phone vibrate: 170Hz rattle, two pulses."""
    n = int(0.36 * SR)
    t = np.arange(n) / SR
    gate = ((t % 0.18) < 0.13).astype(float)
    return np.sign(tone(170, n)) * lowpass(gate, 60) * 0.18


def blip() -> np.ndarray:
    n = int(0.09 * SR)
    return tone(1760, n) * env(n, 0.001, 0.025) * 0.25


def lock() -> np.ndarray:
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    return (tone(880 + 880 * np.minimum(t / 0.08, 1), n) * env(n, 0.001, 0.12) * 0.3
            + tone(1760, n) * env(n, 0.06, 0.15) * 0.2)


def tick() -> np.ndarray:
    n = int(0.12 * SR)
    return (tone(2400, n) * env(n, 0.0005, 0.02) + highpass(noise(n), 4000) * env(n, 0.0005, 0.006)) * 0.3


def hit() -> np.ndarray:
    """A punchy stab for the 1 Entry / 1 Stop / 1 Exit words."""
    n = int(0.5 * SR)
    chord = sum(tone(f, n) for f in (220, 277.2, 329.6, 440))
    return lowpass(np.tanh(chord * 1.5), 3500) * env(n, 0.002, 0.12) * 0.35 + impact()[:n] * 0.4


def toggle() -> np.ndarray:
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    click = highpass(noise(n), 2000) * env(n, 0.0005, 0.005) * 0.6
    up = tone(600 + 1200 * np.minimum(t / 0.12, 1), n) * env(n, 0.002, 0.10) * 0.3
    return click + up


def zap() -> np.ndarray:
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    return tone(2000 * np.exp(-t / 0.08) + 200, n) * env(n, 0.001, 0.15) * 0.22


def alarm() -> np.ndarray:
    """A short 'denied' buzz for the rejected withdrawal key."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    gate = ((t % 0.15) < 0.1).astype(float)
    return lowpass(np.sign(tone(220, n)), 2500) * gate * env(n, 0.001, 0.3) * 0.14


def sub() -> np.ndarray:
    """808-style sub drop: a pitch-falling sine with a soft saturated tail."""
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    return np.tanh(tone(30 + 55 * np.exp(-t / 0.12), n) * env(n, 0.002, 0.55) * 1.6) * 0.7


def glitch() -> np.ndarray:
    """Stuttered, bit-crushed noise + square chirps: a digital tear on a cut."""
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    crushed = np.round(noise(n) * 4) / 4
    gate = ((t % 0.035) < 0.02).astype(float) * (t < 0.3)
    chirp = np.sign(tone(900 + 2600 * ((t * 23) % 1), n)) * 0.3
    return (highpass(crushed, 1200) * 0.5 + chirp) * gate * env(n, 0.001, 0.2) * 0.5


def tap() -> np.ndarray:
    """A glassy screen tap."""
    n = int(0.15 * SR)
    return (tone(3100, n) * env(n, 0.0005, 0.018) * 0.3 + highpass(noise(n), 5000) * env(n, 0.0003, 0.004) * 0.4)


def unlock() -> np.ndarray:
    """Mechanical padlock: two clicks, then a rising two-note chime."""
    n = int(0.8 * SR)
    out = np.zeros(n)
    for at in (0.0, 0.07):
        i = int(at * SR)
        m = int(0.05 * SR)
        out[i:i + m] += highpass(noise(m), 1500) * env(m, 0.0003, 0.008) * 0.8
    for at, f in ((0.14, 1046.5), (0.24, 1568.0)):
        i = int(at * SR)
        m = n - i
        out[i:] += tone(f, m) * env(m, 0.002, 0.25) * 0.28
    return out


def shatter() -> np.ndarray:
    """Bright glassy burst: noise + a cluster of detuned high partials."""
    n = int(1.0 * SR)
    r = np.random.default_rng(7)
    bells = sum(tone(f, n) * env(n, 0.001, 0.08 + 0.3 * r.random()) for f in r.uniform(2500, 7000, 9)) / 9
    return (highpass(noise(n), 3500) * env(n, 0.0005, 0.12) * 0.6 + bells * 0.8)


def scramble() -> np.ndarray:
    """Fast random blips — digits decoding."""
    n = int(0.75 * SR)
    out = np.zeros(n)
    r = np.random.default_rng(3)
    step = int(0.035 * SR)
    for k, i in enumerate(range(0, n - step, step)):
        f = r.choice([1320, 1760, 2093, 2637, 3136])
        out[i:i + step] += tone(f, step) * env(step, 0.0005, 0.012) * 0.22 * (1 - k * step / n * 0.6)
    return out


def stamp() -> np.ndarray:
    """A heavy rubber-stamp thud with a short slap."""
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    thud = tone(70 + 90 * np.exp(-t / 0.03), n) * env(n, 0.001, 0.12)
    slap = lowpass(noise(n), 2500) * env(n, 0.0005, 0.03) * 0.7
    return (thud + slap) * 0.9


SFX = {k: v for k, v in globals().items() if k in {
    "impact", "whoosh", "riser1", "ding", "buzz", "blip", "lock", "tick", "hit", "toggle", "zap", "alarm",
    "sub", "glitch", "tap", "unlock", "shatter", "scramble", "stamp"}}

# Chord loops, one chord per bar of 4 beats: (bass root Hz, pad voicing).
PROGS = {
    # Am  F  C  G — the hero's bright, driving loop.
    "am": [(110.0, (220.0, 261.6, 329.6)), (87.3, (174.6, 220.0, 261.6)),
           (130.8, (261.6, 329.6, 392.0)), (98.0, (196.0, 246.9, 293.7))],
    # Fm  Db  Ab  Eb — darker, tenser; suits a reveal.
    "dark": [(87.3, (174.6, 207.7, 261.6)), (69.3, (138.6, 174.6, 207.7)),
             (103.8, (207.7, 261.6, 311.1)), (77.8, (155.6, 196.0, 233.1))],
    # Em  C  G  D — lifts into resolution.
    "lift": [(82.4, (164.8, 196.0, 246.9)), (65.4, (130.8, 164.8, 196.0)),
             (98.0, (196.0, 246.9, 293.7)), (73.4, (146.8, 185.0, 220.0))],
}
PROG = PROGS["am"]


def place(buf: np.ndarray, snd: np.ndarray, at_ms: float, gain: float = 1.0) -> None:
    i = int(at_ms / 1000 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(snd))
    buf[i:j] += snd[: j - i] * gain


def build(cues: dict) -> np.ndarray:
    beat = 60000 / cues.get("bpm", 120)
    end = cues["end"]
    until = cues.get("music_until", end)
    start = cues.get("music_from", 0)
    # Drums (and the bass that rides them) may enter later than the pad, so an
    # ad can open on tension and DROP the beat on its first cut.
    dstart = cues.get("drums_from", start)
    prog = PROGS.get(cues.get("prog", "am"), PROGS["am"])
    n = int(end / 1000 * SR)
    drums = np.zeros(n)
    music = np.zeros(n)
    fx = np.zeros(n)

    k, h = kick(), hat()
    t = dstart
    while t < until:
        place(drums, k, t, 0.9)
        place(drums, h, t + beat / 2, 0.5)
        t += beat

    # Sidechain: duck bass + pad under each kick.
    duck = np.ones(n)
    t = dstart
    while t < until:
        i = int(t / 1000 * SR)
        m = min(n, i + int(0.25 * SR))
        duck[i:m] = 1 - 0.75 * np.exp(-np.arange(m - i) / SR / 0.07)
        t += beat

    bar = beat * 4
    t, idx = start, 0
    while t < end:
        root, chord = prog[idx % len(prog)]
        seg = int(min(bar, end - t) / 1000 * SR)
        if seg <= 0:
            break
        if t + bar > dstart and t < until:
            # 8th-note bass on the root, saw-ish and filtered; enters with the drums.
            for s in range(8):
                if t + s * beat / 2 < dstart:
                    continue
                bn = int(beat / 2 / 1000 * SR)
                x = sum(tone(root * m, bn) / m for m in (1, 2, 3, 4))
                place(music, lowpass(x, 700) * env(bn, 0.003, 0.12) * 0.45, t + s * beat / 2)
        pad = sum(tone(f * d, seg) for f in chord for d in (0.997, 1.003)) / 6
        fade = np.minimum(1, np.arange(seg) / (0.05 * SR))
        place(music, lowpass(pad, 1800) * fade * 0.22, t)
        t += bar
        idx += 1
    music *= duck

    for at, name in cues.get("sfx", []):
        place(fx, SFX[name](), at)

    # After the music stops, fade the pad out across the end card.
    tail = np.ones(n)
    i = int(until / 1000 * SR)
    tail[i:] = np.linspace(1, 0.0, n - i) ** 1.5
    music *= tail * np.where(np.arange(n) >= i, 0.7, 1.0)

    mix = drums * 0.8 + music + fx * 0.9
    mix = np.tanh(mix)
    mix /= np.max(np.abs(mix)) + 1e-9
    return mix * 0.89  # ~ -1 dBFS peak


def read_cues(ad_dir: pathlib.Path) -> dict | None:
    html = (ad_dir / "index.html").read_text()
    m = re.search(r'<script type="application/json" id="soundtrack">(.*?)</script>', html, re.S)
    return json.loads(m.group(1)) if m else None


def write_wav(path: pathlib.Path, mono: np.ndarray) -> None:
    # Slight stereo width: delay the right channel by 8ms on the pad-heavy mix.
    d = int(0.008 * SR)
    right = np.concatenate([mono[:d] * 0, mono[:-d]]) * 0.5 + mono * 0.5
    stereo = np.stack([mono, right], axis=1)
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def render(ad_dir: pathlib.Path, out: pathlib.Path) -> bool:
    cues = read_cues(ad_dir)
    if not cues:
        return False
    write_wav(out, build(cues))
    return True


if __name__ == "__main__":
    ok = render(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
    sys.exit(0 if ok else "no #soundtrack cue list in that ad")
