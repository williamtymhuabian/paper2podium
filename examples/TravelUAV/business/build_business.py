#!/usr/bin/env python3
"""TravelUAV 商业展出 · 展台循环版（business-ppt skill 示例）。

风格 B 画廊深色：近黑底 + 暖白宋体 + 陶土强调色 + 全幅仿真影像。
10 页 / 约 84 秒循环。数据来自 TravelUAV 预印本（Table 2/3、数据集统计），
不包含客户 logo、市占率等未经证实信息。
"""
import os
import subprocess
import sys

from lxml import etree
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from pptx.oxml.ns import qn

import qrcode

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "..", "figures")
IMG = os.path.join(BASE, "img")
BRAND = os.path.join(BASE, "brand")
OUT = os.path.join(BASE, "TravelUAV_世界无人机大会_展台循环.pptx")

W, H, M = 13.333, 7.5, 0.8

# 风格 B · 画廊深色
BG = RGBColor(0x0E, 0x11, 0x10)
TEXT = RGBColor(0xF4, 0xF1, 0xEA)
MUTED = RGBColor(0xA8, 0xA3, 0x99)
ACCENT = RGBColor(0xC9, 0x6A, 0x3F)
LINE = RGBColor(0x3A, 0x3B, 0x36)
DIM = RGBColor(0x6F, 0x6A, 0x61)
PANEL = RGBColor(0x1A, 0x1D, 0x1B)
PAPER = RGBColor(0xF7, 0xF5, 0xF0)
INK = RGBColor(0x17, 0x19, 0x1C)

SERIF = "Noto Serif CJK SC"
SANS = "Noto Sans CJK SC"
LATIN = "Arial"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
blank = prs.slide_layouts[6]

# ---------------------------------------------------------------- helpers


def _font(run, name):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    latin = rPr.find(qn("a:latin"))
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = etree.SubElement(rPr, qn("a:ea"))
    ea.set("typeface", name)
    cs = rPr.find(qn("a:cs"))
    if cs is None:
        cs = etree.SubElement(rPr, qn("a:cs"))
    cs.set("typeface", name)
    if latin is not None:
        latin.addnext(ea)
        ea.addnext(cs)


def _alpha(shape, opacity):
    srgb = shape.fill.fore_color._xFill.find(qn("a:srgbClr"))
    a = etree.SubElement(srgb, qn("a:alpha"))
    a.set("val", str(int(opacity * 100000)))


def bg(name="content", style="premium"):
    s = prs.slides.add_slide(blank)
    pic(s, os.path.join(BASE, "bg", f"{style}_{name}.png"), 0, 0, W, H)
    return s


def pic(s, path, x, y, w, h, cover=False, border=None, descr=None):
    p = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    if cover:
        iw, ih = Image.open(path).size
        ir, tr = iw / ih, w / h
        if ir > tr:
            f = (1 - tr / ir) / 2
            p.crop_left = p.crop_right = f
        elif ir < tr:
            f = (1 - ir / tr) / 2
            p.crop_top = p.crop_bottom = f
    if border:
        p.line.color.rgb = border
        p.line.width = Pt(0.75)
    if descr:
        p._element.nvPicPr.cNvPr.set("descr", descr)
    return p


def scrim(s, x, y, w, h, color=BG, opacity=0.55):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    _alpha(shp, opacity)
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def rect(s, x, y, w, h, color, line=None):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line:
        shp.line.color.rgb = line
        shp.line.width = Pt(0.75)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def rule(s, x, y, w, color=LINE, weight=0.75):
    shp = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y))
    shp.line.color.rgb = color
    shp.line.width = Pt(weight)
    return shp


def vrule(s, x, y, h, color=LINE, weight=0.75):
    shp = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x), Inches(y + h))
    shp.line.color.rgb = color
    shp.line.width = Pt(weight)
    return shp


def text(s, x, y, w, h, paras, size=16, color=TEXT, font=SANS, bold=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line=1.0, spc=0):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if isinstance(paras, str):
        paras = [[(paras, {})]]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line
        for txt, st in para:
            r = p.add_run()
            r.text = txt
            f = r.font
            _font(r, st.get("font", font))
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.color.rgb = st.get("color", color)
            s2 = st.get("spc", spc)
            if s2:
                r._r.get_or_add_rPr().set("spc", str(int(s2 * 100)))
    return box


