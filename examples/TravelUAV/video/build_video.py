#!/usr/bin/env python3
"""TravelUAV · 3-minute paper promo video.

Frames are drawn with PIL at 2x (3840x2160), animated with ffmpeg zoompan,
narrated per segment with edge-tts, then concatenated and captioned.

Data and figures: Wang et al., arXiv:2410.07087 (preprint).
"""
import asyncio
import math
import os
import re
import shutil
import subprocess
import sys

import edge_tts
import imageio_ffmpeg
import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.abspath(os.path.join(BASE, "..", "figures"))
FRAMES = os.path.join(BASE, "frames")
AUDIO = os.path.join(BASE, "audio")
SEGS = os.path.join(BASE, "segments")
OUT = os.path.join(BASE, "TravelUAV_3min_promo.mp4")
FF = imageio_ffmpeg.get_ffmpeg_exe()

W, H, S = 1920, 1080, 2
M = 100

PAPER = (251, 250, 247)
WHITE = (255, 255, 255)
INK = (26, 29, 36)
MUTED = (95, 102, 115)
PRIMARY = (31, 78, 121)
DARK = (18, 50, 77)
ACCENT = (192, 57, 43)
LINE = (213, 219, 227)
SOFT = (242, 245, 248)
STEEL = (70, 110, 145)

FR = "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
FB = "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
FI = "/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf"

VOICE = "en-US-AndrewNeural"
RATE = "-8%"

FONT_CACHE = {}


def sc(v):
    return int(round(v * S))


def font(size, bold=False, italic=False):
    key = (size, bold, italic)
    if key not in FONT_CACHE:
        path = FB if bold else (FI if italic else FR)
        FONT_CACHE[key] = ImageFont.truetype(path, sc(size))
    return FONT_CACHE[key]


def wrap(s, size, bold, max_w):
    f = font(size, bold)
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= sc(max_w) or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def txt(d, x, y, s, size, color=INK, bold=False, italic=False, anchor="lt"):
    d.text((sc(x), sc(y)), s, font=font(size, bold, italic), fill=color, anchor=anchor)


def block(d, x, y, s, size, color=INK, bold=False, italic=False,
          max_w=None, line=1.18, align="left", anchor_y="lt"):
    lines = wrap(s, size, bold, max_w) if max_w else s.split("\n")
    for ln in lines:
        anchor = {"left": "lt", "center": "mt", "right": "rt"}[align]
        if anchor_y == "middle":
            anchor = anchor[0] + "m"
        d.text((sc(x), sc(y)), ln, font=font(size, bold, italic), fill=color, anchor=anchor)
        y += size * line
    return y


def frame(bg=PAPER):
    im = Image.new("RGB", (W * S, H * S), bg)
    return im, ImageDraw.Draw(im)


def rect(d, box, fill=WHITE, outline=None, width=2, radius=0):
    b = [sc(box[0]), sc(box[1]), sc(box[2]), sc(box[3])]
    if radius:
        d.rounded_rectangle(b, radius=sc(radius), fill=fill, outline=outline, width=sc(width))
    else:
        d.rectangle(b, fill=fill, outline=outline, width=sc(width))


def rule(d, x, y, w, color=PRIMARY, width=2):
    d.rectangle([sc(x), sc(y), sc(x + w), sc(y + width)], fill=color)


def header(d, idx, label, title):
    txt(d, M, 52, label, 24, ACCENT, bold=True)
    txt(d, W - M, 52, f"{idx:02d} / 10", 22, MUTED, anchor="rt")
    lines = wrap(title, 68, True, W - 2 * M)
    y = 100
    for ln in lines:
        txt(d, M, y, ln, 68, INK, bold=True)
        y += 80
    rule(d, M, y + 14, W - 2 * M, PRIMARY, 3)
    return y + 14 + 40


def put_image(canvas, d, path, box, pad=8):
    im = Image.open(path).convert("RGB")
    bw = (box[2] - box[0]) - 2 * pad
    bh = (box[3] - box[1]) - 2 * pad
    k = min(sc(bw) / im.width, sc(bh) / im.height)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    cx = sc((box[0] + box[2]) / 2) - im.width // 2
    cy = sc((box[1] + box[3]) / 2) - im.height // 2
    canvas.paste(im, (cx, cy))
    rect(d, box, None, LINE, 2)


