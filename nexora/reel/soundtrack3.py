"""Soundtrack for reel3.html (hair salon booking at 23:04, 15 s). Usage: python3 soundtrack3.py out.wav"""
import sys
import audio_lib as a

a.init(15.0, seed=75)
# quiet night intro, beat drops when the phone appears
a.music(drums=(4.75, 12.5), arp=(3.0, 14.5), breaks=[(10.75, 11.0)], outro=12.5, pad_gain=0.2)
for k in range(6):                                  # clock ticking, 2 per second
    a.add(a.tick(1900 if k % 2 else 2300), k * 0.5, 0.45)
a.add(a.chime(1760), 1.5, 0.2, rev=0.6)             # 23:04 -> 23:05
a.add(a.pop(700), 1.0, 0.35)
a.add(a.whoosh(0.5, 6000, 500, .7), 2.5, 0.35)
for i, f in enumerate((700, 850, 1000)):
    a.add(a.pop(f), 3.0 + i * 0.25, 0.45)
a.add(a.riser(1.0), 3.75, 0.4)
a.add(a.whoosh(0.6, 200, 4000, .85), 4.2, 0.4)      # phone rises
a.add(a.impact(0.8), 4.75, 0.8, rev=0.5)
for at in (6.0, 7.0, 8.0, 8.5, 9.5):                # taps
    a.add(a.tick(3200), at, 0.5)
    a.add(a.pop(1400), at, 0.3, rev=0.15)
for at in (6.25, 7.5, 8.75, 10.0):                  # screen slides
    a.add(a.whoosh(0.3, 1200, 6000, .6), at - 0.1, 0.25, pan=-0.4)
a.add(a.chime(1318.5), 10.5, 0.45, rev=0.6)         # booked
a.add(a.chime(1975.5), 10.62, 0.25, rev=0.6)
a.add(a.whoosh(0.5, 5000, 400, .7), 10.6, 0.35)
a.add(a.pop(700), 11.0, 0.45); a.add(a.pop(950), 11.25, 0.45)
a.add(a.impact(1.2), 12.5, 1.0, rev=0.8)            # logo
for i, f in enumerate((750, 900, 1100)):
    a.add(a.pop(f), 13.0 + i * 0.25, 0.4)
a.add(a.chime(880), 13.75, 0.45, rev=0.6)
a.finish(sys.argv[1] if len(sys.argv) > 1 else "soundtrack3.wav")