def header(s, num, label, page, total=10):
    text(s, M, 0.52, 6.0, 0.3,
         [[(f"{num}  ", {"color": ACCENT}), (label, {"color": MUTED})]],
         size=10.5, font=LATIN, bold=True, spc=2.6)
    text(s, W - M - 2.4, 0.52, 2.4, 0.3, "TRAVELUAV",
         size=9.5, color=MUTED, font=LATIN, bold=True, align=PP_ALIGN.RIGHT, spc=2.6)
    rule(s, M, 1.0, W - 2 * M)
    text(s, W - M - 1.2, 7.02, 1.2, 0.25, f"{page:02d} / {total}",
         size=9, color=MUTED, font=LATIN, align=PP_ALIGN.RIGHT)
    text(s, M, 7.02, 7.0, 0.25, "TRAVELUAV  ·  2026 世界无人机大会  ·  上海",
         size=9, color=MUTED, font=LATIN, spc=1.2)
    rule(s, M, 6.92, W - 2 * M)


def notes(s, txt):
    s.notes_slide.notes_text_frame.text = txt


# ---------------------------------------------------------------- image prep

def prep(src, dst, size, grade=True):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    tw, th = size
    tr = tw / th
    iw, ih = im.size
    if iw / ih > tr:
        nw = int(ih * tr)
        x = (iw - nw) // 2
        im = im.crop((x, 0, x + nw, ih))
    else:
        nh = int(iw / tr)
        y = int((ih - nh) * 0.42)
        im = im.crop((0, y, iw, y + nh))
    im = im.resize((tw, th), Image.LANCZOS)
    if grade:
        im = ImageEnhance.Color(im).enhance(0.88)
        im = ImageEnhance.Contrast(im).enhance(1.08)
        im = ImageEnhance.Brightness(im).enhance(0.98)
        warm = Image.new("RGB", im.size, (255, 238, 218))
        im = Image.blend(im, warm, 0.06)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=3))
    im.save(dst, quality=94, subsampling=1)
    return dst


def assets():
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(BRAND, exist_ok=True)
    jobs = {
        "hero_city.jpg": ("scenes/scene_1.png", (2400, 1350)),
        "hero_aerial.jpg": ("scenes/scene_2.png", (2400, 1350)),
        "problem_canal.jpg": ("scenes/scene_4.png", (1300, 1150)),
        "scene_city.jpg": ("scenes/scene_1.png", (1200, 800)),
        "scene_forest.jpg": ("scenes/scene_5.png", (1200, 800)),
        "scene_disaster.jpg": ("scenes/scene_7.png", (1200, 800)),
    }
    for name, (src, size) in jobs.items():
        prep(os.path.join(SRC, src), os.path.join(IMG, name), size)

    # 底部渐变遮罩：避免整块半透明矩形产生硬边
    def bottom_scrim(path, color=(14, 17, 16), start=0.28, max_alpha=215):
        im = Image.new("RGBA", (2400, 1350), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        for y in range(1350):
            t = max(0.0, (y / 1350 - start) / (1 - start))
            a = int(max_alpha * t ** 1.7)
            dr.line([(0, y), (2400, y)], fill=color + (a,))
        im.save(path)
    bottom_scrim(os.path.join(IMG, "scrim_bottom.png"))

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=18, border=4)
    qr.add_data("https://example.com/traveluav-demo?utm_source=booth&utm_campaign=expo2026")
    qr.make(fit=True)
    qr.make_image(fill_color="#17191C", back_color="#F7F5F0").save(
        os.path.join(BRAND, "qr_demo.png"))


# ---------------------------------------------------------------- pages

