#!/usr/bin/env python3
"""竞赛版 v3（17 页）讲稿：注入中英 deck + 导出对照 md。"""
import os
from pptx import Presentation
BASE = os.path.dirname(os.path.abspath(__file__))
N = [
("尊敬的各位评委，大家好！我们是北航 ColaLab 团队，带来的项目是「天行 TravelUAV」——会听懂的无人机。封面就是平台实况：无人机在城市上空自主飞行，右上角是它的第一视角。项目已产出 12,149 条真实专家轨迹、6 自由度飞行动力学平台，核心指标超越基线 109%。","Distinguished judges, good afternoon! We are ColaLab from Beihang University, presenting TravelUAV — the drone that listens. The cover shows the platform in action: a UAV flying autonomously over a city with its first-person view in the corner. We have delivered 12,149 real expert trajectories, a 6-DoF physics platform, and 109% SR gain over baselines."),
("汇报六部分：市场痛点、产品方案、核心技术、商业模式、团队价值、发展规划——正好对应大赛评审的五个维度。","Six parts: market pain, product, core technology, business model, team and value, and roadmap — mapping onto the five judging dimensions."),
("先看赛道。低空经济已写入政府工作报告：民航局预测 2025 年 1.5 万亿、2035 年 3.5 万亿；工信部数据，2025 年民用无人机整机产值 1761 亿、工业级占比超七成。但自动化是瓶颈——绝大多数作业仍依赖专业飞手。语言交互加自主搜索，就是无人机智能化的下一跳。","The track first: a 1.5-trillion-yuan low-altitude economy by 2025 and 3.5 trillion by 2035 per CAAC; civil drone output 176.1 billion in 2025 per MIIT. But automation is the bottleneck — most missions still need professional pilots. Language interaction plus autonomous search is the next leap."),
("这个瓶颈有多痛？同一段指令下，人类飞手成功率 94.5%，固定动作程序只有 2.27%——41 倍的能力鸿沟。原因三点：听不懂、飞不真、学不会。","How painful? Identical instructions: human pilots 94.5% vs fixed-action programs 2.27% — a 41x gap. Three root causes: can't listen, can't fly real, can't learn."),
("我们的产品是四位一体全栈方案：OpenUAV 仿真平台、12,149 条专家轨迹数据集、三级助导基准、导航大模型。左边就是产品实况——第三视角与机载第一视角同屏，全部自研、全部开源。","Our product is a four-in-one stack: the OpenUAV platform, a 12,149-trajectory dataset, the three-tier benchmark, and the navigation LLM. The left shows it live — third-person and onboard views simultaneously. All self-developed, all open source."),
("看一次真实演示：给一句话——目标在左前方、黄色轿车——它就理解指令、分层规划连续轨迹、检出目标即降落，端到端无人工规则。","A live demo: one sentence — the target is front-left, a yellow sedan — it understands, plans hierarchically, and lands on detection. End to end, no hand-crafted rules."),
("环境适应性：22 类高保真场景覆盖城市到自然，动态光照、植被摆动，89 类物体运行时摆放，为 Sim-to-Real 打底。","Environment coverage: 22 high-fidelity scene types from city to wilderness, dynamic lighting and vegetation, 89 object categories placed at runtime — the ground for Sim-to-Real."),
("技术架构：多模态大模型驱动的分层轨迹生成。指令与五视角图像编码进 Vicuna-7B 底座的 MLLM，查询 token 出远距目标位姿，前视细化解码器输出六自由度轨迹，全部自研可控。","The architecture: hierarchical trajectory generation driven by a multimodal LLM. Instructions and five-view images are encoded into the Vicuna-7B MLLM; a query token yields the long-range pose; a front-view decoder outputs 6-DoF trajectories. Fully self-controlled."),
("三大创新：一，行业改坐标造假动力学，我们自研物理级飞控；二，行业只有静态描述，我们提出 L1 到 L3 三级助导基准；三，行业用离散分类器，我们用 MLLM 生成连续轨迹，SR 提升 109%。","Three innovations: physics-level flight control vs faked dynamics; the L1–L3 assistant benchmark vs static descriptions; and MLLM continuous trajectories vs discrete classifiers — SR up 109%."),
("成果四项落地：arXiv 论文、GitHub 开源、HuggingFace 数据、开放基准；知识产权两项申报中，路演版将附受理通知书。","Four deliverables landed: the arXiv paper, GitHub code, HuggingFace data, and the open benchmark; two IP filings in progress, acceptance letters to be attached."),
("市场三层：TAM 低空经济 1.5 万亿，SAM 民用无人机整机 1761 亿，SOM 自主导航软件与服务——我们测算窗口期 3 到 5 年。政策、技术、需求三浪叠加。","Three market layers: TAM 1.5 trillion, SAM 176.1 billion, SOM navigation software and services — a 3-to-5-year window by our estimate. Policy, technology and demand converge."),
("竞品矩阵一目了然：飞控套件、航线规划、学术方案各有短板，只有我们同时具备六自由度连续轨迹、语言交互、三级引导、开放生态与大模型驱动。定位：不做硬件，做无人机大脑的训练场加大脑。","The matrix says it all: only we combine continuous 6-DoF trajectories, language interaction, tiered guidance, open ecosystem and an LLM driver. Positioning: no hardware — the training ground and the brain."),
("三线收入：平台订阅面向高校院所，数据与评测面向 AI 企业，行业方案面向应急电网安防。右侧是数据飞轮：越多人用、数据越多、模型越强、方案越值钱。","Three revenue lines: subscriptions for academia, data and evaluation for AI companies, vertical solutions for rescue, grid and security. The flywheel on the right: more users, more data, stronger models, higher-value solutions."),
("师生共创：刘偲教授国家青年人才，廖裕渊研究员、李嘉胜教授来自 CUHK MMLab；六位核心学生完成平台、数据、模型三大模块，依托北航人工智能研究院。","A co-creation team: Prof. Si Liu, Dr. Yue Liao and Prof. Hongsheng Li advising; six core students delivered the three modules, hosted by Beihang's Institute of AI."),
("社会价值四层：搜救黄金 72 小时提效、无人化巡检替代高危作业、催生新岗位、开源反哺教育。科技向善，服务国家低空战略。","Social value on four levels: faster golden-72-hour rescue, safer unmanned inspection, new jobs, and open-source education. Tech for good, serving the national strategy."),
("三年三步：2024 全栈开源已达成；2025 社区扩数据、知产申报；2026 真机验证加首批试点；2027 订阅规模化、方案复制。近期目标：2026 年两个行业试点合同加真机演示。","Three years: open source done in 2024; data growth and IP in 2025; Sim-to-Real and first pilots in 2026; scaled subscriptions in 2027+. Near-term: two pilot contracts plus a live demo in 2026."),
("我们的汇报到此结束。天行 TravelUAV，让无人机听懂人话。恳请各位评委专家批评指正，谢谢！","That's our presentation. TravelUAV — the drone that listens. We welcome your feedback. Thank you!"),
]
assert len(N) == 17, len(N)

for path, idx in [("competition/TravelUAV_竞赛版路演.pptx", 0), ("competition/TravelUAV_Competition_Roadshow_EN.pptx", 1)]:
    prs = Presentation(os.path.join(BASE, path))
    slides = list(prs.slides)
    assert len(slides) == 17, path
    for sl, pair in zip(slides, N):
        sl.notes_slide.notes_text_frame.text = pair[idx]
    prs.save(os.path.join(BASE, path))
    print("notes ->", os.path.basename(path))
with open(os.path.join(BASE, "competition/讲稿_竞赛版_中英对照.md"), "w", encoding="utf-8") as f:
    f.write("# TravelUAV 竞赛版（国创赛路演 · v3）讲稿（中英对照）\n\n")
    for i, (zh, en) in enumerate(N, 1):
        f.write(f"## 第 {i} 页\n\n**中文：** {zh}\n\n**English:** {en}\n\n")
print("md ok")
