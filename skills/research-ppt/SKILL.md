---
name: research-ppt
description: 生成科研/学术风格的精美演示文稿与配套物料：组会汇报、学术会议报告、毕业论文答辩、开题/结题、基金申报、论文讲解、A0 学术海报、3 分钟论文宣传片。当用户提到"科研PPT、学术PPT、答辩PPT、组会PPT、论文汇报、学术报告、开题、中期、结题、lab meeting、thesis defense、学术海报、A0 poster、海报、3分钟视频、论文宣传片、paper video"，或要求"把这篇论文做成PPT/汇报/海报/视频"、"从论文 PDF 提取框架图/实验图放进幻灯片"时使用。基于 Assertion-Evidence 学术排版规范与 Nature/Science 图表美学，内置从论文 PDF 精准分割框架图的高清提取管线。
---

# 科研 PPT（学术演示文稿）

为学术场景产出**克制冷静、以图为证**的演示文稿：组会、会议报告、答辩、基金汇报。
与商业 PPT 的本质区别：每页是**一句论断 + 一份证据**（assertion–evidence），不是口号。

构建工具链与官方 pptx skill 一致（pptxgenjs，画布 13.33 × 7.5"），本 skill 负责学术场景的设计系统、
叙事结构与论文图表提取。构建前先通读本文件，再按需读：

- `references/design-system.md` —— 配色 / 字体 / 逐页版式配方（含坐标），**写构建脚本前必读**
- `references/figure-extraction.md` —— 论文 PDF 图表提取的实战细节与疑难场景，**输入含论文 PDF 时必读**
- `references/poster-and-video.md` —— A0 海报与 3 分钟论文视频的版式、分镜、TTS/ffmpeg 管线与版权清单，**做海报或宣传片时必读**

## 0. 触发后的第一件事：盘点素材

向用户（或从任务上下文）确认三类输入，缺什么补什么：

1. **汇报材料**：论文 PDF / 大纲 / 数据 —— 决定叙事线
2. **场合与时长**：组会 15min ≈ 12–18 页；会议报告 15–20min ≈ 15–20 页；答辩 20min ≈ 20–28 页（网评版可更多）
3. **单位与场合要素**：校徽/院徽图片、学校主题色（有则吸收进主色）、导师与单位署名

## 1. 从论文 PDF 提取图表（核心能力）

框架图、实验曲线、消融表是学术 PPT 的主角。**绝不用截图，绝不明整页塞进来**——用自带脚本精准分割：

```bash
# 自动提取（caption 锚定：Figure/Fig/图/表/Table）
python3 <skill_dir>/scripts/extract_figures.py paper.pdf -o figures/ --dpi 450

# 结果不理想时：先渲染整页预览，用 Read 看清版面
python3 <skill_dir>/scripts/extract_figures.py paper.pdf -o figures/ --render-page 3

# 再按 PDF 坐标手动精裁（页码,x0,y0,x1,y1，pt）
python3 <skill_dir>/scripts/extract_figures.py paper.pdf -o figures/ --crop 3,72,220,540,560
```

产出 `figures/*.png + manifest.json`（页码/标签/原生 caption/类型/置信度）。
标准闭环：**自动提取 → Read 抽查 PNG → 置信度低或裁歪的用 preview+crop 修正**。
选图原则与疑难场景（扫描件、矢量图、双栏）见 `references/figure-extraction.md`。

依赖：`pip install pymupdf`（缺失时脚本会提示）。

## 2. 叙事结构（按场合裁剪）

主线：**封面 → 背景（漏斗式 2–3 页：领域 → 具体 → gap）→ 方法（每页一张图，先总框架后逐模块）
→ 实验（每页开头一句话结论 + 主图/主表）→ 结论（编号贡献）→ 致谢/Q&A**，附录页放备查细节。

- 标题写**论断句**，不写话题词：❌"实验结果" ✅"XX 方法在三个基准上平均提升 4.7%"
- 方法部分是重头：总框架图一页全宽（从论文提取，占版面 75%+），每个模块再各一页
- 实验页一张主图讲一件事；消融用三线表，最优值加粗
- 每页底部标注数据/图来源（"图源：Zhang et al., 2025, Fig.3"），引用必须真实

## 3. 设计系统（摘要，细节见 references/design-system.md）

