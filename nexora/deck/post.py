"""Adds Morph transitions, auto-playing looped videos and automatic entrance animations to the deck.

Usage: python3 post.py nexora-presentation.pptx anim-plan.json
Reads the per-slide plan written by build.js ([objectName, effect, delayMs]) and writes <p:transition>
and <p:timing> into each slide. Effects ending in "With" start with the previous one; the others
start after it.
"""
import json
import re
import shutil
import sys
import tempfile
import zipfile

DECK, PLAN = sys.argv[1], sys.argv[2]
plan = json.load(open(PLAN))

MORPH = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
    '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
    '<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="1400">'
    '<p159:morph option="byObject"/></p:transition></mc:Choice>'
    '<mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>'
)

DUR = 650  # ms per entrance effect


class Ids:
    def __init__(self):
        self.n = 2

    def __call__(self):
        self.n += 1
        return self.n


def set_visible(nid, spid):
    return (f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>')


def fade(nid, spid, dur=DUR):
    return (f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')


def anim(nid, spid, attr, frames, dur=DUR, decel=True):
    tavs = "".join(f'<p:tav tm="{tm}"><p:val><p:strVal val="{v}"/></p:val></p:tav>' for tm, v in frames)
    acc = ' decel="100000"' if decel else ""
    return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{nid()}" dur="{dur}" fill="hold"{acc}/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:tavLst>{tavs}</p:tavLst></p:anim>')


def rotate(nid, spid, by=-360, dur=DUR):
    return (f'<p:animRot by="{by * 60000}"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}" fill="hold" decel="100000"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')


def behaviours(kind, nid, spid):
    k = kind.replace("With", "")
    out = [set_visible(nid, spid), fade(nid, spid)]
    if k == "fadeUp":
        out.append(anim(nid, spid, "ppt_y", [(0, "#ppt_y+0.05"), (100000, "#ppt_y")]))
    elif k == "fadeDown":
        out.append(anim(nid, spid, "ppt_y", [(0, "#ppt_y-0.04"), (100000, "#ppt_y")]))
    elif k == "fadeLeft":
        out.append(anim(nid, spid, "ppt_x", [(0, "#ppt_x-0.04"), (100000, "#ppt_x")]))
    elif k == "riseUp":
        out.append(anim(nid, spid, "ppt_y", [(0, "#ppt_y+0.18"), (100000, "#ppt_y")], dur=900))
    elif k in ("zoom", "spin"):
        out.append(anim(nid, spid, "ppt_w", [(0, "#ppt_w*0.6"), (100000, "#ppt_w")]))
        out.append(anim(nid, spid, "ppt_h", [(0, "#ppt_h*0.6"), (100000, "#ppt_h")]))
        if k == "spin":
            out.append(rotate(nid, spid))
    elif k == "pop":
        out.append(anim(nid, spid, "ppt_w", [(0, "#ppt_w*0.4"), (70000, "#ppt_w*1.08"), (100000, "#ppt_w")], dur=550, decel=False))
        out.append(anim(nid, spid, "ppt_h", [(0, "#ppt_h*0.4"), (70000, "#ppt_h*1.08"), (100000, "#ppt_h")], dur=550, decel=False))
    return "".join(out)


PRESET = {"fade": 10, "fadeUp": 42, "fadeDown": 47, "fadeLeft": 47, "riseUp": 42, "zoom": 53, "spin": 53, "pop": 53}


def timing(spids, entries, video_id):
    nid = Ids()
    groups, t = [], 0
    for name, kind, delay in entries:
        spid = spids.get(name)
        if spid is None:
            raise SystemExit(f"unknown object {name!r}")
        with_prev = kind.endswith("With")
        if not with_prev or not groups:
            start = t if groups else 0
            groups.append({"start": start, "items": []})
        g = groups[-1]
        g["items"].append((spid, kind, delay, "withEffect" if with_prev or len(g["items"]) else "afterEffect"))
        t = max(t, g["start"] + delay + DUR + (250 if kind.startswith("riseUp") else 0))
    built = []
    for gi, g in enumerate(groups):
        items = []
        if gi == 0 and video_id:
            items.append(f'<p:par><p:cTn id="{nid()}" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="withEffect">'
                         f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:cmd type="call" cmd="playFrom(0.0)">'
                         f'<p:cBhvr><p:cTn id="{nid()}" dur="4000" fill="hold"/><p:tgtEl><p:spTgt spid="{video_id}"/></p:tgtEl></p:cBhvr>'
                         f'</p:cmd></p:childTnLst></p:cTn></p:par>')
        for spid, kind, delay, node in g["items"]:
            base = kind.replace("With", "")
            cid = nid()
            items.append(f'<p:par><p:cTn id="{cid}" presetID="{PRESET[base]}" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="{node}">'
                         f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>{behaviours(kind, nid, spid)}</p:childTnLst></p:cTn></p:par>')
        built.append(f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="{g["start"]}"/></p:stCondLst>'
                     f'<p:childTnLst>{"".join(items)}</p:childTnLst></p:cTn></p:par>')
    click = (f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
             f'<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>{"".join(built)}</p:childTnLst></p:cTn></p:par>')
    seq = (f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{click}</p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>')
    media = ""
    if video_id:
        media = (f'<p:video><p:cMediaNode vol="80000" mute="1"><p:cTn id="{nid()}" repeatCount="indefinite" fill="hold" display="0">'
                 f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{video_id}"/></p:tgtEl></p:cMediaNode></p:video>')
    bld = "".join(f'<p:bldP spid="{spid}" grpId="0" animBg="1"/>' for spid in sorted({i[0] for g in groups for i in g["items"]}, key=int) if spid in SP_IDS)
    return (f'<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>{seq}{media}'
            f'</p:childTnLst></p:cTn></p:par></p:tnLst>{"<p:bldLst>" + bld + "</p:bldLst>" if bld else ""}</p:timing>')


tmp = tempfile.mkdtemp()
with zipfile.ZipFile(DECK) as z:
    z.extractall(tmp)
    names = z.namelist()

for i, sp in enumerate(plan, start=1):
    p = f"{tmp}/ppt/slides/slide{i}.xml"
    xml = open(p, encoding="utf-8").read()
    xml = re.sub(r"<p:transition.*?</p:transition>|<p:transition[^>]*/>|<p:timing>.*?</p:timing>", "", xml, flags=re.S)
    spids = {}
    SP_IDS = set()
    for m in re.finditer(r'<p:(sp|pic)>\s*<p:nv(?:Sp|Pic)Pr>\s*<p:cNvPr id="(\d+)" name="([^"]*)"', xml):
        kind, sid, name = m.groups()
        name = name.replace("&apos;", "'").replace("&amp;", "&")
        spids.setdefault(name, sid)
        if kind == "sp":
            SP_IDS.add(sid)
    tm = re.search(r'<p:cNvPr id="(\d+)" name="[^"]*"[^>]*>(?:(?!</p:nvSpPr>).)*<p:ph[^>]*type="title"', xml, flags=re.S)
    if tm and "Titre" not in spids:
        spids["Titre"] = tm.group(1)
        SP_IDS.add(tm.group(1))
    vm = re.search(r'<p:cNvPr id="(\d+)" name="Clip 3D">', xml)
    video_id = vm.group(1) if (vm and sp["video"]) else None
    extra = MORPH + timing(spids, sp["anims"], video_id)
    xml = xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + extra, 1)
    open(p, "w", encoding="utf-8").write(xml)

out = DECK + ".tmp"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.write(f"{tmp}/{n}", n, compress_type=zipfile.ZIP_STORED if n.endswith(".mp4") else zipfile.ZIP_DEFLATED)
shutil.move(out, DECK)
shutil.rmtree(tmp)
print("post-processed", len(plan), "slides")
