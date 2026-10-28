#!/usr/bin/env python3
"""从 logo 提取品牌色板，并生成深/浅底单色 logo。

用法:
  python3 brand_kit.py logo.png -o brand/
  python3 brand_kit.py logo.png -o brand/ --primary 1F4E79   # 单色 logo 或指定官方色

产出:
  brand/palette.json       primary / secondary / accent / ink / paper + tint/shade
  brand/palette.png        1600x400 色板预览（人眼复核）
  brand/logo_ink.png       单色深版（浅底用）
  brand/logo_white.png     单色白版（深底用）

提取逻辑：去掉近白/近黑背景 → 量化取主色 → 按"占比 × 饱和度"排序 → 挑主色与次色。
渐变/灰调/含照片的 logo 可能提取不准，务必人眼复核；品牌手册有官方色时以手册为准。
依赖: pip install pillow
"""
import argparse
import colorsys
import json
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont

INK = "#17191C"
PAPER = "#F7F5F0"
FALLBACK = "#B4552D"


def hexrgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def rgbhex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def lum(rgb):
    r, g, b = [c / 255 for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def sat(rgb):
    r, g, b = [c / 255 for c in rgb]
    mx, mn = max(r, g, b), min(r, g, b)
    return 0 if mx == 0 else (mx - mn) / mx


def hue(rgb):
    r, g, b = [c / 255 for c in rgb]
    h, _, _ = colorsys.rgb_to_hsv(r, g, b)
    return h * 360


def alpha_mask(im):
    """取 alpha；无 alpha 时从四角 flood fill 抠掉外部白底（保留 logo 内部白色）。"""
    im = im.convert("RGBA")
    if im.getchannel("A").getextrema()[0] < 250:
        return im
    rgb = im.convert("RGB")
    w, h = rgb.size
    sentinel = (255, 0, 255)
    for pt in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        try:
            ImageDraw.floodfill(rgb, pt, sentinel, thresh=18)
        except ValueError:
            pass
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, sentinel))
    r, g, b = diff.split()
    total = ImageChops.add(ImageChops.add(r, g), b)
    alpha = total.point(lambda v: 0 if v < 6 else 255)
    im.putalpha(alpha)
    return im


def mono(im, color, out):
    mask = im.getchannel("A")
    solid = Image.new("RGBA", im.size, hexrgb(color) + (255,))
    solid.putalpha(mask)
    bbox = solid.getbbox()
    if bbox:
        solid = solid.crop(bbox)
    w, h = solid.size
    if w > 1600:
        solid = solid.resize((1600, int(h * 1600 / w)), Image.LANCZOS)
    solid.save(out)
    return solid.size


def extract(im, k=10):
    flat = Image.new("RGB", im.size, (255, 255, 255))
    flat.paste(im, mask=im.getchannel("A"))
    flat.thumbnail((240, 240), Image.LANCZOS)
    q = flat.quantize(colors=k, method=Image.MEDIANCUT)
    pal = q.getpalette()[: k * 3]
    counts = sorted(q.getcolors(), reverse=True)
    cands = []
    for count, idx in counts:
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        L, S = lum(rgb), sat(rgb)
        if L > 0.93 or L < 0.12:
            continue
        if S < 0.22:
            continue
        cands.append((count * (0.25 + S), rgb, count, S))
    cands.sort(reverse=True)
    return cands


def pick(cands, exclude_hue=None):
    for _, rgb, _, _ in cands:
        if exclude_hue is None:
            return rgb
        dh = abs(hue(rgb) - exclude_hue)
        dh = min(dh, 360 - dh)
        if dh > 28:
            return rgb
    return None


def logo_preview(ink_path, white_path, path):
    W, H = 1600, 400
    img = Image.new("RGB", (W, H), hexrgb(PAPER))
    dr = ImageDraw.Draw(img)
    dr.rectangle([W // 2, 0, W, H], fill=hexrgb(INK))
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        label = ImageFont.truetype(font_path, 18)
    except OSError:
        label = ImageFont.load_default()
    for i, (src, caption, color) in enumerate([
        (ink_path, "ON LIGHT", hexrgb("#6F6A61")),
        (white_path, "ON DARK", hexrgb("#A8A399")),
    ]):
        logo = Image.open(src).convert("RGBA")
        logo.thumbnail((620, 220), Image.LANCZOS)
        cx = W // 4 + i * W // 2
        img.paste(logo, (cx - logo.width // 2, (H - logo.height) // 2 - 12), logo)
        dr.text((cx - 46, H - 52), caption, fill=color, font=label)
    img.save(path)


def palette_png(colors, path):
    W, H = 1600, 400
    img = Image.new("RGB", (W, H), hexrgb(PAPER))
    dr = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        f_big = ImageFont.truetype(font_path, 26)
        f_small = ImageFont.truetype(font_path, 18)
    except OSError:
        f_big = f_small = ImageFont.load_default()
    n = len(colors)
    sw = W // n
    for i, (role, hx) in enumerate(colors):
        rgb = hexrgb(hx)
        x0 = i * sw
        dr.rectangle([x0, 0, x0 + sw, H - 92], fill=rgb)
        text_color = (255, 255, 255) if lum(rgb) < 0.55 else hexrgb(INK)
        dr.text((x0 + 24, H - 78), role.upper(), fill=hexrgb(INK), font=f_small)
        dr.text((x0 + 24, H - 84 - 34), hx, fill=text_color, font=f_big)
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logo")
    ap.add_argument("-o", "--out", default="brand")
    ap.add_argument("--primary", default=None, help="官方品牌主色；给定时覆盖提取结果")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    src = alpha_mask(Image.open(args.logo))
    bbox = src.getchannel("A").getbbox()
    if bbox:
        src = src.crop(bbox)

    ink_path = os.path.join(args.out, "logo_ink.png")
    white_path = os.path.join(args.out, "logo_white.png")
    mono(src, INK, ink_path)
    mono(src, "#FFFFFF", white_path)

    cands = extract(src)
    if args.primary:
        primary = hexrgb(args.primary)
        note = "使用 --primary 指定的官方色"
    elif cands:
        primary = cands[0][1]
        note = "从 logo 提取"
    else:
        primary = hexrgb(FALLBACK)
        note = "logo 无可用彩色，回退默认色；请用 --primary 指定官方色"

    secondary = pick(cands, exclude_hue=hue(primary)) if cands else None
    if secondary is None:
        secondary = mix(primary, hexrgb(INK), 0.35)
    accent = secondary

    def hx(rgb):
        return rgbhex(rgb)

    data = {
        "source": os.path.abspath(args.logo),
        "note": note,
        "primary": hx(primary),
        "secondary": hx(secondary),
        "accent": hx(accent),
        "ink": INK,
        "paper": PAPER,
        "tint90": hx(mix(primary, (255, 255, 255), 0.90)),
        "tint75": hx(mix(primary, (255, 255, 255), 0.75)),
        "tint60": hx(mix(primary, (255, 255, 255), 0.60)),
        "shade20": hx(mix(primary, (0, 0, 0), 0.20)),
    }
    with open(os.path.join(args.out, "palette.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    palette_png([
        ("primary", data["primary"]), ("secondary", data["secondary"]),
        ("tint90", data["tint90"]), ("tint75", data["tint75"]),
        ("ink", data["ink"]), ("paper", data["paper"]),
    ], os.path.join(args.out, "palette.png"))
    logo_preview(ink_path, white_path, os.path.join(args.out, "logo_preview.png"))

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
