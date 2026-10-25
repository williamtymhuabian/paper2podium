#!/usr/bin/env python3
"""从学术论文 PDF 精准提取插图（框架图 / 流程图 / 实验曲线 / 表格）。

算法（caption 锚定，参考 pdffigures2, Clark & Divvala AAAI 2015）：
  1. 逐页定位 caption 行（"Figure 1:" / "图 1" / "Table 2" 等行首模式）
  2. 估计栏边界（单栏 / 双栏）；图 caption 在图下方 → 向上扩张，表 caption 在表上方 → 向下扩张
  3. 用"图形证据"修正区域：嵌入光栅图 bbox（get_image_info）
     + 矢量绘图聚类 bbox（cluster_drawings）——框架图几乎都是矢量，必须按 bbox 整块渲染
  4. 过滤 logo / 分隔线 / 页眉页脚 / 整页背景
  5. 高 DPI clip 渲染输出 PNG（矢量图唯一正确的提取方式）；
     单一干净光栅图尝试直接抽取原生位图（分辨率最高）

三种用法：
  自动提取:  python3 extract_figures.py paper.pdf -o figures/ [--dpi 450] [--pages 1-10]
  整页预览:  python3 extract_figures.py paper.pdf -o figures/ --render-page 3 [--render-page 5 ...]
             （供肉眼核对版面，配合 --crop 精确提取）
  手动精裁:  python3 extract_figures.py paper.pdf -o figures/ --crop 3,100,200,500,600
             （页面号,x0,y0,x1,y1，PDF 坐标 pt，原点左上）

输出: figures/*.png + figures/manifest.json（含页码、标签、caption、类型、置信度）
依赖: pip install pymupdf
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf  # 兼容旧安装名
    except ImportError:
        sys.exit("缺少 PyMuPDF，请先运行: pip install pymupdf")

CAP_RE = re.compile(
    r"^(Figure|Fig\.?|FIGURE|Scheme|图|表|Table|TABLE)\s*\.?\s*(\d+|[IVXLCDM]+)\s*([:.：.、)]+)?\s*(.*)"
)
HEADER_BAND, FOOTER_BAND = 55.0, 50.0  # pt，页眉/页脚带高度


def iter_lines(page):
    """产出 (bbox, text, size, flags, font)。flags: 2=italic 16=bold。"""
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            spans = [s for s in l["spans"] if s["text"].strip()]
            if not spans:
                continue
            txt = "".join(s["text"] for s in spans).strip()
            if txt:
                yield (pymupdf.Rect(l["bbox"]), txt,
                       spans[0]["size"], spans[0]["flags"], spans[0]["font"])


def body_font_size(page):
    """正文字号 ≈ 全页按字符数加权的字号众数（图内小字/页眉被自然稀释）。"""
    cnt = Counter()
    for _, txt, size, _, _ in iter_lines(page):
        cnt[round(size, 1)] += len(txt)
    return cnt.most_common(1)[0][0] if cnt else 10.0


def find_captions(page):
    """打分式 caption 识别。正文行首引用（"Figure 3 shows..."）靠标点/字号/加粗特征排除。"""
    body = body_font_size(page)
    out = []
    for bbox, txt, size, flags, font in iter_lines(page):
        if bbox.y0 < HEADER_BAND:  # 页眉里的 "Figure" 不算
            continue
        m = CAP_RE.match(txt)
        if not m:
            continue
        kw, num, punct, tail = m.groups()
        score = 0
        if punct:
            score += 2
        if size < body - 0.3:  # caption 常比正文小一档
            score += 1
        if flags & 18 or "Bold" in font:  # bold / italic
            score += 1
        if tail and (tail[0].isupper() or "\u4e00" <= tail[0] <= "\u9fff"):
            score += 1
        if score < 2:
            continue  # 大概率是正文引用
        out.append({
            "label": f"{kw.rstrip('.')} {num}",
            "kind": "table" if kw in ("表", "Table", "TABLE") else "figure",
            "bbox": bbox, "score": score, "caption": txt,
        })
    return out


def column_bounds(page):
    """按正文行 x0 聚类估计栏边界：返回 [(x0, x1), ...]。"""
    W = page.rect.width
    xs = [round(w[0]) for w in page.get_text("words")
          if HEADER_BAND < w[1] < page.rect.height - FOOTER_BAND]
    cnt = Counter(xs)
    starts = sorted(x for x, c in cnt.items() if c >= 3)
    if not starts:
        return [(0.0, W)]
    groups = [[starts[0]]]
    for x in starts[1:]:
        if x - groups[-1][-1] <= 14:
            groups[-1].append(x)
        else:
            groups.append([x])
    centers = [sum(g) / len(g) for g in groups]
    right = min(max(w[2] for w in page.get_text("words")), W) if xs else W
    left = min(centers)
    if len(centers) >= 2 and any(c < W * 0.45 for c in centers) and any(c > W * 0.55 for c in centers):
        mid = (max(c for c in centers if c < W * 0.45)
               + min(c for c in centers if c > W * 0.55)) / 2
        return [(left - 4, mid - 6), (mid + 6, right + 4)]
    return [(left - 4, right + 4)]


def body_lines(page, col):
    """与栏相交、近似正文字号、宽度 ≥ 60% 栏宽的行 → 图/表区域的边界。"""
    body = body_font_size(page)
    x0, x1 = col
    return [b for b, _, size, _, _ in iter_lines(page)
            if size >= body - 0.6
            and b.x0 >= x0 - 8  # 行必须起于本栏内（防另一栏溢出行干扰边界）
            and b.x0 < x1 and b.x1 > x0
            and (b.x1 - b.x0) >= 0.6 * (x1 - x0)]


def expand_region(page, cap, col):
    """caption → 候选图/表区域。图: caption 上方向上；表: caption 下方向下。"""
    x0, x1 = col
    span_caption = cap["bbox"].x0 < W_HALF(page) and cap["bbox"].x1 > W_HALF(page)
    if span_caption:  # 跨栏 caption 对应跨栏图
        x0, x1 = column_bounds(page)[0]
    if cap["kind"] == "figure":
        top = HEADER_BAND
        above = [b for b in body_lines(page, (x0, x1)) if b.y1 <= cap["bbox"].y0 + 1]
        if above:
            top = max(b.y1 for b in above) + 3
        return pymupdf.Rect(x0, top, x1, cap["bbox"].y0 - 2)
    bottom = page.rect.height - FOOTER_BAND
    below = [b for b in body_lines(page, (x0, x1)) if b.y0 >= cap["bbox"].y1 - 1]
    if below:
        bottom = min(b.y0 for b in below) - 3
    return pymupdf.Rect(x0, cap["bbox"].y1 + 2, x1, bottom)


def W_HALF(page):
    return page.rect.width / 2


def graphic_rects(page, region):
    """区域内的图形证据：嵌入光栅图 bbox + 矢量聚类 bbox。"""
    rects = []
    for info in page.get_image_info():
        r = pymupdf.Rect(info["bbox"])
        if r.intersects(region) and r.width > 8 and r.height > 8:
            rects.append(("raster", r, info))
    try:
        for r in page.cluster_drawings():
            r = pymupdf.Rect(r)
            if r.intersects(region) and r.width > 8 and r.height > 8:
                rects.append(("vector", r, None))
    except Exception:
        pass  # 旧版 PyMuPDF 无此 API，只靠光栅 + 区域扩张
    # cluster_drawings 的 final_filter 会丢弃细规线 → 表格证据从原始 path 补捞
    # 注意 Rect.intersects() 对零高度退化矩形（水平线）返回 False，必须用区间重叠判断
    def _overlap(r, reg):
        return r.x0 < reg.x1 and r.x1 > reg.x0 and r.y0 < reg.y1 and r.y1 > reg.y0
    try:
        for p in page.get_drawings():
            r = pymupdf.Rect(p["rect"])
            if (_overlap(r, region) and r.width > 60 and 0 <= r.height <= 8
                    and r.y0 > HEADER_BAND and r.y1 < page.rect.height - FOOTER_BAND):
                # 零高度矩形 is_empty=True，做并集时会被忽略 → 垫高 2pt
                r = pymupdf.Rect(r.x0, r.y0, r.x1, max(r.y1, r.y0 + 2))
                rects.append(("vector", r, None))
    except Exception:
        pass
    return rects


def acceptable(r, page, min_size):
    return (r.width >= min_size and r.height >= min_size
            and r.get_area() >= min_size * min_size
            and not (r.width > page.rect.width * 0.98
                     and r.height > page.rect.height * 0.9))  # 整页背景


def try_native_image(doc, page, raster_entries, region):
    """区域内恰一张干净光栅图且覆盖 70% 以上 → 抽原生位图（含 smask 透明通道）。"""
    if len(raster_entries) != 1:
        return None
    r = raster_entries[0][1]
    if r.get_area() < 0.7 * max(region.get_area(), 1):
        return None
    try:
        info = page.get_image_info(xrefs=True)
        xref = next((i["xref"] for i in info
                     if pymupdf.Rect(i["bbox"]).intersects(r) and i.get("xref", 0) > 0), 0)
        if not xref:
            return None
        img = doc.extract_image(xref)
        pix = pymupdf.Pixmap(img["image"]) if img["ext"] != "jpg" else pymupdf.Pixmap(
            "jpg", img["image"])
        if img.get("smask", 0):
            mask = doc.extract_image(img["smask"])
            pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(mask["image"]))
        if pix.n > 4:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        return pix
    except Exception:
        return None


def sanitize(s):
    return re.sub(r"[^\w\u4e00-\u9fff-]+", "_", s).strip("_")[:40]


def save_page_crop(doc, pno, rect, out, dpi):
    page = doc[pno]
    rect = pymupdf.Rect(rect) & page.rect
    pix = page.get_pixmap(clip=rect, dpi=dpi)
    pix.save(out)
    return pix.width, pix.height


def auto_extract(doc, args, outdir):
    manifest = []
    for pno in resolve_pages(doc, args.pages):
        page = doc[pno]
        for cap in find_captions(page):
            region = expand_region(page, cap, pick_col(page, cap["bbox"]))
            evidence = graphic_rects(page, region)
            raster_entries = [e for e in evidence if e[0] == "raster"]
            if evidence:
                # 图形证据取并集，但仍约束在扩张区域内（区域是列边界内的上限）
                u = evidence[0][1]
                for _, r, _ in evidence[1:]:
                    u |= r
                u = u & pymupdf.Rect(max(region.x0 - 4, 0), max(region.y0 - 4, 0),
                                     min(region.x1 + 4, page.rect.width),
                                     min(region.y1 + 4, page.rect.height))
                bbox = (u + (-4, -4, 4, 4)) & page.rect
                conf = "high"
            else:
                bbox = region & page.rect  # 无图形证据：保底输出扩张区域
                conf = "low"
            if not acceptable(bbox, page, args.min_size):
                continue
            name = f"p{pno + 1:02d}_{sanitize(cap['label'])}.png"
            out = os.path.join(outdir, name)
            pix = try_native_image(doc, page, raster_entries, bbox)
            src = "native"
            if pix is not None and pix.width * pix.height > 640 * 640:
                if pix.n - pix.alpha > 3:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                pix.save(out)
                w, h = pix.width, pix.height
            else:
                w, h = save_page_crop(doc, pno, bbox, out, args.dpi)
                src = "render"
            manifest.append({
                "file": name, "page": pno + 1, "label": cap["label"],
                "kind": cap["kind"], "type": src, "confidence": conf,
                "caption": cap["caption"][:180],
                "bbox": [round(v, 1) for v in bbox], "w_px": w, "h_px": h,
            })
            print(f"[p{pno + 1}] {cap['label']} ({cap['kind']}/{src}/{conf}) "
                  f"{w}x{h}px -> {name}")
    return manifest


def pick_col(page, bbox):
    cols = column_bounds(page)
    for c in cols:
        if bbox.x0 >= c[0] - 6 and bbox.x0 <= c[1]:
            return c
    return cols[0]


def resolve_pages(doc, spec):
    n = doc.page_count
    if not spec:
        return range(n)
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += [p for p in range(int(a) - 1, min(int(b), n))]
        else:
            p = int(part) - 1
            if 0 <= p < n:
                out.append(p)
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out", default="figures")
    ap.add_argument("--dpi", type=int, default=450,
                    help="渲染 DPI（答辩投影建议 450+）")
    ap.add_argument("--pages", default="", help="页码范围，如 1-8,12")
    ap.add_argument("--min-size", type=float, default=36.0,
                    help="图最小边长 pt（过滤 logo）")
    ap.add_argument("--render-page", action="append", default=[], type=int,
                    help="渲染整页低清预览图（可多次）")
    ap.add_argument("--crop", default="",
                    help="手动裁剪: 页码,x0,y0,x1,y1 (pt)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    doc = pymupdf.open(args.pdf)

    for p in args.render_page:
        out = os.path.join(args.out, f"preview_p{p:02d}.png")
        w, h = save_page_crop(doc, p - 1, doc[p - 1].rect, out, 130)
        print(f"preview p{p} -> {out} ({w}x{h})")

    if args.crop:
        pno, x0, y0, x1, y1 = (float(v) for v in args.crop.split(","))
        out = os.path.join(args.out, f"manual_p{int(pno):02d}.png")
        w, h = save_page_crop(doc, int(pno) - 1,
                              pymupdf.Rect(x0, y0, x1, y1), out, args.dpi)
        print(f"manual crop p{int(pno)} -> {out} ({w}x{h})")

    manifest = auto_extract(doc, args, args.out)
    mf = os.path.join(args.out, "manifest.json")
    with open(mf, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"\n{len(manifest)} figures -> {mf}")
    if not manifest:
        print("未发现 caption 锚定的图。用 --render-page 渲染整页看清版面后，"
              "用 --crop 页码,x0,y0,x1,y1 手动精裁。")


if __name__ == "__main__":
    main()
