#!/usr/bin/env python3
"""科研版 TravelUAV 组会汇报 deck —— research-ppt skill 设计系统。
白底学术蓝灰、Assertion-Evidence 排版、论文图表为主体。14 页。
"""
import sys, os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---- 色板（学术蓝灰，references/design-system.md）----
BG      = RGBColor(0xFF, 0xFF, 0xFF)
BG_SOFT = RGBColor(0xF6, 0xF8, 0xFA)
PRIMARY = RGBColor(0x1F, 0x4E, 0x79)
ACCENT  = RGBColor(0xC0, 0x39, 0x2B)
TEXT    = RGBColor(0x2B, 0x2B, 0x2B)
MUTED   = RGBColor(0x6B, 0x72, 0x80)
LINE    = RGBColor(0xD8, 0xDE, 0xE6)
OKABE_BLUE = RGBColor(0x00, 0x72, 0xB2)
OKABE_ORNG = RGBColor(0xE6, 0x9F, 0x00)

FONT = "微软雅黑"
W, H, M = 13.33, 7.5, 0.6
BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
blank = prs.slide_layouts[6]

def slide():
    return prs.slides.add_slide(blank)

def tb(s, x, y, w, h, runs, size=20, color=TEXT, bold=False, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, leading=1.0, space_after=0):
    """通用文本框。runs: str 或 [(text,{bold,color,size}),...]"""
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
    tb(s, M, 0.42, W - 2 * M, 0.55, assertion, size=26, color=PRIMARY, bold=True)
    if sub:
        tb(s, M, 1.02, W - 2 * M, 0.35, sub, size=14, color=MUTED)

def pageno(s, n):
    tb(s, W - M - 0.5, H - 0.42, 0.5, 0.3, str(n), size=11, color=MUTED, align=PP_ALIGN.RIGHT)

def hline(s, x, y, w, color=LINE, weight=1.0):
    from pptx.util import Emu
    ln = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y))
    ln.line.color.rgb = color; ln.line.width = Pt(weight)

def pic(s, path, x=None, y=None, maxw=None, maxh=None, center_x=None, border=False):
    """等比放图，返回 (x,y,w,h)。"""
    from PIL import Image
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
    tb(s, x, y, w, 0.55, text, size=13, color=MUTED, leading=1.15)

def source(s, text):
    tb(s, M, H - 0.45, W - 2 * M - 0.6, 0.3, text, size=11.5, color=MUTED)

# ============ P1 封面 ============
s = slide()
tb(s, M, 1.15, W - 2 * M, 0.35, "组会论文汇报  ·  Vision-Language Navigation", size=15, color=MUTED)
tb(s, M, 1.75, W - 2 * M, 1.7, [
    [("Towards Realistic UAV Vision-Language Navigation:", {"size": 33, "bold": True, "color": PRIMARY})],
    [("Platform, Benchmark, and Methodology", {"size": 33, "bold": True, "color": PRIMARY})],
], leading=1.12)
tb(s, M, 3.55, W - 2 * M, 0.4, "面向真实无人机视觉-语言导航：平台、基准与方法（TravelUAV / OpenUAV）",
   size=17, color=TEXT)
hline(s, M, 4.35, 2.2, PRIMARY, 1.5)
tb(s, M, 4.6, W - 2 * M, 1.2, [
    [("论文：", {"bold": True}), ("Xiangyu Wang*, Donglin Yang*, Ziqin Wang*, Hohin Kwan, Jinyu Chen, Wenjun Wu, Hongsheng Li, Yue Liao†, Si Liu†", {})],
    [("单位：", {"bold": True}), ("北京航空航天大学人工智能研究院 · CUHK MMLab · CPII", {})],
    [("出处：", {"bold": True}), ("arXiv:2410.07087 (2024) · 项目主页 prince687028.github.io/OpenUAV", {})],
], size=13, color=MUTED, leading=1.35)
tb(s, M, H - 0.75, 6, 0.35, "汇报人：____　　日期：2026 年 10 月", size=13, color=TEXT)

