#!/usr/bin/env python3
"""给 PPTX 写入展台循环：每页自动换页 + 放映循环，F5 即无人值守。

用法:
  python3 set_loop.py deck.pptx --seconds 8 --fade -o deck_loop.pptx
  python3 set_loop.py deck.pptx --seconds 8 --first 10 --last 12   # 首尾页更长
  python3 set_loop.py deck.pptx --seconds 8 --no-loop               # 只写换页，不循环

原理:
  p:sld/p:transition@advTm="8000"        自动换页（毫秒）
  p:sld/p:transition/p:fade              0.4s 淡入（可选）
  p:presentationPr/p:showPr@loop="1"     循环放映（写入 presProps.xml）
兼容 PowerPoint 2016+ / WPS；不修改任何内容与版式。
"""
import argparse
import io
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def set_transition(slide, ms, fade):
    sld = slide._element
    old = sld.find(qn("p:transition"))
    if old is not None:
        sld.remove(old)
    tr = etree.Element(qn("p:transition"))
    tr.set("spd", "med")
    tr.set("advTm", str(int(ms)))
    if fade:
        etree.SubElement(tr, qn("p:fade"))
    # schema 顺序: cSld, clrMapOvr, transition, timing, extLst
    anchor = sld.find(qn("p:timing"))
    if anchor is None:
        anchor = sld.find(qn("p:extLst"))
    if anchor is not None:
        anchor.addprevious(tr)
    else:
        sld.append(tr)


def set_show_loop(path, loop):
    """在 ppt/presProps.xml 写入 <p:showPr loop="1" show="1" useTimings="1"/>。"""
    tmp = path + ".tmp"
    found = False
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "ppt/presProps.xml":
                found = True
                root = etree.fromstring(data)
                old = root.find(qn("p:showPr"))
                if old is not None:
                    root.remove(old)
                show = etree.Element(qn("p:showPr"))
                show.set("loop", "1" if loop else "0")
                show.set("show", "1")
                show.set("useTimings", "1")
                root.insert(0, show)
                data = etree.tostring(root, xml_declaration=True,
                                      encoding="UTF-8", standalone=True)
            zout.writestr(item, data)
    os.replace(tmp, path)
    return found


def verify(path):
    with zipfile.ZipFile(path) as z:
        loop = None
        if "ppt/presProps.xml" in z.namelist():
            root = etree.fromstring(z.read("ppt/presProps.xml"))
            show = root.find(f"{{{P_NS}}}showPr")
            loop = show.get("loop") if show is not None else None
        slides = sorted((n for n in z.namelist()
                         if n.startswith("ppt/slides/slide") and n.endswith(".xml")),
                        key=lambda n: int(n[len("ppt/slides/slide"):-len(".xml")]))
        adv = []
        for n in slides:
            root = etree.fromstring(z.read(n))
            tr = root.find(f"{{{P_NS}}}transition")
            adv.append(tr.get("advTm") if tr is not None else None)
    return loop, adv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--seconds", type=float, default=8)
    ap.add_argument("--first", type=float, default=None)
    ap.add_argument("--last", type=float, default=None)
    ap.add_argument("--fade", action="store_true", help="0.4s 淡入转场")
    ap.add_argument("--no-loop", action="store_true")
    args = ap.parse_args()

    prs = Presentation(args.pptx)
    n = len(prs.slides)
    if n == 0:
        raise SystemExit("deck 没有幻灯片")
    for i, slide in enumerate(prs.slides):
        sec = args.seconds
        if i == 0 and args.first is not None:
            sec = args.first
        if i == n - 1 and args.last is not None:
            sec = args.last
        set_transition(slide, sec * 1000, args.fade)

    out = args.out or str(Path(args.pptx).with_name(Path(args.pptx).stem + "_loop.pptx"))
    if Path(out).resolve() == Path(args.pptx).resolve():
        fd, tmp = tempfile.mkstemp(suffix=".pptx")
        os.close(fd)
        prs.save(tmp)
        shutil.move(tmp, out)
    else:
        prs.save(out)

    found = set_show_loop(out, loop=not args.no_loop)
    loop, adv = verify(out)
    print(f"saved: {out}")
    print(f"slides: {n}  loop={loop}  advance_ms={adv}")
    if not found:
        print("WARN: 未找到 ppt/presProps.xml，循环放映未写入；请在 PowerPoint 中用"
              "「幻灯片放映 → 设置放映方式 → 循环放映」手动开启。")


if __name__ == "__main__":
    main()
