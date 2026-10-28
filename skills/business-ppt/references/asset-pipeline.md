# 商业素材管线（品牌 / 影像 / 二维码 / 展台交付）

商业 deck 的质感 70% 来自素材一致性，而不是版式花活。本节给出从原始物料到现场屏幕的
可复现流程；所有脚本纯离线、无网络依赖（二维码库除外）。

## 1. 品牌资产

### 输入清单
- logo：矢量（SVG/AI/EPS）优先；没有矢量就用 ≥ 2000px 宽的透明 PNG；**不要**从官网截图
- 品牌色：品牌手册 hex 优先；没有手册才从 logo 取色
- 品牌字体：名称 + 授权文件；拿不到就回到 skill 默认字体，不要用未授权字体
- 公司全称 / 英文名 / 简称：三个都要，封面用全称或英文名，页脚用简称 wordmark

### 从 logo 提取色板
```bash
python3 <skill_dir>/scripts/brand_kit.py logo.png -o brand/
# 产出：
#   brand/palette.json    primary / secondary / accent / ink / paper + tint 系列
#   brand/palette.png     1600×400 色板预览（人眼复核用）
#   brand/logo_ink.png    单色深版（浅底用）
#   brand/logo_white.png  单色白版（深底用）
```
脚本会剔除接近白/黑的背景像素、按"占比 × 饱和度"排序取主色。**必须人眼复核**：
渐变 logo、灰色 logo、含照片的 logo 可能提出脏色；品牌手册有官方色时以手册为准，
把 hex 直接写进构建脚本，不要用提取值覆盖官方值。

### 使用纪律
- logo 四周留白 ≥ logo 高度的 1/2（clearspace），任何文字/细线不得侵入
- 深底用 `logo_white.png`，浅底用 `logo_ink.png`；不要给彩色 logo 加描边或阴影
- 合作方 logo 一律转灰度、统一视觉高度（0.45–0.6"），不要拉伸到同宽高
- 没有授权 logo 就不放；用文字列出合作类型，比放一堆灰 logo 更可信

## 2. 影像处理

### 分辨率与比例
| 用途 | 最小像素 | 比例 |
|---|---|---|
| 全幅封面/hero（1080p 屏） | 1920×1080 | 16:9 |
| 全幅（4K 屏/近看） | 3840×2160 | 16:9 |
| 半幅图（左/右半版） | 1400×2100 | 2:3 或按版面 |
| 产品方图 | 1600×1600 | 1:1 |

低于 1400px 宽的图不要全幅放；宁可缩小放半版或换成色块 + 数据。

### 统一裁切（先裁后放，禁止拉伸）
```python
from PIL import Image, ImageOps, ImageEnhance

def cover_crop(src, dst, ratio=(16, 9), warm=1.02, sat=0.92, contrast=1.05):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    tw, th = ratio
    target = tw / th
    w, h = im.size
    if w / h > target:                       # 太宽 → 裁两侧
        nw = int(h * target); x = (w - nw) // 2
        im = im.crop((x, 0, x + nw, h))
    else:                                    # 太高 → 裁上下（略偏上，保留主体）
        nh = int(w / target); y = int((h - nh) * 0.42)
        im = im.crop((0, y, w, y + nh))
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Brightness(im).enhance(warm)
    im.save(dst, quality=92, subsampling=1)
```
同一 deck 的所有现场图用同一组参数；产品图不做暖调，保持中性。

### 产品图
- 统一背景：品牌浅灰 `F2F0EB` / 暖白 `F7F5F0` / 近黑 `0E1110`，三选一
- 统一投影：右下 15–25% 透明软阴影，或干脆无阴影（更高级）
- 抠图不干净：不要硬抠，改为等比放在色块中央，四周留 15% 呼吸
- 多产品并排：统一视觉高度，不统一外框尺寸

### 人物与场景
- 肖像需授权；展会现场图避免可识别人脸（或取得同意）
- 不要用"西装握手""地球仪""玻璃幕墙大楼"类图库图；宁可用产品/场景实拍
- AI 生成图必须标注（如公司政策要求），且不得冒充实拍/客户现场

## 3. 二维码（展台承接）