def bezier(p0, p1, p2, p3, n=160):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
        y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def drone(d, x, y, size=34, color=PRIMARY, width=4):
    d.line([sc(x - size), sc(y), sc(x + size), sc(y)], fill=color, width=sc(width))
    d.line([sc(x), sc(y - size), sc(x), sc(y + size)], fill=color, width=sc(width))
    for dx, dy in ((-size, 0), (size, 0), (0, -size), (0, size)):
        r = size * 0.36
        d.ellipse([sc(x + dx - r), sc(y + dy - r), sc(x + dx + r), sc(y + dy + r)],
                  outline=color, width=sc(width))
    r = size * 0.28
    d.ellipse([sc(x - r), sc(y - r), sc(x + r), sc(y + r)], fill=color)


def bar(d, x, base_y, w, value, maxv, color, label=None, value_txt=None, hmax=360):
    hh = value / maxv * hmax
    d.rectangle([sc(x), sc(base_y - hh), sc(x + w), sc(base_y)], fill=color)
    if value_txt:
        txt(d, x + w / 2, base_y - hh - 38, value_txt, 24, INK, bold=True, anchor="mt")
    if label:
        txt(d, x + w / 2, base_y + 18, label, 22, MUTED, anchor="mt")


# ---------------------------------------------------------------- frames
def f_title():
    im, d = frame(DARK)
    d.rectangle([0, 0, W * S, sc(10)], fill=ACCENT)
    # faint trajectory
    pts = bezier((1120, 940), (1300, 560), (1520, 830), (1780, 330))
    for i in range(0, len(pts) - 1, 3):
        d.line([sc(pts[i][0]), sc(pts[i][1]), sc(pts[i + 1][0]), sc(pts[i + 1][1])],
               fill=(38, 78, 108), width=sc(3))
    for i in range(0, len(pts), 12):
        x, y = pts[i]
        d.ellipse([sc(x - 4), sc(y - 4), sc(x + 4), sc(y + 4)], fill=STEEL)
    tx, ty = pts[-1]
    d.ellipse([sc(tx - 34), sc(ty - 34), sc(tx + 34), sc(ty + 34)], outline=ACCENT, width=sc(4))
    d.ellipse([sc(tx - 10), sc(ty - 10), sc(tx + 10), sc(ty + 10)], fill=ACCENT)
    drone(d, 1120, 940, 30, (120, 160, 195), 3)

    txt(d, M, 96, "PREPRINT  ·  ARXIV:2410.07087", 24, (219, 154, 145), bold=True)
    txt(d, M, 250, "Towards Realistic", 94, WHITE, bold=True)
    txt(d, M, 356, "UAV Vision-Language Navigation", 94, WHITE, bold=True)
    txt(d, M, 516, "Platform, Benchmark, and Methodology", 46, (176, 202, 224))
    txt(d, M, 700, "Xiangyu Wang, Donglin Yang, Ziqin Wang, Hohin Kwan, Jinyu Chen,", 24, (206, 219, 232))
    txt(d, M, 738, "Wenjun Wu, Hongsheng Li, Yue Liao, Si Liu", 24, (206, 219, 232))
    txt(d, M, 800, "Beihang University  ·  MMLab, CUHK  ·  CPII", 22, (150, 178, 200))
    txt(d, M, 960, "3-minute paper preview  ·  demo, non-commercial use", 20, (130, 158, 182))
    txt(d, W - M, 960, "OpenUAV", 20, (130, 158, 182), anchor="rt")
    return im


