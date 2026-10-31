# 实战演示：TravelUAV → 三套 deck + 海报 + 宣传片

同一篇论文（[arXiv:2410.07087](https://arxiv.org/abs/2410.07087)），三种技能、五种产物：

| 产物 | 页数 | 说明 |
|---|---|---|
| 学术版（中/英） | 14 | 组会/答辩向，Assertion-Evidence 学术排版 |
| 竞演版（中/英） | 17 | 国创赛路演向，深空科技蓝，对标评审五维度 |
| 商业版（中） | 10 | 展台大屏向，品牌编辑风，86 秒自动循环 + 静音可读 |
| A0 海报（英） | 1 | 会议现场向，三栏栅格，主数字 + 主表 + arXiv 二维码 |
| 3 分钟宣传片（英） | 10 段 | 会议投稿 / 主页 / 社交媒体，配音 + 硬字幕 + SRT |

学术/竞演版含每页 30–60 秒讲稿（演讲者备注 + 中英对照文档）；商业版附
`business/讲稿_展台循环.md`（逐页字幕、30 秒电梯稿、3 分钟路线、Q&A、布展清单）。

`preview/` 内为逐页缩略拼图与视频分镜接触表；完整 `.pptx` / PDF 在 `showcase/decks/`，
A0 PDF 在 `showcase/poster/`，成片 MP4 在 `showcase/video/`。按下述步骤可复现。

## 复现步骤

```bash
# 0) 依赖
pip install PyMuPDF python-pptx pillow qrcode[pil] edge-tts imageio-ffmpeg

# 1) 下载论文 PDF（arXiv 2410.07087）
curl -sL -o TravelUAV.pdf https://arxiv.org/pdf/2410.07087

# 2) 自动提取论文图表（caption 锚定 + 450dpi 裁剪）
python3 ../../skills/research-ppt/scripts/extract_figures.py TravelUAV.pdf -o figures --dpi 450
#    多面板图若被裁小 → 按技能内闭环修正：
python3 ../../skills/research-ppt/scripts/extract_figures.py TravelUAV.pdf -o figures --render-page 2   # 看版面
python3 ../../skills/research-ppt/scripts/extract_figures.py TravelUAV.pdf -o figures --crop 2,108,86,504,281.5

# 3) 下载论文官方项目图（封面主视觉/架构图等，来自项目主页）
mkdir -p figures/web
for f in header2.png show.png dataset2.png method2.png; do
  curl -sL "https://prince687028.github.io/OpenUAV/static/images/$f" -o "figures/web/$f"
done

# 4) 生成竞演版深空背景 + 切场景卡（论文附录场景墙 4x2 网格）
python3 ../../skills/competition-ppt/scripts/make_backgrounds.py -o bg --style techblue
#    场景卡与飞行序列条由构建脚本内的白隙检测自动完成

# 5) 构建（五份 deck）并注入讲稿
python3 build_research.py && python3 build_research_en.py
python3 build_competition.py && python3 build_competition_en.py
python3 add_notes.py && python3 competition_notes.py

# 6) 商业展台循环（10 页 / 86 秒，脚本自动写入循环与切页）
#    交付前替换 build_business.py 中的 QR_DATA、展位号与日期
python3 ../../skills/business-ppt/scripts/make_backgrounds.py -o business/bg --style premium
python3 business/build_business.py

# 7) A0 学术海报（1 页，33.11 × 46.81 in）
python3 poster/build_poster.py
soffice --headless --convert-to pdf poster/TravelUAV_A0_海报.pptx --outdir poster

# 8) 3 分钟宣传片（需要 edge-tts + imageio-ffmpeg；首次会联网合成配音）
python3 video/build_video.py
#    输出 video/TravelUAV_3min_promo.mp4 + TravelUAV_3min.srt
```

## 目录文件说明

- `build_research*.py` / `build_competition*.py` / `business/build_business.py`：五份 deck 的完整
  构建脚本（python-pptx），坐标、字号、色板全部显式可改——改完重跑即得新版本。
- `poster/build_poster.py`：A0 海报构建脚本；`video/build_video.py`：10 段分镜、PIL 静帧、
  edge-tts 配音、ffmpeg 合成与字幕烧录。`video/解说词与分镜.md` 是逐段时间码与英文解说词。
- `add_notes.py` / `competition_notes.py`：讲稿数据与注入器（讲稿改这里）；
  `business/讲稿_展台循环.md` 为展台循环的口播与执行文档。
- 论文 PDF、提取出的图表与官方项目图未入库（版权与体积原因），按上面步骤可全部重新获得。
- 海报与视频只用 arXiv 预印本图，页脚/片尾保留作者、arXiv 号与 non-commercial 声明；
  视频未使用版权音乐。
