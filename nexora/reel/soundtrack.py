"""Original soundtrack for the Nexora reel, synthesized from scratch (no samples, no licensing).

120 BPM, 2-second bars starting at t=0. Every cue below matches a motion event in reel.html.
Usage: python3 soundtrack.py out.wav
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 24.0
N = int(SR * DUR)
rng = np.random.default_rng(73)
BEAT = 0.5

L = np.zeros(N)
R = np.zeros(N)
REV_L = np.zeros(N)
REV_R = np.zeros(N)
DUCK = np.ones(N)


def t_axis(d):
    return np.arange(int(SR * d)) / SR


def add(sig, at, gain=1.0, pan=0.0, rev=0.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    lg = gain * np.sqrt((1 - pan) / 2) * np.sqrt(2)
    rg = gain * np.sqrt((1 + pan) / 2) * np.sqrt(2)
    L[i:i + len(sig)] += sig * lg
    R[i:i + len(sig)] += sig * rg
    if rev:
        REV_L[i:i + len(sig)] += sig * lg * rev
        REV_R[i:i + len(sig)] += sig * rg * rev


def filt(x, kind, f):
    sos = butter(2, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def sweep_bp(x, f0, f1, q=2.0):
    """Time-varying state-variable band-pass, frequency glides f0 -> f1 (log)."""
    n = len(x)
    freqs = np.geomspace(f0, f1, n)
    lp = bp = 0.0
    out = np.empty(n)
    damp = 1.0 / q
    for k in range(n):
        f = 2 * np.sin(np.pi * min(freqs[k], SR / 6) / SR)
        hp = x[k] - lp - damp * bp
        bp += f * hp
        lp += f * bp
        out[k] = bp
    return out


def env(n, a, d):
    """Attack / exponential decay envelope, times in seconds."""
    t = np.arange(n) / SR
    e = np.exp(-np.maximum(t - a, 0) / max(d, 1e-4))
    if a > 0:
        e *= np.clip(t / a, 0, 1)
    return e


def saw(freq, t):
    return 2 * ((freq * t) % 1) - 1


# ---------------------------------------------------------------- instruments
def kick():
    t = t_axis(0.45)
    f = 45 + 95 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.22)
    s[:240] += rng.normal(0, 0.4, 240) * np.linspace(1, 0, 240)
    return np.tanh(s * 1.6)


def clap():
    t = t_axis(0.3)
    n = rng.normal(0, 1, len(t))
    e = np.zeros(len(t))
    for off in (0, 0.012, 0.024):
        e += np.exp(-np.maximum(t - off, 0) / 0.012) * (t >= off)
    e += 0.5 * np.exp(-t / 0.09)
    return filt(n * e, "bandpass", [900, 4000]) * 0.9


def hat(dec=0.035):
    t = t_axis(0.12)
    return filt(rng.normal(0, 1, len(t)), "highpass", 7000) * np.exp(-t / dec)


def bass_note(freq, d):
    t = t_axis(d)
    s = saw(freq, t) + 0.5 * saw(freq * 1.005, t)
    cut = 180 + 900 * np.exp(-t / 0.06)
    # approximate a closing filter by blending two static low-passes
    lo = filt(s, "lowpass", 180)
    hi = filt(s, "lowpass", 1100)
    w = (cut - 180) / 920
    return (lo * (1 - w) + hi * w) * env(len(t), 0.004, 0.18)


def pad_chord(freqs, d):
    t = t_axis(d)
    s = np.zeros(len(t))
    for f in freqs:
        for det in (-0.006, 0, 0.007):
            s += saw(f * (1 + det), t + rng.random())
    s = filt(s, "lowpass", 1400)
    a = np.clip(t / 0.35, 0, 1) * np.clip((d - t) / 0.3, 0, 1)
    return s * a / (len(freqs) * 3)


def pluck(freq, d=0.35):
    t = t_axis(d)
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) + 0.15 * np.sign(np.sin(2 * np.pi * freq * t))
    return filt(s, "lowpass", 3500) * env(len(t), 0.002, 0.11)


def whoosh(d=0.5, f0=300, f1=5000, peak=0.7):
    n = int(SR * d)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    s = sweep_bp(noise, f0, f1, q=1.4)
    e = np.where(t < d * peak, (t / (d * peak)) ** 2, np.exp(-(t - d * peak) / (d * 0.12)))
    return s * e * 0.9


def riser(d):
    n = int(SR * d)
    t = np.arange(n) / SR
    s = sweep_bp(rng.normal(0, 1, n), 200, 9000, q=3.0)
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 880, n)) / SR) * 0.25
    return (s + tone) * (t / d) ** 2.2


def impact(big=1.0):
    t = t_axis(2.5)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t / 0.08)) / SR) * np.exp(-t / (0.5 + 0.5 * big))
    nz = filt(rng.normal(0, 1, len(t)), "lowpass", 2500) * np.exp(-t / 0.18)
    return np.tanh((sub * 1.3 + nz * 0.5 * big) * 1.4)


def pop(freq=900):
    t = t_axis(0.09)
    f = freq * (1 + 1.2 * np.exp(-t / 0.008))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.025)


def tick(freq=2600):
    t = t_axis(0.03)
    return np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.006)


def thud():
    t = t_axis(0.4)
    s = np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.12)
    return s + filt(rng.normal(0, 1, len(t)), "lowpass", 900) * np.exp(-t / 0.04) * 0.6


def slash():
    n = int(SR * 0.22)
    t = np.arange(n) / SR
    s = sweep_bp(rng.normal(0, 1, n), 9000, 900, q=2.5)
    return s * np.exp(-t / 0.07) * np.clip(t / 0.005, 0, 1) * 1.4


def glitch(d=0.45):
    t = t_axis(d)
    s = np.zeros(len(t))
    seg = int(SR * 0.03)
    for k in range(0, len(t), seg):
        f = rng.choice([110, 220, 330, 440, 880, 1760, 147])
        tt = t[k:k + seg]
        s[k:k + seg] = np.sign(np.sin(2 * np.pi * f * tt)) * (0.4 + 0.6 * rng.random())
    s = np.round(s * 6) / 6
    return filt(s, "bandpass", [200, 5000]) * 0.45 * np.clip((d - t) / 0.05, 0, 1)


def chime(base=880):
    t = t_axis(2.2)
    s = sum(a * np.sin(2 * np.pi * base * m * t) * np.exp(-t / dd) for m, a, dd in ((1, 1, .9), (2.01, .5, .5), (3.0, .25, .3), (4.2, .12, .2)))
    return s * np.clip(t / 0.003, 0, 1) * 0.5


def ir(d=1.8):
    t = t_axis(d)
    n = rng.normal(0, 1, len(t)) * np.exp(-t / 0.45)
    return filt(n, "lowpass", 5000) * 0.03


# ---------------------------------------------------------------- music
# Am - F - C - G, one chord per 2 s bar
CHORDS = [
    (55.00, [220.00, 261.63, 329.63]),  # Am
    (43.65, [174.61, 220.00, 261.63]),  # F
    (65.41, [196.00, 261.63, 329.63]),  # C
    (49.00, [196.00, 246.94, 293.66]),  # G
]


def chord_at(t):
    return CHORDS[int(t // 2) % 4]


# pad: whole track, ducked by kicks
for bar in range(12):
    root, tri = chord_at(bar * 2)
    g = 0.22 if bar * 2 < 2.5 else 0.16
    if bar * 2 >= 20:
        g = 0.26
    add(pad_chord(tri, 2.05), bar * 2, g, rev=0.4)

DRUMS = (2.5, 19.5)
for k in range(int(DUR / BEAT)):
    b = k * BEAT
    if DRUMS[0] <= b < DRUMS[1]:
        add(kick(), b, 0.95)
        i = int(b * SR)
        DUCK[i:i + int(0.25 * SR)] = np.minimum(DUCK[i:i + int(0.25 * SR)], 0.35 + 0.65 * np.linspace(0, 1, int(0.25 * SR)) ** 0.6)
        beat_in_bar = k % 4
        if beat_in_bar in (1, 3):
            add(clap(), b, 0.55, rev=0.25)
        add(hat(), b + BEAT / 2, 0.22, pan=0.3)
        if b >= 9.0:
            add(hat(0.02), b + BEAT / 4, 0.1, pan=-0.3)
            add(hat(0.02), b + 3 * BEAT / 4, 0.1, pan=-0.3)
    # bass eighths
    for half in (0, BEAT / 2):
        tb = b + half
        if DRUMS[0] <= tb < DRUMS[1]:
            root, _ = chord_at(tb)
            mult = 2 if half else 1
            add(bass_note(root * mult, 0.24), tb, 0.42)

# arpeggio from the phone scene on, and in the outro
for k in range(int(9.0 / 0.25), int(23.0 / 0.25)):
    tb = k * 0.25
    if 19.5 <= tb < 20.0:
        continue
    _, tri = chord_at(tb)
    seq = [tri[0] * 2, tri[1] * 2, tri[2] * 2, tri[1] * 2]
    g = 0.11 if tb < 20 else 0.15
    add(pluck(seq[k % 4]), tb, g, pan=0.35 * (1 if k % 2 else -1), rev=0.5)

# ---------------------------------------------------------------- sound design cues
add(riser(2.0), 0.5, 0.35, rev=0.3)                 # build-up into the first drop
add(whoosh(1.0, 400, 6000, .8), 0.45, 0.25)         # the mark draws itself
add(tick(1800), 1.5, 0.35)                          # subtitle appears
add(impact(1.0), 2.5, 0.9, rev=0.5)                 # drop: "Ton commerce mérite mieux."
for i, f in enumerate((700, 800, 900, 1200)):       # one pop per word
    add(pop(f), 2.5 + i * 0.25, 0.45)
add(whoosh(0.35, 800, 7000, .6), 3.5, 0.3, pan=-0.4)  # amber underline
add(whoosh(0.5, 6000, 500, .7), 4.65, 0.45)         # words leave
add(pop(650), 5.5, 0.45); add(pop(900), 5.75, 0.45)  # "Pas un site / comme ça."
add(thud(), 6.0, 0.7)                               # old website lands
add(glitch(), 7.0, 0.55)                            # it shakes
add(slash(), 7.5, 0.6, pan=-0.3, rev=0.2)           # X, first stroke
add(slash(), 7.75, 0.6, pan=0.3, rev=0.2)           # X, second stroke
add(whoosh(0.6, 3000, 200, .5), 8.4, 0.5)           # it falls away
add(impact(0.6), 9.0, 0.6, rev=0.4)                 # "Plutôt ça."
add(whoosh(0.6, 200, 4000, .85), 8.55, 0.4)         # phone rises
for at, pan in ((10.5, -0.6), (11.0, 0.6), (11.5, -0.6)):  # feature tags pop on their side
    add(pop(1300), at, 0.5, pan=pan, rev=0.2)
add(whoosh(0.5, 5000, 400, .7), 13.2, 0.4)          # phone leaves
add(pop(800), 14.0, 0.45); add(pop(1000), 14.25, 0.4)
for k in range(13):                                 # 1 -> 14 jours counter
    add(tick(2200 + k * 60), 14.25 + k * 0.05, 0.3)
add(pop(800), 15.0, 0.45); add(pop(1000), 15.25, 0.4)
prev = 0
for i in range(int(0.75 * SR / 200)):               # 0 -> 400 € counter, one tick per 25 €
    x = i * 200 / SR / 0.75
    v = int((1 - (1 - x) ** 4) * 400) // 25
    if v != prev:
        add(tick(2000 + v * 50), 15.25 + i * 200 / SR, 0.28)
        prev = v
add(chime(1318.5), 16.0, 0.35, rev=0.5)             # 400 € lands
add(whoosh(0.5, 6000, 500, .7), 16.15, 0.4)         # numbers leave
add(pop(700), 17.0, 0.45); add(pop(950), 17.25, 0.4)
for i in range(3):                                  # three offer rows slide in from the right
    add(whoosh(0.3, 900, 5000, .7), 17.5 + i * 0.5 - 0.21, 0.3, pan=0.5)
add(riser(1.0), 19.0, 0.4)                          # break before the logo
add(impact(1.3), 20.0, 1.0, rev=0.8)                # logo
add(whoosh(1.0, 300, 4000, .9), 20.0, 0.2)          # mark draws itself
for i in range(6):                                  # N E X O R A
    add(tick(1500 + i * 180), 20.5 + i * 0.125, 0.35, pan=-0.5 + i * 0.2)
add(whoosh(0.4, 600, 3000, .6), 21.3, 0.2)          # tagline
add(chime(880), 22.0, 0.45, rev=0.6)                # call to action
add(tick(3200), 23.0, 0.3, rev=0.4)                 # amber dot on the ridge

# ---------------------------------------------------------------- mix
L *= 1.0; R *= 1.0
# sidechain only the musical bed would need separate buses; a light global duck is enough here
duck = DUCK ** 0.35
L *= duck; R *= duck
rv = ir()
L += fftconvolve(REV_L, rv)[:N]
R += fftconvolve(REV_R, rv)[:N]
fade = np.ones(N)
fo = int(1.0 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix = np.stack([L, R], axis=1) * fade[:, None]
mix = filt(mix.T, "highpass", 28).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6)
mix = mix / np.max(np.abs(mix)) * 0.89

out = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
import wave
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", out)
