# 实战演示：TravelUAV → 两套成品 deck

同一篇论文（[arXiv:2410.07087](https://arxiv.org/abs/2410.07087)），两套风格、四种产物：

| 产物 | 页数 | 说明 |
|---|---|---|
| 学术版（中/英） | 14 | 组会/答辩向，Assertion-Evidence 学术排版 |
| 竞演版（中/英） | 17 | 国创赛路演向，深空科技蓝，对标评审五维度 |

每种均含每页 30–60 秒讲稿（演讲者备注 + 中英对照文档）。

`preview/` 内为逐页缩略拼图。完整 `.pptx` 未入库（体积原因），按下述步骤可在约 10 分钟内复现。

## 复现步骤

```bash
# 0) 依赖
pip install PyMuPDF python-pptx pillow

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

# 5) 构建（四份 deck）并注入讲稿
python3 build_research.py && python3 build_research_en.py
python3 build_competition.py && python3 build_competition_en.py
python3 add_notes.py && python3 competition_notes.py
```

## 目录文件说明

- `build_research*.py` / `build_competition*.py`：四份 deck 的完整构建脚本（python-pptx），
  坐标、字号、色板全部显式可改——改完重跑即得新版本。
- `add_notes.py` / `competition_notes.py`：讲稿数据与注入器（讲稿改这里）。
- 论文 PDF、提取出的图表与官方项目图未入库（版权与体积原因），按上面步骤可全部重新获得。