```bash
# qrcode 库（一次性安装）
python3 -m pip install "qrcode[pil]"

# 生成品牌色二维码（脚本片段，可直接放进构建脚本）
python3 - <<'PY'
import qrcode
from qrcode.constants import ERROR_CORRECT_H
qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H,
                   box_size=16, border=4)
qr.add_data("https://example.com/demo?utm_source=booth&utm_campaign=exp2026")
qr.make(fit=True)
qr.make_image(fill_color="#17191C", back_color="#F7F5F0").save("qr_demo.png")
PY
```

规则：
- 指向**具体落地页**（预约演示/白皮书/企微），带 UTM；不要指向官网首页
- 容错等级 H（30%），中间可放 logo ≤ 20% 面积；四周 quiet zone ≥ 4 模块，不得裁掉
- 屏幕显示尺寸 ≥ 1.2"（1080p 下约 173px），对比度 ≥ 4.5:1；深色底用白卡托底
- 旁边必须有动作指令（"扫码预约 30 分钟场景评估"），不要只放一个码
- 交付前用两台手机实扫（iOS/Android 各一），并在展台实际亮度/距离下再扫一次
- 用动态二维码便于换链接；印刷物料与屏幕用同一个码，避免现场对不上

## 4. 展台循环交付

### 写入自动换页 + 循环
```bash
python3 <skill_dir>/scripts/set_loop.py deck.pptx --seconds 8 --fade -o deck_loop.pptx
# 可对不同页用不同停留：--seconds 8 --first 10 --last 12
```
脚本做两件事：给每页写入 `p:transition`（`advTm` 毫秒 + 可选淡入），给演示文稿写入
`p:showPr loop="1"`。PowerPoint 打开后按 F5 即无人值守循环；WPS 亦兼容。
现场同时准备：
1. `deck_loop.pptx`（主播放）
2. `deck.pdf`（字体缺失/软件故障备份）
3. `png/` 逐页图（用看图软件全屏轮播，最兜底）
4. `讲稿_展台循环.md`（销售现场讲解版）

### 屏幕与现场
- 分辨率按屏幕原生设置（1920×1080 或 3840×2160），不要缩放输出
- 色彩 sRGB；展馆屏幕常偏艳，交付前在目标屏上看一遍灰阶与肤色
- 画面比例 16:9；竖屏展位需单独出 9:16 版（重排，不旋转）
- 安全区 5%：标题、二维码、展位号离边缘 ≥ 0.65"（1080p 约 94px）
- 关闭系统通知、屏保、自动更新；用展台账号，桌面只留播放文件
- 音量关闭（展台通常无音响），所有信息必须在画面上
- 循环总长 60–90s；单页 6–12s；转场只用 0.4s 淡入淡出

### 导出命令
```bash
soffice --headless --convert-to pdf --outdir pdf/ deck_loop.pptx
pdftoppm -png -r 144 pdf/deck_loop.pdf png/slide     # 1920×1080 逐页图
# 远距离检查：再缩到 480px 宽看主标题/数字是否仍可读
python3 - <<'PY'
from PIL import Image; import glob, os
os.makedirs("png/check", exist_ok=True)
for p in sorted(glob.glob("png/slide-*.png")):
    im = Image.open(p); im.thumbnail((480, 480))
    im.save("png/check/" + os.path.basename(p))
PY
```

## 5. 合规与事实

- 客户 logo、案例、评价：书面授权；未授权用匿名行业描述
- 数据：注明口径、时间、来源；预测值标"预测/测算"，不与实测混排
- 对外版本移除：内部代号、未发布功能、其他客户名称、个人手机号
- 图片：商用授权（Unsplash/Pexels 可商用但需注意肖像/商标）；企业官网图不等于可商用
- AI 生成内容：按公司政策标注；不得用于伪造客户现场、资质或团队照片
- 按" deck 会被拍照发到行业群"的标准做脱敏

## 6. 交付目录

```
<项目>/
  build_business.py          # 构建脚本（改字重跑）
  bg/                        # make_backgrounds.py 产出
  brand/                     # logo / palette.json / 单色 logo / qr
  img/                       # 统一裁切后的影像
  out/
    <公司>_<展会>_展台循环.pptx
    <公司>_<展会>_展台循环.pdf
    png/                     # 逐页图 + check/ 远距离检查图
  讲稿_展台循环.md
```