def p1_cover():
    s = bg("cover")
    pic(s, os.path.join(IMG, "hero_city.jpg"), 0, 0, W, H, cover=True,
        descr="OpenUAV 仿真城市街区俯瞰")
    scrim(s, 0, 0, W, H, BG, 0.30)
    pic(s, os.path.join(IMG, "scrim_bottom.png"), 0, 0, W, H)

    text(s, M, 0.58, 5.0, 0.3, "TRAVELUAV", size=13, color=TEXT,
         font=LATIN, bold=True, spc=4.5)
    rule(s, M + 1.85, 0.72, 1.1, color=TEXT, weight=0.75)
    text(s, W - M - 3.0, 0.58, 3.0, 0.3, "SHANGHAI  ·  2026", size=10.5,
         color=MUTED, font=LATIN, align=PP_ALIGN.RIGHT, spc=3)

    rule(s, M, 2.42, 0.6, color=ACCENT, weight=2.5)
    text(s, M, 2.62, 6.0, 0.3, "EMBODIED AERIAL NAVIGATION", size=10.5,
         color=ACCENT, font=LATIN, bold=True, spc=3.2)
    text(s, M, 2.98, 8.4, 2.2, [[("让无人机听懂人话，", {})], [("自己找到目标", {})]],
         size=55, color=TEXT, font=SERIF, bold=True, line=1.12)
    text(s, M, 5.18, 8.2, 0.4,
         "面向真实场景的具身导航平台  ·  OpenUAV 仿真  ·  12k 轨迹数据集",
         size=17, color=MUTED, font=SANS)

    rule(s, M, 6.18, 7.5, color=TEXT, weight=0.75)
    text(s, M, 6.32, 4.2, 0.3, "2026 世界无人机大会  ·  上海", size=11,
         color=TEXT, font=SANS)
    text(s, M + 4.4, 6.32, 3.1, 0.3, "展位 B-17  ·  9.2–9.5 馆", size=11,
         color=MUTED, font=SANS)

    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.02),
                              Inches(4.88), Inches(1.5), Inches(1.5))
    card.adjustments[0] = 0.04
    card.fill.solid()
    card.fill.fore_color.rgb = PAPER
    card.line.fill.background()
    card.shadow.inherit = False
    s.shapes.add_picture(os.path.join(BRAND, "qr_demo.png"), Inches(11.13),
                         Inches(4.99), Inches(1.28), Inches(1.28))
    text(s, 10.86, 6.47, 1.85, 0.3, "扫码预约现场演示", size=9.5, color=TEXT,
         font=SANS, align=PP_ALIGN.CENTER)

    notes(s, "【画面字幕】让无人机听懂人话，自己找到目标。\n"
             "【30 秒口播】我们是 TravelUAV，做的是让无人机理解自然语言、在真实场景里自主完成目标搜索。"
             "这套能力建立在 OpenUAV 仿真平台、12k 条真实动力学轨迹和 UAV-Need-Help 评测基准之上。"
             "今天在 B-17 展位有实时演示，扫码可以预约 30 分钟的场景评估。")


def p2_manifesto():
    s = bg()
    header(s, "01", "WHY WE EXIST", 2)
    rule(s, M, 1.72, 0.6, color=ACCENT, weight=2.5)
    text(s, M, 1.95, 11.6, 3.4,
         [[("无人机已经会飞。", {"color": MUTED})],
          [("下一步，是", {}), ("听懂一句话", {"color": ACCENT}), ("，", {})],
          [("自己完成一次搜索。", {})]],
         size=43, color=TEXT, font=SERIF, bold=True, line=1.28)
    rule(s, M, 5.52, W - 2 * M)
    cols = [
        ("自然语言指令", "目标描述与空间关系，直接说给飞机听"),
        ("真实飞行动力学", "6 DoF 连续控制，不是简化后的航点"),
        ("零样本泛化", "换地图、换目标，仍然能起飞去找"),
    ]
    xs = [M, 4.75, 8.7]
    for x, (t, d) in zip(xs, cols):
        text(s, x, 5.78, 3.55, 0.3, t, size=17, color=TEXT, font=SANS, bold=True)
        text(s, x, 6.14, 3.55, 0.5, d, size=12, color=MUTED, font=SANS, line=1.4)
    vrule(s, 4.55, 5.75, 0.95, color=LINE)
    vrule(s, 8.5, 5.75, 0.95, color=LINE)
    notes(s, "【画面字幕】无人机已经会飞，下一步是听懂一句话，自己完成一次搜索。\n"
             "【30 秒口播】过去的无人机自动化，本质还是人把任务拆成航点。我们想往前一步："
             "操作者只说“找什么”，飞机自己理解目标、生成可行轨迹、边飞边确认。三个支点是语言理解、"
             "真实动力学和泛化能力。")


