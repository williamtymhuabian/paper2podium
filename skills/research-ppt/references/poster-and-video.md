# 学术海报与 3 分钟论文视频

同一篇论文的两种「会外」产物：**A0 学术海报**（现场站立讲解）与 **3 分钟会议宣传片**（投稿系统 / 实验室主页 / 社交媒体）。
两者都复用 research-ppt 的学术白底 + `1F4E79` 主色 + `C0392B` 强调色，不引入第二套视觉语言。

可运行示例：

- `examples/TravelUAV/poster/build_poster.py`
- `examples/TravelUAV/video/build_video.py`

---

## 一、A0 学术海报

### 1. 画布与栅格

| 项 | 值 |
|---|---|
| 成品尺寸 | A0 竖版 33.11 × 46.81 in（841 × 1189 mm） |
| 页边距 | 1.1 in |
| 栏数 | 3 栏，栏宽 9.87 in，栏间距 0.65 in |
| 阅读距离 | 1–1.5 m，正文不小于 24 pt |

三栏不是平均分内容，而是三条阅读动线：

1. **为什么做**（动机 → 现有基准的缺口 → 平台 → 贡献）
2. **做了什么**（数据采集 → 数据规模 → 基准设计 → 指令示例）
3. **怎么做、效果如何**（方法 → 主结果 → 泛化 → 定性）

### 2. 字号阶梯

| 元素 | 字号 |
|---|---|
| 主标题 | 72 pt Bold |
| 副标题 | 52 pt |
| 栏内小节标题 | 40 pt Bold（**标题过长会换行并被下方图片盖住，控制在 ~20 字符内**） |
| 正文 | 26–30 pt，行距 1.22–1.26 |
| 表格 | 20–21 pt |
| 图注 / 脚注 | 18–19 pt Italic |

标题字号不要靠自动缩放：LibreOffice 不会替你把 40 pt 标题压进一行。`section()` 的标题框高度固定，
第二行会被后绘制的图片覆盖——这是海报最常见的「字消失」原因。

### 3. 页眉与二维码

- 左上：`领域 · PREPRINT 年份`（小号、强调色）+ 英文主标题 + 副标题
- 作者行：共同一作 `*`、通讯作者 `†`，单位一行
- 右上：**arXiv 二维码 3.1 in**，下方 `arXiv:xxxx.xxxxx` + 项目页；二维码内容用 `https://arxiv.org/abs/...`
- 页脚：作者、论文名、arXiv 号、代码/数据地址、`Demo poster, non-commercial use.`

### 4. 内容取舍

- 一张海报只讲 **1 个方法 + 1 个主结果 + 1 个泛化结论**；消融、实现细节、附录全部舍弃
- 表格只保留「与最强基线对比」的必要列；最优值/本方法行加粗、浅色底
- 每张图配一句「结论型」图注，而不是「图 3：方法框架」
- 数字必须能回到论文：轨迹数、类别数、场景数、主表数值逐一核对
- 海报不放参考文献列表；用页脚 + 二维码指向论文

### 5. 三栏内容模板（可直接套用）

**左栏**

1. `01 MOTIVATION`：3 条「现状 → 为什么不够」的短段落 + 一句加粗结论
2. `02 WHY EXISTING BENCHMARKS FALL SHORT`：3 条差距 + 对比表（DoF / 动力学 / 规模 / 环境）
3. `03 PLATFORM`：平台总图 + 3 条能力
4. `04 CONTRIBUTIONS`：编号贡献 3 条

**中栏**

5. `05 DATA COLLECTION`：采集管线图 + 3 条流程
6. `06 DATASET AT A GLANCE`：4 个大数字 + 划分表
7. `07 BENCHMARK`：任务定义 + L1/L2/L3 三档助手
8. `08 INSTRUCTION EXAMPLE`：一条真实指令原句 + 一句解释

**右栏**

