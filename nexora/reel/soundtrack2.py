"""Soundtrack for reel2.html (restaurant before/after, 16 s). Usage: python3 soundtrack2.py out.wav"""
import sys
import audio_lib as a

a.init(16.0, seed=74)
a.music(drums=(0.5, 12.25), arp=(6.0, 15.0), breaks=[(5.5, 6.0)], outro=12.25)
a.add(a.riser(0.5), 0.0, 0.25)
a.add(a.impact(0.7), 0.5, 0.7, rev=0.4)
for i, f in enumerate((700, 800, 900)):            # three title lines
    a.add(a.pop(f), 0.5 + i * 0.25, 0.45)
a.add(a.whoosh(0.5, 6000, 500, .7), 2.6, 0.4)
a.add(a.thud(), 3.25, 0.7)                          # old site lands
for at, pan in ((3.75, -0.6), (4.25, 0.6), (4.75, -0.6)):
    a.add(a.pop(500), at, 0.5, pan=pan)             # red flags, lower pitch
a.add(a.glitch(0.5), 5.0, 0.55)
a.add(a.slash(), 5.0, 0.6, pan=-0.3, rev=0.2)
a.add(a.slash(), 5.25, 0.6, pan=0.3, rev=0.2)
a.add(a.riser(0.5), 5.5, 0.45)
a.add(a.whoosh(0.35, 300, 7000, .85), 5.7, 0.5)     # amber wipe
a.add(a.impact(1.2), 6.0, 1.0, rev=0.7)
a.add(a.pop(800), 6.1, 0.4); a.add(a.pop(1100), 6.35, 0.4)
a.add(a.whoosh(0.6, 200, 4000, .85), 7.05, 0.4)     # phone rises
a.add(a.pop(900), 7.5, 0.4)
for at, pan in ((8.5, -0.6), (9.5, 0.6), (10.5, -0.6)):
    a.add(a.pop(1300), at, 0.5, pan=pan, rev=0.2)
a.add(a.tick(3000), 11.0, 0.45)                     # tap on "Réserver"
a.add(a.chime(1318.5), 11.05, 0.25, rev=0.4)
a.add(a.whoosh(0.5, 5000, 400, .7), 11.6, 0.4)
a.add(a.impact(1.0), 12.25, 0.9, rev=0.8)           # logo
a.add(a.pop(800), 13.0, 0.4); a.add(a.pop(1050), 13.25, 0.4)
a.add(a.chime(880), 14.0, 0.45, rev=0.6)
a.add(a.tick(3200), 14.5, 0.3, rev=0.4)
a.finish(sys.argv[1] if len(sys.argv) > 1 else "soundtrack2.wav")