def p3_problem():
    s = bg()
    header(s, "02", "THE GAP", 3)
    text(s, M, 1.28, 6.2, 1.2, [[("换一个场景，", {})], [("飞手要重新教一遍", {})]],
         size=33, color=TEXT, font=SERIF, bold=True, line=1.15)

    items = [
        ("01", "指令仍是坐标", "任务以航点下发，操作者要先把“找什么”翻译成“怎么飞”。"),
        ("02", "仿真不够真", "简化动力学让策略在仿真里成立，一上实机就漂移。"),
        ("03", "换场景就重来", "新地图、新目标、新光照，都要重新采集与标注。"),
    ]
    ys = [2.78, 4.06, 5.34]
    for (num, t, d), y in zip(items, ys):
        text(s, M, y, 0.5, 0.3, num, size=11, color=ACCENT, font=LATIN, bold=True, spc=2)
        text(s, M, y + 0.26, 5.6, 0.35, t, size=20, color=TEXT, font=SANS, bold=True)
        text(s, M, y + 0.68, 5.55, 0.7, d, size=12.5, color=MUTED, font=SANS, line=1.55)
    rule(s, M, 3.94, 5.75)
    rule(s, M, 5.22, 5.75)

    pic(s, os.path.join(IMG, "problem_canal.jpg"), 7.05, 1.18, 6.28, 5.52,
        cover=True, border=LINE, descr="OpenUAV 运河街区仿真场景")
    scrim(s, 7.05, 1.18, 6.28, 5.52, BG, 0.22)
    text(s, 7.3, 6.74, 5.9, 0.25,
         "OpenUAV 仿真场景 · 运河街区  |  真实世界的长尾，远超固定航线",
         size=9.5, color=MUTED, font=SANS)
    notes(s, "【画面字幕】换一个场景，飞手要重新教一遍。\n"
             "【30 秒口播】今天部署一套无人机搜索能力，最大的成本不在飞，而在把任务翻译成航点、"
             "把场景重新采集标注。仿真里训练的模型，到了实机和新场景又容易失效。这就是我们要解决的三件事。")


def p4_hero():
    s = bg()
    pic(s, os.path.join(IMG, "hero_aerial.jpg"), 0, 0, W, H, cover=True,
        descr="OpenUAV 仿真城市高楼区俯瞰")
    scrim(s, 0, 0, W, H, BG, 0.26)
    pic(s, os.path.join(IMG, "scrim_bottom.png"), 0, 0, W, H)

    text(s, M, 0.58, 5.0, 0.3, "TRAVELUAV", size=12, color=TEXT,
         font=LATIN, bold=True, spc=4.5)
    text(s, W - M - 3.0, 0.58, 3.0, 0.3, "04  /  PRODUCT", size=10.5,
         color=MUTED, font=LATIN, align=PP_ALIGN.RIGHT, spc=2.6)

    text(s, M, 3.58, 8.0, 0.3, "ONE INSTRUCTION. ONE SEARCH.",
         size=10.5, color=ACCENT, font=LATIN, bold=True, spc=3.2)
    text(s, M, 3.88, 9.2, 1.9, [[("一句话下达任务，", {})], [("全自主完成搜索", {})]],
         size=43, color=TEXT, font=SERIF, bold=True, line=1.14)
    text(s, M, 5.63, 8.8, 0.4,
         "目标描述、空间关系、途中复核，都在一次任务里完成。",
         size=16, color=MUTED, font=SANS)

    rule(s, M, 6.3, 11.6, color=TEXT, weight=0.75)
    labels = [("自然语言", "听懂“找什么”"), ("6 DoF 轨迹", "贴近真实飞行"), ("在线复核", "不确定就回看")]
    xs = [M, M + 3.85, M + 7.7]
    for x, (t, d) in zip(xs, labels):
        text(s, x, 6.46, 2.8, 0.25, t, size=10.5, color=MUTED, font=LATIN, bold=True, spc=2)
        text(s, x, 6.7, 2.8, 0.25, d, size=9.5, color=MUTED, font=SANS)
    text(s, W - M - 1.2, 7.02, 1.2, 0.25, "04 / 10", size=9, color=MUTED,
         font=LATIN, align=PP_ALIGN.RIGHT)
    notes(s, "【画面字幕】一句话下达任务，全自主完成搜索。\n"
             "【30 秒口播】这是产品最核心的一页：操作者只需要用一句话描述目标，"
             "比如“前方右侧、穿棕色外套的人，泳池边”。系统自己理解空间关系、生成 6 自由度轨迹，"
             "飞行过程中持续复核目标，不确定就回看。人不再需要拆航点。")


