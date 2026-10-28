#!/usr/bin/env python3
"""生成商业 PPT 背景图（PIL，离线）：暖纸白 / 画廊深色 / 品牌 tint。

商业编辑风的背景不喧宾夺主：纸张颗粒、极淡网格、柔和光晕，内容页必须"安静"。

用法:
  python3 make_backgrounds.py -o bg/ --style editorial
  python3 make_backgrounds.py -o bg/ --style premium
  python3 make_backgrounds.py -o bg/ --style brand --brand 1F4E79
  python3 make_backgrounds.py -o bg/ --all          # editorial + premium

每种风格输出 3 张 2560x1440 PNG:
  {style}_cover.png    封面/全幅页：光晕 + 颗粒 + 极淡网格
  {style}_section.png  章节页：一侧柔光 + 大留白
  {style}_content.png  内容页：仅颗粒与极淡网格，文字为王
依赖: pip install pillow
"""
import argparse
import os
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 2560, 1440


def hexrgb(s):
    s = s.strip().lstrip("#")
    if len(s) != 6:
        raise ValueError(f"invalid hex color: {s}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(stops):
    """三段纵向渐变。stops = [(r,g,b) x3]，上→中→下。"""
    img = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(img)
    a, b, c = stops
    for y in range(H):
        t = y / (H - 1)
        if t < 0.5:
            col = mix(a, b, t / 0.5)
        else:
            col = mix(b, c, (t - 0.5) / 0.5)
        dr.line([(0, y), (W, y)], fill=col)
    return img.convert("RGBA")


def radial_glow(img, rgb, cx, cy, radius, peak=70):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    dr.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
               fill=rgb + (peak,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.6))
    return Image.alpha_composite(img, layer)


def vignette(img, strength=26):
    """底部轻微压暗，托住页脚。"""
    layer = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(layer)
    for y in range(int(H * 0.55), H):
        t = (y - H * 0.55) / (H * 0.45)
        dr.line([(0, y), (W, y)], fill=int(strength * t * t))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    dark.putalpha(layer)
    return Image.alpha_composite(img, dark)


def grain(img, sigma=5, alpha=7):
    noise = Image.effect_noise((W, H), sigma).convert("L")
    layer = Image.new("RGBA", (W, H))
    layer.paste(Image.merge("RGB", (noise, noise, noise)).convert("RGBA"),
                (0, 0))
    layer.putalpha(alpha)
    return Image.alpha_composite(img, layer)


def grid(img, rgb, step=80, alpha=6, major=320):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    for x in range(0, W, step):
        a = alpha * 2 if x % major == 0 else alpha
        dr.line([(x, 0), (x, H)], fill=rgb + (a,), width=1)
    for y in range(0, H, step):
        a = alpha * 2 if y % major == 0 else alpha
        dr.line([(0, y), (W, y)], fill=rgb + (a,), width=1)
    return Image.alpha_composite(img, layer)


def editorial(name, seed=11):
    paper = hexrgb("F7F5F0")
    warm = hexrgb("E8DFCE")
    ink = hexrgb("17191C")
    img = gradient([paper, paper, mix(paper, warm, 0.35)])
    if name == "cover":
        img = radial_glow(img, warm, int(W * 0.82), int(H * 0.18), 760, 56)
        img = radial_glow(img, paper, int(W * 0.12), int(H * 0.9), 620, 44)
    elif name == "section":
        img = radial_glow(img, warm, int(W * 0.1), int(H * 0.45), 700, 44)
    img = grid(img, ink, step=80, alpha=4, major=320)
    img = grain(img, sigma=4, alpha=6)
    if name != "content":
        img = vignette(img, 18)
    return img.convert("RGB")


def premium(name, seed=11):
    base = hexrgb("0E1110")
    top = hexrgb("1A201D")
    bot = hexrgb("080A09")
    accent = hexrgb("C96A3F")
    img = gradient([top, base, bot])
    if name == "cover":
        img = radial_glow(img, accent, int(W * 0.86), int(H * 0.2), 620, 40)
        img = radial_glow(img, hexrgb("F4F1EA"), int(W * 0.18), int(H * 0.78), 820, 22)
    elif name == "section":
        img = radial_glow(img, accent, int(W * 0.12), int(H * 0.5), 640, 32)
    img = grain(img, sigma=6, alpha=8)
    if name != "content":
        img = vignette(img, 34)
    return img.convert("RGB")


def brand(name, hex_color):
    b = hexrgb(hex_color)
    white = (255, 255, 255)
    p1 = mix(b, white, 0.94)
    p2 = mix(b, white, 0.87)
    img = gradient([p1, p1, mix(p2, hexrgb("E9E4D8"), 0.35)])
    if name == "cover":
        img = radial_glow(img, b, int(W * 0.85), int(H * 0.15), 780, 34)
        img = radial_glow(img, white, int(W * 0.15), int(H * 0.9), 640, 60)
    elif name == "section":
        img = radial_glow(img, b, int(W * 0.1), int(H * 0.5), 720, 26)
    img = grid(img, mix(b, hexrgb("17191C"), 0.5), step=80, alpha=4, major=320)
    img = grain(img, sigma=4, alpha=6)
    if name != "content":
        img = vignette(img, 16)
    return img.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="bg")
    ap.add_argument("--style", default="editorial",
                    choices=["editorial", "premium", "brand"])
    ap.add_argument("--brand", default=None, help="品牌主色 hex（--style brand 必填）")
    ap.add_argument("--all", action="store_true", help="生成 editorial + premium")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    jobs = []
    if args.all:
        jobs = [("editorial", editorial), ("premium", premium)]
    elif args.style == "brand":
        if not args.brand:
            ap.error("--style brand 需要 --brand 1F4E79")
        jobs = [("brand", lambda n: brand(n, args.brand))]
    else:
        jobs = [(args.style, editorial if args.style == "editorial" else premium)]

    for style, fn in jobs:
        for name in ("cover", "section", "content"):
            img = fn(name)
            path = os.path.join(args.out, f"{style}_{name}.png")
            img.save(path, optimize=True)
            print(path)


if __name__ == "__main__":
    main()