9. `09 METHOD`：方法总图 + 3 条机制 + 一张 `far-to-near` 解释卡
10. `10 RESULTS`：一个巨大主数字（如 `2.1×`）+ 主表 + 实验协议
11. `11 GENERALIZATION`：两组对比数字 + 定性 rollout 图

栏底留白用**一句 pull quote** 或一张解释卡填充，不要硬拉大图。

### 6. 构建与 QA

```bash
python3 build_poster.py                 # python-pptx 生成 A0 单页
soffice --headless --convert-to pdf TravelUAV_A0_海报.pptx
pdftoppm -png -r 40 TravelUAV_A0_海报.pdf preview/poster
```

QA 清单：

1. **越界**：python-pptx 遍历 shape，检查 `left/top/width/height` 是否超出画布
2. **换行**：所有 40 pt 小节标题必须单行；渲染后逐栏看标题是否被图片覆盖
3. **重叠**：图注按字数预估行数预留高度（`lines = ceil(len(caption)/92)`），不要让正文压图注
4. **缩略测试**：把 A0 预览缩到 480 px 宽，标题和小节标题仍应可读
5. **二维码**：全尺寸 PNG 上跑 `cv2.QRCodeDetector().detectAndDecode()`，必须解出 arXiv 链接
6. **PDF**：确认 1 页、尺寸 33.11 × 46.81 in、字体已嵌入（`pdffonts`）
7. **打印**：交付 PDF（不要交付 PPTX 给打印店）；图在 A0 上的实际分辨率 ≥ 200 dpi

### 7. 版权

- 只用 **arXiv 预印本**中的图，不用出版社排版版（publisher PDF）的截图
- 页脚保留作者、论文名、arXiv 号与 `non-commercial use`
- 海报用于会议/实验室展示通常属于学术传播；若用于商业宣传，先取得作者/单位授权

---

## 二、3 分钟论文宣传片

目标：**不熟悉论文的人 3 分钟内听懂「问题—平台—基准—方法—结果」**，并知道去哪里读论文。

### 1. 交付规格

| 项 | 值 |
|---|---|
| 时长 | 2:50–3:10 |
| 画面 | 1920 × 1080，30 fps，H.264 High，yuv420p |
| 音频 | AAC 48 kHz，响度归一化 `I=-16 LUFS, TP=-1.5` |
| 体积 | 20–30 MB（CRF 24；GitHub 单文件 <100 MB） |
| 字幕 | 英文硬字幕（ASS 烧录）+ 同名 `.srt` 旁挂 |
| 配乐 | 默认不加（避免版权与盖过人声）；如必须，用可商用授权曲目并压到 -28 LUFS |

### 2. 10 段分镜（约 176 s）

| # | 段落 | 时长 | 画面 | 叙事任务 |
|---|---|---|---|---|
| 1 | Title | 14 s | 深蓝封面 + 标题/作者 + 轨迹线 | 一句钩子 + 论文名 |
| 2 | The gap | 17 s | 左：离散图；右：连续 6-DoF 曲线 | 为什么 waypoint 不够 |
| 3 | Platform | 17 s | 平台总图 + 3 张能力卡 | OpenUAV 是什么 |
| 4 | Data | 17 s | 采集管线图 + 4 个大数字 | 数据规模与可信度 |
| 5 | Benchmark | 18 s | L1/L2/L3 三张卡 | 任务怎么定义 |
| 6 | Method | 20 s | 方法图 + 右侧四级流程 | far → near 一句话讲清 |
| 7 | Results | 19 s | `2.1×` + 柱状图 | 主结果 |
| 8 | Generalization | 17 s | 两组水平对比条 | 不重训也能迁移 |
| 9 | Rollouts | 18 s | 定性 rollout 网格 + 3 条观察 | 闭环行为 |
| 10 | Outro | 19 s | 三条贡献 + 大二维码 | 记忆点 + 行动 |

