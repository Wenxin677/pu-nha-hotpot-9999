#!/usr/bin/env python3
"""Synthesise the short ambience clip used on the history page (the audio
element the rubric asks for), with the standard library only: a low room hum,
bubbling broth blips and a little steam noise.  Deterministic (seeded), so the
file is reproducible.

Run:  python tools/make_audio.py
"""
import math
import os
import random
import struct
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")
os.makedirs(OUT, exist_ok=True)

RATE = 22050
SECONDS = 14
rnd = random.Random(9999)

n = RATE * SECONDS
buf = [0.0] * n

# 1. low room hum: two detuned sines with a slow tremolo
for i in range(n):
    t = i / RATE
    trem = 0.75 + 0.25 * math.sin(2 * math.pi * 0.13 * t)
    buf[i] += 0.10 * trem * math.sin(2 * math.pi * 72 * t)
    buf[i] += 0.06 * trem * math.sin(2 * math.pi * 108.5 * t)

# 2. steam: filtered white noise, slow amplitude drift
noise = 0.0
for i in range(n):
    t = i / RATE
    noise = 0.92 * noise + 0.08 * (rnd.random() * 2 - 1)
    buf[i] += 0.055 * noise * (0.6 + 0.4 * math.sin(2 * math.pi * 0.07 * t + 1.1))

# 3. bubbles: short decaying sine pops with a small upward pitch bend
t_cursor = 0.15
while t_cursor < SECONDS - 0.3:
    dur = rnd.uniform(0.06, 0.16)
    freq = rnd.uniform(180, 760)
    amp = rnd.uniform(0.05, 0.14)
    start = int(t_cursor * RATE)
    length = int(dur * RATE)
    for k in range(length):
        idx = start + k
        if idx >= n:
            break
        env = math.exp(-6.0 * k / length)
        f = freq * (1.0 + 0.35 * k / length)
        buf[idx] += amp * env * math.sin(2 * math.pi * f * k / RATE)
    t_cursor += rnd.uniform(0.09, 0.42)

# 4. end fade in / out so the loop does not click
fade = int(0.35 * RATE)
for i in range(fade):
    buf[i] *= i / fade
    buf[n - 1 - i] *= i / fade

peak = max(abs(v) for v in buf) or 1.0
scale = 0.85 / peak
frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * scale)) * 32767)) for v in buf)

path = os.path.join(OUT, "kitchen-ambience.wav")
with wave.open(path, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(frames)

print("wrote", path, round(os.path.getsize(path) / 1024), "KB,", SECONDS, "s", RATE, "Hz mono")
