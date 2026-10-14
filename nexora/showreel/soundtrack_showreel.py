"""Soundtrack for showreel.html (60 s): music, sound design and French voice-over (Piper TTS).

Usage: python3 soundtrack_showreel.py <voice.onnx> <out.wav>
Voice lines are synthesized with Piper, cleaned up (EQ, compression, no reverb) and placed on
their cue; the music and effects are ducked under the voice.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from scipy.signal import resample_poly

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reel"))
import audio_lib as a  # noqa: E402

VOICE, OUT = sys.argv[1], sys.argv[2]
DUR = 60.0

# (start time, text) — each line starts with its scene
VO = [
    (3.2, "Nexora. Des sites web qui font venir des clients."),
    (8.8, "Ici, en Savoie, les artisans et les commerçants font un travail exceptionnel."),
    (14.6, "Mais leur site, lui, n'est pas toujours à la hauteur."),
    (20.25, "Un site vitrine clair, rapide, pensé pour le téléphone."),
    (25.25, "Une boutique en ligne, pour vendre même le dimanche."),
    (30.25, "Et pour marquer les esprits : du motion design, sur mesure."),
    (35.25, "Ton commerce, trouvé sur Google. Avec un bouton pour t'appeler."),
    (40.25, "En ligne en une à deux semaines. À partir de quatre cents euros."),
    (46.25, "Et ensuite ? Tu demandes. Je modifie."),
    (51.0, "Nexora. Création de sites web à Chambéry et en Savoie. Demande ton devis gratuit, en message."),
]


def tts(text):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    subprocess.run([sys.executable, "-m", "piper", "-m", VOICE, "-f", path, "--length-scale", "0.97"],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(path) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float) / 32768
    os.unlink(path)
    return resample_poly(x, a.SR, sr)


def polish(x):
    x = a.filt(x, "highpass", 90)
    x = x + 0.35 * a.filt(x, "bandpass", [2500, 6000])        # presence
    env = np.sqrt(a.filt(x ** 2, "lowpass", 30).clip(1e-9))   # simple compressor
    gain = np.minimum(1, (0.12 / env) ** 0.5)
    x = x * gain
    return x / np.max(np.abs(x))


# ---------------------------------------------------------------- music + sound design
a.init(DUR, seed=76)
a.music(drums=(8.0, 50.0), arp=(20.0, 58.5), breaks=[(17.5, 18.5), (49.5, 50.5)], outro=50.0,
        drum_gaps=[(17.5, 18.0), (49.5, 50.0)], pad_gain=0.18)

# S1: particles gather into the N
a.add(a.riser(2.3), 0.3, 0.4, rev=0.4)
a.add(a.whoosh(2.0, 200, 6000, .9), 0.6, 0.25)
a.add(a.impact(1.1), 2.6, 0.9, rev=0.7)
a.add(a.chime(880), 2.62, 0.3, rev=0.7)
for i in range(6):
    a.add(a.tick(1400 + i * 160), 3.0 + i * 0.08, 0.3, pan=-0.5 + i * 0.2)
a.add(a.whoosh(1.0, 6000, 300, .5), 6.3, 0.45)            # N bursts into dust
a.add(a.riser(1.2), 6.8, 0.3)
# S2: Savoie
a.add(a.impact(0.7), 8.0, 0.65, rev=0.6)
a.add(a.whoosh(3.0, 300, 2500, .5), 8.4, 0.15, pan=-0.3)   # ridge line draws
for i, f in enumerate((700, 820, 950)):
    a.add(a.pop(f), 8.8 + i * 0.2, 0.4)
a.add(a.whoosh(0.6, 5000, 400, .7), 13.4, 0.35)
# S3: the old website, shake, shatter
a.add(a.whoosh(0.7, 200, 3000, .8), 13.7, 0.35)
a.add(a.thud(), 14.4, 0.6)
a.add(a.pop(650), 14.6, 0.4)
a.add(a.glitch(0.8), 17.2, 0.5)
a.add(a.impact(1.4), 18.0, 1.0, rev=0.8)
glass = a.filt(a.rng.normal(0, 1, int(a.SR * 1.2)), "highpass", 3500) * np.exp(-np.arange(int(a.SR * 1.2)) / a.SR / 0.25)
a.add(glass, 18.0, 0.35, rev=0.5)
a.add(a.slash(), 18.0, 0.5)
a.add(a.pop(500), 18.05, 0.4); a.add(a.pop(420), 18.25, 0.4)
rev_whoosh = a.whoosh(1.0, 400, 5000, .95)
a.add(rev_whoosh, 19.0, 0.4)                                # cubes fly back together
# S4: phone
a.add(a.thud(), 20.0, 0.6); a.add(a.chime(1318.5), 20.02, 0.3, rev=0.5)
for at, pan in ((21.5, -0.6), (22.25, 0.6), (23.0, -0.6)):
    a.add(a.pop(1300), at, 0.45, pan=pan, rev=0.2)
a.add(a.whoosh(0.6, 4000, 500, .6), 24.8, 0.35, pan=-0.5)
# S5: shop
a.add(a.whoosh(0.6, 200, 3000, .8), 24.9, 0.3)
for i, at in enumerate((26.55, 27.05, 27.55, 28.05)):
    a.add(a.thud(), at, 0.45)
    a.add(a.pop(600 + i * 120), at, 0.3)
for at, pan in ((27.0, -0.5), (27.6, 0.5)):
    a.add(a.pop(1400), at, 0.35, pan=pan)
# S6: motion playground
a.add(a.impact(0.9), 30.0, 0.7, rev=0.6)
a.add(a.whoosh(1.5, 300, 7000, .5), 30.0, 0.25, pan=0.4)
a.add(a.whoosh(1.5, 7000, 300, .5), 32.0, 0.2, pan=-0.4)
a.add(a.whoosh(0.5, 5000, 400, .7), 34.8, 0.35)
# S7: Google
a.add(a.whoosh(0.6, 200, 3000, .8), 34.6, 0.3)
q = "boulangerie chambéry"
for i in range(len(q)):
    a.add(a.tick(2600 + (i % 3) * 300), 35.6 + 1.3 * i / len(q), 0.28)
for i in range(3):
    a.add(a.pop(900 + i * 150), 37.0 + i * 0.2, 0.35)
fall = np.sin(2 * np.pi * np.cumsum(np.geomspace(1800, 300, int(a.SR * .5))) / a.SR) * np.linspace(.2, 1, int(a.SR * .5))
a.add(fall, 37.6, 0.18)
a.add(a.thud(), 38.1, 0.6)
for i in range(3):
    a.add(a.chime(660 * (1 + i * .25)), 38.1 + i * 0.25, 0.12, rev=0.5)
a.add(a.pop(1300), 38.3, 0.4, pan=-0.5)
# S8: calendar + coin
a.add(a.whoosh(0.6, 5000, 400, .7), 39.6, 0.3)
for i in range(14):
    a.add(a.tick(1500 + i * 90), 40.6 + i * 0.1, 0.35, pan=-0.6 + i * 0.09)
a.add(a.chime(1760), 42.0, 0.2, rev=0.5)
a.add(a.whoosh(1.6, 500, 6000, .4), 43.0, 0.25)            # coin spins
prev = -1
for i in range(int(1.2 * a.SR / 200)):
    x = i * 200 / a.SR / 1.2
    v = int((1 - (1 - x) ** 4) * 400) // 25
    if v != prev:
        a.add(a.tick(2000 + v * 50), 43.2 + i * 200 / a.SR, 0.25)
        prev = v
a.add(a.chime(1318.5), 44.6, 0.4, rev=0.6); a.add(a.chime(1975.5), 44.7, 0.25, rev=0.6)
a.add(a.whoosh(0.5, 5000, 400, .7), 45.4, 0.35)
# S9: chat
a.add(a.pop(700), 46.2, 0.4); a.add(a.pop(950), 46.4, 0.4)
for at, f in ((46.8, 1100), (47.8, 1500), (48.6, 1100)):
    a.add(a.pop(f), at, 0.45, rev=0.2); a.add(a.pop(f * 1.5), at + 0.07, 0.3, rev=0.2)
# S10: everything gathers back into the N
a.add(a.riser(2.4), 50.0, 0.45, rev=0.4)
a.add(a.whoosh(2.0, 6000, 200, .9), 50.4, 0.25)
a.add(a.impact(1.5), 52.4, 1.0, rev=0.9)
a.add(a.chime(880), 52.42, 0.35, rev=0.8)
for i in range(6):
    a.add(a.tick(1400 + i * 160), 53.0 + i * 0.08, 0.3, pan=-0.5 + i * 0.2)
a.add(a.chime(1318.5), 55.0, 0.35, rev=0.7)
a.add(a.tick(3200), 55.6, 0.3, rev=0.5)

bed = a.mixdown(fade_s=2.0)
bed = bed / np.max(np.abs(bed)) * 0.5

# ---------------------------------------------------------------- voice-over
vo = np.zeros(a.N)
for at, text in VO:
    x = polish(tts(text))
    i = int(at * a.SR)
    vo[i:i + len(x)] += x[: a.N - i]
vo = vo / np.max(np.abs(vo)) * 0.62
env = a.filt(np.abs(vo), "lowpass", 4)
env = np.clip(env / (np.max(env) * 0.25), 0, 1)
bed = bed * (1 - 0.6 * env)[:, None]

mix = bed + np.stack([vo, vo], axis=1)
mix = np.tanh(mix * 1.15)
mix = mix / np.max(np.abs(mix)) * 0.89
a.write(OUT, mix)
print("wrote", OUT, "vo lines:", len(VO))