# ============ P2 提纲 ============
s = slide(); title(s, "汇报提纲")
items = [
    ("01", "研究背景与动机", "地面 VLN 设定难以直接迁移到无人机"),
    ("02", "OpenUAV 仿真平台", "逼真环境 × 真实飞控 × 算法支持"),
    ("03", "数据集与基准", "12,149 条 6-DoF 轨迹 + UAV-Need-Help"),
    ("04", "UAV 导航大模型", "MLLM 分层轨迹生成 + 回溯采样 DAgger"),
    ("05", "实验与结果", "全面超越基线，与人类差距依然显著"),
    ("06", "结论与展望", "贡献总结与未来方向"),
]
y = 1.65
for num, name, desc in items:
    tb(s, M, y, 0.8, 0.5, num, size=24, color=PRIMARY, bold=True)
    tb(s, M + 0.95, y + 0.02, 3.6, 0.45, name, size=20, bold=True, color=TEXT)
    tb(s, M + 4.8, y + 0.09, 7, 0.4, desc, size=15, color=MUTED)
    y += 0.88
pageno(s, 2)

# ============ P3 背景：两大失配 ============
s = slide()
title(s, "直接沿用地面 VLN 设定，无法胜任真实无人机导航", "Background · 两类智能体的运动学与任务复杂度存在本质差异")
cards = [
    ("运动动力学失配", ["地面智能体：水平面移动，离散动作（前进/转向）即可规划",
                      "无人机：三维空域 6 自由度机动——俯仰、翻滚、偏航同时发生",
                      "连续轨迹难以分解为离散动作 → 固定动作集产生「非真实」导航"]),
    ("任务复杂度失配", ["无人机多在开阔户外执行长距离、长航时任务",
                      "视点高速变化、遮挡频发，仅凭目标描述难以精确搜索",
                      "需要环境信息与在线引导的持续支持"]),
]
x = M
for name, points in cards:
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.75), Inches(5.95), Inches(4.35))
    box.fill.solid(); box.fill.fore_color.rgb = BG_SOFT
    box.line.color.rgb = LINE; box.line.width = Pt(0.75)
    box.shadow.inherit = False
    tb(s, x + 0.4, 2.1, 5.2, 0.5, name, size=21, bold=True, color=PRIMARY)
    tb(s, x + 0.4, 2.85, 5.2, 3.0, [[("• ", {"color": PRIMARY, "bold": True}), (p, {})] for p in points],
       size=15.5, leading=1.25, space_after=10)
    x += 6.18
tb(s, M, 6.45, W - 2 * M, 0.4, [[("结论：", {"bold": True, "color": ACCENT}),
   ("需要为无人机 VLN 重建平台、数据与方法的整个技术栈", {"bold": True})]], size=16)
source(s, "图源/数据：Wang et al., arXiv:2410.07087, Fig.1 与 Sec.1")
pageno(s, 3)

# ============ P4 相关数据集对比（三线表） ============
s = slide()
title(s, "现有 UAV VLN 数据集均未覆盖真实 6-DoF 飞行动态", "Related Work · 与代表性 VLN 数据集对比（Table 1）")
rows = [
    ["数据集", "DoF", "运动学", "轨迹数", "词表", "轨迹长(m)", "指令长", "动作数"],
    ["R2R (2018)", "—", "✗", "7,189", "3.1K", "10", "29", "5"],
    ["TouchDown (2019)", "2", "✗", "9,326", "5K", "310", "90", "35"],
    ["AVDN (2022)", "3", "✗", "6,269", "3.3K", "144", "89", "7"],
    ["AerialVLN (2023)", "4", "✗", "8,446", "4.5K", "661", "83", "204"],
    ["CityNav (2024)", "4", "✗", "32,637", "6.6K", "545", "26", "—"],
    ["本文 TravelUAV", "6", "✓", "12,149", "10.8K", "255", "104", "264"],
]
tw, th = 12.13, 4.6
gt = s.shapes.add_table(len(rows), 8, Inches(M), Inches(1.8), Inches(tw), Inches(th)).table
widths = [3.2, 1.0, 1.15, 1.45, 1.25, 1.45, 1.25, 1.38]
for i, cw in enumerate(widths): gt.columns[i].width = Inches(cw)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci); c.text = val
        c.margin_left = c.margin_right = Inches(0.08)
        c.margin_top = c.margin_bottom = Inches(0.03)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        for r in p.runs:
            r.font.name = FONT; r.font.size = Pt(16)
            last = ri == len(rows) - 1
            r.font.bold = ri == 0 or last
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if ri == 0 else (PRIMARY if last else TEXT)
        c.fill.solid()
        c.fill.fore_color.rgb = PRIMARY if ri == 0 else (BG_SOFT if last else BG)
