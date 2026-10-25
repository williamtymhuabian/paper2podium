#!/usr/bin/env python3
"""Competition deck v3 (English) — TravelUAV roadshow. No standalone section pages (17 slides); one distinct layout archetype per slide.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")
WEB = os.path.join(FIG, "web")
BGD = os.path.join(BASE, "bg")

PRIMARY = RGBColor(0x2F, 0x80, 0xFF)
ACCENT  = RGBColor(0xFF, 0xC5, 0x3D)
CYAN    = RGBColor(0x38, 0xD6, 0xFF)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
MUTED   = RGBColor(0xA8, 0xC3, 0xE8)
CARD    = RGBColor(0x13, 0x29, 0x4F)
DEEP    = RGBColor(0x0A, 0x1F, 0x3C)
HAIR    = RGBColor(0x3A, 0x55, 0x80)
FONT, FN = "Arial", "Arial"
W, H, M = 13.33, 7.5, 0.55
NAVS = ["Market", "Product", "Technology", "Business", "Team", "Roadmap"]

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
blank = prs.slide_layouts[6]

def _alpha(fill_fmt, pct):
    sf = fill_fmt._xPr.find(qn('a:solidFill'))
    etree.SubElement(sf.find(qn('a:srgbClr')), qn('a:alpha')).set('val', str(pct))

def slide(bg="content", nav=None):
    s = prs.slides.add_slide(blank)
    if bg:
        s.shapes.add_picture(os.path.join(BGD, f"techblue_{bg}.png"), 0, 0, Inches(W), Inches(H))
    if nav:
        x = M
        for name in NAVS:
            cur = name == nav
            r = s.shapes.add_textbox(Inches(x), Inches(0.22), Inches(1.15), Inches(0.3))
            tf = r.text_frame; tf.word_wrap = False
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            run = tf.paragraphs[0].add_run(); run.text = name
            run.font.name = FONT; run.font.size = Pt(12.5); run.font.bold = cur
            run.font.color.rgb = WHITE if cur else MUTED
            x += 1.28
    return s

def tb(s, x, y, w, h, runs, size=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, leading=1.0, font=None, space_after=0):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if isinstance(runs, str):
        runs = [[(runs, {})]]
    elif runs and isinstance(runs[0], tuple):
        runs = [runs]
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if leading != 1.0: p.line_spacing = leading
        if space_after: p.space_after = Pt(space_after)
        for txt, st in para:
            r = p.add_run(); r.text = txt
            f = r.font
            f.name = st.get("font", font or FONT)
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.color.rgb = st.get("color", color)
    return box

def head(s, kicker, t):
    """章节角标 + 标题（替代独立章节页）。"""
    tb(s, M, 0.38, 8, 0.32, kicker, size=13, color=CYAN, bold=True)
    tb(s, M, 0.72, W - 2 * M, 0.62, t, size=27, bold=True, color=WHITE)

def hair(s, x, y, w, color=HAIR, weight=0.75):
    ln = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y))
    ln.line.color.rgb = color; ln.line.width = Pt(weight)

def vhair(s, x, y, h):
    ln = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x), Inches(y + h))
    ln.line.color.rgb = HAIR; ln.line.width = Pt(0.75)

def card(s, x, y, w, h, alpha_pct=25000):
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    c.adjustments[0] = 0.05
    c.fill.solid(); c.fill.fore_color.rgb = CARD
    if alpha_pct: _alpha(c.fill, alpha_pct)
    c.line.color.rgb = PRIMARY; c.line.width = Pt(0.75)
    c.shadow.inherit = False
    return c

def pic(s, path, x=None, y=None, w=None, h=None, center_x=None, border=True):
    iw, ih = Image.open(path).size
    if w is not None:
        h2 = w * ih / iw; w2 = w
    else:
        w2 = h * iw / ih; h2 = h
    x = center_x - w2 / 2 if center_x is not None else x
    p = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w2), Inches(h2))
    if border:
        p.line.color.rgb = MUTED; p.line.width = Pt(1)
    return x, y, w2, h2

def cover_pic(s, path):
    s.shapes.add_picture(path, 0, 0, Inches(W), Inches(H))
    ov = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    ov.fill.solid(); ov.fill.fore_color.rgb = DEEP
    _alpha(ov.fill, 52000)
    ov.line.fill.background(); ov.shadow.inherit = False

def dark_chart(s, ctype, cd, x, y, w, h, base_color, hi_idx=None, fmt='0.0'):
    gf = s.shapes.add_chart(ctype, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart; ch.has_legend = False; ch.has_title = False
    cs = ch._chartSpace
    spPr = etree.Element(qn('c:spPr'))
    etree.SubElement(spPr, qn('a:noFill'))
    ln = etree.SubElement(spPr, qn('a:ln')); etree.SubElement(ln, qn('a:noFill'))
    cs.find(qn('c:chart')).addnext(spPr)
    pl = ch.plots[0]; pl.vary_by_categories = False; pl.gap_width = 70
    pl.has_data_labels = True
    dl = pl.data_labels
    dl.show_value = True; dl.number_format = fmt; dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(14); dl.font.bold = True; dl.font.color.rgb = WHITE; dl.font.name = FN
    ser = pl.series[0]
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = base_color
    ser.format.line.fill.background()
    if hi_idx is not None:
        p_ = ser.points[hi_idx]
        p_.format.fill.solid(); p_.format.fill.fore_color.rgb = ACCENT
    for ax in (ch.category_axis, ch.value_axis):
        ax.tick_labels.font.size = Pt(13)
        ax.tick_labels.font.color.rgb = MUTED
        ax.tick_labels.font.name = FONT
        ax.format.line.color.rgb = HAIR
    ch.value_axis.has_major_gridlines = False
    ch.value_axis.visible = False
    return ch

def img_label_chip(s, x, y, text):
    chip = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(1.5), Inches(0.4))
    chip.adjustments[0] = 0.5; chip.fill.solid(); chip.fill.fore_color.rgb = DEEP
    _alpha(chip.fill, 55000); chip.line.fill.background(); chip.shadow.inherit = False
    tb(s, x, y + 0.075, 1.5, 0.3, text, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

def src_line(s, text, y=None):
    tb(s, M, y or (H - 0.38), 12.2, 0.3, text, size=11.5, color=MUTED)

# ══════════ P1 封面：全幅航拍主视觉 ══════════
s = slide(bg=None, nav=None)
cover_pic(s, os.path.join(FIG, "derived", "hero_169.jpg"))
tb(s, M, 0.55, 10, 0.4, "China International College Students' Innovation Competition · Roadshow", size=14, color=CYAN)
tb(s, M, 2.35, 12.2, 1.9, [
    [("天行 TravelUAV", {"size": 48, "bold": True})],
    [("The Drone That Listens · Realistic Vision-Language Navigation", {"size": 22, "bold": True, "color": RGBColor(0xE3, 0xEE, 0xFB)})],
], leading=1.18)
tb(s, M, 4.35, 11.5, 0.5, "A multimodal-LLM platform letting UAVs understand language and search targets in real 3-D airspace", size=16, color=WHITE)
ln = s.shapes.add_connector(1, Inches(M), Inches(5.1), Inches(M + 3.2), Inches(5.1))
ln.line.color.rgb = ACCENT; ln.line.width = Pt(2)
tb(s, M, 5.3, 12.2, 0.8, [
    [("12,149 real expert trajectories · 6-DoF flight dynamics · SR +109% over baselines", {"size": 15, "bold": True, "color": ACCENT})],
    [("Beihang ColaLab × CUHK MMLab | Advisors: Prof. Si Liu · Dr. Yue Liao · Prof. Hongsheng Li", {"size": 13, "color": MUTED})],
], leading=1.5)

# ══════════ P2 Agenda：左列表 + 右大图（非对称分栏） ══════════
s = slide(nav="市场痛点")
tb(s, M, 0.72, 5, 0.6, "Agenda", size=30, bold=True)
items = [("01", "Market & Pain", "trillion track · 41x gap"), ("02", "Product", "four-in-one + live demo"),
         ("03", "Technology", "three innovations"), ("04", "Business", "TAM/SAM/SOM · revenue"),
         ("05", "Team & Value", "co-creation · social value"), ("06", "Roadmap", "three years, three steps")]
y = 1.72
for n, t, d in items:
    tb(s, M, y, 0.75, 0.45, n, size=20, bold=True, color=CYAN, font=FN)
    tb(s, M + 0.8, y - 0.02, 2.2, 0.45, t, size=18, bold=True)
    tb(s, M + 0.8, y + 0.38, 4.2, 0.35, d, size=13, color=MUTED)
    y += 0.87
pic(s, os.path.join(WEB, "show.png"), x=6.1, y=1.35, w=6.68)
tb(s, 6.1, 1.35 + 6.68 * 859 / 1135 + 0.1, 6.68, 0.35, "OpenUAV high-fidelity scene library (22 scenes · 89 object categories)",
   size=12, color=MUTED, align=PP_ALIGN.CENTER)

# ══════════ P3 市场机会：数字横带 + 全宽场景条（开放版式） ══════════
s = slide(nav="市场痛点")
head(s, "01 · Market", "Policy tailwind: the low-altitude economy is a national strategy")
nums = [("1.5T", "low-altitude economy 2025E", "CAAC", ACCENT),
        ("3.5T", "projected scale 2035E", "CAAC", CYAN),
        ("176.1B", "civil drone output 2025 · industrial >70%", "MIIT", CYAN)]
band_y = 1.72
for i, (v, l, src, c) in enumerate(nums):
    cx = M + i * 4.14
    tb(s, cx, band_y, 3.95, 0.85, v, size=44, bold=True, color=c, align=PP_ALIGN.CENTER, font=FN)
    tb(s, cx + 0.2, band_y + 0.95, 3.55, 0.55, l, size=14, color=WHITE, align=PP_ALIGN.CENTER, leading=1.15)
    tb(s, cx, band_y + 1.5, 3.95, 0.3, f"Source: {src}", size=11.5, color=MUTED, align=PP_ALIGN.CENTER)
    if i < 2: vhair(s, cx + 4.02, band_y + 0.15, 1.6)
pic(s, os.path.join(FIG, "derived", "market_strip.jpg"), x=M, y=3.85, w=12.23, border=False)
tb(s, M, 6.35, 12.2, 0.5, [[("Entry point: ", {"bold": True, "color": ACCENT}),
   ("UAV uses are scaling fast, but automation lags — language + autonomous search is the next leap", {})]], size=14.5)
src_line(s, "Sources: CAAC (Xinhua 2025-12), MIIT 2025 civil drone bulletin; image: OpenUAV city scenes")

# ══════════ P4 痛点：左垂直大数字对比 + 右错位台阶 ══════════
s = slide(nav="市场痛点")
head(s, "01 · Market", "The core pain: drones cannot listen, fly real, or learn")
vhair(s, 6.3, 1.55, 5.3)
tb(s, M, 1.5, 5.5, 0.35, "Success rate under identical instructions", size=14.5, color=MUTED)
tb(s, M, 1.9, 5.5, 1.05, "94.5%", size=58, bold=True, color=CYAN, font=FN)
tb(s, M, 2.98, 5.5, 0.4, "human pilots", size=15, color=MUTED)
tb(s, M, 3.38, 5.5, 1.05, "2.27%", size=58, bold=True, color=ACCENT, font=FN)
tb(s, M, 4.46, 5.5, 0.4, "fixed-action program", size=15, color=MUTED)
pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(M), Inches(4.98), Inches(3.4), Inches(0.62))
pill.adjustments[0] = 0.5; pill.fill.solid(); pill.fill.fore_color.rgb = ACCENT
_alpha(pill.fill, 18000); pill.line.color.rgb = ACCENT; pill.line.width = Pt(1); pill.shadow.inherit = False
tb(s, M, 5.125, 3.4, 0.4, "41x capability gap", size=16, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
from math import sin as _sin
card(s, M, 5.68, 5.9, 1.38, alpha_pct=15000)
vhair(s, M + 3.0, 5.82, 1.1)
tb(s, M + 0.22, 5.8, 2.6, 0.3, "Legacy: discrete actions", size=11.5, color=MUTED)
for _i in range(5):
    _sq = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M + 0.28 + _i * 0.5), Inches(6.72 - _i * 0.13), Inches(0.34), Inches(0.26))
    _sq.fill.solid(); _sq.fill.fore_color.rgb = PRIMARY; _alpha(_sq.fill, 55000)
    _sq.line.fill.background(); _sq.shadow.inherit = False
tb(s, M + 0.22, 6.85, 2.8, 0.3, "grid steps · unrealistic flight", size=10, color=MUTED)
tb(s, M + 3.22, 5.8, 2.7, 0.3, "Ours: 6-DoF continuous", size=11.5, color=CYAN, bold=True)
for _i in range(22):
    _dx = M + 3.25 + _i * 0.12
    _dy = 6.5 + 0.3 * _sin(_i * 0.58 + 0.4)
    _dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(_dx), Inches(_dy), Inches(0.09), Inches(0.09))
    _dot.fill.solid(); _dot.fill.fore_color.rgb = CYAN; _dot.line.fill.background(); _dot.shadow.inherit = False
tb(s, M + 3.22, 6.85, 2.7, 0.3, "continuous pitch·roll·yaw", size=10, color=MUTED)
pains = [("01", "Can't listen", "language cannot drive missions; expert pilots required"),
         ("02", "Can't fly real", "discrete actions ignore true 6-DoF dynamics"),
         ("03", "Can't learn", "no real trajectory data to learn expert skill from")]
y = 1.6
for i, (n, k, v) in enumerate(pains):
    x = 6.9 + i * 0.38  # 错位台阶
    tb(s, x, y, 0.8, 0.5, n, size=26, bold=True, color=PRIMARY, font=FN)
    tb(s, x + 0.95, y + 0.02, 2.4, 0.5, k, size=22, bold=True)
    tb(s, x + 0.95, y + 0.58, 4.9 - i * 0.38, 0.7, v, size=14, color=MUTED, leading=1.2)
    if i < 2: hair(s, 6.9, y + 1.5, 5.9)
    y += 1.78
src_line(s, "Source: arXiv:2410.07087, Table 2 (UAV-Need-Help benchmark)")

# ══════════ P5 产品总览：大图左出血 + 右侧开放特性列 ══════════
s = slide(nav="产品方案")
head(s, "02 · Product", "TravelUAV: a full-stack autonomous navigation solution")
pic(s, os.path.join(WEB, "header2.png"), x=0, y=1.62, w=9.35, border=False)
img_label_chip(s, 0.25, 1.8, "Live view")
feats = [("OpenUAV Platform", "22 scenes · 6-DoF physics · open"),
         ("Expert Dataset", "12,149 trajectories · GPT-4 + review"),
         ("Assistant Benchmark", "L1/L2/L3 tiers · human-UAV teamwork"),
         ("Navigation LLM", "Vicuna-7B · hierarchical generation")]
y = 1.7
for t, d in feats:
    tb(s, 9.75, y, 3.1, 0.4, t, size=16, bold=True)
    tb(s, 9.75, y + 0.42, 3.15, 0.65, d, size=11.5, color=MUTED, leading=1.2)
    y += 1.28
    if y < 6.3: hair(s, 9.75, y - 0.18, 3.05)
tb(s, 0, 6.15, 9.35, 0.5, [[("Four in one, fully open source", {"bold": True, "color": ACCENT}),
   (" — researchers and industry can reproduce and extend directly", {})]], size=14, align=PP_ALIGN.CENTER)

# ══════════ P6 产品演示：飞行序列 + 指令引用条 + 三步开放流 ══════════
s = slide(nav="产品方案")
head(s, "02 · Product", "Live demo: understand one sentence, find the target")
pic(s, os.path.join(FIG, "scenes", "demo_strip_1.png"), x=M, y=1.55, w=12.23)
tb(s, M, 3.82, 12.23, 0.35, "OpenUAV closed-loop simulation: 12 consecutive frames (success case: the described yellow sedan)",
   size=12, color=MUTED, align=PP_ALIGN.CENTER)
qb = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(4.3), Inches(0.07), Inches(1.15))
qb.fill.solid(); qb.fill.fore_color.rgb = CYAN; qb.line.fill.background(); qb.shadow.inherit = False
tb(s, M + 0.25, 4.28, 7.3, 0.35, "Instruction (example)", size=13, color=CYAN, bold=True)
tb(s, M + 0.25, 4.63, 7.3, 0.8,
   "\u201cThe target is front-left... a yellow sedan at the center, surrounded by multi-story buildings. Please find it.\u201d",
   size=14, color=WHITE, leading=1.2)
tb(s, 8.6, 4.28, 4.15, 1.2, [
    [("End-to-end", {"size": 21, "bold": True, "color": ACCENT}),
     (": pixels + language straight to trajectories — no hand-crafted rules", {"size": 13, "color": MUTED})],
], leading=1.3, anchor=MSO_ANCHOR.MIDDLE)
hair(s, M, 5.75, 12.23)
steps = [("Understand", "MLLM parses target & scene"), ("Search", "hierarchical 6-DoF planning"), ("Land", "land on detection")]
x = M
for i, (t, d) in enumerate(steps):
    tb(s, x, 5.95, 3.6, 0.45, f"{i+1}  {t}", size=18, bold=True, color=ACCENT)
    tb(s, x + 0.55, 6.48, 3.2, 0.4, d, size=12.5, color=MUTED)
    if i < 2:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 3.55), Inches(6.1), Inches(0.35), Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb = PRIMARY; ar.line.fill.background(); ar.shadow.inherit = False
    x += 4.1
src_line(s, "Demo frames: arXiv:2410.07087, Fig.4 (rendered in OpenUAV)")

# ══════════ P7 场景能力：非对称拼图 + 右下注解列 ══════════
s = slide(nav="产品方案")
head(s, "02 · Product", "22 high-fidelity scenes, city to wilderness")
pic(s, os.path.join(FIG, "scenes", "scene_3.png"), x=0, y=1.6, w=7.35, border=False)
img_label_chip(s, 0.25, 1.78, "Urban")
pic(s, os.path.join(FIG, "scenes", "scene_5.png"), x=7.6, y=1.6, w=5.18, border=False)
img_label_chip(s, 7.85, 1.78, "Natural")
tb(s, 7.6, 4.62, 5.2, 2.0, [
    [("Fidelity & dynamics", {"size": 15, "bold": True, "color": ACCENT})],
    [("• UE4 rendering: dynamic lighting, swaying vegetation", {"size": 12.5, "color": MUTED})],
    [("• 89 object categories placed at runtime via API", {"size": 12.5, "color": MUTED})],
    [("• Rural / industrial and more covered (Appendix A)", {"size": 12.5, "color": MUTED})],
    [("• Laying the ground for Sim-to-Real transfer", {"size": 12, "color": WHITE, "bold": True})],
], leading=1.4)
src_line(s, "Scenes: OpenUAV platform (Appendix A, arXiv:2410.07087)")

# ══════════ P8 技术架构：全宽官方框架图 ══════════
s = slide(nav="核心技术")
head(s, "03 · Technology", "Architecture: multimodal-LLM hierarchical trajectory generation")
pic(s, os.path.join(WEB, "method2.png"), y=1.5, w=12.23, center_x=W / 2)
tb(s, M, 6.27, 12.23, 0.55,
   "Instructions and five-view images encoded into the MLLM (Vicuna-7B): a waypoint query token predicts the long-range pose; a front-view decoder outputs fine 6-DoF trajectories",
   size=12, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, M, 6.85, 12.2, 0.4, "Fully self-controlled core tech: hierarchical decoding · backtracking DAgger · Grounding-DINO landing",
   size=13, color=ACCENT, bold=True)

# ══════════ P9 三大创新：三段变奏（大字左右交替） ══════════
s = slide(nav="核心技术")
head(s, "03 · Technology", "Three innovations: from fake flight to real autonomy")
# 段1：大字左
hair(s, M, 1.7, 12.23)
tb(s, M, 1.95, 3.4, 0.9, "6-DoF", size=44, bold=True, color=CYAN, font=FN)
_f = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.35), Inches(2.05), Inches(2.42), Inches(0.52))
_f.adjustments[0] = 0.5; _f.fill.solid(); _f.fill.fore_color.rgb = PRIMARY; _alpha(_f.fill, 28000)
_f.line.color.rgb = PRIMARY; _f.line.width = Pt(0.75); _f.shadow.inherit = False
tb(s, 10.35, 2.185, 2.42, 0.32, "P = {x, y, z, θ, φ, ψ}", size=13, bold=True, color=CYAN, align=PP_ALIGN.CENTER, font=FN)
tb(s, 4.2, 1.95, 8.5, 1.4, [
    [("Innovation 1 · Real 6-DoF platform", {"size": 17.5, "bold": True})],
    [("Industry fakes dynamics by teleporting → our UE4+AirSim physics control, full state logging, 16x on 8×A100", {"size": 12.5, "color": MUTED})],
], leading=1.35)
hair(s, M, 3.55, 12.23)
# 段2：大字右
tb(s, M, 3.8, 8.3, 1.4, [
    [("Innovation 2 · Assistant benchmark", {"size": 17.5, "bold": True})],
    [("Static descriptions only → L1 full guidance / L2 correction / L3 avoidance; the first benchmark mirroring real teamwork", {"size": 12.5, "color": MUTED})],
], leading=1.35)
tb(s, 10.2, 3.8, 2.6, 0.9, "L1→L3", size=40, bold=True, color=CYAN, font=FN)
for _j, (_lt, _ln) in enumerate([("L1", "constant"), ("L2", "corrective"), ("L3", "avoidance")]):
    _lx = M + _j * 1.78
    _c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(_lx), Inches(4.78), Inches(1.62), Inches(0.46))
    _c.adjustments[0] = 0.5; _c.fill.solid(); _c.fill.fore_color.rgb = PRIMARY; _alpha(_c.fill, 28000)
    _c.line.color.rgb = PRIMARY; _c.line.width = Pt(0.75); _c.shadow.inherit = False
    tb(s, _lx, 4.875, 1.62, 0.3, [[(_lt + " ", {"bold": True, "color": CYAN}), (_ln, {"color": WHITE})]], size=11, align=PP_ALIGN.CENTER)
hair(s, M, 5.4, 12.23)
# 段3：大字左 + 金色更大
tb(s, M, 5.65, 3.4, 1.0, "+109%", size=48, bold=True, color=ACCENT, font=FN)
_g = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.35), Inches(5.85), Inches(2.42), Inches(0.52))
_g.adjustments[0] = 0.5; _g.fill.solid(); _g.fill.fore_color.rgb = ACCENT; _alpha(_g.fill, 18000)
_g.line.color.rgb = ACCENT; _g.line.width = Pt(0.75); _g.shadow.inherit = False
tb(s, 10.35, 5.985, 2.42, 0.32, "SR 8.37 → 17.45", size=13, bold=True, color=ACCENT, align=PP_ALIGN.CENTER, font=FN)
tb(s, 4.2, 5.65, 8.5, 1.4, [
    [("Innovation 3 · Hierarchical LLM", {"size": 17.5, "bold": True})],
    [("Discrete-action classifiers → MLLM generates continuous trajectories; SR doubled (8.37 → 17.45)", {"size": 12.5, "color": MUTED})],
], leading=1.35)
src_line(s, "Comparison: arXiv:2410.07087, Table 2", y=7.12)

# ══════════ P10 成果落地：横向成果链 + 下方图表/知产分栏 ══════════
s = slide(nav="核心技术")
head(s, "03 · Technology", "Deliverables: paper, code, data and benchmark — all landed")
chain_y = 1.95
hair(s, 1.5, chain_y, 10.3, color=PRIMARY, weight=1.5)
chain = [("Paper", "arXiv:2410.07087", "platform+benchmark+method"),
         ("Open Source", "GitHub · buaa-colalab", "training & evaluation code"),
         ("Open Data", "HuggingFace", "12,149 trajectories"),
         ("Benchmark", "UAV-Need-Help", "three-tier protocol")]
for i, (t, k, d) in enumerate(chain):
    cx = 1.9 + i * 3.0
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - 0.08), Inches(chain_y - 0.08), Inches(0.16), Inches(0.16))
    dot.fill.solid(); dot.fill.fore_color.rgb = CYAN; dot.line.fill.background(); dot.shadow.inherit = False
    tb(s, cx - 1.35, chain_y - 0.62, 2.7, 0.4, t, size=17, bold=True, align=PP_ALIGN.CENTER)
    tb(s, cx - 1.35, chain_y + 0.18, 2.7, 0.35, k, size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    tb(s, cx - 1.35, chain_y + 0.56, 2.7, 0.35, d, size=12.5, color=MUTED, align=PP_ALIGN.CENTER)
cd = CategoryChartData()
cd.categories = ["CMA baseline", "Ours", "Ours+DA"]
cd.add_series("SR (%)", (8.37, 16.10, 17.45))
dark_chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, cd, M, 3.55, 6.5, 2.7, PRIMARY, hi_idx=2)
tb(s, M, 6.32, 6.5, 0.35, "Key metric SR (success rate): +109% over the strongest baseline", size=13.5, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, 7.6, 3.6, 5.2, 0.4, "IP pipeline", size=16.5, bold=True, color=ACCENT)
tb(s, 7.6, 4.1, 5.2, 1.8, [
    [("• Invention patent (language-guided trajectory generation) under filing", {"size": 12.5, "color": MUTED})],
    [("• Software copyright (OpenUAV platform) under registration", {"size": 12.5, "color": MUTED})],
    [("• Dataset & benchmark open-sourced as a community moat", {"size": 12.5, "color": MUTED})],
], leading=1.4)
src_line(s, "Note: IP filings in progress; acceptance letters attached in the roadshow version")

# ══════════ P11 市场规模：TAM/SAM/SOM 嵌套 + 右侧时机列 ══════════
s = slide(nav="商业模式")
head(s, "04 · Business", "Market size: from the trillion-yuan economy to UAV intelligence")
t_ = [(M, 1.6, 7.3, 5.0, "TAM · low-altitude economy", "1.5T (2025E) → 3.5T (2035E)", PRIMARY, 22000),
      (M + 0.55, 2.28, 6.2, 3.7, "SAM · civil drones", "176.1B (2025) · industrial >70%", RGBColor(0x1F, 0x6F, 0xD0), 45000),
      (M + 1.1, 3.0, 5.1, 2.4, "SOM · navigation software & services", "team estimate: 3–5 year window", ACCENT, 60000)]
for x, y, w2, h2, name, val, c, a in t_:
    rc = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w2), Inches(h2))
    rc.adjustments[0] = 0.04; rc.fill.solid(); rc.fill.fore_color.rgb = c
    _alpha(rc.fill, a); rc.line.color.rgb = c; rc.line.width = Pt(1); rc.shadow.inherit = False
rcs = [s.shapes[-3], s.shapes[-2], s.shapes[-1]]
for rc, (x, y, w2, h2, name, val, c, a) in zip(rcs, t_):
    dark = c is ACCENT
    tb(s, x + 0.28, y + 0.18, w2 - 0.55, 0.4, name, size=14.5, bold=True, color=DEEP if dark else WHITE)
    tb(s, x + 0.28, y + 0.62, w2 - 0.55, 0.4, val, size=12, color=DEEP if dark else MUTED)
vhair(s, 8.15, 1.6, 5.0)
tb(s, 8.5, 1.6, 4.3, 0.4, "Why now", size=17, bold=True, color=ACCENT)
why = [("Policy", "low-altitude economy in the Work Report; airspace pilots"),
       ("Tech", "multimodal LLMs broke the language-to-action barrier"),
       ("Demand", "inspection & rescue costly; pilot shortage"),
       ("Window", "academic flagship set (us); 3–5 year window")]
y = 2.2
for k, v in why:
    tb(s, 8.5, y, 0.9, 0.4, k, size=14.5, bold=True, color=CYAN)
    tb(s, 9.4, y, 3.4, 0.8, v, size=12, color=MUTED, leading=1.2)
    y += 1.05
src_line(s, "Sources: CAAC, MIIT public reports; SOM is a team estimate")

# ══════════ P12 竞品矩阵 ══════════
s = slide(nav="商业模式")
head(s, "04 · Business", "Competitors: the only stack with real dynamics + language + open ecosystem")
rows = [
    ["Capability", "Flight-control suites", "Route planners", "Academic AerialVLN/CityNav", "TravelUAV"],
    ["Continuous 6-DoF", "✗ manual", "✗ waypoints", "✗ discrete", "✓ physics-based"],
    ["Natural language", "✗", "✗ waypoints only", "partial short cmds", "✓ multi-view + long"],
    ["Online guidance", "✗", "✗", "✗", "✓ L1–L3 tiers"],
    ["Open data/benchmark", "✗ closed", "✗ closed", "partial data", "✓ fully open"],
    ["LLM-driven", "✗", "✗", "✗ LSTM", "✓ MLLM end-to-end"],
    ["Overall", "●○○○", "●●○○", "●●○○", "●●●●"],
]
gt = s.shapes.add_table(len(rows), 5, Inches(M), Inches(1.6), Inches(12.23), Inches(4.5)).table
for i, cw in enumerate([2.4, 2.0, 2.0, 3.2, 2.63]): gt.columns[i].width = Inches(cw)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci); c.text = val
        c.margin_left = c.margin_right = Inches(0.08); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        ours = ci == 4
        for r in p.runs:
            r.font.name = FONT; r.font.size = Pt(15)
            r.font.bold = ri == 0 or ours
            if ri == 0: r.font.color.rgb = WHITE
            elif ours: r.font.color.rgb = ACCENT if val.startswith("✓") else WHITE
            else: r.font.color.rgb = MUTED
        c.fill.solid()
        if ri == 0: c.fill.fore_color.rgb = PRIMARY
        elif ours: c.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x66)
        else: c.fill.fore_color.rgb = CARD
tb(s, M, 6.45, 12.2, 0.4, "Positioning: no hardware — the training ground and the brain of UAVs", size=14.5, bold=True, color=ACCENT)
src_line(s, "Competitor info from public materials (product sites & papers, 2024–2025)")

# ══════════ P13 商业模式：左开放收入行 + 右数据飞轮 ══════════
s = slide(nav="商业模式")
head(s, "04 · Business", "Three revenue lines: academia first, industry next")
biz = [("Line 1 · SaaS", "universities & institutes", "OpenUAV subscription + support", "academic funnel"),
       ("Line 2 · Data", "AI companies & labs", "trajectory licensing · evaluation", "exclusive 6-DoF assets"),
       ("Line 3 · Solutions", "rescue / grid / security", "vertical solutions per project", "scenario moats")]
y = 1.65
for t, who, what, moat in biz:
    tb(s, M, y, 6.9, 0.45, t, size=18, bold=True, color=ACCENT)
    tb(s, M, y + 0.5, 6.9, 0.4, [[("To: ", {"color": CYAN, "bold": True}), (who, {}),
                                    ("  |  Moat: ", {"color": CYAN, "bold": True}), (moat, {})]], size=12, color=MUTED)
    tb(s, M, y + 0.92, 6.9, 0.4, what, size=12.5, color=MUTED)
    y += 1.62
    hair(s, M, y - 0.28, 6.9)
vhair(s, 7.75, 1.6, 5.2)
# 数据飞轮
fcx, fcy, fr = 10.35, 4.15, 1.5
ring = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(fcx - fr), Inches(fcy - fr), Inches(fr * 2), Inches(fr * 2))
ring.fill.background(); ring.line.color.rgb = PRIMARY; ring.line.width = Pt(1.5); ring.shadow.inherit = False
tb(s, fcx - 0.9, fcy - 0.25, 1.8, 0.5, "Data flywheel", size=15.5, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
nodes = [(fcx, fcy - fr, "Research adoption", -1.0, -0.62), (fcx + fr, fcy, "Data flywheel", 0.2, -0.2),
         (fcx, fcy + fr, "Stronger models", -1.0, 0.12), (fcx - fr, fcy, "Solution premium", -2.35, -0.2)]
for nx, ny, lab, dx, dy in nodes:
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(nx - 0.07), Inches(ny - 0.07), Inches(0.14), Inches(0.14))
    d.fill.solid(); d.fill.fore_color.rgb = CYAN; d.line.fill.background(); d.shadow.inherit = False
    tb(s, nx + dx, ny + dy, 2.1, 0.35, lab, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, M, 6.72, 12.2, 0.4, "The flywheel: more users → more data → stronger models → higher-value solutions", size=13.5, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

# ══════════ P14 团队：头像圆 + 开放列表（无卡片） ══════════
s = slide(nav="团队价值")
head(s, "05 · Team", "Co-creation: Beihang ColaLab × CUHK MMLab")
mentors = [("S", "Prof. Si Liu", "Beihang · Institute of AI", "national young scholar · multimodal"),
           ("L", "Dr. Yue Liao", "CUHK MMLab", "rising scholar in VLN"),
           ("L", "Prof. Hongsheng Li", "CUHK MMLab", "known scholar in MLLM")]
x = M
for ch, n, org, tag in mentors:
    circ = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(1.65), Inches(0.78), Inches(0.78))
    circ.fill.solid(); circ.fill.fore_color.rgb = PRIMARY; _alpha(circ.fill, 45000)
    circ.line.color.rgb = PRIMARY; circ.line.width = Pt(1); circ.shadow.inherit = False
    tb(s, x, 1.83, 0.78, 0.45, ch, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tb(s, x + 0.95, 1.63, 3.2, 0.4, n, size=16.5, bold=True, color=ACCENT)
    tb(s, x + 0.95, 2.08, 3.2, 0.35, org, size=13, color=CYAN)
    tb(s, x + 0.95, 2.45, 3.3, 0.4, tag, size=11.5, color=MUTED)
    x += 4.14
hair(s, M, 3.1, 12.23)
tb(s, M, 3.3, 8, 0.4, "Core student members (paper co-authors)", size=14, bold=True, color=CYAN)
buaa = ["Xiangyu Wang*", "Donglin Yang*", "Ziqin Wang*", "Hohin Kwan", "Jinyu Chen", "Wenjun Wu"]
x, y = M, 3.85
for n in buaa:
    chip = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(2.45), Inches(0.72))
    chip.adjustments[0] = 0.5; chip.fill.background()
    chip.line.color.rgb = PRIMARY; chip.line.width = Pt(1); chip.shadow.inherit = False
    tb(s, x, y + 0.17, 2.45, 0.4, n, size=15, bold=True, align=PP_ALIGN.CENTER)
    x += 2.7
    if x > 8.6: x, y = M, y + 0.95
tb(s, M, y + 0.95, 8.5, 0.35, "* equal contribution (platform, data and model modules) · per paper authorship", size=11, color=MUTED)
card(s, 9.35, 3.85, 3.43, 2.3, alpha_pct=0)
tb(s, 9.62, 4.05, 2.9, 0.4, "Hosted by", size=14, bold=True, color=CYAN)
tb(s, 9.62, 4.52, 2.95, 1.5, [
    [("• Institute of AI, Beihang", {"size": 12.5, "color": MUTED})],
    [("• CUHK MMLab", {"size": 12.5, "color": MUTED})],
    [("• Long depth in embodied AI", {"size": 12.5, "color": MUTED})],
], leading=1.35)

hair(s, M, 6.42, 12.23)
tb(s, M, 6.6, 12.2, 0.45, [[("9 members", {"bold": True, "color": CYAN}), ("  ·  ", {"color": MUTED}),
    ("2 top universities", {"bold": True, "color": CYAN}), ("  ·  ", {"color": MUTED}),
    ("1 arXiv paper", {"bold": True, "color": CYAN}), ("  ·  ", {"color": MUTED}),
    ("4 open-source releases", {"bold": True, "color": CYAN}), ("  ·  ", {"color": MUTED}),
    ("1:3 advisor ratio", {"bold": True, "color": CYAN})]], size=13.5, align=PP_ALIGN.CENTER)

# ══════════ P15 社会价值：左侧图拼 + 右开放价值列 ══════════
s = slide(nav="团队价值")
head(s, "05 · Team", "Social value: faster rescue, safer inspection, better jobs")
pic(s, os.path.join(FIG, "scenes", "scene_4.png"), x=M, y=1.65, w=3.25, border=False)
img_label_chip(s, M + 0.2, 1.82, "Rescue")
pic(s, os.path.join(FIG, "scenes", "scene_6.png"), x=M, y=3.62, w=3.25, border=False)
img_label_chip(s, M + 0.2, 3.79, "Inspection")
vhair(s, 4.35, 1.65, 4.9)
vals = [("Emergency", "search missing persons by description in the golden 72 hours"),
        ("Safety", "unmanned inspection replaces hazardous manual work"),
        ("Employment", "new roles: annotation, route ops, drone trainers"),
        ("Education", "open stack feeds teaching; paper-to-product loop")]
y = 1.7
for k, v in vals:
    tb(s, 4.75, y, 2.6, 0.4, k, size=16.5, bold=True, color=ACCENT)
    tb(s, 7.5, y + 0.02, 5.3, 0.75, v, size=14, color=MUTED, leading=1.25)
    y += 1.22
    if y < 6.2: hair(s, 4.75, y - 0.22, 8.0)
tb(s, M, 6.55, 12.2, 0.5, [[("Tech for good · serving the national low-altitude strategy", {"size": 15, "bold": True, "color": ACCENT}),
   ("  (scenes rendered in OpenUAV; deployment subject to real-UAV tests)", {"size": 10, "color": MUTED})]], size=12.5)

# ══════════ P16 发展规划：时间轴 + 近期目标条 ══════════
s = slide(nav="发展规划")
head(s, "06 · Roadmap", "Three years: open ecosystem → real UAVs → scale")
tl_y = 3.55
ln = s.shapes.add_connector(1, Inches(M), Inches(tl_y), Inches(W - M), Inches(tl_y))
ln.line.color.rgb = PRIMARY; ln.line.width = Pt(2)
ms = [("Done", "2024", "full stack open-sourced\narXiv paper", True),
      ("Ongoing", "2025", "community data growth\nIP filings", True),
      ("Next", "2026", "Sim-to-Real validation\nfirst rescue/grid pilots", False),
      ("Goal", "2027+", "scaled subscriptions\nreplicated solutions", False)]
for i, (tag, t, d, done) in enumerate(ms):
    cx = M + 0.85 + i * 3.02
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - 0.09), Inches(tl_y - 0.09), Inches(0.18), Inches(0.18))
    dot.fill.solid(); dot.fill.fore_color.rgb = CYAN if done else CARD
    dot.line.color.rgb = CYAN; dot.line.width = Pt(1.5); dot.shadow.inherit = False
    tb(s, cx - 1.3, tl_y - 0.82, 2.6, 0.4, t, size=16, bold=True, color=CYAN if done else MUTED, align=PP_ALIGN.CENTER, font=FN)
    tb(s, cx - 1.3, tl_y + 0.3, 2.6, 0.4, tag, size=15, bold=True, align=PP_ALIGN.CENTER, color=ACCENT if not done else WHITE)
    tb(s, cx - 1.45, tl_y + 0.85, 2.9, 1.1, d, size=12, color=MUTED, align=PP_ALIGN.CENTER, leading=1.25)
hair(s, M, 6.0, 12.23)
tb(s, M, 6.14, 12.2, 0.5, [[("Near-term: ", {"bold": True, "color": ACCENT}),
   ("two industry pilots + a live drone demo in 2026; the de-facto UAV-brain standard long term", {})]], size=14.5)
tb(s, M, 6.68, 12.2, 0.4, [[("Risk plan: ", {"bold": True, "color": CYAN}),
   ("Sim-to-Real staged validation; market pacing — academia first, industry second", {"color": MUTED})]], size=12)

# ══════════ P17 致谢：主视觉收尾 ══════════
s = slide(bg=None, nav=None)
cover_pic(s, os.path.join(FIG, "derived", "hero_169.jpg"))
tb(s, M, 2.6, 12.2, 1.0, "Thank you — we welcome your feedback", size=35, bold=True, align=PP_ALIGN.CENTER)
tb(s, M, 3.85, 12.2, 0.5, "TravelUAV · The Drone That Listens", size=17, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, M, 4.45, 12.2, 0.4, "E N D · T H A N K   Y O U", size=14, color=CYAN, align=PP_ALIGN.CENTER)
tb(s, M, H - 0.65, 12.2, 0.35, "Figures & data from arXiv:2410.07087 and CAAC/MIIT public reports; IP filings in progress", size=11.5, color=MUTED, align=PP_ALIGN.CENTER)

out = os.path.join(BASE, "competition", "TravelUAV_Competition_Roadshow_EN.pptx")
prs.save(out)
print("saved:", out, "slides:", len(prs.slides._sldIdLst))
