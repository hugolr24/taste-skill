"""Music bed for the presentation video: 120 BPM groove, a whoosh on each slide change. Usage: python3 soundtrack_deck.py out.wav"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reel"))
import audio_lib as a  # noqa: E402

LENGTHS_MS = [7205, 7705, 9155, 8455, 9805, 9005, 7855, 7855, 9405, 9455, 8355]
frames = [round(l / 1000 * 30) for l in LENGTHS_MS]
starts, t = [], 0
for f in frames:
    starts.append(t / 30)
    t += f
DUR = t / 30
a.init(DUR, seed=77)
a.music(drums=(4.0, DUR - 6.0), arp=(12.0, DUR - 1.0), outro=DUR - 6.0, pad_gain=0.2)
a.add(a.riser(1.5), 0.0, 0.3)
a.add(a.impact(1.0), 0.6, 0.7, rev=0.6)
for s in starts[1:]:
    a.add(a.whoosh(0.7, 300, 5000, .6), s - 0.2, 0.3, pan=-0.3)
    a.add(a.pop(900), s + 0.65, 0.25)
a.add(a.impact(1.2), starts[-1] + 0.3, 0.8, rev=0.8)
a.add(a.chime(880), starts[-1] + 1.6, 0.35, rev=0.6)
a.finish(sys.argv[1] if len(sys.argv) > 1 else "deck.wav", fade_s=3.0)
print("duration", DUR)