def p5_how():
    s = bg()
    header(s, "03", "HOW IT WORKS", 5)
    text(s, M, 1.28, 11.0, 0.6,
         [[("听懂", {"color": ACCENT}), ("  →  规划  →  找到，一次闭环", {})]],
         size=33, color=TEXT, font=SERIF, bold=True)

    steps = [
        ("01", "听懂意图", "多模态模型解析目标描述、空间关系与场景线索，形成可执行的任务意图。"),
        ("02", "生成轨迹", "在 6 DoF 连续动作空间里生成可行轨迹，贴合真实飞行约束与障碍。"),
        ("03", "边飞边找", "在线复核目标；不确定就回看，而不是一条航线飞到底。"),
    ]
    xs = [M, 4.75, 8.7]
    for x, (num, t, d) in zip(xs, steps):
        text(s, x, 2.12, 0.6, 0.3, num, size=11, color=ACCENT, font=LATIN, bold=True, spc=2)
        text(s, x, 2.42, 3.4, 0.4, t, size=22, color=TEXT, font=SERIF, bold=True)
        text(s, x, 2.95, 3.4, 1.0, d, size=12.5, color=MUTED, font=SANS, line=1.6)
    vrule(s, 4.55, 2.08, 1.95)
    vrule(s, 8.5, 2.08, 1.95)

    text(s, M, 4.34, 8.0, 0.25,
         "同一任务的城市街区执行序列  ·  OpenUAV 仿真",
         size=9.5, color=MUTED, font=SANS)
    pic(s, os.path.join(SRC, "scenes/demo_strip_1.png"), M, 4.64, 11.72, 2.16,
        border=LINE, descr="同一任务的城市街区执行序列")
    scrim(s, M, 4.64, 11.72, 2.16, BG, 0.10)
    text(s, W - M - 1.2, 7.02, 1.2, 0.25, "05 / 10", size=9, color=MUTED,
         font=LATIN, align=PP_ALIGN.RIGHT)
    notes(s, "【画面字幕】听懂、规划、找到，一次闭环。\n"
             "【30 秒口播】第一步听懂，目标描述里的颜色、方位、参照物都会被解析；"
             "第二步生成 6 自由度轨迹，而不是离散动作；第三步边飞边复核，目标不确定就回看。"
             "下面这条序列是同一任务在仿真里的执行过程。")


def p6_evidence():
    s = bg()
    header(s, "04", "PROOF", 6)
    text(s, M, 1.28, 7.0, 1.2, [[("相同评测条件下，", {})], [("成功率约为基线的 2.1 倍", {})]],
         size=32, color=TEXT, font=SERIF, bold=True, line=1.16)

    text(s, M, 2.92, 2.0, 0.25, "CMA 基线", size=11.5, color=MUTED, font=SANS)
    rect(s, M, 3.24, 6.2, 0.36, PANEL)
    rect(s, M, 3.24, 6.2 * 8.37 / 17.45, 0.36, DIM)
    text(s, 3.96, 3.23, 1.5, 0.35, "8.37%", size=18, color=MUTED, font=LATIN, bold=True)

    text(s, M, 3.94, 2.6, 0.25, "TravelUAV", size=11.5, color=TEXT, font=SANS, bold=True)
    rect(s, M, 4.26, 6.2, 0.36, PANEL)
    rect(s, M, 4.26, 6.2, 0.36, ACCENT)
    text(s, 7.12, 4.25, 1.8, 0.35, "17.45%", size=18, color=ACCENT, font=LATIN, bold=True)
    text(s, M, 4.86, 6.2, 0.3, "SR（成功率）  ·  Test Seen  ·  L1 助手",
         size=10, color=MUTED, font=SANS)

    text(s, 8.1, 2.38, 3.4, 1.1, "2.1×", size=76, color=ACCENT, font=LATIN, bold=True, line=1)
    text(s, 8.1, 3.46, 4.2, 0.3, "相对 CMA 基线的成功率提升", size=11.5, color=MUTED, font=SANS)
    rule(s, 8.1, 3.86, 4.35)

    text(s, 8.1, 4.06, 2.0, 0.6, "48.87%", size=32, color=TEXT, font=LATIN, bold=True)
    text(s, 8.1, 4.62, 2.0, 0.25, "OSR", size=10.5, color=MUTED, font=LATIN, bold=True, spc=2)
    text(s, 10.4, 4.06, 2.0, 0.6, "15.76", size=32, color=TEXT, font=LATIN, bold=True)
    text(s, 10.4, 4.62, 2.0, 0.25, "SPL", size=10.5, color=MUTED, font=LATIN, bold=True, spc=2)

    text(s, M, 6.32, 11.6, 0.45,
         "来源：TravelUAV, 2025（预印本）· Table 2 · Test Seen · L1 · Ours-DA 17.45% vs CMA 8.37%。"
         "OSR/SPL 同表。飞行任务仍受空域法规与现场条件约束。",
         size=9, color=MUTED, font=SANS, line=1.35)
    text(s, W - M - 1.2, 7.02, 1.2, 0.25, "06 / 10", size=9, color=MUTED,
         font=LATIN, align=PP_ALIGN.RIGHT)
    notes(s, "【画面字幕】相同评测条件下，成功率约为基线的 2.1 倍。\n"
             "【30 秒口播】这是论文 Table 2 的 Test Seen、L1 助手结果：CMA 基线成功率 8.37%，"
             "我们的方法 17.45%，约 2.1 倍；OSR 48.87%，SPL 15.76。需要说明，这是仿真评测结果，"
             "不是实机承诺；实机还要考虑空域、风和现场条件。")