tb(s, M, 6.55, W - 2 * M, 0.4, [[("首个具备真实飞行动力学（6-DoF 运动学 ✓）的无人机 VLN 数据集", {"bold": True, "color": ACCENT})]], size=16)
source(s, "数据源：Wang et al., arXiv:2410.07087, Table 1")
pageno(s, 4)

# ============ P5 平台总览（Figure 1 大图） ============
s = slide()
title(s, "OpenUAV 平台：逼真环境、真实飞控与算法支持三位一体")
r = pic(s, f"{FIG}/fig1_platform.png", y=1.35, maxw=10.8, maxh=5.0, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.42 + r[3] + 0.12, 10,
        "图 1｜平台与基准总览：左为 OpenUAV 平台（闭环仿真、并行化、可复现条件、传感器配置、轨迹回放），右为 UAV-Need-Help 助导式目标搜索任务。")
source(s, "图源：arXiv:2410.07087, Fig.1")
pageno(s, 5)

# ============ P6 平台要点 ============
s = slide()
title(s, "OpenUAV 平台：UE4 + AirSim，22 场景全流程开放")
feats = [
    ("逼真环境", ["UE4 高保真渲染，22 类城市场景", "89 类可放置物体资产，运行时 API 自动摆放", "动态环境：植被摆动、光照变化"]),
    ("真实飞控", ["AirSim 物理仿真，6-DoF 位姿 P={x,y,z,θ,φ,ψ}", "遥控器（PX4）/ 手动 / 位置模式三种人控接口", "RGB+深度×5 视角、360° LiDAR、IMU、GPS"]),
    ("算法支持", ["闭环仿真：模型输出→飞控→环境反馈", "DAgger 数据聚合 + 回溯策略内置", "8×A100 并行 16× 加速，160–1600 fps"]),
]
x = M
for name, pts in feats:
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.7), Inches(3.92), Inches(4.4))
    box.fill.solid(); box.fill.fore_color.rgb = BG_SOFT
    box.line.color.rgb = LINE; box.line.width = Pt(0.75); box.shadow.inherit = False
    tb(s, x + 0.32, 2.02, 3.3, 0.5, name, size=20, bold=True, color=PRIMARY)
    tb(s, x + 0.32, 2.7, 3.35, 3.3, [[("• ", {"color": PRIMARY, "bold": True}), (p, {})] for p in pts],
       size=14, leading=1.22, space_after=9)
    x += 4.11
tb(s, M, 6.4, W - 2 * M, 0.45, [[("全平台开源", {"bold": True, "color": ACCENT}),
   ("：环境、飞控、采集、训练、评测一体化，支撑连续轨迹 VLN 研究全流程", {})]], size=16)
source(s, "内容源：arXiv:2410.07087, Sec.3")
pageno(s, 6)

# ============ P7 数据集（Figure 2） ============
s = slide()
title(s, "12,149 条 6-DoF 真实轨迹：GPT-4 生成描述 + 人工驾机采集")
r = pic(s, f"{FIG}/fig2_dataset.png", y=1.35, maxw=10.2, maxh=4.75, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.42 + r[3] + 0.12, 10,
        "图 2｜数据构建与统计：五视角拍摄→GPT-4 生成目标描述→人工复核；飞手实时驾机、状态等间隔记录、传感器异步补采；右侧为轨迹长度/目标距离/物体类别/数据划分分布。")
