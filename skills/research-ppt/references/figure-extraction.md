# 论文 PDF 图表提取实战手册

`scripts/extract_figures.py` 的算法：caption 行锚定（"Figure 1:" / "图 1"）→ 估计栏边界 →
caption 上/下方扩张出候选区域 → 用图形证据（嵌入光栅 bbox + 矢量聚类 bbox）收紧 →
过滤 logo/分隔线 → 450dpi clip 渲染。表格走对称逻辑（caption 在表上方，向下扩张）。

## 标准工作流（感知闭环）

1. `python3 scripts/extract_figures.py paper.pdf -o figures/ --dpi 450` 读完输出清单
2. **Read 抽查** manifest 里 confidence=high 的图 + 全部 figure 类：裁剪是否带正文、是否截断
3. 对可疑页 `--render-page N` 渲染整页预览（130dpi），Read 看清版面后 `--crop N,x0,y0,x1,y1` 精裁
   （坐标单位 pt，原点页面左上；预览图 130dpi 下像素 ÷ 1.8 ≈ pt，直接估算即可）
4. 把最终选用的图记入构建脚本，caption 从 manifest 取原文后**改写为口语化图注**

## 判断图类型（决定提图策略）

| 类型 | 特征 | 策略 |
|---|---|---|
| 矢量框架图 | Visio/PPT/TikZ 导出，放大不糊 | 必须 clip 渲染（manifest type=render）|
| 嵌入光栅图 | matplotlib/实验截图/照片 | 优先原生位图（type=native，分辨率最高）|
| 混合 | 矢量底 + 位图贴片 | clip 渲染（原生抽取会丢矢量部分）|
| 表格 | kind=table | 一般不入 PPT，数据重排为三线表更优雅；确需截图再渲染 |

## 疑难场景

- **扫描版 PDF（图片页）**：无文本层 → caption 定位失效。直接 `--render-page` 看版面 + `--crop` 手动裁
- **PPT 导出的 PDF / 单栏大图论文**：caption 常缺失 → 自动提取为空。用 preview+crop 两步走
- **arXiv 预印本双栏**：脚本已按栏边界约束，不会把另一栏裁进来；跨栏图（全宽）自动放宽到页宽
- **caption 误报**（正文行首恰好 "Figure 3 shows…"）：打分机制已排除（要求标点/小字号/加粗）；
  仍误报时忽略 manifest 中 caption 明显是句子的条目
- **图在下一页**（caption 与图分离）：manifest 该页 confidence=low 或区域全白 → 检查下一页
- **图太小/截断**：`--min-size` 调低（默认 36pt）；或对 bbox 手动外扩后用 --crop
- **中文论文**：已支持 "图 1 / 表 1"；GB/T 排版图注同样在图下、表上，逻辑通用

## 提取后的质检

- Read 打开 PNG：四边不应切到图内容（bbox 略外扩 4pt 已内置，仍不够就 crop 外扩）
- 不应包含周围正文行、页眉页脚
- w_px < 800 的图在全宽（≈12"）展示会糊：优先找更高 DPI 源、或只放半宽
- 同一图多次出现（模板页眉 logo 等）按 manifest page 去重

## 放进 PPT 前的最后一步

从论文原图直接可用，但**图注必须重写**（口语化、结论先行），并标注图源；
论文图内文字若 <14pt 等效字号，投影不可读 —— 可用 --crop 放大关键局部另成一页。
