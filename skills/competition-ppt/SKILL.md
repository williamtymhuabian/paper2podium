---
name: competition-ppt
description: 生成中国大学生竞赛路演级演示文稿：挑战杯（大挑/小挑）、中国国际大学生创新大赛（原互联网+）、创青春、三创赛、节能减排等科创/创业竞赛的省赛国赛答辩与路演。当用户提到"竞赛PPT、挑战杯PPT、路演PPT、答辩PPT、创赛、国赛、省赛、项目路演、网评PPT"，或要求"做一套能打国赛的项目展示/申报书配套PPT"时使用。国赛金奖主流的深空科技蓝视觉（渐变+星空背景+顶部导航+超大数字成果页），固定"痛点-方案-技术-市场-团队"叙事线，支持从论文 PDF 提取技术框架图。
---

# 竞赛 PPT（挑战杯 / 大创赛路演级）

为竞赛答辩/路演产出**有冲击力、信息密度可控、评委 3 秒抓住重点**的演示文稿。
国赛获奖 deck 的共性：深空科技蓝主视觉、渐变星空背景、顶部导航栏、超大数字成果、
固定叙事线（痛点→方案→技术→市场→商业模式→团队→规划）。

构建工具链与官方 pptx skill 一致（pptxgenjs，画布 13.33 × 7.5"），本 skill 负责竞赛场景的
设计系统、叙事结构与素材管线。写构建脚本前按需读：

- `references/design-system.md` —— 三种风格色板 / 字体 / 逐页版式配方（含坐标），**必读**
- `references/narrative-and-pages.md` —— 叙事线、页数配比、网评版 vs 路演版、每页内容清单，**必读**

## 0. 触发后第一件事：确认竞赛参数

1. **赛事与赛道**：挑战杯大挑（学术）/ 小挑（创业计划）/ 大创赛（高教主赛道、红旅赛道、产业赛道）…
   - 学术类 → 偏重研究背景、数据论证；创业类 → 偏重痛点、市场、商业模式
   - 红旅/公益/党建相关 → 默认改用**红色庄重风**（design-system.md 变体 B）
2. **版本与时长**：路演版（现场 8–10 min，20–28 页）还是网评版（30–40 页，信息更全）——默认路演版
3. **素材盘点**：项目名/校名/队名、校徽图片、团队照片、产品图/实物图、专利证书/获奖图、
   论文 PDF（技术框架图来源）、财务/市场数据。缺图先列清单问用户要，不用占位假图

## 1. 生成背景图（本风格的根基）

pptxgenjs 无原生渐变，星空渐变背景必须先用脚本生成：

```bash
python3 <skill_dir>/scripts/make_backgrounds.py -o bg/ --style techblue   # 默认深空科技蓝
# 或 --style red（红旅/党政风）/ --style light（浅色简约）/ --all 全部
```

产出 `cover/section/content` 三张 2560×1440 PNG：封面浓粒子+光晕、章节页侧光晕、
内容页极淡（文字为王）。内容页背景务必用 content 版，不得把封面背景用在内容页。

## 2. 从论文 PDF 提取技术框架图

技术架构页的证据图（系统框架、算法流程、实验对比）从论文精准分割，不截图：

```bash
python3 <skill_dir>/scripts/extract_figures.py paper.pdf -o figures/ --dpi 450          # 自动（caption 锚定）
python3 <skill_dir>/scripts/extract_figures.py paper.pdf -o figures/ --render-page 3    # 整页预览定位
python3 <skill_dir>/scripts/extract_figures.py paper.pdf -o figures/ --crop 3,72,220,540,560  # 手动精裁
```

闭环：自动提取 → Read 抽查 PNG → 裁歪的 preview+crop 修正。深色页放白底论文图要加
0.75pt 浅色描边防"白块浮起"。依赖 `pip install pymupdf`。

## 3. 设计系统（摘要，细节见 references/design-system.md）

- **默认风格 A 深空科技蓝**：深海军蓝渐变星空背景；主色科技蓝 `2F80FF`；强调金 `FFC53D`
  （奖牌/核心数字）；亮青 `38D6FF`（数据/光效线）；白字 + 雾蓝 `A8C3E8` 次要字
- **变体 B 红色庄重风**（红旅/公益/党建赛道）：深红渐变 + 金色点缀
- **变体 C 浅色简约**（评委偏好清爽/医疗民生类）：白底 + 品蓝
- **字体**：微软雅黑 Bold 大标题（封面 40–52pt）/ Regular 正文 18–22pt；数字用 Arial Bold 放大
- **顶部导航**（本风格签名）：每页顶部一行章节名文字导航，当前章白字加粗、其余 40% 透明雾蓝，
  无底色条；页码右下角。封面/致谢页不出现导航
- **数字为王**：任何成果数字放大到 60–96pt 金色/亮青，配 14–16pt 灰蓝单位说明；正文禁止长段落
- **卡片**：深蓝半透明卡（`1A2A54` + 透明度 20–35% 或 1pt 科技蓝描边）承载痛点/功能/团队成员；
  卡片圆角 0.08"，不加侧边彩条

## 4. 构建要点（pptxgenjs）

- `LAYOUT_WIDE`；色板常量定义在脚本顶部；背景 `slide.background = { path: "bg/xxx.png" }`
- 逐页配方（含坐标）在 `references/design-system.md`；叙事与页数在 `references/narrative-and-pages.md`
- 时间轴/路线图/流程图用原生 shape（chevron/箭头/圆点+连线）构建，继承色板
- 数据图用原生 `addChart`（科技蓝系 chartColors），关键柱用金色单点高亮
- 沿用官方 pptx skill 机制：hex 不带 `#`、bullet 工厂函数 `indent:12`、`breakLine:true`、
  shadow offset 非负、图片 `sizing:{type:'cover'}`、LAYOUT_WIDE 必须显式设置

## 5. QA（交付前）

1. 溢出检查（python-pptx 脚本：文本越界/形状重叠/超出画布）
2. 视觉审查：`soffice --headless --convert-to pdf` → `pdftoppm -png -r 150` 渲染逐页检查
   （或 visual-judge 子代理）：导航章节点亮是否正确、背景是否用对（content 页必须安静）、
   大数字是否溢出、论文图是否清晰无变形
3. 内容检查：叙事线完整（痛点→方案→技术→市场→团队→规划）、无占位符、每页有且只有一个焦点
4. 交付命名如 `XX项目_挑战杯国赛路演.pptx`；speaker notes 写入每页 30 秒讲稿

## 6. 竞赛场禁忌

- ❌ 内容页用封面级浓背景（文字看不清，评委观感"糊"）
- ❌ 假数据/无来源市场数字（评委必问，标注来源"艾瑞咨询 2025"类真实出处或"团队测算"）
- ❌ 花哨转场动画（默认全部不加）
- ❌ 团队页放网络图片冒充实物/场景图；缺图向用户要
- ❌ 每页多个焦点、满屏小字（路演页是给评委扫的，不是读物）
