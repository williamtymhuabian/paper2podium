#!/usr/bin/env python3
"""Research deck (English) — TravelUAV group-meeting presentation.
Same design system as build_research.py (white academic, assertion-evidence),
all strings in English, Latin font Arial.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")

BG      = RGBColor(0xFF, 0xFF, 0xFF)
BG_SOFT = RGBColor(0xF6, 0xF8, 0xFA)
PRIMARY = RGBColor(0x1F, 0x4E, 0x79)
ACCENT  = RGBColor(0xC0, 0x39, 0x2B)
TEXT    = RGBColor(0x2B, 0x2B, 0x2B)
MUTED   = RGBColor(0x6B, 0x72, 0x80)
LINE    = RGBColor(0xD8, 0xDE, 0xE6)
OKABE_BLUE = RGBColor(0x00, 0x72, 0xB2)

FONT = "Arial"
W, H, M = 13.33, 7.5, 0.6

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
blank = prs.slide_layouts[6]

def tb(s, x, y, w, h, runs, size=20, color=TEXT, bold=False, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, leading=1.0, space_after=0):
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
            f.name = st.get("font", FONT)
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.color.rgb = st.get("color", color)
    return box

def title(s, assertion, sub=None):
    tb(s, M, 0.42, W - 2 * M, 0.6, assertion, size=25, color=PRIMARY, bold=True)
    if sub:
        tb(s, M, 1.04, W - 2 * M, 0.35, sub, size=13.5, color=MUTED)

def pageno(s, n):
    tb(s, W - M - 0.5, H - 0.42, 0.5, 0.3, str(n), size=11, color=MUTED, align=PP_ALIGN.RIGHT)

def hline(s, x, y, w, color=LINE, weight=1.0):
    ln = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y))
    ln.line.color.rgb = color; ln.line.width = Pt(weight)

def pic(s, path, x=None, y=None, maxw=None, maxh=None, center_x=None, border=False):
    iw, ih = Image.open(path).size
    r = min(maxw / iw, maxh / ih)
    w, h = iw * r, ih * r
    x = center_x - w / 2 if center_x is not None else x
    y = y if y is not None else 0
    p = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    if border:
        p.line.color.rgb = LINE; p.line.width = Pt(0.75)
    return x, y, w, h

def caption(s, x, y, w, text):
    tb(s, x, y, w, 0.55, text, size=12.5, color=MUTED, leading=1.15)

def source(s, text):
    tb(s, M, H - 0.45, W - 2 * M - 0.6, 0.3, text, size=11.5, color=MUTED)

# ============ P1 Cover ============
s = prs.slides.add_slide(blank)
tb(s, M, 1.15, W - 2 * M, 0.35, "Group Meeting · Paper Presentation · Vision-Language Navigation", size=14, color=MUTED)
tb(s, M, 1.72, W - 2 * M, 1.75, [
    [("Towards Realistic UAV Vision-Language Navigation:", {"size": 32, "bold": True, "color": PRIMARY})],
    [("Platform, Benchmark, and Methodology", {"size": 32, "bold": True, "color": PRIMARY})],
], leading=1.14)
tb(s, M, 3.6, W - 2 * M, 0.4, "TravelUAV / OpenUAV — a platform, dataset, benchmark and navigation LLM for realistic UAV VLN",
   size=16, color=TEXT)
hline(s, M, 4.4, 2.2, PRIMARY, 1.5)
tb(s, M, 4.65, W - 2 * M, 1.2, [
    [("Authors: ", {"bold": True}), ("Xiangyu Wang*, Donglin Yang*, Ziqin Wang*, Hohin Kwan, Jinyu Chen, Wenjun Wu, Hongsheng Li, Yue Liao†, Si Liu†", {})],
    [("Affiliation: ", {"bold": True}), ("Institute of AI, Beihang University · MMLab, CUHK · CPII", {})],
    [("Source: ", {"bold": True}), ("arXiv:2410.07087 (2024) · project page prince687028.github.io/OpenUAV", {})],
], size=12.5, color=MUTED, leading=1.35)
tb(s, M, H - 0.75, 6, 0.35, "Presenter: ________    Date: Oct 2026", size=13, color=TEXT)

# ============ P2 Outline ============
s = prs.slides.add_slide(blank); title(s, "Outline")
items = [
    ("01", "Background & Motivation", "Ground-based VLN settings do not transfer to UAVs"),
    ("02", "OpenUAV Platform", "Realistic environments × flight control × toolchain"),
    ("03", "Dataset & Benchmark", "12,149 6-DoF trajectories + UAV-Need-Help"),
    ("04", "UAV Navigation LLM", "Hierarchical trajectory generation + backtracking DAgger"),
    ("05", "Experiments", "Outperforms all baselines; large gap to humans remains"),
    ("06", "Conclusion & Outlook", "Contributions and future directions"),
]
y = 1.65
for num, name, desc in items:
    tb(s, M, y, 0.8, 0.5, num, size=24, color=PRIMARY, bold=True)
    tb(s, M + 0.95, y + 0.02, 4.1, 0.45, name, size=19, bold=True, color=TEXT)
    tb(s, M + 5.3, y + 0.09, 6.6, 0.4, desc, size=14, color=MUTED)
    y += 0.88
pageno(s, 2)

# ============ P3 Background ============
s = prs.slides.add_slide(blank)
title(s, "Ground-based VLN settings cannot handle realistic UAV navigation",
      "Background · fundamental disparities in dynamics and task complexity")
cards = [
    ("Dynamics mismatch", ["Ground agents move in a horizontal plane — discrete actions suffice",
                           "UAVs fly in 3-D with 6 DoF: pitch, roll and yaw occur simultaneously",
                           "Continuous trajectories resist discrete decomposition — fixed action sets yield unrealistic flight"]),
    ("Task complexity mismatch", ["UAVs operate in open outdoor scenes over long ranges",
                                  "Shifting viewpoints and occlusions defeat pure target descriptions",
                                  "Online guidance from an assistant becomes necessary"]),
]
x = M
for name, points in cards:
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.72), Inches(5.95), Inches(4.4))
    box.fill.solid(); box.fill.fore_color.rgb = BG_SOFT
    box.line.color.rgb = LINE; box.line.width = Pt(0.75); box.shadow.inherit = False
    tb(s, x + 0.4, 2.05, 5.2, 0.5, name, size=20, bold=True, color=PRIMARY)
    tb(s, x + 0.4, 2.7, 5.2, 3.2, [[("• ", {"color": PRIMARY, "bold": True}), (p, {})] for p in points],
       size=14, leading=1.22, space_after=9)
    x += 6.18
tb(s, M, 6.45, W - 2 * M, 0.4, [[("Takeaway: ", {"bold": True, "color": ACCENT}),
   ("the entire stack — platform, data and method — must be rebuilt for UAV VLN", {"bold": True})]], size=15.5)
source(s, "Source: Wang et al., arXiv:2410.07087, Fig.1 & Sec.1")
pageno(s, 3)

# ============ P4 Dataset comparison table ============
s = prs.slides.add_slide(blank)
title(s, "No existing UAV VLN dataset captures realistic 6-DoF flight", "Related Work · comparison with representative VLN datasets (Table 1)")
rows = [
    ["Dataset", "DoF", "Kinematics", "#Traj", "Vocab", "TrajLen(m)", "InstrLen", "Actions"],
    ["R2R (2018)", "—", "✗", "7,189", "3.1K", "10", "29", "5"],
    ["TouchDown (2019)", "2", "✗", "9,326", "5K", "310", "90", "35"],
    ["AVDN (2022)", "3", "✗", "6,269", "3.3K", "144", "89", "7"],
    ["AerialVLN (2023)", "4", "✗", "8,446", "4.5K", "661", "83", "204"],
    ["CityNav (2024)", "4", "✗", "32,637", "6.6K", "545", "26", "—"],
    ["Ours (TravelUAV)", "6", "✓", "12,149", "10.8K", "255", "104", "264"],
]
gt = s.shapes.add_table(len(rows), 8, Inches(M), Inches(1.8), Inches(12.13), Inches(4.6)).table
for i, cw in enumerate([3.1, 0.95, 1.3, 1.35, 1.2, 1.5, 1.28, 1.45]): gt.columns[i].width = Inches(cw)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci); c.text = val
        c.margin_left = c.margin_right = Inches(0.08)
        c.margin_top = c.margin_bottom = Inches(0.03)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        for r in p.runs:
            r.font.name = FONT; r.font.size = Pt(15.5)
            last = ri == len(rows) - 1
            r.font.bold = ri == 0 or last
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if ri == 0 else (PRIMARY if last else TEXT)
        c.fill.solid()
        c.fill.fore_color.rgb = PRIMARY if ri == 0 else (BG_SOFT if last else BG)
tb(s, M, 6.55, W - 2 * M, 0.4, [[("The first UAV VLN dataset with realistic flight dynamics (6 DoF, kinematics ✓)", {"bold": True, "color": ACCENT})]], size=15.5)
source(s, "Source: arXiv:2410.07087, Table 1")
pageno(s, 4)

# ============ P5 Platform overview (Fig 1) ============
s = prs.slides.add_slide(blank)
title(s, "OpenUAV: realistic environments, flight control and toolchain in one platform")
r = pic(s, f"{FIG}/fig1_platform.png", y=1.35, maxw=10.8, maxh=5.0, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.42 + r[3] + 0.12, 10,
        "Fig. 1 | Platform & benchmark overview. Left: OpenUAV (closed-loop simulation, parallelization, reproducible conditions, configurable sensors, trajectory replay). Right: the UAV-Need-Help assistant-guided object search task.")
source(s, "Figure source: arXiv:2410.07087, Fig.1")
pageno(s, 5)

# ============ P6 Platform highlights ============
s = prs.slides.add_slide(blank)
title(s, "OpenUAV is built on UE4 + AirSim with 22 open scenes")
feats = [
    ("Realistic environments", ["UE4 high-fidelity rendering, 22 urban scenes",
                                "89 placeable object assets via runtime API",
                                "Dynamic effects: swaying vegetation, lighting"]),
    ("Realistic flight", ["AirSim physics, 6-DoF pose P={x,y,z,θ,φ,ψ}",
                          "PX4 remote / manual / position control interfaces",
                          "RGB-D ×5 views, 360° LiDAR, IMU, GPS"]),
    ("Algorithmic support", ["Closed loop: model output → flight → feedback",
                             "Built-in DAgger aggregation + backtracking policy",
                             "16× speedup on 8×A100, 160–1600 fps"]),
]
x = M
for name, pts in feats:
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.7), Inches(3.92), Inches(4.4))
    box.fill.solid(); box.fill.fore_color.rgb = BG_SOFT
    box.line.color.rgb = LINE; box.line.width = Pt(0.75); box.shadow.inherit = False
    tb(s, x + 0.32, 2.02, 3.3, 0.5, name, size=18.5, bold=True, color=PRIMARY)
    tb(s, x + 0.32, 2.66, 3.35, 3.3, [[("• ", {"color": PRIMARY, "bold": True}), (p, {})] for p in pts],
       size=13, leading=1.22, space_after=9)
    x += 4.11
tb(s, M, 6.4, W - 2 * M, 0.45, [[("Fully open-sourced", {"bold": True, "color": ACCENT}),
   (": environment, flight control, collection, training and evaluation in one stack", {})]], size=15.5)
source(s, "Source: arXiv:2410.07087, Sec.3")
pageno(s, 6)

# ============ P7 Dataset (Fig 2) ============
s = prs.slides.add_slide(blank)
title(s, "12,149 6-DoF expert trajectories: GPT-4 descriptions + human-piloted collection")
r = pic(s, f"{FIG}/fig2_dataset.png", y=1.35, maxw=10.2, maxh=4.75, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.42 + r[3] + 0.12, 10,
        "Fig. 2 | Dataset construction & statistics. Five-view capture → GPT-4 description → human review; pilots fly manually while states are logged and sensor data is collected asynchronously. Right: trajectory length, goal distance, object categories and data splits.")
source(s, "Figure source: arXiv:2410.07087, Fig.2 · Splits: Train 9,152 / Test Seen 1,410 / Unseen Map 958 / Unseen Object 629")
pageno(s, 7)

# ============ P8 Benchmark ============
s = prs.slides.add_slide(blank)
title(s, "UAV-Need-Help: three assistant tiers mirror real human-UAV teamwork",
      "Benchmark · the assistant provides online guidance at varying granularity")
lv = [
    ("L1 Constant", "Continuously tracks the closest oracle-path point and issues high-frequency cruise/turn/land commands", "Ground-station collaboration"),
    ("L2 Corrective", "Steps in only on collision risk or large deviation, low-frequency corrections", "Remote supervisor"),
    ("L3 Avoidance", "Only issues obstacle-avoidance commands in hazardous situations", "Max autonomy, hardest setting"),
]
y = 1.8
for name, desc, tag in lv:
    tb(s, M, y, 2.3, 0.5, name, size=18, bold=True, color=PRIMARY)
    tb(s, M + 2.6, y, 6.9, 0.9, desc, size=14.5, leading=1.2)
    tb(s, M + 9.8, y + 0.04, 2.4, 0.5, tag, size=12.5, color=MUTED)
    hline(s, M, y + 0.92, W - 2 * M)
    y += 1.12
tb(s, M, 5.5, W - 2 * M, 1.2, [
    [("Formulation: ", {"bold": True}), ("each step takes {target description I, state S, five-view RGB R & depth D, assistant instruction I′} and outputs a 6-DoF trajectory; landing within ", {}),
     ("20 m", {"bold": True, "color": ACCENT}), (" of the target counts as success.", {})],
], size=15.5, leading=1.3)
source(s, "Source: arXiv:2410.07087, Sec.5")
pageno(s, 8)

# ============ P9 Method overview (Fig 3) ============
s = prs.slides.add_slide(blank)
title(s, "UAV navigation LLM: a learnable query drives hierarchical trajectory generation")
r = pic(s, f"{FIG}/fig3_method.png", y=1.3, maxw=11.4, maxh=4.9, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.36 + r[3] + 0.1, 10,
        "Fig. 3 | Left: the three-tier assistant. Right: instructions and multi-view images are encoded into an MLLM (Vicuna-7B); a waypoint query token predicts a long-range target pose, refined by a front-view trajectory completion model.")
source(s, "Figure source: arXiv:2410.07087, Fig.3")
pageno(s, 9)

# ============ P10 Method details ============
s = prs.slides.add_slide(blank)
title(s, "Hierarchical decoding: long-range target pose first, fine trajectory second")
steps = [
    ("Multimodal tokenization", ["EVA-CLIP + Q-former: 1 global + 16 local tokens per view",
                                 "Concatenate <T_img, T_task, T_instr> into Vicuna-7B"]),
    ("High-level decode", ["Learnable waypoint token T_wp extracts trajectory features",
                           "MLP decodes the next target pose P_target (long-range planning)"]),
    ("Fine-grained decode", ["Front-view tokens × pose features → pose sequence",
                             "Grounding DINO detection triggers landing"]),
]
x = M
for i, (name, pts) in enumerate(steps):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.75), Inches(3.92), Inches(3.55))
    box.fill.solid(); box.fill.fore_color.rgb = BG_SOFT
    box.line.color.rgb = LINE; box.line.width = Pt(0.75); box.shadow.inherit = False
    tb(s, x + 0.3, 2.05, 0.7, 0.5, f"0{i+1}", size=22, bold=True, color=OKABE_BLUE)
    tb(s, x + 0.3, 2.62, 3.35, 0.5, name, size=17, bold=True, color=PRIMARY)
    tb(s, x + 0.3, 3.18, 3.4, 1.9, [[("• ", {"color": PRIMARY, "bold": True}), (p, {})] for p in pts],
       size=13, leading=1.22, space_after=8)
    if i < 2:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 3.98), Inches(3.3), Inches(0.28), Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb = PRIMARY; ar.line.fill.background(); ar.shadow.inherit = False
    x += 4.11
tb(s, M, 5.7, W - 2 * M, 0.9, [[("Training boost: ", {"bold": True}),
   ("backtracking-sampling DAgger — on collision the UAV reverts two frames and follows the teacher, mining avoidance samples from failure", {})]], size=15.5, leading=1.3)
source(s, "Source: arXiv:2410.07087, Sec.6")
pageno(s, 10)

# ============ P11 Main results ============
s = prs.slides.add_slide(blank)
title(s, "All metrics beat baselines: +5pt average SR over CMA", "Experiments · Test Seen, L1 assistant (Table 2, Full)")
rows = [
    ["Method", "NE (m) ↓", "SR (%) ↑", "OSR (%) ↑", "SPL (%) ↑"],
    ["Random", "222.20", "0.14", "0.21", "0.07"],
    ["Fixed Action", "188.61", "2.27", "8.16", "1.40"],
    ["CMA (LSTM)", "135.73", "8.37", "18.72", "7.90"],
    ["Ours", "106.28", "16.10", "44.26", "14.30"],
    ["Ours + bt-DAgger", "98.66", "17.45", "48.87", "15.76"],
    ["Human", "14.15", "94.51", "94.51", "77.84"],
]
gt = s.shapes.add_table(len(rows), 5, Inches(M), Inches(1.75), Inches(7.6), Inches(4.3)).table
for i, cw in enumerate([2.5, 1.28, 1.28, 1.28, 1.28]): gt.columns[i].width = Inches(cw)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci); c.text = val
        c.margin_left = c.margin_right = Inches(0.06); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        for r in p.runs:
            r.font.name = FONT; r.font.size = Pt(15.5)
            hl = ri in (5, 6)
            r.font.bold = ri == 0 or hl
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if ri == 0 else (ACCENT if hl else TEXT)
        c.fill.solid()
        c.fill.fore_color.rgb = PRIMARY if ri == 0 else (BG_SOFT if hl else BG)
tb(s, 8.6, 1.9, 4.1, 4.2, [
    [("+109%", {"size": 34, "bold": True, "color": ACCENT})],
    [("SR gain over CMA (8.37 → 17.45)", {"size": 13, "color": MUTED})],
    [("", {})],
    [("3.4×", {"size": 34, "bold": True, "color": PRIMARY})],
    [("OSR gain (18.72 → 48.87): nearly half of episodes touch the optimal path", {"size": 13, "color": MUTED})],
    [("", {})],
    [("Gap remains", {"size": 22, "bold": True, "color": TEXT})],
    [("Human SR 94.51 vs model 17.45 — far from solved", {"size": 13, "color": MUTED})],
], leading=1.1)
source(s, "Source: arXiv:2410.07087, Table 2 · NE = average final distance to target")
pageno(s, 11)

# ============ P12 Generalization charts ============
s = prs.slides.add_slide(blank)
title(s, "Best generalization on unseen objects (SR 22.4%); more data keeps helping")
cd = CategoryChartData()
cd.categories = ["Random", "Fixed", "CMA", "Ours"]
cd.add_series("SR (%)", (0.16, 3.66, 9.06, 22.42))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(M), Inches(1.85), Inches(5.9), Inches(4.2), cd)
ch = gf.chart; ch.has_legend = False
ch.category_axis.tick_labels.font.size = Pt(13); ch.value_axis.tick_labels.font.size = Pt(13)
pl = ch.plots[0]; pl.vary_by_categories = False; pl.gap_width = 80
pl.has_data_labels = True
pl.data_labels.show_value = True; pl.data_labels.number_format = '0.0'; pl.data_labels.number_format_is_linked = False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.data_labels.font.size = Pt(14); pl.data_labels.font.bold = True; pl.data_labels.font.color.rgb = TEXT
ser = pl.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = OKABE_BLUE
pt = ser.points[3]
pt.format.fill.solid(); pt.format.fill.fore_color.rgb = ACCENT
tb(s, M, 6.1, 5.9, 0.4, "Test Unseen Object (L1 assistant), SR %", size=12.5, color=MUTED, align=PP_ALIGN.CENTER)
cd2 = CategoryChartData()
cd2.categories = ["10% data", "50% data", "100% data"]
cd2.add_series("SR (%)", (10.78, 13.19, 16.10))
gf2 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(7.0), Inches(1.85), Inches(5.7), Inches(4.2), cd2)
ch2 = gf2.chart; ch2.has_legend = False
ch2.category_axis.tick_labels.font.size = Pt(13)
pl2 = ch2.plots[0]; pl2.vary_by_categories = False; pl2.gap_width = 80
pl2.has_data_labels = True
pl2.data_labels.show_value = True; pl2.data_labels.number_format = '0.00'; pl2.data_labels.number_format_is_linked = False
pl2.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl2.data_labels.font.size = Pt(14); pl2.data_labels.font.bold = True; pl2.data_labels.font.color.rgb = TEXT
pl2.series[0].format.fill.solid(); pl2.series[0].format.fill.fore_color.rgb = PRIMARY
tb(s, 7.0, 6.1, 5.7, 0.4, "Training-data ablation (Test Seen, L1, SR %)", size=12.5, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, M, 6.55, W - 2 * M, 0.4, [[("SR drops to 4.18% on Unseen Map", {"bold": True, "color": ACCENT}),
   (" — unseen city scenes remain the core challenge", {})]], size=15)
source(s, "Source: arXiv:2410.07087, Table 3 / Table 4")
pageno(s, 12)

# ============ P13 Qualitative ============
s = prs.slides.add_slide(blank)
title(s, "Successes follow instructions end-to-end; failures stem from collisions")
r = pic(s, f"{FIG}/fig4_qualitative.png", y=1.4, maxw=10.6, maxh=4.8, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.46 + r[3] + 0.1, 10,
        "Fig. 4 | Top two rows: success cases — the UAV locates the described vehicle and cow; frames 3–5 show a turning maneuver changing viewpoint. Bottom row: a failure colliding with trees in a forest scene.")
source(s, "Figure source: arXiv:2410.07087, Fig.4")
pageno(s, 13)

# ============ P14 Conclusion ============
s = prs.slides.add_slide(blank)
title(s, "Conclusion: platform + benchmark + method reshape realistic UAV VLN")
concl = [
    ("Platform", "OpenUAV — the first fully open-source simulation platform for continuous-trajectory UAV VLN (UE4+AirSim, 22 scenes)"),
    ("Data & Benchmark", "12,149 6-DoF trajectories + the three-tier UAV-Need-Help benchmark, all released"),
    ("Method", "UAV navigation LLM: hierarchical generation + backtracking DAgger, +5pt average SR over CMA"),
]
y = 1.7
for i, (k, v) in enumerate(concl):
    tb(s, M, y, 0.8, 0.5, f"0{i+1}", size=24, bold=True, color=PRIMARY)
    tb(s, M + 0.95, y + 0.03, 2.5, 0.5, k, size=18, bold=True)
    tb(s, M + 3.6, y + 0.06, 8.4, 0.9, v, size=14.5, leading=1.2)
    hline(s, M, y + 0.85, W - 2 * M)
    y += 1.05
tb(s, M, 5.05, W - 2 * M, 0.85, [
    [("Limitations & outlook: ", {"bold": True}),
     ("a 77pt SR gap to human operators remains; unseen-scene generalization (Unseen Map SR 4.18%) and real-UAV deployment are the next frontiers.", {})],
], size=14.5, color=TEXT, leading=1.3)
tb(s, M, 6.3, W - 2 * M, 0.6, "Thanks — questions welcome · Q&A", size=24, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)
pageno(s, 14)

out = os.path.join(BASE, "research", "TravelUAV_Research_GroupMeeting_EN.pptx")
prs.save(out)
print("saved:", out, "slides:", len(prs.slides._sldIdLst))