def p7_scenes():
    s = bg()
    header(s, "05", "WHERE IT WORKS", 7)
    text(s, M, 1.28, 11.0, 0.6, "从城市街区，到没有地图的地方",
         size=33, color=TEXT, font=SERIF, bold=True)

    scenes = [
        ("scene_city.jpg", "城市街区搜索", "楼宇遮挡与动态人流"),
        ("scene_forest.jpg", "山地林区巡护", "无路网、弱信号"),
        ("scene_disaster.jpg", "灾后区域排查", "目标不确定、环境变化快"),
    ]
    xs = [M, 4.72, 8.64]
    for x, (f, t, d) in zip(xs, scenes):
        pic(s, os.path.join(IMG, f), x, 2.02, 3.75, 2.52, cover=True,
            border=LINE, descr=f"OpenUAV 仿真场景：{t}")
        scrim(s, x, 2.02, 3.75, 2.52, BG, 0.14)
        text(s, x, 4.74, 3.75, 0.4, t, size=17.5, color=TEXT, font=SERIF, bold=True)
        text(s, x, 5.14, 3.75, 0.3, d, size=11, color=MUTED, font=SANS)

    rule(s, M, 6.18, W - 2 * M)
    text(s, M, 6.34, 11.4, 0.35,
         "场景均为 OpenUAV 仿真环境；实机试点按项目定制，并受空域法规与现场条件约束。",
         size=9.5, color=MUTED, font=SANS)
    text(s, W - M - 1.2, 7.02, 1.2, 0.25, "07 / 10", size=9, color=MUTED,
         font=LATIN, align=PP_ALIGN.RIGHT)
    notes(s, "【画面字幕】从城市街区，到没有地图的地方。\n"
             "【30 秒口播】同一套能力可以放进三类场景：城市街区的目标搜索、山地林区的巡护、"
             "灾后区域的排查。共同点是路网不完整、目标不确定、环境变化快，正好是传统航点方案最吃力的地方。")