def f_gap():
    im, d = frame()
    y = header(d, 2, "THE GAP", "Waypoints are not flight.")

    # left: discrete graph
    rect(d, [M, y, 860, 860], WHITE, LINE, 2, 10)
    txt(d, M + 34, y + 28, "GROUND VLN", 22, MUTED, bold=True)
    gx, gy = M + 90, y + 120
    nodes = []
    for r in range(3):
        for c in range(4):
            nodes.append((gx + c * 170, gy + r * 105))
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if j > i and abs(x1 - x2) <= 171 and abs(y1 - y2) <= 106:
                d.line([sc(x1), sc(y1), sc(x2), sc(y2)], fill=(210, 217, 226), width=sc(3))
    path = [nodes[0], nodes[1], nodes[5], nodes[6], nodes[10]]
    for a, b in zip(path, path[1:]):
        d.line([sc(a[0]), sc(a[1]), sc(b[0]), sc(b[1])], fill=PRIMARY, width=sc(7))
    for i, (x, yv) in enumerate(nodes):
        r = 15 if i in (0, 10) else 11
        col = ACCENT if i == 10 else (PRIMARY if i in path else (170, 180, 193))
        d.ellipse([sc(x - r), sc(yv - r), sc(x + r), sc(yv + r)], fill=col)
    txt(d, M + 34, y + 470, "discrete moves on a graph", 30, MUTED, italic=True)

    # right: continuous flight
    rect(d, [W / 2 + 20, y, W - M, 860], WHITE, LINE, 2, 10)
    txt(d, W / 2 + 54, y + 28, "UAV FLIGHT", 22, MUTED, bold=True)
    p0 = (W / 2 + 110, y + 390)
    p3 = (W - M - 120, y + 150)
    pts = bezier(p0, (W / 2 + 300, y + 470), (W - M - 380, y + 70), p3)
    for i in range(0, len(pts) - 1, 2):
        d.line([sc(pts[i][0]), sc(pts[i][1]), sc(pts[i + 1][0]), sc(pts[i + 1][1])],
               fill=ACCENT, width=sc(7))
    drone(d, p0[0], p0[1], 34, PRIMARY, 4)
    d.ellipse([sc(p3[0] - 30), sc(p3[1] - 30), sc(p3[0] + 30), sc(p3[1] + 30)],
              outline=ACCENT, width=sc(5))
    txt(d, W / 2 + 54, y + 470, "continuous 6-DoF motion", 30, MUTED, italic=True)

    chips = ["Inertia", "Attitude", "Obstacles"]
    for i, c in enumerate(chips):
        x = 490 + i * 340
        rect(d, [x, 866, x + 260, 922], SOFT, None, 0, 8)
        txt(d, x + 130, 894, c, 24, PRIMARY, bold=True, anchor="mm")
    return im


def f_platform():
    im, d = frame()
    y = header(d, 3, "01 · PLATFORM", "OpenUAV: closed-loop simulation")
    put_image(im, d, os.path.join(FIG, "fig1_platform.png"), [M, y, 1180, 830])
    txt(d, M, 846, "Closed-loop simulation  ·  human control interface  ·  configurable sensors", 21, MUTED, italic=True)

    items = [
        ("Unreal Engine 4 + AirSim", "high-fidelity rendering"),
        ("22 scenes", "diverse objects and lighting"),
        ("Parallel, reproducible", "deterministic resets"),
    ]
    for i, (a, b) in enumerate(items):
        yy = y + i * 160
        rect(d, [1240, yy, W - M, yy + 130], WHITE, LINE, 2, 8)
        d.rectangle([sc(1240), sc(yy), sc(1248), sc(yy + 130)], fill=ACCENT)
        txt(d, 1270, yy + 28, a, 30, PRIMARY, bold=True)
        txt(d, 1270, yy + 76, b, 21, MUTED)
    return im


