# 竞赛 PPT 设计系统（国赛路演级）

画布 13.33 × 7.5 英寸，边距 M = 0.55"，导航带 y 0.22–0.52。所有坐标英寸。

## 1. 风格与色板

### 风格 A · 深空科技蓝（默认，理工/信息/智能装备类）
```js
const BG_DARK  = "0A1F3C";  // 底色基准（背景图由 make_backgrounds.py 生成）
const PRIMARY  = "2F80FF";  // 科技蓝：标题重点、图表主色、描边
const ACCENT   = "FFC53D";  // 强调金：核心数字、奖章、唯一焦点（每页至多一处大用）
const CYAN     = "38D6FF";  // 亮青：数据高亮、光效线、次强调
const TEXT     = "FFFFFF";  // 主文字
const MUTED    = "A8C3E8";  // 雾蓝次要文字
const CARD     = "13294F";  // 卡片底（配合 25% 透明度使用更透）
```

### 风格 B · 红色庄重（红旅/公益/党建/思政类）
```js
const PRIMARY = "D2453C"; const ACCENT = "F7C65B"; const CYAN = "F2A93B";
const TEXT = "FFFFFF"; const MUTED = "E8C3B0"; const CARD = "5C1018";
// 背景用 make_backgrounds.py --style red；庄重感来自克制：金色仅点缀数字与分隔
```

### 风格 C · 浅色简约（医疗/民生/教育类或评委偏好清爽）
```js
const BG = "FFFFFF"; const PRIMARY = "2563EB"; const ACCENT = "F59E0B";
const TEXT = "1E293B"; const MUTED = "64748B"; const CARD = "F1F5FB";
// 背景用 --style light；浅色下数字用 PRIMARY，ACCENT 只给一处
```

## 2. 字体与字号

```js
const F = "微软雅黑";          // 全 deck 显式指定
const FN = "Arial";            // 数字/英文大数字用 Arial Bold 更挺拔
```

| 元素 | 字号 | 备注 |
|---|---|---|
| 封面项目名 | 40–52 | Bold 白，两行以内 |
| 封面赛事/队名信息 | 16–18 | MUTED |
| 章节过渡页大标题 | 40–44 | Bold + 巨号章节数字 110pt 10% 透明度置于底层 |
| 页标题 | 30–34 | Bold 白，左对齐，y≈0.62 |
| 导航章名 | 12 | 当前章白 Bold，其余 MUTED 40% 透明 |
| 正文/卡片文字 | 18–20 | 每卡 ≤3 行 |
| 核心数字 | 60–96 | Arial Bold，ACCENT 或 CYAN |
| 数字下标签 | 14–16 | MUTED |

## 3. 全局签名元素

### 顶部导航（每内容页，功能性元素承载结构，不是装饰条）
```
y=0.30，从 M 到 W-M：章节名 12pt 依次排开，间隔 " · "（细点分隔）
当前章：FFFFFF Bold；其余：MUTED + transparency 55
右下角页码 12pt MUTED；章节过渡后第一页起导航点亮新章
```

### 卡片（承载痛点/功能/团队/荣誉）
- 底 `CARD` 透明度 25%（浅色风格用 `CARD` 实底），圆角 `rectRadius 0.08`
- 或 1pt `PRIMARY` 40% 透明描边、无底；两种二选一全 deck 统一
- 卡内：编号/数字（24pt CYAN Bold）+ 标题（20pt Bold 白）+ 说明（16pt MUTED，≤2 行）
- 禁止侧边彩条、禁止阴影堆叠

## 4. 逐页版式配方（默认路演版 22 页结构，见 narrative-and-pages.md）

### P1 封面（cover 背景）
- 赛事名 16pt CYAN 字符加宽（charSpacing 3），如 "第十九届挑战杯全国决赛"
- 项目名 44–52pt Bold 白，居中 y≈2.6–3.6（两行以内，主标题拆行控制节奏）
- 一句话定位 18pt MUTED，如 "基于多模态大模型的工业质检系统"
- 底部：校徽图 0.85"（左 M）+ 队名/负责人/指导教师 14pt（居中或右侧）

### P2 目录/导航总览
6 章横排或 2×3：巨号编号 01–06（32pt CYAN Bold）+ 章名 22pt Bold 白 + 一句话 14pt MUTED。

### 章节过渡页（section 背景）
- 巨号章节数字 "03" 110pt Bold，PRIMARY 15% 透明度，右下大块
- 章名 40pt Bold 白 y≈3.0；本章要讲的一句线 18pt MUTED
- 导航条本章点亮

### 痛点页（1–2 页）
三卡横排：卡 3.75×3.2"，y≈2.2，x = M / M+4.21 / M+8.42；
卡内 01/02/03 编号 + 痛点名 + 两行数据支撑（有来源）。
可用一行市场反差数字置顶（如 "85% 工厂仍依赖人工目检" 48pt ACCENT）作页焦点。

### 方案/产品页
左 55%：方案示意（原生 shape 流程图：输入→模块→输出，圆角矩形+箭头，PRIMARY 描边白底 8% 透明填充）；
右 45%：三条创新点（编号卡或列表），每条 ≤2 行。
有产品实物图时改为：大图左 60%（sizing cover 圆角），右列创新点。

### 技术架构页（招牌页）
- 页标题 "技术架构：三层闭环实现 X"
- 论文框架图（extract_figures 450dpi）居中，宽 ≤ 9"，按像素比定高，垂直居中 y 1.5–6.9
- 白底图加 0.75pt `A8C3E8` 描边防浮起；四周留呼吸
- 图下三枚技术指标小卡（准确率/延迟/成本，24pt CYAN 数字）
- 无论文图时用原生 shape 重绘架构（浅色 8% 透明填充模块 + PRIMARY 连线箭头），效果同样好且可编辑

### 数据成果页（评委记忆点）
- 顶部一行结论 22pt Bold 白
- 中部 3–4 个超大数字并排：数字 72–96pt Arial Bold ACCENT（仅一个金，其余 CYAN），
  下标签 16pt MUTED；数字间 1px 30% 透明分隔线
- 底部对比图（原生 bar：我方 ACCENT 高亮 vs 对手 PRIMARY），含真实来源行 11pt

### 市场/商业模式页
- 市场：TAM/SAM/SOM 同心圆或嵌套条（原生 shape），旁配一列增速数据
- 商业模式：流程图 shape（客户→渠道→收入），定价表用简表（表头 PRIMARY 底白字）

### 团队页
成员卡横排（0.3–0.5 间隔）：照片 1.5×1.9"（sizing cover，圆角）+ 姓名 18pt Bold +
角色/专业 14pt MUTED；下方指导教师一行；获奖/专利以徽标图或文字列表（灰色小字）呈现。

### 规划/里程碑页
横向时间轴：主轴线 2pt PRIMARY 40% 透明，节点圆点 0.16" CYAN，节点上时间 16pt Bold 白、
下事件 14pt MUTED；已完成节点实心、未来节点空心。

### 致谢页（cover 背景）
"恳请各位评委专家批评指正" 36pt Bold 白居中；队名/校徽/联系方式 14pt MUTED；
底部一行 "汇报完毕 · 感谢聆听" CYAN 14pt charSpacing 4。

## 5. 图片规则

- 实物/场景/团队照片：`sizing:{type:'cover'}` 裁切填充，先算比例再定位
- 论文框架图：等比完整展示（manifest 的 w_px/h_px 算尺寸），不裁切不拉伸
- 证书/奖状：白底描边卡内放图 + 12pt 图注说明
- 浅色风格下照片直接放，深色风格照片加 1pt 40% 透明 PRIMARY 描边融合