def p8_engagement():
    s = bg()
    header(s, "06", "ENGAGEMENT", 8)
    text(s, M, 1.28, 11.0, 0.6, "三种合作方式，从评估到落地",
         size=33, color=TEXT, font=SERIF, bold=True)

    ways = [
        ("01", "平台授权", "OpenUAV 仿真平台与 12k 轨迹数据集授权，支持本地部署与二次开发。",
         "适合：建立自研导航能力"),
        ("02", "基准评测", "用 UAV-Need-Help 对现有模型做零样本与泛化评测，输出可复现报告。",
         "适合：验证技术路线"),
        ("03", "联合试点", "围绕一个真实场景做数据采集、微调与实机验证，2–6 周一个周期。",
         "适合：快速 PoC"),
    ]
    xs = [M, 4.75, 8.7]
    for x, (num, t, d, fit) in zip(xs, ways):
        text(s, x, 2.22, 0.6, 0.3, num, size=11, color=ACCENT, font=LATIN, bold=True, spc=2)
        text(s, x, 2.52, 3.4, 0.4, t, size=23, color=TEXT, font=SERIF, bold=True)
        text(s, x, 3.08, 3.4, 1.2, d, size=13, color=MUTED, font=SANS, line=1.62)
        rule(s, x, 4.78, 3.4)
        text(s, x, 4.94, 3.4, 0.3, fit, size=10.5, color=DIM, font=SANS)
    vrule(s, 4.55, 2.18, 3.3)
    vrule(s, 8.5, 2.18, 3.3)

    text(s, M, 5.95, 11.4, 0.4,
         [[("所有合作，从一次 ", {"color": TEXT}), ("30 分钟的场景评估", {"color": ACCENT}),
           ("开始。", {"color": TEXT})]],
         size=16, color=TEXT, font=SANS)
    text(s, W - M - 1.2, 7.02, 1.2, 0.25, "08 / 10", size=9, color=MUTED,
         font=LATIN, align=PP_ALIGN.RIGHT)
    notes(s, "【画面字幕】三种合作方式，从评估到落地。\n"
             "【30 秒口播】如果你们在做无人机自主导航，可以从平台授权开始；"
             "如果已经有模型，想验证泛化能力，我们做基准评测；如果有一个明确场景，"
             "就做 2 到 6 周的联合试点。都从一次 30 分钟的场景评估开始。")


def p9_foundation():
    s = bg()
    header(s, "07", "FOUNDATION", 9)
    text(s, M, 1.28, 11.2, 0.6, "不是演示视频，是可复现的研究底座",
         size=33, color=TEXT, font=SERIF, bold=True)

    stats = [
        ("12k+", "真实动力学轨迹", "首个真实 UAV VLN 数据集，覆盖连续飞行。" ),
        ("6 DoF", "连续动作空间", "不是离散航点，贴近真实飞行约束与姿态变化。" ),
        ("4", "评测子集", "含未见地图与未见物体，专门检验零样本泛化。" ),
    ]
    xs = [M, 4.75, 8.7]
    for x, (num, label, body) in zip(xs, stats):
        text(s, x, 2.42, 3.5, 1.5, num, size=78, color=TEXT, font=LATIN, bold=True, line=1)
        text(s, x, 3.78, 3.5, 0.3, label, size=12.5, color=ACCENT, font=SANS, bold=True)
        text(s, x, 4.16, 3.45, 0.9, body, size=11.5, color=MUTED, font=SANS, line=1.55)
    vrule(s, 4.55, 2.38, 2.85)
    vrule(s, 8.5, 2.38, 2.85)

    rule(s, M, 5.62, W - 2 * M)
    text(s, M, 5.8, 11.2, 0.7,
         "平台、数据、基准与方法已在论文中完整披露；评测协议可复现，"
         "便于在采购前做独立验证。",
         size=13, color=MUTED, font=SANS, line=1.6)
    text(s, M, 6.58, 11.2, 0.3,
         "来源：TravelUAV, 2025（预印本）· 数据集统计与评测协议见论文第 4–5 节。",
         size=9, color=DIM, font=SANS)
    text(s, W - M - 1.2, 7.02, 1.2, 0.25, "09 / 10", size=9, color=MUTED,
         font=LATIN, align=PP_ALIGN.RIGHT)
    notes(s, "【画面字幕】不是演示视频，是可复现的研究底座。\n"
             "【30 秒口播】支撑这套能力的不是一段剪辑，而是三样可验证的东西："
             "12k 条真实动力学轨迹、6 自由度连续动作空间、以及包含未见地图和未见物体的四个评测子集。"
             "平台、数据、基准都在论文里公开，采购前可以独立复现。")


