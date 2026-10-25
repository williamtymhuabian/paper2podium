#!/usr/bin/env python3
"""竞赛版 TravelUAV 路演 deck v3 —— 国创赛国赛风格。
v3 要点：① 无独立章节页（17 页），章节感由顶部导航 + 标题角标承载；
② 每页一种版式原型：大图左出血 / 数字横带 / 垂直对比 / 错位台阶 / 拼图 / 三段变奏 /
成果链 / 嵌套矩形 / 矩阵表 / 飞轮图 / 开放列表，杜绝全场卡片格子。
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
FONT, FN = "微软雅黑", "Arial"
W, H, M = 13.33, 7.5, 0.55
NAVS = ["市场痛点", "产品方案", "核心技术", "商业模式", "团队价值", "发展规划"]

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
tb(s, M, 0.55, 10, 0.4, "中国国际大学生创新大赛（高教主赛道）· 项目路演", size=14, color=CYAN)
tb(s, M, 2.35, 12.2, 1.9, [
    [("天行 TravelUAV", {"size": 48, "bold": True})],
    [("会听懂的无人机 · 真实世界视觉-语言导航平台", {"size": 22, "bold": True, "color": RGBColor(0xE3, 0xEE, 0xFB)})],
], leading=1.18)
tb(s, M, 4.35, 11.5, 0.5, "基于多模态大模型，让无人机听懂人类语言，在真实三维空域中自主搜索目标", size=16, color=WHITE)
ln = s.shapes.add_connector(1, Inches(M), Inches(5.1), Inches(M + 3.2), Inches(5.1))
ln.line.color.rgb = ACCENT; ln.line.width = Pt(2)
tb(s, M, 5.3, 12.2, 0.8, [
    [("12,149 条真实专家轨迹　·　6-DoF 飞行动力学　·　SR 超基线 +109%", {"size": 15, "bold": True, "color": ACCENT})],
    [("北京航空航天大学 ColaLab × 香港中文大学 MMLab　｜　指导教师：刘偲 教授 · 廖裕渊 研究员 · 李嘉胜 教授", {"size": 13, "color": MUTED})],
], leading=1.5)

# ══════════ P2 汇报内容：左列表 + 右大图（非对称分栏） ══════════
s = slide(nav="市场痛点")
tb(s, M, 0.72, 5, 0.6, "汇报内容", size=30, bold=True)
items = [("01", "市场痛点", "万亿赛道 · 41 倍能力鸿沟"), ("02", "产品方案", "四位一体 + 实飞演示"),
         ("03", "核心技术", "三大创新 · 成果落地"), ("04", "商业模式", "TAM/SAM/SOM · 三线收入"),
         ("05", "团队价值", "师生共创 · 社会价值"), ("06", "发展规划", "三年三步走")]
y = 1.72
for n, t, d in items:
    tb(s, M, y, 0.75, 0.45, n, size=20, bold=True, color=CYAN, font=FN)
    tb(s, M + 0.8, y - 0.02, 2.2, 0.45, t, size=18, bold=True)
    tb(s, M + 0.8, y + 0.38, 4.2, 0.35, d, size=13, color=MUTED)
    y += 0.87
pic(s, os.path.join(WEB, "show.png"), x=6.1, y=1.35, w=6.68)
tb(s, 6.1, 1.35 + 6.68 * 859 / 1135 + 0.1, 6.68, 0.35, "OpenUAV 平台高保真城市场景库（22 类场景 · 89 类物体）",
   size=12, color=MUTED, align=PP_ALIGN.CENTER)

# ══════════ P3 市场机会：数字横带 + 全宽场景条（开放版式） ══════════
s = slide(nav="市场痛点")
head(s, "01 · 市场痛点", "政策东风：低空经济成为国家战略性新兴产业")
nums = [("1.5 万亿", "2025E 低空经济规模", "中国民航局", ACCENT),
        ("3.5 万亿", "2035E 预期规模", "中国民航局", CYAN),
        ("1761 亿", "2025 民用无人机整机产值 · 工业级占比 >70%", "工信部", CYAN)]
band_y = 1.72
for i, (v, l, src, c) in enumerate(nums):
    cx = M + i * 4.14
    tb(s, cx, band_y, 3.95, 0.85, v, size=44, bold=True, color=c, align=PP_ALIGN.CENTER, font=FN)
    tb(s, cx + 0.2, band_y + 0.95, 3.55, 0.55, l, size=14, color=WHITE, align=PP_ALIGN.CENTER, leading=1.15)
    tb(s, cx, band_y + 1.5, 3.95, 0.3, f"来源：{src}", size=11.5, color=MUTED, align=PP_ALIGN.CENTER)
    if i < 2: vhair(s, cx + 4.02, band_y + 0.15, 1.6)
pic(s, os.path.join(FIG, "derived", "market_strip.jpg"), x=M, y=3.85, w=12.23, border=False)
tb(s, M, 6.35, 12.2, 0.5, [[("切入点：", {"bold": True, "color": ACCENT}),
   ("无人机应用全面铺开，但自动化是瓶颈——「语言交互 + 自主搜索」是智能化的下一跳", {})]], size=15)
src_line(s, "数据来源：中国民航局（新华社 2025-12）、工信部 2025 民用无人机产值公报；图为 OpenUAV 平台城市场景")

# ══════════ P4 痛点：左垂直大数字对比 + 右错位台阶 ══════════
s = slide(nav="市场痛点")
head(s, "01 · 市场痛点", "核心痛点：无人机「听不懂、飞不真、学不会」")
vhair(s, 6.3, 1.55, 5.3)
tb(s, M, 1.5, 5.5, 0.35, "同一段任务指令下的成功率", size=15, color=MUTED)
tb(s, M, 1.9, 5.5, 1.05, "94.5%", size=58, bold=True, color=CYAN, font=FN)
tb(s, M, 2.98, 5.5, 0.4, "人类飞手", size=16, color=MUTED)
tb(s, M, 3.38, 5.5, 1.05, "2.27%", size=58, bold=True, color=ACCENT, font=FN)
tb(s, M, 4.46, 5.5, 0.4, "固定动作程序", size=16, color=MUTED)
pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(M), Inches(4.98), Inches(3.4), Inches(0.62))
pill.adjustments[0] = 0.5; pill.fill.solid(); pill.fill.fore_color.rgb = ACCENT
_alpha(pill.fill, 18000); pill.line.color.rgb = ACCENT; pill.line.width = Pt(1); pill.shadow.inherit = False
tb(s, M, 5.125, 3.4, 0.4, "41 倍能力鸿沟", size=17, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
# 底部示意：离散动作 vs 连续轨迹（原生图形）
from math import sin as _sin
card(s, M, 5.68, 5.9, 1.38, alpha_pct=15000)
vhair(s, M + 3.0, 5.82, 1.1)
tb(s, M + 0.22, 5.8, 2.6, 0.3, "传统：离散动作", size=12, color=MUTED)
for _i in range(5):
    _sq = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M + 0.28 + _i * 0.5), Inches(6.72 - _i * 0.13), Inches(0.34), Inches(0.26))
    _sq.fill.solid(); _sq.fill.fore_color.rgb = PRIMARY; _alpha(_sq.fill, 55000)
    _sq.line.fill.background(); _sq.shadow.inherit = False
tb(s, M + 0.22, 6.85, 2.7, 0.3, "上下左右跳格 · 脱离真实飞行", size=10.5, color=MUTED)
tb(s, M + 3.22, 5.8, 2.6, 0.3, "天行：6-DoF 连续轨迹", size=12, color=CYAN, bold=True)
for _i in range(22):
    _dx = M + 3.25 + _i * 0.12
    _dy = 6.5 + 0.3 * _sin(_i * 0.58 + 0.4)
    _dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(_dx), Inches(_dy), Inches(0.09), Inches(0.09))
    _dot.fill.solid(); _dot.fill.fore_color.rgb = CYAN; _dot.line.fill.background(); _dot.shadow.inherit = False
tb(s, M + 3.22, 6.85, 2.6, 0.3, "俯仰·翻滚·偏航连续输出", size=10.5, color=MUTED)
pains = [("01", "听不懂", "语言指令无法直接驱动作业，依赖专业飞手遥控"),
         ("02", "飞不真", "离散动作设定脱离真实 6-DoF 飞行动力学"),
         ("03", "学不会", "行业没有真实轨迹数据，模型学不到专家经验")]
y = 1.6
for i, (n, k, v) in enumerate(pains):
    x = 6.9 + i * 0.38  # 错位台阶
    tb(s, x, y, 0.8, 0.5, n, size=26, bold=True, color=PRIMARY, font=FN)
    tb(s, x + 0.95, y + 0.02, 2.4, 0.5, k, size=22, bold=True)
    tb(s, x + 0.95, y + 0.58, 4.9 - i * 0.38, 0.7, v, size=14, color=MUTED, leading=1.2)
    if i < 2: hair(s, 6.9, y + 1.5, 5.9)
    y += 1.78
src_line(s, "数据来源：arXiv:2410.07087, Table 2（UAV-Need-Help 基准）")

# ══════════ P5 产品总览：大图左出血 + 右侧开放特性列 ══════════
s = slide(nav="产品方案")
head(s, "02 · 产品方案", "天行 TravelUAV：无人机自主导航全栈方案")
pic(s, os.path.join(WEB, "header2.png"), x=0, y=1.62, w=9.35, border=False)
img_label_chip(s, 0.25, 1.8, "平台实况")
feats = [("仿真平台 OpenUAV", "22 场景 · 6-DoF 物理飞控 · 开源"),
         ("专家轨迹数据集", "12,149 条 · GPT-4 描述 · 人工复核"),
         ("助导任务基准", "L1/L2/L3 三级 · 模拟人机协作"),
         ("导航大模型", "Vicuna-7B 底座 · 分层轨迹生成")]
y = 1.7
for t, d in feats:
    tb(s, 9.75, y, 3.1, 0.4, t, size=16, bold=True)
    tb(s, 9.75, y + 0.42, 3.15, 0.65, d, size=12.5, color=MUTED, leading=1.2)
    y += 1.28
    if y < 6.3: hair(s, 9.75, y - 0.18, 3.05)
tb(s, 0, 6.15, 9.35, 0.5, [[("四位一体、全部开源", {"bold": True, "color": ACCENT}),
   ("：让研究者与行业直接复现、扩展、二次开发", {})]], size=14.5, align=PP_ALIGN.CENTER)

# ══════════ P6 产品演示：飞行序列 + 指令引用条 + 三步开放流 ══════════
s = slide(nav="产品方案")
head(s, "02 · 产品方案", "真实演示：听懂一段话，自主找到目标")
pic(s, os.path.join(FIG, "scenes", "demo_strip_1.png"), x=M, y=1.55, w=12.23)
tb(s, M, 3.82, 12.23, 0.35, "OpenUAV 闭环仿真：12 帧连续飞行（成功案例：按指令搜索黄色车辆）",
   size=12, color=MUTED, align=PP_ALIGN.CENTER)
qb = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(4.3), Inches(0.07), Inches(1.15))
qb.fill.solid(); qb.fill.fore_color.rgb = CYAN; qb.line.fill.background(); qb.shadow.inherit = False
tb(s, M + 0.25, 4.28, 7.3, 0.35, "输入指令（示例）", size=13, color=CYAN, bold=True)
tb(s, M + 0.25, 4.63, 7.3, 0.8,
   "「目标在无人机左前方……画面中央有一辆黄色轿车，周边是多栋不同风格的多层建筑，请控制无人机找到它。」",
   size=14, color=WHITE, leading=1.2)
tb(s, 8.6, 4.28, 4.15, 1.2, [
    [("端到端", {"size": 24, "bold": True, "color": ACCENT}),
     ("：图像+语言直接到连续轨迹，无人工规则映射", {"size": 13, "color": MUTED})],
], leading=1.3, anchor=MSO_ANCHOR.MIDDLE)
hair(s, M, 5.75, 12.23)
steps = [("理解指令", "MLLM 解析目标与环境"), ("空中搜索", "分层规划 6-DoF 轨迹"), ("精准降落", "检出目标即降落")]
x = M
for i, (t, d) in enumerate(steps):
    tb(s, x, 5.95, 3.6, 0.45, f"{i+1}　{t}", size=18, bold=True, color=ACCENT)
    tb(s, x + 0.55, 6.48, 3.2, 0.4, d, size=12.5, color=MUTED)
    if i < 2:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 3.55), Inches(6.1), Inches(0.35), Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb = PRIMARY; ar.line.fill.background(); ar.shadow.inherit = False
    x += 4.1
src_line(s, "演示画面来源：arXiv:2410.07087, Fig.4（OpenUAV 平台渲染）")

# ══════════ P7 场景能力：非对称拼图 + 右下注解列 ══════════
s = slide(nav="产品方案")
head(s, "02 · 产品方案", "22 类高保真场景，覆盖城市到自然")
pic(s, os.path.join(FIG, "scenes", "scene_3.png"), x=0, y=1.6, w=7.35, border=False)
img_label_chip(s, 0.25, 1.78, "城市场景")
pic(s, os.path.join(FIG, "scenes", "scene_5.png"), x=7.6, y=1.6, w=5.18, border=False)
img_label_chip(s, 7.85, 1.78, "自然地貌")
tb(s, 7.6, 4.62, 5.2, 2.0, [
    [("高保真与动态性", {"size": 15, "bold": True, "color": ACCENT})],
    [("• UE4 渲染：动态光照、植被摆动", {"size": 13.5, "color": MUTED})],
    [("• 89 类物体资产，运行时 API 自动摆放", {"size": 13.5, "color": MUTED})],
    [("• 乡村 / 工业园区等全类型覆盖（附录 A）", {"size": 13.5, "color": MUTED})],
    [("• 为 Sim-to-Real 真机迁移打底", {"size": 12.5, "color": WHITE, "bold": True})],
], leading=1.4)
src_line(s, "场景来源：OpenUAV 平台（论文附录 A，arXiv:2410.07087）")

# ══════════ P8 技术架构：全宽官方框架图 ══════════
s = slide(nav="核心技术")
head(s, "03 · 核心技术", "技术架构：多模态大模型驱动的分层轨迹生成")
pic(s, os.path.join(WEB, "method2.png"), y=1.5, w=12.23, center_x=W / 2)
tb(s, M, 6.27, 12.23, 0.55,
   "指令与五视角图像编码进 MLLM（Vicuna-7B）：waypoint 查询 token 预测远距目标位姿，前视细化解码器输出 6-DoF 精细轨迹",
   size=12, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, M, 6.85, 12.2, 0.4, "核心技术自研可控：分层解码 · 回溯采样 DAgger 训练 · Grounding DINO 精准降落",
   size=13, color=ACCENT, bold=True)

# ══════════ P9 三大创新：三段变奏（大字左右交替） ══════════
s = slide(nav="核心技术")
head(s, "03 · 核心技术", "三大创新点：从「飞不真」到「真实自主」")
# 段1：大字左
hair(s, M, 1.7, 12.23)
tb(s, M, 1.95, 3.4, 0.9, "6-DoF", size=44, bold=True, color=CYAN, font=FN)
_f = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.35), Inches(2.05), Inches(2.42), Inches(0.52))
_f.adjustments[0] = 0.5; _f.fill.solid(); _f.fill.fore_color.rgb = PRIMARY; _alpha(_f.fill, 28000)
_f.line.color.rgb = PRIMARY; _f.line.width = Pt(0.75); _f.shadow.inherit = False
tb(s, 10.35, 2.185, 2.42, 0.32, "P = {x, y, z, θ, φ, ψ}", size=13, bold=True, color=CYAN, align=PP_ALIGN.CENTER, font=FN)
tb(s, 4.2, 1.95, 8.5, 1.4, [
    [("创新一 · 真实 6-DoF 仿真平台", {"size": 18, "bold": True})],
    [("行业改坐标造假动力学 → 自研 UE4+AirSim 物理级飞控，全状态记录，8×A100 并行 16× 加速", {"size": 13.5, "color": MUTED})],
], leading=1.35)
hair(s, M, 3.55, 12.23)
# 段2：大字右
tb(s, M, 3.8, 8.3, 1.4, [
    [("创新二 · 三级助导任务基准", {"size": 18, "bold": True})],
    [("行业只有静态目标描述 → 自研 L1 全程引导 / L2 纠偏 / L3 避障，首个模拟真实人机协作的搜索基准", {"size": 13.5, "color": MUTED})],
], leading=1.35)
tb(s, 10.2, 3.8, 2.6, 0.9, "L1→L3", size=40, bold=True, color=CYAN, font=FN)
for _j, (_lt, _ln) in enumerate([("L1", "全程引导"), ("L2", "困难纠偏"), ("L3", "仅避障")]):
    _lx = M + _j * 1.78
    _c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(_lx), Inches(4.78), Inches(1.62), Inches(0.46))
    _c.adjustments[0] = 0.5; _c.fill.solid(); _c.fill.fore_color.rgb = PRIMARY; _alpha(_c.fill, 28000)
    _c.line.color.rgb = PRIMARY; _c.line.width = Pt(0.75); _c.shadow.inherit = False
    tb(s, _lx, 4.875, 1.62, 0.3, [[(_lt + " ", {"bold": True, "color": CYAN}), (_ln, {"color": WHITE})]], size=11.5, align=PP_ALIGN.CENTER)
hair(s, M, 5.4, 12.23)
# 段3：大字左 + 金色更大
tb(s, M, 5.65, 3.4, 1.0, "+109%", size=48, bold=True, color=ACCENT, font=FN)
_g = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.35), Inches(5.85), Inches(2.42), Inches(0.52))
_g.adjustments[0] = 0.5; _g.fill.solid(); _g.fill.fore_color.rgb = ACCENT; _alpha(_g.fill, 18000)
_g.line.color.rgb = ACCENT; _g.line.width = Pt(0.75); _g.shadow.inherit = False
tb(s, 10.35, 5.985, 2.42, 0.32, "SR 8.37 → 17.45", size=13, bold=True, color=ACCENT, align=PP_ALIGN.CENTER, font=FN)
tb(s, 4.2, 5.65, 8.5, 1.4, [
    [("创新三 · 分层导航大模型", {"size": 18, "bold": True})],
    [("行业用离散动作分类器 → MLLM 端到端生成连续轨迹，SR 翻倍（8.37 → 17.45）", {"size": 13.5, "color": MUTED})],
], leading=1.35)
src_line(s, "对比数据来源：arXiv:2410.07087, Table 2", y=7.12)

# ══════════ P10 成果落地：横向成果链 + 下方图表/知产分栏 ══════════
s = slide(nav="核心技术")
head(s, "03 · 核心技术", "阶段成果：论文、开源、数据、基准四项落地")
chain_y = 1.95
hair(s, 1.5, chain_y, 10.3, color=PRIMARY, weight=1.5)
chain = [("学术论文", "arXiv:2410.07087", "平台/基准/方法一体成文"),
         ("开源代码", "GitHub · buaa-colalab", "训练与评测全流程"),
         ("开放数据", "HuggingFace", "12,149 条可下载"),
         ("开放基准", "UAV-Need-Help", "三级助导评测协议")]
for i, (t, k, d) in enumerate(chain):
    cx = 1.9 + i * 3.0
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - 0.08), Inches(chain_y - 0.08), Inches(0.16), Inches(0.16))
    dot.fill.solid(); dot.fill.fore_color.rgb = CYAN; dot.line.fill.background(); dot.shadow.inherit = False
    tb(s, cx - 1.35, chain_y - 0.62, 2.7, 0.4, t, size=17, bold=True, align=PP_ALIGN.CENTER)
    tb(s, cx - 1.35, chain_y + 0.18, 2.7, 0.35, k, size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    tb(s, cx - 1.35, chain_y + 0.56, 2.7, 0.35, d, size=12.5, color=MUTED, align=PP_ALIGN.CENTER)
cd = CategoryChartData()
cd.categories = ["CMA 基线", "本项目", "本项目+DA"]
cd.add_series("SR (%)", (8.37, 16.10, 17.45))
dark_chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, cd, M, 3.55, 6.5, 2.7, PRIMARY, hi_idx=2)
tb(s, M, 6.32, 6.5, 0.35, "核心指标 SR（成功率）：较最强基线 +109%", size=13.5, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, 7.6, 3.6, 5.2, 0.4, "知识产权规划", size=16.5, bold=True, color=ACCENT)
tb(s, 7.6, 4.1, 5.2, 1.8, [
    [("• 发明专利「无人机语言引导轨迹生成方法」申请中", {"size": 13.5, "color": MUTED})],
    [("• 软件著作权「OpenUAV 仿真平台」登记中", {"size": 13.5, "color": MUTED})],
    [("• 数据集与基准以开源协议发布，形成社区壁垒", {"size": 13.5, "color": MUTED})],
], leading=1.4)
src_line(s, "注：专利/软著为申报中材料，路演版将附受理通知书扫描件")

# ══════════ P11 市场规模：TAM/SAM/SOM 嵌套 + 右侧时机列 ══════════
s = slide(nav="商业模式")
head(s, "04 · 商业模式", "市场空间：从万亿低空经济到无人机智能化服务")
t_ = [(M, 1.6, 7.3, 5.0, "TAM · 低空经济", "1.5 万亿（2025E）→ 3.5 万亿（2035E）", PRIMARY, 22000),
      (M + 0.55, 2.28, 6.2, 3.7, "SAM · 民用无人机整机", "1,761 亿（2025）· 工业级占比 >70%", RGBColor(0x1F, 0x6F, 0xD0), 45000),
      (M + 1.1, 3.0, 5.1, 2.4, "SOM · 自主导航软件与服务", "团队测算：窗口期 3–5 年", ACCENT, 60000)]
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
tb(s, 8.5, 1.6, 4.3, 0.4, "为什么是现在", size=17, bold=True, color=ACCENT)
why = [("政策", "低空经济写入政府工作报告，多地开放空域试点"),
       ("技术", "多模态大模型爆发，语言→行动门槛被击穿"),
       ("需求", "巡检/搜救人力成本高，专业飞手缺口大"),
       ("窗口", "学术标杆已立（本团队），产业化窗口 3–5 年")]
y = 2.2
for k, v in why:
    tb(s, 8.5, y, 0.9, 0.4, k, size=14.5, bold=True, color=CYAN)
    tb(s, 9.4, y, 3.4, 0.8, v, size=12, color=MUTED, leading=1.2)
    y += 1.05
src_line(s, "数据来源：中国民航局、工信部公开报告；SOM 为团队测算")

# ══════════ P12 竞品矩阵 ══════════
s = slide(nav="商业模式")
head(s, "04 · 商业模式", "竞品对比：唯一「真实动力学 + 语言交互 + 开放生态」兼备")
rows = [
    ["能力维度", "传统飞控套件", "航线规划软件", "学术方案 AerialVLN/CityNav", "天行 TravelUAV"],
    ["连续 6-DoF 轨迹", "✗ 遥控为主", "✗ 航点插值", "✗ 离散动作", "✓ 物理级飞控"],
    ["自然语言交互", "✗", "✗ 仅航点", "部分 简短指令", "✓ 多视角+长指令"],
    ["在线引导协作", "✗", "✗", "✗", "✓ L1–L3 三级助导"],
    ["数据与基准开放", "✗ 闭源", "✗ 闭源", "部分 数据集", "✓ 全开源"],
    ["大模型驱动", "✗", "✗", "✗ LSTM", "✓ MLLM 端到端"],
    ["综合能力", "●○○○", "●●○○", "●●○○", "●●●●"],
]
gt = s.shapes.add_table(len(rows), 5, Inches(M), Inches(1.6), Inches(12.23), Inches(4.5)).table
for i, cw in enumerate([2.45, 2.0, 2.0, 3.15, 2.63]): gt.columns[i].width = Inches(cw)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci); c.text = val
        c.margin_left = c.margin_right = Inches(0.08); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        ours = ci == 4
        for r in p.runs:
            r.font.name = FONT; r.font.size = Pt(15.5)
            r.font.bold = ri == 0 or ours
            if ri == 0: r.font.color.rgb = WHITE
            elif ours: r.font.color.rgb = ACCENT if val.startswith("✓") else WHITE
            else: r.font.color.rgb = MUTED
        c.fill.solid()
        if ri == 0: c.fill.fore_color.rgb = PRIMARY
        elif ours: c.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x66)
        else: c.fill.fore_color.rgb = CARD
tb(s, M, 6.45, 12.2, 0.4, "差异化定位：不做整机不做硬件，做无人机大脑的「训练场 + 大脑」", size=14.5, bold=True, color=ACCENT)
src_line(s, "竞品信息基于公开资料整理（各产品官网与论文，2024–2025）")

# ══════════ P13 商业模式：左开放收入行 + 右数据飞轮 ══════════
s = slide(nav="商业模式")
head(s, "04 · 商业模式", "三线收入，先科研渗透、再行业落地")
biz = [("线一 · 平台订阅", "高校与科研院所", "OpenUAV 订阅 + 技术支持", "学术标杆引流"),
       ("线二 · 数据与评测", "AI 企业与研究院", "轨迹授权 · 评测服务", "独家 6-DoF 数据资产"),
       ("线三 · 行业方案", "应急 / 电网 / 安防", "联合解决方案按项目交付", "搜救与巡检场景卡位")]
y = 1.65
for t, who, what, moat in biz:
    tb(s, M, y, 6.9, 0.45, t, size=18, bold=True, color=ACCENT)
    tb(s, M, y + 0.5, 6.9, 0.4, [[("客户：", {"color": CYAN, "bold": True}), (who, {}),
                                    ("　｜　壁垒：", {"color": CYAN, "bold": True}), (moat, {})]], size=12.5, color=MUTED)
    tb(s, M, y + 0.92, 6.9, 0.4, what, size=12.5, color=MUTED)
    y += 1.62
    hair(s, M, y - 0.28, 6.9)
vhair(s, 7.75, 1.6, 5.2)
# 数据飞轮
fcx, fcy, fr = 10.35, 4.15, 1.5
ring = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(fcx - fr), Inches(fcy - fr), Inches(fr * 2), Inches(fr * 2))
ring.fill.background(); ring.line.color.rgb = PRIMARY; ring.line.width = Pt(1.5); ring.shadow.inherit = False
tb(s, fcx - 0.9, fcy - 0.25, 1.8, 0.5, "数据飞轮", size=17, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
nodes = [(fcx, fcy - fr, "科研用户沉淀", -0.9, -0.62), (fcx + fr, fcy, "社区数据反哺", 0.22, -0.2),
         (fcx, fcy + fr, "模型持续领先", -0.9, 0.12), (fcx - fr, fcy, "行业方案溢价", -2.3, -0.2)]
for nx, ny, lab, dx, dy in nodes:
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(nx - 0.07), Inches(ny - 0.07), Inches(0.14), Inches(0.14))
    d.fill.solid(); d.fill.fore_color.rgb = CYAN; d.line.fill.background(); d.shadow.inherit = False
    tb(s, nx + dx, ny + dy, 2.1, 0.35, lab, size=13.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, M, 6.72, 12.2, 0.4, "飞轮逻辑：越多人用 → 数据越多 → 模型越强 → 方案越值钱", size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

# ══════════ P14 团队：头像圆 + 开放列表（无卡片） ══════════
s = slide(nav="团队价值")
head(s, "05 · 团队价值", "师生共创：北航 ColaLab × CUHK MMLab")
mentors = [("刘", "刘偲 教授", "北航人工智能研究院", "国家青年人才 · 多模态智能"),
           ("廖", "廖裕渊 研究员", "CUHK MMLab", "视觉-语言导航新锐学者"),
           ("李", "李嘉胜 教授", "CUHK MMLab", "多模态大模型知名学者")]
x = M
for ch, n, org, tag in mentors:
    circ = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(1.65), Inches(0.78), Inches(0.78))
    circ.fill.solid(); circ.fill.fore_color.rgb = PRIMARY; _alpha(circ.fill, 45000)
    circ.line.color.rgb = PRIMARY; circ.line.width = Pt(1); circ.shadow.inherit = False
    tb(s, x, 1.83, 0.78, 0.45, ch, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tb(s, x + 0.95, 1.63, 3.2, 0.4, n, size=16.5, bold=True, color=ACCENT)
    tb(s, x + 0.95, 2.08, 3.2, 0.35, org, size=13, color=CYAN)
    tb(s, x + 0.95, 2.45, 3.3, 0.4, tag, size=12.5, color=MUTED)
    x += 4.14
hair(s, M, 3.1, 12.23)
tb(s, M, 3.3, 8, 0.4, "核心学生成员（论文共同作者）", size=14.5, bold=True, color=CYAN)
buaa = ["王翔宇*", "杨东林*", "王子衿*", "关浩谦", "陈锦玉", "吴文骏"]
x, y = M, 3.85
for n in buaa:
    chip = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(2.45), Inches(0.72))
    chip.adjustments[0] = 0.5; chip.fill.background()
    chip.line.color.rgb = PRIMARY; chip.line.width = Pt(1); chip.shadow.inherit = False
    tb(s, x, y + 0.17, 2.45, 0.4, n, size=15, bold=True, align=PP_ALIGN.CENTER)
    x += 2.7
    if x > 8.6: x, y = M, y + 0.95
tb(s, M, y + 0.95, 8.5, 0.35, "* 共同一作（完成平台、数据与模型三大模块）　成员以论文署名为准", size=12, color=MUTED)
card(s, 9.35, 3.85, 3.43, 2.3, alpha_pct=0)
tb(s, 9.62, 4.05, 2.9, 0.4, "依托单位", size=14, bold=True, color=CYAN)
tb(s, 9.62, 4.52, 2.95, 1.5, [
    [("• 北航人工智能研究院", {"size": 13, "color": MUTED})],
    [("• CUHK MMLab", {"size": 13, "color": MUTED})],
    [("• 具身智能方向长期积累", {"size": 13, "color": MUTED})],
], leading=1.35)

hair(s, M, 6.42, 12.23)
tb(s, M, 6.6, 12.2, 0.45, [[("9 名成员", {"bold": True, "color": CYAN}), ("　·　", {"color": MUTED}),
    ("2 所顶尖高校", {"bold": True, "color": CYAN}), ("　·　", {"color": MUTED}),
    ("1 篇 arXiv 论文", {"bold": True, "color": CYAN}), ("　·　", {"color": MUTED}),
    ("4 项开源产出", {"bold": True, "color": CYAN}), ("　·　", {"color": MUTED}),
    ("师生比 1:3", {"bold": True, "color": CYAN})]], size=14.5, align=PP_ALIGN.CENTER)

# ══════════ P15 社会价值：左侧图拼 + 右开放价值列 ══════════
s = slide(nav="团队价值")
head(s, "05 · 团队价值", "社会价值：更高效的搜救、更安全的巡检、更高质量的就业")
pic(s, os.path.join(FIG, "scenes", "scene_4.png"), x=M, y=1.65, w=3.25, border=False)
img_label_chip(s, M + 0.2, 1.82, "应急搜救")
pic(s, os.path.join(FIG, "scenes", "scene_6.png"), x=M, y=3.62, w=3.25, border=False)
img_label_chip(s, M + 0.2, 3.79, "电力巡检")
vhair(s, 4.35, 1.65, 4.9)
vals = [("应急救援", "按描述搜索失踪人员，黄金 72 小时内提升覆盖效率"),
        ("公共安全", "无人化巡检替代高危人工作业，降低伤亡风险"),
        ("带动就业", "催生语义标注、航线运营、无人机训练师等新岗位"),
        ("教育价值", "全栈开源反哺教学，学生完成论文到产品的完整闭环")]
y = 1.7
for k, v in vals:
    tb(s, 4.75, y, 2.6, 0.4, k, size=16.5, bold=True, color=ACCENT)
    tb(s, 7.5, y + 0.02, 5.3, 0.75, v, size=14, color=MUTED, leading=1.25)
    y += 1.22
    if y < 6.2: hair(s, 4.75, y - 0.22, 8.0)
tb(s, M, 6.55, 12.2, 0.5, [[("科技向善 · 服务国家低空战略", {"size": 16, "bold": True, "color": ACCENT}),
   ("　（场景图为 OpenUAV 渲染，实际部署以真机联合测试为准）", {"size": 10.5, "color": MUTED})]], size=13)

# ══════════ P16 发展规划：时间轴 + 近期目标条 ══════════
s = slide(nav="发展规划")
head(s, "06 · 发展规划", "三年三步：开源生态 → 真机验证 → 规模落地")
tl_y = 3.55
ln = s.shapes.add_connector(1, Inches(M), Inches(tl_y), Inches(W - M), Inches(tl_y))
ln.line.color.rgb = PRIMARY; ln.line.width = Pt(2)
ms = [("已完成", "2024", "全栈开源 + arXiv 论文", True),
      ("进行中", "2025", "社区共建扩数据 · 知产申报", True),
      ("下一步", "2026", "Sim-to-Real 真机验证\n首批应急/电网试点", False),
      ("目标", "2027+", "平台订阅规模化\n行业方案复制推广", False)]
for i, (tag, t, d, done) in enumerate(ms):
    cx = M + 0.85 + i * 3.02
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - 0.09), Inches(tl_y - 0.09), Inches(0.18), Inches(0.18))
    dot.fill.solid(); dot.fill.fore_color.rgb = CYAN if done else CARD
    dot.line.color.rgb = CYAN; dot.line.width = Pt(1.5); dot.shadow.inherit = False
    tb(s, cx - 1.3, tl_y - 0.82, 2.6, 0.4, t, size=16, bold=True, color=CYAN if done else MUTED, align=PP_ALIGN.CENTER, font=FN)
    tb(s, cx - 1.3, tl_y + 0.3, 2.6, 0.4, tag, size=15, bold=True, align=PP_ALIGN.CENTER, color=ACCENT if not done else WHITE)
    tb(s, cx - 1.45, tl_y + 0.85, 2.9, 1.1, d, size=13, color=MUTED, align=PP_ALIGN.CENTER, leading=1.25)
hair(s, M, 6.0, 12.23)
tb(s, M, 6.14, 12.2, 0.5, [[("近期目标：", {"bold": True, "color": ACCENT}),
   ("2026 年完成 2 个行业试点合同 + 真机演示；中长期成为低空经济「无人机大脑」事实标准", {})]], size=15)
tb(s, M, 6.68, 12.2, 0.4, [[("风险预案：", {"bold": True, "color": CYAN}),
   ("真机迁移 → 分阶段 Sim-to-Real 验证；市场节奏 → 先科研渗透、再行业复制", {"color": MUTED})]], size=12.5)

# ══════════ P17 致谢：主视觉收尾 ══════════
s = slide(bg=None, nav=None)
cover_pic(s, os.path.join(FIG, "derived", "hero_169.jpg"))
tb(s, M, 2.6, 12.2, 1.0, "恳请各位评委专家批评指正", size=38, bold=True, align=PP_ALIGN.CENTER)
tb(s, M, 3.85, 12.2, 0.5, "天行 TravelUAV · 让无人机听懂人话", size=17, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, M, 4.45, 12.2, 0.4, "汇 报 完 毕 · 感 谢 聆 听", size=14, color=CYAN, align=PP_ALIGN.CENTER)
tb(s, M, H - 0.65, 12.2, 0.35, "数据与图表引自 arXiv:2410.07087 及民航局、工信部公开报告；专利/软著申报中", size=11.5, color=MUTED, align=PP_ALIGN.CENTER)

out = os.path.join(BASE, "competition", "TravelUAV_竞赛版路演.pptx")
prs.save(out)
print("saved:", out, "slides:", len(prs.slides._sldIdLst))