- **配色**：白底为主；主色深学术蓝 `1F4E79`；正文 `2B2B2B`；次要 `6B7280`；强调色一个（`C0392B` 类学术红，仅用于最优值/gap 框/关键词）。数据系列用 Okabe-Ito 色盲安全色板。整 deck 不引入第三个色相。
- **字体**：中文微软雅黑（Bold 标题 / Regular 正文），全 deck 显式指定 fontFace；英文数字同族。
  字号：封面主题 40–44pt，页标题 26–30pt，要点 20–24pt（每页 ≤ 6 行），图注/来源 12–14pt。
- **版面**：图占 60–75%，文字要点 ≤ 3 条且为短语；统一 0.6" 边距、0.35" 块间距；
  左对齐正文；**零装饰**（无色带、无图标堆砌、无阴影渐变、无emoji、无3D图表）。
- **图片**：按原始宽高比放置（先读 manifest 的 w_px/h_px 计算目标尺寸再定位），下方 12pt 灰色图注
  （第一句写图的结论而非描述）。禁止拉伸变形。

## 4. 构建（pptxgenjs）

- `pres.layout = 'LAYOUT_WIDE'`；色板以常量定义在脚本顶部（`BG/PRIMARY/ACCENT/TEXT/MUTED`），只引用常量
- 图表用原生 `addChart`（柱/线/散点等），色板传 Okabe-Ito；表格用三线表样式
- 每页配方（含具体坐标）在 `references/design-system.md` —— 按页型取用，勿每页自创
- 常见坑与 pptxgenjs 机制沿用官方 pptx skill：hex 不带 `#`、bullet 用工厂函数加 `indent:12`、
  多行文本 `breakLine:true`、shadow offset 非负、`sizing:{type:'cover'}` 裁图

## 5. QA（交付前）

1. **溢出检查**：python-pptx 跑一遍文本溢出/形状越界脚本，修复真实命中
2. **视觉审查**：`soffice --headless --convert-to pdf` → `pdftoppm -png -r 150` 渲染整 deck，
   逐页检查（或交给 visual-judge 子代理）：图是否清晰无锯齿、比例是否变形、图注与图是否对齐
3. **内容检查**：论断句标题、图有来源、无占位符残留（xxx/TODO/lorem）
4. 交付 `<主题>_答辩PPT.pptx` 类命名；给用户一段每页讲话要点（写入 speaker notes）

## 6. 学术场合禁忌

- ❌ 花哨动画/切换（默认不加任何动画）
- ❌ 装饰性色条、渐变背景、大图标（学术评审视为不专业）
- ❌ 整段文字贴页（讲稿放备注，不放页面）
- ❌ 无来源的数据、编造的实验数字
- ❌ 图片放大到超过其分辨率（450dpi 提取就是为了投影不糊）

## 7. 延伸产物：A0 海报

同一篇论文需要「站台讲解」时，默认做 **A0 竖版三栏海报**，而不是把 deck 放大：

- 画布 33.11 × 46.81 in，三栏 9.87 in、栏距 0.65 in、页边距 1.1 in
- 标题 72 pt，小节 40 pt（**单行、≤ ~20 字符**），正文 26–30 pt，图注 18–19 pt
- 右栏放主数字（如 `2.1×`）与主表；右上角 3.1 in arXiv 二维码
- 内容只留「一个方法 + 一个主结果 + 一个泛化结论」，其余全部舍弃
- 交付 PDF 给打印店；缩略到 480 px 仍可读，二维码必须可解码

完整模板、三栏内容清单与 QA 见 `references/poster-and-video.md`。

## 8. 延伸产物：3 分钟论文宣传片

需要投稿系统/主页/社交媒体的短视频时，按 **10 段 × 12–22 s** 做 2:50–3:10 的 1080p 视频：

- 主线：钩子 → 缺口 → 平台 → 数据 → 基准 → 方法 → 主结果 → 泛化 → 定性 → 行动
- 画面：PIL 2× 超采样静帧 + ffmpeg `zoompan` 1.00→1.05 缓慢推近，段间 0.35 s 淡入淡出
- 配音：edge-tts 分段生成（350–380 词，约 140 wpm），每段后留 1.2 s
- 字幕：ASS 38 pt 底部安全区烧录，同时输出 `.srt`；响度 `loudnorm I=-16 LUFS`
- 交付：1920×1080 / 30 fps / CRF 24 / faststart，20–30 MB

分镜表、可复制命令与版权清单见 `references/poster-and-video.md`。