def p10_contact():
    s = bg("cover")
    pic(s, os.path.join(IMG, "hero_city.jpg"), 0, 0, W, H, cover=True,
        descr="OpenUAV 仿真城市街区")
    scrim(s, 0, 0, W, H, BG, 0.62)
    pic(s, os.path.join(IMG, "scrim_bottom.png"), 0, 0, W, H)

    text(s, M, 0.58, 5.0, 0.3, "TRAVELUAV", size=12, color=TEXT,
         font=LATIN, bold=True, spc=4.5)
    text(s, W - M - 1.2, 0.58, 1.2, 0.3, "10  /  10", size=10.5,
         color=MUTED, font=LATIN, align=PP_ALIGN.RIGHT, spc=2.6)

    text(s, M, 1.28, 5.0, 0.3, "NEXT STEP", size=10.5, color=ACCENT,
         font=LATIN, bold=True, spc=3.2)
    text(s, M, 1.55, 8.0, 1.6, [[("把您的场景，", {})], [("交给它试一次。", {})]],
         size=42, color=TEXT, font=SERIF, bold=True, line=1.16)

    steps = [
        ("01", "扫码预约", "选择到展位或线上的评估时段"),
        ("02", "带上场景", "一段现场视频或一张区域地图即可"),
        ("03", "两周试点", "输出可量化的搜索成功率对比"),
    ]
    ys = [3.52, 4.22, 4.92]
    for (num, t, d), y in zip(steps, ys):
        text(s, M, y, 0.45, 0.3, num, size=10.5, color=ACCENT, font=LATIN, bold=True)
        text(s, M + 0.55, y - 0.02, 2.2, 0.3, t, size=15.5, color=TEXT, font=SANS, bold=True)
        text(s, M + 2.35, y + 0.03, 4.6, 0.3, d, size=12, color=MUTED, font=SANS)
    rule(s, M, 5.62, 7.4)

    text(s, M, 5.74, 2.0, 1.0, "B-17", size=60, color=ACCENT, font=LATIN, bold=True, line=1)
    text(s, M + 2.55, 6.12, 5.2, 0.3, "BOOTH  ·  2026 世界无人机大会  ·  上海",
         size=10, color=MUTED, font=LATIN, spc=2.2)

    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.72),
                              Inches(1.92), Inches(2.72), Inches(3.08))
    card.adjustments[0] = 0.04
    card.fill.solid()
    card.fill.fore_color.rgb = PAPER
    card.line.fill.background()
    card.shadow.inherit = False
    s.shapes.add_picture(os.path.join(BRAND, "qr_demo.png"), Inches(9.94),
                         Inches(2.14), Inches(2.28), Inches(2.28))
    text(s, 9.72, 4.55, 2.72, 0.3, "扫码预约现场演示", size=11, color=INK,
         font=SANS, bold=True, align=PP_ALIGN.CENTER)
    text(s, 9.72, 5.18, 2.72, 0.3, "30 分钟评估  ·  两周试点", size=10,
         color=MUTED, font=SANS, align=PP_ALIGN.CENTER)

    rule(s, M, 6.92, W - 2 * M)
    text(s, M, 7.02, 6.0, 0.25, "TRAVELUAV  ·  2026 世界无人机大会  ·  上海",
         size=9, color=MUTED, font=LATIN, spc=1.2)
    notes(s, "【画面字幕】把您的场景，交给它试一次。\n"
             "【30 秒口播】下一步很简单：扫码预约一个 30 分钟的场景评估，带一段现场视频或一张地图，"
             "我们两周内给一次联合试点，输出可量化的搜索成功率对比。展位 B-17，今天全天都在。")


def set_loop_script():
    """工作区与 paper2podium 仓库两种目录布局下都能找到 set_loop.py。"""
    for rel in (("..", "..", ".zcode", "skills", "business-ppt", "scripts", "set_loop.py"),
                ("..", "..", "..", "skills", "business-ppt", "scripts", "set_loop.py"),
                (os.path.expanduser("~"), ".zcode", "skills", "business-ppt", "scripts", "set_loop.py")):
        p = os.path.abspath(os.path.join(BASE, *rel))
        if os.path.exists(p):
            return p
    return None


def main():
    assets()
    p1_cover()
    p2_manifesto()
    p3_problem()
    p4_hero()
    p5_how()
    p6_evidence()
    p7_scenes()
    p8_engagement()
    p9_foundation()
    p10_contact()
    prs.save(OUT)
    print("saved", OUT)
    loop_script = set_loop_script()
    if loop_script is None:
        print("WARN: 未找到 set_loop.py，请手动运行 skills/business-ppt/scripts/set_loop.py")
        return
    subprocess.run([sys.executable, loop_script,
                    OUT, "--seconds", "8", "--first", "10", "--last", "12",
                    "--fade", "-o", OUT], check=True)


if __name__ == "__main__":
    main()