每段音频后再留 **1.2 s**（0.4 s 起播延迟 + 0.8 s 尾部），段间 0.35 s 淡入淡出。

### 3. 解说写法

- 每段 30–45 词，全片 350–380 词；目标语速 135–150 wpm
- 一句话只放一个信息点；数字用英文读法写进文稿（`17.45` → `seventeen point four five`）
- 首段用问题开场，末段用「one platform / one benchmark / one policy」收束
- 解说词、字幕、画面三者对齐：字幕按语义短语切 4–6 条/段，不按标点机械切

### 4. 画面生成

- **2× 超采样**：PIL 在 3840 × 2160 上绘制，ffmpeg 输出 1920 × 1080，文字边缘更干净
- 统一组件：顶部 kicker、68 pt 论断式标题、3 px 主色分隔线、右上 `07 / 10` 页码
- 数据图优先用论文原图；原图放进白卡片 + 1 px 边框，不拉伸
- 运动只做 **1.00 → 1.05 缓慢推近**（`zoompan`），相邻段交替推/拉，避免每段同一方向
- 底部预留 **~110 px 字幕安全区**：正文、脚注、标签都不要放进去

### 5. 音频与合成管线

```bash
# 1) 分段 TTS（edge-tts，英文男声；缓存 mp3，改文案才重跑）
edge-tts --voice en-US-AndrewNeural --rate=-8% \
         --text "..." --write-media audio/01_title.mp3

# 2) 每段：静帧 + 配音 + zoompan + 淡入淡出
ffmpeg -y -i frames/01_title.png -i audio/01_title.mp3 \
  -filter_complex "[0:v]zoompan=z='1+0.05*on/420':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=420:s=1920x1080:fps=30,fade=t=in:st=0:d=0.35,fade=t=out:st=13.6:d=0.4,format=yuv420p[v];[1:a]adelay=400:all=1,apad=pad_dur=1.2[a]" \
  -map "[v]" -map "[a]" -t 14.2 -c:v libx264 -crf 18 -c:a aac -b:a 192k segments/01.mp4

# 3) 拼接（同参数可直接 copy）
ffmpeg -f concat -safe 0 -i list.txt -c copy silent.mp4

# 4) 烧字幕 + 响度归一化
ffmpeg -y -i silent.mp4 -vf "ass=subs.ass" \
  -c:v libx264 -preset medium -crf 24 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:a aac -b:a 128k -ar 48000 -movflags +faststart out.mp4
```

### 6. 字幕

ASS 样式（1920×1080）：

```
Style: Cap,Liberation Sans,38,&H00FFFFFF,&H000000FF,&H00101010,&H96000000,
       0,0,0,0,100,100,0,0,3,10,0,2,120,120,56,1
```

- 每屏 1–2 行，按语义短语切分；超过 2 行自动对半拆
- 底部 `MarginV=56`，半透明黑底（`BorderStyle=3`）
- 同时输出 `.srt`，方便上传 B 站/YouTube 后替换或翻译
- 中文版只需替换字幕文本，不用重跑画面与配音（除非另录中文旁白）

### 7. QA

1. `ffmpeg -i out.mp4` 核对 1920×1080 / 30 fps / 时长 2:50–3:10
2. 在 3、18、35、55、78、100、125、145、160、172 s 抽帧，逐帧看标题、表格、字幕是否重叠
3. `volumedetect`：mean ≈ -16 dB，max ≤ -1 dB；无人声段不应有爆音
4. 抽末帧跑二维码解码
5. 文件 ≤ 35 MB；`-movflags +faststart` 让网页可边下边播
6. 片尾保留 `figures from the arXiv preprint · demo video, non-commercial use`

### 8. 版权

- 只用 arXiv 预印本图；片尾标注作者与 arXiv 号
- 不使用版权音乐；默认纯人声
- 若要在会议官方渠道/商业账号发布，先取得全体作者与单位宣传部门同意
