#!/usr/bin/env python3
"""生成竞赛 PPT 科技风背景图（PIL，离线）：深空渐变 + 粒子星点 + 光晕。

pptxgenjs 不支持原生渐变填充，竞赛风"科技蓝渐变+星空"背景必须预生成 PNG。

用法:
  python3 make_backgrounds.py -o bg/ [--style techblue|red|light] [--all]
  # --all 一次生成三种风格；默认只生成指定风格

每风格输出 3 张 2560x1440 PNG:
  {style}_cover.png    封面：浓粒子 + 双侧大光晕
  {style}_section.png  章节过渡页：左侧光晕
  {style}_content.png  内容页：极淡粒子，底部略深（衬托顶部导航文字）
依赖: pip install pillow
"""
import argparse
import os
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 2560, 1440

STYLES = {
    "techblue": {
        "stops": [(10, 28, 62), (18, 52, 106), (8, 22, 52)],   # 上→中→下
        "particle": (168, 205, 255),
        "glow": (56, 140, 255),
        "card": (18, 42, 84),
    },
    "red": {
        "stops": [(86, 8, 18), (146, 18, 34), (64, 5, 13)],
        "particle": (255, 216, 150),
        "glow": (255, 96, 92),
        "card": (110, 14, 26),
    },
    "light": {
        "stops": [(255, 255, 255), (241, 246, 252), (226, 236, 249)],
        "particle": (140, 172, 220),
        "glow": (170, 205, 255),
        "card": (235, 242, 250),
    },
}


def vertical_gradient(stops):
    img = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(img)
    (a, b, c) = stops
    for y in range(H):
        t = y / (H - 1)
        if t < 0.5:
            k = t / 0.5
            col = tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
        else:
            k = (t - 0.5) / 0.5
            col = tuple(int(b[i] + (c[i] - b[i]) * k) for i in range(3))
        dr.line([(0, y), (W, y)], fill=col)
    return img.convert("RGBA")


def particles(img, rgb, count, rmax=3, alpha=(50, 170), ymin=0, ymax=H):
    rnd = random.Random(42)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    for _ in range(count):
        x = rnd.uniform(0, W)
        y = rnd.uniform(ymin, ymax)
        r = rnd.uniform(0.6, rmax)
        a = rnd.randint(*alpha)
        dr.ellipse([x - r, y - r, x + r, y + r], fill=rgb + (a,))
    return Image.alpha_composite(img, layer)


def glow(img, rgb, cx, cy, radius, peak=110):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    dr.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
               fill=rgb + (peak,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    return Image.alpha_composite(img, layer)


def thin_lines(img, rgb, n=4):
    """若干极淡的斜向光轨线（科技感），透明度很低不抢戏。"""
    rnd = random.Random(7)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    for _ in range(n):
        x0 = rnd.uniform(-0.2 * W, 1.1 * W)
        y0 = rnd.uniform(0, 0.5 * H)
        length = rnd.uniform(0.3 * W, 0.8 * W)
        ang = rnd.uniform(0.25, 0.45)
        dr.line([(x0, y0), (x0 + length, y0 + length * ang)],
                fill=rgb + (rnd.randint(10, 26),), width=rnd.randint(1, 2))
    return Image.alpha_composite(img, layer)


def build(style, name, spec):
    img = vertical_gradient(spec["stops"])
    p, g = spec["particle"], spec["glow"]
    if name == "cover":
        img = glow(img, g, int(W * 0.88), int(H * 0.16), 520, 120)
        img = glow(img, g, int(W * 0.10), int(H * 0.95), 460, 90)
        img = particles(img, p, 520, rmax=3.2)
        img = thin_lines(img, p, 5)
    elif name == "section":
        img = glow(img, g, int(W * 0.16), int(H * 0.5), 500, 100)
        img = particles(img, p, 300, rmax=2.6, ymax=int(H * 0.8))
    else:  # content —— 内容页背景必须安静，文字为王
        img = particles(img, p, 90, rmax=1.8, alpha=(28, 70))
        img = glow(img, g, int(W * 0.95), int(H * 1.02), 380, 46)
    out = img.convert("RGB")
    out.save(os.path.join(OUT, f"{style}_{name}.png"), optimize=True)
    print(f"{style}_{name}.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="bg")
    ap.add_argument("--style", default="techblue", choices=list(STYLES))
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    global OUT
    OUT = args.out
    os.makedirs(OUT, exist_ok=True)
    for st in (STYLES if args.all else [args.style]):
        for kind in ("cover", "section", "content"):
            build(st, kind, STYLES[st])