source(s, "图源：arXiv:2410.07087, Fig.2；划分：Train 9,152 / Test Seen 1,410 / Unseen Map 958 / Unseen Object 629")
pageno(s, 7)

# ============ P8 基准：UAV-Need-Help ============
s = slide()
title(s, "UAV-Need-Help：三级助导机制适配真实搜救场景", "Benchmark · 助手依据场景提供不同粒度的在线引导")
lv = [
    ("L1 全程引导", "持续计算 UAV 与最优路径最近点，高频给出巡航/转向/降落指令", "贴近真实地面站协作"),
    ("L2 纠偏引导", "仅当深度图判定碰撞风险或偏离路径时介入，低频纠正", "模拟远程监督者"),
    ("L3 避障引导", "仅在危险临近障碍时发出避障指令", "最大 autonomy，最难设定"),
]
y = 1.8
for name, desc, tag in lv:
    tb(s, M, y, 2.6, 0.5, name, size=19, bold=True, color=PRIMARY)
    tb(s, M + 2.9, y, 6.6, 0.9, desc, size=15.5, leading=1.2)
    tb(s, M + 9.8, y + 0.04, 2.4, 0.5, tag, size=13, color=MUTED)
    hline(s, M, y + 0.92, W - 2 * M)
    y += 1.12
tb(s, M, 5.5, W - 2 * M, 1.2, [
    [("任务形式化：", {"bold": True}), ("每回合输入 {目标描述 I, 状态 S, 五视角 RGB R 与深度 D, 助手指令 I′} → 模型输出 6-DoF 轨迹序列；降落点距目标 ", {}),
     ("20 米内", {"bold": True, "color": ACCENT}), ("记为成功。", {})],
], size=16, leading=1.3)
source(s, "内容源：arXiv:2410.07087, Sec.5")
pageno(s, 8)

# ============ P9 方法总框架（Figure 3 招牌页） ============
s = slide()
title(s, "UAV 导航大模型：以可学习查询驱动分层轨迹生成")
r = pic(s, f"{FIG}/fig3_method.png", y=1.3, maxw=11.4, maxh=4.9, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.36 + r[3] + 0.1, 10,
        "图 3｜左：三级助手机制；右：导航 LLM——指令与多视角图像编码进 MLLM（Vicuna-7B），waypoint 查询 token 提取特征预测远距目标位姿，再由前视细化解码器生成精细轨迹。")
source(s, "图源：arXiv:2410.07087, Fig.3")
pageno(s, 9)

# ============ P10 方法细节 ============
s = slide()
title(s, "分层解码：先定远距目标位姿，再生成精细轨迹")
steps = [
    ("多模态 tokenization", ["EVA-CLIP + Q-former：每视角 1 全局 + 16 局部 token", "拼接 <T_img, T_task, T_instr> 输入 Vicuna-7B"]),
    ("高层轨迹解码", ["可学习 waypoint token T_wp 经 LLM 提取轨迹特征", "MLP 解码下一目标位姿 P_target（远距离规划）"]),
    ("细粒度路径解码", ["前视 token + 目标位姿特征对齐 → MLP 输出位姿序列", "Grounding DINO 检出目标即触发降落"]),
]
x = M
for i, (name, pts) in enumerate(steps):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.75), Inches(3.92), Inches(3.55))
    box.fill.solid(); box.fill.fore_color.rgb = BG_SOFT
    box.line.color.rgb = LINE; box.line.width = Pt(0.75); box.shadow.inherit = False
    tb(s, x + 0.3, 2.05, 0.7, 0.5, f"0{i+1}", size=22, bold=True, color=OKABE_BLUE)
    tb(s, x + 0.3, 2.62, 3.35, 0.5, name, size=18, bold=True, color=PRIMARY)
    tb(s, x + 0.3, 3.18, 3.4, 1.9, [[("• ", {"color": PRIMARY, "bold": True}), (p, {})] for p in pts],
       size=13.5, leading=1.22, space_after=8)
    if i < 2:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 3.98), Inches(3.3), Inches(0.28), Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb = PRIMARY; ar.line.fill.background()
    x += 4.11