def f_data():
    im, d = frame()
    y = header(d, 4, "02 · DATA", "12,149 human-flown trajectories")
    put_image(im, d, os.path.join(FIG, "fig2_dataset.png"), [M, y, 1150, 830])
    txt(d, M, 846, "Human pilots  ·  asynchronous sensors  ·  GPT-4 descriptions, human-checked", 21, MUTED, italic=True)

    stats = [("12,149", "trajectories"), ("6 DoF", "continuous flight"),
             ("89", "object categories"), ("22", "scenes")]
    for i, (n, lab) in enumerate(stats):
        x = 1210 + (i % 2) * 310
        yy = y + (i // 2) * 250
        txt(d, x, yy, n, 64, PRIMARY, bold=True)
        txt(d, x, yy + 80, lab, 21, MUTED)
    return im


def f_benchmark():
    im, d = frame()
    y = header(d, 5, "03 · BENCHMARK", "How much help should the assistant give?")
    levels = [
        ("L1", "Full guidance", "Continuous guidance to the target throughout the episode."),
        ("L2", "Coarse guidance", "Guidance only at critical states, when the policy is uncertain."),
        ("L3", "Avoidance", "Warns about collisions and hazards only."),
    ]
    for i, (n, name, desc) in enumerate(levels):
        x = M + i * 580
        rect(d, [x, y, x + 530, y + 480], WHITE, LINE, 2, 12)
        txt(d, x + 34, y + 36, n, 78, ACCENT, bold=True)
        txt(d, x + 34, y + 150, name, 36, PRIMARY, bold=True)
        block(d, x + 34, y + 215, desc, 24, INK, max_w=460, line=1.25)
        d.rectangle([sc(x + 34), sc(y + 438), sc(x + 120), sc(y + 443)], fill=PRIMARY)
    txt(d, M, 850, "Same scene, same policy \u2014 only the assistant changes.", 32, PRIMARY, bold=True)
    return im


def f_method():
    im, d = frame()
    y = header(d, 6, "04 · METHOD", "Decide far, then near.")
    put_image(im, d, os.path.join(FIG, "fig3_method.png"), [M, y, 1200, 780])

    steps = ["Instruction + 5 RGB views", "MLLM task representation",
             "Far target pose", "Fine 6-DoF trajectory"]
    for i, s in enumerate(steps):
        yy = y + i * 112
        rect(d, [1250, yy, W - M, yy + 88], WHITE, PRIMARY if i == 3 else LINE, 3 if i == 3 else 2, 8)
        txt(d, 1272, yy + 44, s, 23, PRIMARY if i == 3 else INK, bold=(i == 3), anchor="lm")
        if i < 3:
            d.line([sc(1420), sc(yy + 88), sc(1420), sc(yy + 112)], fill=MUTED, width=sc(3))
            d.polygon([(sc(1412), sc(yy + 104)), (sc(1428), sc(yy + 104)), (sc(1420), sc(yy + 116))],
                      fill=MUTED)
    txt(d, 1250, y + 510, "Backtracking data aggregation adds recovery trajectories.", 21, MUTED,
        italic=True, anchor="lt")
    return im


def f_results():
    im, d = frame()
    y = header(d, 7, "05 · RESULTS", "2.1\u00d7 the CMA baseline")
    txt(d, M, y + 10, "2.1\u00d7", 190, ACCENT, bold=True)
    txt(d, M + 6, y + 250, "success rate over the CMA baseline", 32, INK, bold=True)
    txt(d, M + 6, y + 305, "17.45% vs 8.37%  ·  same protocol", 26, MUTED)

    base = 720
    for v in (0, 20, 40):
        yy = base - v / 55 * 360
        d.line([sc(840), sc(yy), sc(1770), sc(yy)], fill=LINE, width=sc(2))
        txt(d, 826, yy, str(v), 18, MUTED, anchor="rm")
    bar(d, 900, base, 90, 8.37, 55, (150, 160, 174), "CMA", "8.37", 360)
    bar(d, 1010, base, 90, 17.45, 55, PRIMARY, "Ours-DA", "17.45", 360)
    bar(d, 1390, base, 90, 18.72, 55, (150, 160, 174), "CMA", "18.72", 360)
    bar(d, 1500, base, 90, 48.87, 55, ACCENT, "Ours-DA", "48.87", 360)
    txt(d, 950, base + 70, "Success rate", 24, INK, bold=True, anchor="mt")
    txt(d, 1440, base + 70, "OSR", 24, INK, bold=True, anchor="mt")
    txt(d, 840, base + 150, "Test Seen · L1 assistant · human SR 94.51%", 21, MUTED)
    return im


def f_generalization():
    im, d = frame()
    y = header(d, 8, "06 · GENERALIZATION", "New maps, new objects, no retraining")

    def panel(x, title, v1, v2, maxv):
        rect(d, [x, y, x + 820, y + 480], WHITE, LINE, 2, 12)
        txt(d, x + 34, y + 28, title, 28, MUTED, bold=True)
        for i, (lab, val, col) in enumerate((("CMA", v1, (150, 160, 174)), ("Ours", v2, PRIMARY))):
            yy = y + 130 + i * 150
            txt(d, x + 34, yy + 24, lab, 24, TEXTISH, bold=True, anchor="lm")
            d.rectangle([sc(x + 130), sc(yy), sc(x + 130 + 520), sc(yy + 54)], fill=(235, 239, 244))
            d.rectangle([sc(x + 130), sc(yy), sc(x + 130 + 520 * val / maxv), sc(yy + 54)], fill=col)
            txt(d, x + 670, yy + 24, f"{val:.2f}%", 28, INK, bold=True, anchor="lm")

    panel(M, "Unseen object categories", 9.06, 22.42, 25)
    panel(W / 2 + 20, "Unseen maps", 2.30, 4.18, 5)
    txt(d, M, 850, "Same policy. Zero retraining.", 34, ACCENT, bold=True)
    return im


TEXTISH = (70, 76, 86)


def f_rollouts():
    im, d = frame()
    y = header(d, 9, "07 · CLOSED-LOOP ROLLOUTS", "Search, re-observe, avoid")
    put_image(im, d, os.path.join(FIG, "fig4_qualitative.png"), [M, y, 1320, 840])
    txt(d, M, 856, "Closed-loop rollouts in held-out scenes. Simulation only.", 20, MUTED, italic=True)
    block(d, 1380, y + 20, "When the target is ambiguous, the policy re-observes.", 34, PRIMARY,
          bold=True, max_w=430, line=1.18)
    notes = ["Searches from the instruction and live views.",
             "Re-plans continuously in 6 DoF.",
             "Avoids obstacles along the route."]
    yy = y + 190
    for n in notes:
        d.ellipse([sc(1384), sc(yy + 11), sc(1396), sc(yy + 23)], fill=ACCENT)
        yy = block(d, 1410, yy, n, 21, INK, max_w=380, line=1.2) + 16
    return im


def f_outro():
    im, d = frame(DARK)
    d.rectangle([0, 0, W * S, sc(10)], fill=ACCENT)
    txt(d, M, 100, "OPENUAV  ·  UAV-NEED-HELP", 24, (219, 154, 145), bold=True)
    txt(d, M, 180, "One platform.", 78, WHITE, bold=True)
    txt(d, M, 270, "One benchmark.", 78, WHITE, bold=True)
    txt(d, M, 360, "One policy.", 78, WHITE, bold=True)
    items = [
        ("1", "OpenUAV", "Realistic, closed-loop UAV simulation."),
        ("2", "UAV-Need-Help", "12k trajectories, three assistance levels."),
        ("3", "Hierarchical LLM", "Far pose, then fine 6-DoF trajectory."),
    ]
    yy = 520
    for n, a, b in items:
        txt(d, M, yy, n, 28, (219, 154, 145), bold=True)
        txt(d, M + 44, yy - 4, a, 30, WHITE, bold=True)
        txt(d, M + 400, yy, b, 24, (186, 203, 220))
        yy += 86

    rect(d, [1450, 250, 1810, 610], WHITE, None, 0, 12)
    qr = Image.open(os.path.join(BASE, "qr_arxiv.png")).convert("RGB").resize((sc(320), sc(320)))
    im.paste(qr, (sc(1470), sc(270)))
    txt(d, 1630, 630, "arXiv:2410.07087", 24, WHITE, bold=True, anchor="mt")
    txt(d, 1630, 668, "prince687028.github.io/OpenUAV", 19, (160, 185, 206), anchor="mt")
    txt(d, M, 930, "Wang et al.  ·  figures from the arXiv preprint  ·  demo video, non-commercial use.",
        19, (140, 165, 188))
    return im


# ---------------------------------------------------------------- narration
SEGMENTS = [
    dict(id="title", draw=f_title, label="PREPRINT",
         narration="What if you could tell a drone \u201cfind the person in the brown jacket,\u201d "
                   "and it simply flew there? Vision-language navigation is still mostly flown as "
                   "waypoints. This is Towards Realistic UAV Vision-Language Navigation.",
         captions=["What if you could tell a drone",
                   "\u201cfind the person in the brown jacket,\u201d",
                   "and it simply flew there?",
                   "Vision-language navigation is still mostly flown as waypoints.",
                   "This is Towards Realistic",
                   "UAV Vision-Language Navigation."]),
    dict(id="gap", draw=f_gap, label="THE GAP",
         narration="Ground navigation assumes a graph of discrete moves. A drone lives in six "
                   "degrees of freedom: continuous motion, inertia, attitude, and obstacles. "
                   "Simplified simulators hide that gap, and real missions need continuous flight.",
         captions=["Ground navigation assumes a graph of discrete moves.",
                   "A drone lives in six degrees of freedom:",
                   "continuous motion, inertia, attitude, and obstacles.",
                   "Simplified simulators hide that gap.",
                   "Real missions need continuous flight."]),
    dict(id="platform", draw=f_platform, label="01 PLATFORM",
         narration="OpenUAV closes the loop. Built on Unreal Engine Four and AirSim, it provides "
                   "twenty-two high-fidelity scenes, configurable sensors, reproducible parallel "
                   "simulation, and a human control interface that records real continuous flights.",
         captions=["OpenUAV closes the loop.",
                   "Built on Unreal Engine Four and AirSim:",
                   "twenty-two high-fidelity scenes,",
                   "configurable sensors, reproducible parallel simulation,",
                   "and a human control interface that records continuous flights."]),
    dict(id="data", draw=f_data, label="02 DATA",
         narration="Human pilots fly each trajectory, while sensor streams are recorded "
                   "asynchronously. GPT-4 writes target descriptions, checked by humans. The result: "
                   "twelve thousand one hundred and forty-nine trajectories, across eighty-nine "
                   "object categories and twenty-two scenes.",
         captions=["Human pilots fly each trajectory;",
                   "sensor streams are recorded asynchronously.",
                   "GPT-4 writes target descriptions, checked by humans.",
                   "12,149 trajectories, 89 object categories, 22 scenes."]),
    dict(id="benchmark", draw=f_benchmark, label="03 BENCHMARK",
         narration="UAV-Need-Help turns assistance into a benchmark. Level one gives full guidance. "
                   "Level two helps only at critical states. Level three warns about collisions. "
                   "The policy must search from the description, the scene, and whatever help it receives.",
         captions=["UAV-Need-Help turns assistance into a benchmark.",
                   "Level one: full guidance.",
                   "Level two: help only at critical states.",
                   "Level three: collision warnings only.",
                   "Search from the description, the scene, and the available help."]),
    dict(id="method", draw=f_method, label="04 METHOD",
         narration="The method is hierarchical. An MLLM fuses the instruction with five RGB views. "
                   "It first predicts a far target pose, then a fine six-DoF trajectory in continuous "
                   "action space. Backtracking data aggregation adds recovery trajectories, improving "
                   "obstacle avoidance.",
         captions=["The method is hierarchical.",
                   "An MLLM fuses the instruction with five RGB views.",
                   "First: a far target pose.",
                   "Then: a fine six-DoF trajectory in continuous action space.",
                   "Backtracking data aggregation adds recovery trajectories."]),
    dict(id="results", draw=f_results, label="05 RESULTS",
         narration="On the seen test split with a level-one assistant, the policy reaches seventeen "
                   "point four five percent success, more than twice the CMA baseline. Under the same "
                   "protocol, OSR rises from eighteen point seven to forty-eight point nine percent.",
         captions=["Test Seen, level-one assistant:",
                   "17.45% success, more than twice the CMA baseline.",
                   "Under the same protocol,",
                   "OSR rises from 18.72% to 48.87%."]),
    dict(id="generalization", draw=f_generalization, label="06 GENERALIZATION",
         narration="The same policy transfers without retraining: twenty-two point four two percent "
                   "success on unseen object categories, and four point one eight percent on unseen "
                   "maps. Both are far above the baseline.",
         captions=["The same policy transfers without retraining.",
                   "22.42% success on unseen object categories.",
                   "4.18% success on unseen maps.",
                   "Both far above the baseline."]),
    dict(id="rollouts", draw=f_rollouts, label="07 ROLLOUTS",
         narration="In closed-loop rollouts, the drone searches, re-observes when the target is "
                   "ambiguous, and avoids obstacles. These are simulation results; real flights still "
                   "depend on airspace and site conditions.",
         captions=["In closed-loop rollouts, the drone searches,",
                   "re-observes when the target is ambiguous,",
                   "and avoids obstacles.",
                   "Simulation results; real flights depend on site conditions."]),
    dict(id="outro", draw=f_outro, label="OPENUAV",
         narration="OpenUAV, UAV-Need-Help, and a hierarchical navigation LLM: one platform, one "
                   "benchmark, one policy for continuous flight. Code, data, and benchmark are open. "
                   "Scan the code to read the preprint.",
         captions=["OpenUAV, UAV-Need-Help, and a hierarchical navigation LLM.",
                   "One platform. One benchmark. One policy.",
                   "Code, data, and benchmark are open.",
                   "Scan the code to read the preprint."]),
]


def ensure_dirs():
    for p in (FRAMES, AUDIO, SEGS):
        os.makedirs(p, exist_ok=True)


def make_qr():
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
    q.add_data("https://arxiv.org/abs/2410.07087")
    q.make(fit=True)
    q.make_image(fill_color="#1F4E79", back_color="#FFFFFF").save(os.path.join(BASE, "qr_arxiv.png"))


async def _tts(text, path):
    c = edge_tts.Communicate(text, VOICE, rate=RATE)
    await c.save(path)


def narrate():
    async def run():
        for i, seg in enumerate(SEGMENTS, 1):
            p = os.path.join(AUDIO, f"{i:02d}_{seg['id']}.mp3")
            if not os.path.exists(p):
                for attempt in range(3):
                    try:
                        await _tts(seg["narration"], p)
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise
                        await asyncio.sleep(2)
            seg["audio"] = p
    asyncio.run(run())


def audio_dur(path):
    out = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        raise RuntimeError("cannot read duration " + path)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def srt_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def main():
    ensure_dirs()
    make_qr()

    for i, seg in enumerate(SEGMENTS, 1):
        seg["frame"] = os.path.join(FRAMES, f"{i:02d}_{seg['id']}.png")
        seg["draw"]().save(seg["frame"])

    narrate()
    total_audio = sum(audio_dur(s["audio"]) for s in SEGMENTS)
    print(f"narration {total_audio:.1f}s across {len(SEGMENTS)} segments")

    # build segments
    starts, caps_srt, caps_ass = [], [], []
    cursor = 0.0
    for i, seg in enumerate(SEGMENTS, 1):
        adur = audio_dur(seg["audio"])
        hold = 1.2
        total = adur + hold
        seg["total"] = total
        starts.append(cursor)
        n = round(total * 30)
        out = os.path.join(SEGS, f"{i:02d}.mp4")
        zoom = "1+0.05*on/%d" % n if i % 2 else "1.05-0.05*on/%d" % n
        vf = (f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"d={n}:s=1920x1080:fps=30,"
              f"fade=t=in:st=0:d=0.35,fade=t=out:st={total - 0.4:.2f}:d=0.4,format=yuv420p")
        af = f"adelay=400:all=1,apad=pad_dur={hold:.1f}"
        cmd = [FF, "-y", "-i", seg["frame"],
               "-i", seg["audio"], "-filter_complex", f"[0:v]{vf}[v];[1:a]{af}[a]",
               "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-r", "30", out]
        subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # captions
        words = [len(c.split()) for c in seg["captions"]]
        wsum = sum(words)
        t = cursor + 0.4
        for c, w in zip(seg["captions"], words):
            d = adur * w / wsum
            caps_srt.append((t, t + d, c))
            caps_ass.append((t, t + d, c))
            t += d
        cursor += total

    total = cursor
    print(f"video {total:.1f}s")

    with open(os.path.join(BASE, "list.txt"), "w") as f:
        for i in range(1, len(SEGMENTS) + 1):
            f.write(f"file 'segments/{i:02d}.mp4'\n")
    silent = os.path.join(BASE, "silent.mp4")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(BASE, "list.txt"), "-c", "copy", silent],
                   check=True, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # srt
    with open(os.path.join(BASE, "TravelUAV_3min.srt"), "w", encoding="utf-8") as f:
        for i, (a, b, c) in enumerate(caps_srt, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{c}\n\n")

    # ass: two-line wrap, bottom safe area
    with open(os.path.join(BASE, "subs.ass"), "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
                "WrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
                "[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
                "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                "Style: Cap,Liberation Sans,38,&H00FFFFFF,&H000000FF,&H00101010,&H96000000,"
                "0,0,0,0,100,100,0,0,3,10,0,2,120,120,56,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a, b, c in caps_ass:
            lines = wrap(c, 38, False, 1560)
            if len(lines) > 2:
                mid = math.ceil(len(lines) / 2)
                text = r"\N".join([" ".join(lines[:mid]), " ".join(lines[mid:])])
            else:
                text = r"\N".join(lines)
            f.write(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{text}\n")

    cmd = [FF, "-y", "-i", silent, "-vf", "ass=subs.ass",
           "-c:v", "libx264", "-preset", "medium", "-crf", "24",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
           "-movflags", "+faststart", OUT]
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("saved", OUT, "size", round(os.path.getsize(OUT) / 1e6, 1), "MB", "duration", round(total, 1), "s")


if __name__ == "__main__":
    main()
