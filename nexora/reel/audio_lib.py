"""Shared synth instruments and mixer for Nexora reels (no samples, no licensing). 120 BPM, 2 s bars."""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
BEAT = 0.5
rng = np.random.default_rng(73)
DUR = N = L = R = REV_L = REV_R = DUCK = None


def init(dur, seed=73):
    global DUR, N, L, R, REV_L, REV_R, DUCK, rng
    DUR = dur
    N = int(SR * dur)
    L, R, REV_L, REV_R = (np.zeros(N) for _ in range(4))
    DUCK = np.ones(N)
    rng = np.random.default_rng(seed)


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


# ---------------------------------------------------------------- music bed
CHORDS = [
    (55.00, [220.00, 261.63, 329.63]),  # Am
    (43.65, [174.61, 220.00, 261.63]),  # F
    (65.41, [196.00, 261.63, 329.63]),  # C
    (49.00, [196.00, 246.94, 293.66]),  # G
]


def chord_at(t, chords=CHORDS):
    return chords[int(t // 2) % len(chords)]


def music(drums, arp=None, breaks=(), outro=None, chords=CHORDS, pad_gain=0.16):
    """drums=(start, end) for kick/clap/hats/bass, arp=(start, end), breaks=[(a, b)] silence for arp."""
    for bar in range(int(np.ceil(DUR / 2))):
        _, tri = chord_at(bar * 2, chords)
        g = pad_gain * (1.4 if bar * 2 + 2 <= drums[0] or (outro and bar * 2 >= outro) else 1)
        add(pad_chord(tri, 2.05), bar * 2, g, rev=0.4)
    for k in range(int(DUR / BEAT)):
        b = k * BEAT
        if drums[0] <= b < drums[1]:
            add(kick(), b, 0.95)
            i = int(b * SR); n = int(0.25 * SR)
            DUCK[i:i + n] = np.minimum(DUCK[i:i + n], 0.35 + 0.65 * np.linspace(0, 1, len(DUCK[i:i + n])) ** 0.6)
            if k % 4 in (1, 3):
                add(clap(), b, 0.55, rev=0.25)
            add(hat(), b + BEAT / 2, 0.22, pan=0.3)
            if arp and b >= arp[0]:
                add(hat(0.02), b + BEAT / 4, 0.1, pan=-0.3)
                add(hat(0.02), b + 3 * BEAT / 4, 0.1, pan=-0.3)
        for half in (0, BEAT / 2):
            tb = b + half
            if drums[0] <= tb < drums[1]:
                root, _ = chord_at(tb, chords)
                add(bass_note(root * (2 if half else 1), 0.24), tb, 0.42)
    if arp:
        for k in range(int(arp[0] / 0.25), int(arp[1] / 0.25)):
            tb = k * 0.25
            if any(a <= tb < b for a, b in breaks):
                continue
            _, tri = chord_at(tb, chords)
            seq = [tri[0] * 2, tri[1] * 2, tri[2] * 2, tri[1] * 2]
            g = 0.15 if outro and tb >= outro else 0.11
            add(pluck(seq[k % 4]), tb, g, pan=0.35 * (1 if k % 2 else -1), rev=0.5)


def finish(out, fade_s=1.0):
    global L, R
    duck = DUCK ** 0.35
    l, r = L * duck, R * duck
    rv = ir()
    l = l + fftconvolve(REV_L, rv)[:N]
    r = r + fftconvolve(REV_R, rv)[:N]
    fade = np.ones(N)
    fo = int(fade_s * SR)
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    mix = np.stack([l, r], axis=1) * fade[:, None]
    mix = filt(mix.T, "highpass", 28).T
    mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6)
    mix = mix / np.max(np.abs(mix)) * 0.89
    import wave
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