tb(s, M, 5.7, W - 2 * M, 0.9, [[("训练增强：", {"bold": True}),
   ("回溯采样 DAgger——模型输出致碰撞时回退两帧并改用教师轨迹，从失败中采集避障样本", {})]], size=16, leading=1.3)
source(s, "内容源：arXiv:2410.07087, Sec.6")
pageno(s, 10)

# ============ P11 主实验表 ============
s = slide()
title(s, "全部指标超越基线：SR 较 CMA 平均提升 5 个百分点", "Experiments · Test Seen，L1 助手（Table 2，Full 口径）")
rows = [
    ["方法", "NE (m) ↓", "SR (%) ↑", "OSR (%) ↑", "SPL (%) ↑"],
    ["Random", "222.20", "0.14", "0.21", "0.07"],
    ["Fixed Action", "188.61", "2.27", "8.16", "1.40"],
    ["CMA (LSTM)", "135.73", "8.37", "18.72", "7.90"],
    ["Ours", "106.28", "16.10", "44.26", "14.30"],
    ["Ours + 回溯DA", "98.66", "17.45", "48.87", "15.76"],
    ["Human", "14.15", "94.51", "94.51", "77.84"],
]
gt = s.shapes.add_table(len(rows), 5, Inches(M), Inches(1.75), Inches(7.6), Inches(4.3)).table
for i, cw in enumerate([2.4, 1.3, 1.3, 1.3, 1.3]): gt.columns[i].width = Inches(cw)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci); c.text = val
        c.margin_left = c.margin_right = Inches(0.06); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        for r in p.runs:
            r.font.name = FONT; r.font.size = Pt(16)
            hl = ri in (5, 6)
            r.font.bold = ri == 0 or hl
            r.font.color.rgb = RGBColor(0xFF,0xFF,0xFF) if ri == 0 else (ACCENT if hl else TEXT)
        c.fill.solid()
        c.fill.fore_color.rgb = PRIMARY if ri == 0 else (BG_SOFT if hl else BG)
tb(s, 8.6, 1.9, 4.1, 4.2, [
    [("+109%", {"size": 34, "bold": True, "color": ACCENT})],
    [("SR 相对 CMA 提升（8.37→17.45）", {"size": 13, "color": MUTED})],
    [("", {})],
    [("3.4×", {"size": 34, "bold": True, "color": PRIMARY})],
    [("OSR 提升（18.72→48.87）：接近半数任务可途经最优路径", {"size": 13, "color": MUTED})],
    [("", {})],
    [("差距仍大", {"size": 22, "bold": True, "color": TEXT})],
    [("人类 SR 94.51 vs 模型 17.45——任务远未解决", {"size": 13, "color": MUTED})],
], leading=1.1)
source(s, "数据源：arXiv:2410.07087, Table 2；NE=终点距目标平均距离")
pageno(s, 11)

# ============ P12 泛化与数据效率（原生图表） ============
s = slide()
title(s, "未见物体上泛化最优：SR 22.4%，数据越多性能越强")
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
cd = CategoryChartData()
cd.categories = ["Random", "Fixed", "CMA", "Ours"]
cd.add_series("SR (%)", (0.16, 3.66, 9.06, 22.42))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(M), Inches(1.85), Inches(5.9), Inches(4.2), cd)
ch = gf.chart; ch.has_legend = False
ch.category_axis.tick_labels.font.size = Pt(13); ch.value_axis.tick_labels.font.size = Pt(13)
pl = ch.plots[0]; pl.vary_by_categories = False
pl.has_data_labels = True
pl.data_labels.show_value = True; pl.data_labels.number_format = '0.0'; pl.data_labels.number_format_is_linked = False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.data_labels.font.size = Pt(14); pl.data_labels.font.bold = True
ser = pl.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = OKABE_BLUE
pt = ser.points[3]  # 最后一根柱子（Ours）换成强调色
pt.format.fill.solid(); pt.format.fill.fore_color.rgb = ACCENT
tb(s, M, 6.1, 5.9, 0.4, "Test Unseen Object（L1 助手）SR 对比", size=13, color=MUTED, align=PP_ALIGN.CENTER)
cd2 = CategoryChartData()
cd2.categories = ["10% 数据", "50% 数据", "100% 数据"]
cd2.add_series("SR (%)", (10.78, 13.19, 16.10))
gf2 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(7.0), Inches(1.85), Inches(5.7), Inches(4.2), cd2)
ch2 = gf2.chart; ch2.has_legend = False
ch2.category_axis.tick_labels.font.size = Pt(13)
pl2 = ch2.plots[0]; pl2.vary_by_categories = False
pl2.has_data_labels = True
pl2.data_labels.show_value = True; pl2.data_labels.number_format = '0.00'; pl2.data_labels.number_format_is_linked = False
pl2.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl2.data_labels.font.size = Pt(14); pl2.data_labels.font.bold = True
pl2.series[0].format.fill.solid(); pl2.series[0].format.fill.fore_color.rgb = PRIMARY
tb(s, 7.0, 6.1, 5.7, 0.4, "训练数据量消融（Test Seen, L1, SR%）", size=13, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, M, 6.55, W - 2 * M, 0.4, [[("Unseen Map 上 SR 仅 4.18%", {"bold": True, "color": ACCENT}),
   ("：未见城市场景仍是核心挑战", {})]], size=15)
source(s, "数据源：arXiv:2410.07087, Table 3 / Table 4")
pageno(s, 12)

# ============ P13 定性结果 ============
s = slide()
title(s, "成功案例遵循指令完成搜索；失败多源于复杂场景碰撞")
r = pic(s, f"{FIG}/fig4_qualitative.png", y=1.4, maxw=10.6, maxh=4.8, center_x=W / 2, border=True)
caption(s, W / 2 - 5, 1.46 + r[3] + 0.1, 10,
        "图 4｜前两行为成功案例：无人机依指令定位车辆与奶牛，第 3–5 帧可见转向机动改变视点；第三行为失败案例：森林场景中与树木碰撞。")
source(s, "图源：arXiv:2410.07087, Fig.4")
pageno(s, 13)

# ============ P14 结论 ============
s = slide()
title(s, "结论：平台、基准、方法三件套重塑真实无人机 VLN")
concl = [
    ("平台", "OpenUAV：首个面向连续轨迹无人机 VLN 的全开源仿真平台（UE4+AirSim，22 场景）"),
    ("数据与基准", "12,149 条 6-DoF 轨迹数据集 + UAV-Need-Help 三级助导基准，均开源"),
    ("方法", "UAV 导航大模型：分层轨迹生成 + 回溯采样 DAgger，SR 较 CMA 平均 +5pt"),
]
y = 1.7
for i, (k, v) in enumerate(concl):
    tb(s, M, y, 0.8, 0.5, f"0{i+1}", size=24, bold=True, color=PRIMARY)
    tb(s, M + 0.95, y + 0.03, 2.5, 0.5, k, size=19, bold=True)
    tb(s, M + 3.6, y + 0.06, 8.4, 0.9, v, size=15.5, leading=1.2)
    hline(s, M, y + 0.85, W - 2 * M)
    y += 1.05
tb(s, M, 5.05, W - 2 * M, 0.85, [
    [("不足与展望：", {"bold": True}),
     ("模型与人类操作员仍有 77pt SR 差距；未见场景泛化（Unseen Map SR 4.18%）与真实无人机部署是下一步核心方向。", {})],
], size=15, color=TEXT, leading=1.3)
tb(s, M, 6.3, W - 2 * M, 0.6, "谢谢大家，敬请批评指正 · Q&A", size=24, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)
pageno(s, 14)

out = os.path.join(BASE, "research", "TravelUAV_科研版组会汇报.pptx")
prs.save(out)
print("saved:", out, "slides:", len(prs.slides.__iter__.__self__._sldIdLst))
