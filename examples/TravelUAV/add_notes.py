#!/usr/bin/env python3
"""为四份 TravelUAV deck 注入演讲者备注（讲稿），并导出中英对照 Markdown 讲稿。
中文 deck 配中文讲稿，英文 deck 配英文讲稿。
"""
import os
from pptx import Presentation

BASE = os.path.dirname(os.path.abspath(__file__))

# 每页 (中文讲稿, 英文讲稿)
RESEARCH = [
# 1 封面
("各位老师、同学好，今天我给大家分享一篇北航 ColaLab 2024 年的工作 TravelUAV，题目是《面向真实无人机视觉-语言导航：平台、基准与方法》。这篇文章一口气给出了平台、数据集、基准和方法四件套，是无人机 VLN 方向比较系统的工程。",
 "Good afternoon everyone. Today I'm presenting TravelUAV from Beihang's ColaLab, 2024 — 'Towards Realistic UAV Vision-Language Navigation: Platform, Benchmark, and Methodology'. It delivers a platform, a dataset, a benchmark and a method in one paper — a fairly systematic piece of work for UAV VLN."),
# 2 提纲
("汇报分六部分：先讲动机，再依次介绍 OpenUAV 平台、数据集与基准、导航大模型，然后是实验结果，最后总结。重点会放在方法和实验两块。",
 "The talk has six parts: motivation, the OpenUAV platform, dataset and benchmark, the navigation LLM, experiments, and conclusions. I'll spend the most time on method and experiments."),
# 3 背景
("动机核心是两个失配。第一，运动动力学：地面智能体在水平面移动，离散动作就够；而无人机是六自由度三维机动，俯仰翻滚偏航耦合发生，把连续轨迹硬拆成离散动作会导致飞行不真实。第二，任务复杂度：无人机在开阔户外执行长距离任务，视点剧变、遮挡频发，单靠一段目标描述很难精确搜索。所以作者认为必须重建整个技术栈。",
 "The motivation is two mismatches. First, dynamics: ground agents move in a plane, so discrete actions suffice; UAVs fly with six degrees of freedom where pitch, roll and yaw happen together — forcing continuous flight into discrete steps is unrealistic. Second, task complexity: UAVs handle long-range outdoor tasks with shifting views and occlusions, where a static target description is rarely enough. Hence the authors rebuild the whole stack."),
# 4 数据集对比
("这是与现有 VLN 数据集的对比表。可以看到 R2R、TouchDown 这些地面数据集只有 2 自由度；无人机方向 AVDN、AerialVLN、CityNav 最多 4 自由度，而且运动学一列都是叉——轨迹是改坐标改出来的，不是真实飞控产生的。本文数据集是第一个 6 自由度带真实运动学的，1 万 2 千条轨迹、词表 1 万、平均轨迹 255 米。",
 "This table compares existing VLN datasets. Ground datasets like R2R and TouchDown have at most 2 DoF. For UAVs, AVDN, AerialVLN and CityNav reach 4 DoF but the kinematics column is all crosses — trajectories were made by teleporting coordinates, not by real flight control. This work is the first with 6 DoF and real kinematics: 12k trajectories, 10.8k vocabulary, 255 meters average length."),
# 5 平台总览
("这一页是论文的图 1，左边 OpenUAV 平台：基于 UE4 加 AirSim，提供闭环仿真、并行化、可复现条件、可配置传感器、轨迹回放；右边是 UAV-Need-Help 任务示意，助手会给无人机在线引导。这张图建议大家记住结构，后面会拆开讲。",
 "This is Figure 1. On the left, the OpenUAV platform: UE4 plus AirSim, offering closed-loop simulation, parallelization, reproducible conditions, configurable sensors and trajectory replay. On the right, the UAV-Need-Help task, where an assistant gives online guidance. Keep this structure in mind — I'll unpack it next."),
# 6 平台要点
("平台三块能力。环境：22 类高保真场景、89 类物体，支持运行时 API 自动摆放。飞控：AirSim 物理仿真，位姿六元组全记录，人控有遥控器、手动、位置三种接口，传感器覆盖五视角 RGB 加深度、360 度激光雷达。算法：内置闭环仿真接口、DAgger 和回溯策略，8 张 A100 并行能到 16 倍加速、最高 1600 帧。全平台开源。",
 "Three capability blocks. Environments: 22 high-fidelity scenes, 89 object categories with runtime placement API. Flight: AirSim physics with the full 6-tuple pose, three human-control interfaces, five-view RGB-D plus 360-degree LiDAR. Algorithms: closed-loop interface, built-in DAgger and backtracking, 16x speedup on 8 A100s at up to 1600 fps. Fully open source."),
# 7 数据集
("数据怎么来？五视角拍摄目标，GPT-4 生成描述再人工复核；飞手实飞采集轨迹，飞行中只记状态，传感器数据事后异步补采，这样不打断操作。一共 12,149 条有效轨迹，右侧是统计：轨迹长度、目标距离 50 到 400 米、89 类物体分布和四个数据划分。",
 "How was data collected? Five-view capture, GPT-4 descriptions with human review; pilots fly manually while only states are logged during flight — sensor data is back-filled asynchronously so annotation isn't interrupted. In total 12,149 valid trajectories. On the right: length distribution, 50-to-400-meter goal distances, 89 object categories, and the four splits."),
# 8 基准
("UAV-Need-Help 基准把助手指令分三级：L1 全程高频引导，始终把无人机拉回最优路径；L2 只在困难或偏航时纠偏；L3 只在危险时避障。这三级非常贴近真实的人机协作场景。任务定义：输入描述、状态、五视角图像和助手指令，输出六自由度轨迹，降落点距目标 20 米内算成功。",
 "The benchmark tiers assistant guidance into three levels: L1 gives constant high-frequency guidance along the oracle path; L2 only corrects on difficulty or deviation; L3 only issues avoidance commands in danger. These mirror real human-UAV teamwork. Formally: description, state, five-view images and instructions in; a 6-DoF trajectory out; landing within 20 meters counts as success."),
# 9 方法总框架
("方法框架图。指令和多视角图像分别做 token 化，拼接送进以 Vicuna-7B 为底座的 MLLM；一个可学习的 waypoint 查询 token 从 LLM 里抽取轨迹特征，经 MLP 解出远距目标位姿；然后前视细化解码器结合前视 token 生成精细轨迹序列。检测到目标就触发降落。",
 "The architecture. Instructions and multi-view images are tokenized, concatenated, and fed into an MLLM based on Vicuna-7B. A learnable waypoint query token extracts trajectory features from the LLM, decoded by an MLP into a long-range target pose. A front-view completion model then refines that into a fine-grained pose sequence. Grounding DINO detection triggers landing."),
# 10 方法细节
("分层三步。第一步多模态 token 化：EVA-CLIP 加 Q-former，每个视角 1 个全局加 16 个局部 token。第二步高层解码：waypoint token 出远距目标位姿。第三步细粒度解码：前视 token 拼上目标位姿特征出轨迹序列。训练上还有回溯采样 DAgger：碰撞就回退两帧改走教师轨迹，从失败里挖避障样本。",
 "Three hierarchical steps. One, multimodal tokenization: EVA-CLIP plus Q-former, one global and sixteen local tokens per view. Two, high-level decoding: the waypoint token yields the long-range target pose. Three, fine-grained decoding: front-view tokens plus pose features produce the trajectory. Training adds backtracking-sampling DAgger — on collision, revert two frames and follow the teacher, mining avoidance samples from failures."),
# 11 主实验
("主结果，Test Seen、L1 助手设定。随机 0.14，固定动作 2.27，经典 CMA 8.37；本文方法 16.10，加回溯 DAgger 后 17.45，SR 相对 CMA 提升 109%；OSR 到了 48.87，说明接近一半任务能途经最优路径。但注意人类是 94.51，差距仍然巨大，这个任务远没有解决。",
 "Main results on Test Seen with the L1 assistant. Random gets 0.14, fixed actions 2.27, the classic CMA 8.37. Ours reaches 16.10, and 17.45 with backtracking DAgger — a 109% relative SR gain over CMA. OSR hits 48.87, meaning nearly half the episodes touch the optimal path. But humans sit at 94.51 — a huge gap remains; this task is far from solved."),
# 12 泛化
("两张图。左边是未见物体测试集：CMA 只有 9.06，本文 22.42，说明语言理解带来了类别迁移能力。右边数据量消融：10% 数据 10.78，50% 13.19，全量 16.10，还有增长空间。补充一句，未见地图上 SR 只有 4.18，新场景探索是下一个难点。",
 "Two charts. Left, unseen objects: CMA only 9.06 versus our 22.42 — language understanding transfers across categories. Right, the data ablation: 10.78 at 10% data, 13.19 at 50%, 16.10 at full — still headroom to grow. One caveat: on unseen maps SR drops to 4.18; exploring new scenes is the next challenge."),
# 13 定性
("定性结果。前两行是成功案例：按指令找到车辆和奶牛，第 3 到 5 帧能看到转向机动改变视点。第三行是失败案例，在森林场景撞树了——这也是回溯采样想解决的问题。",
 "Qualitative results. The top two rows are successes: the UAV finds the described vehicle and cow; frames three to five show a turning maneuver changing viewpoint. The bottom row is a failure — a collision with trees in a forest, exactly what backtracking sampling aims to mitigate."),
# 14 结论
("总结三点贡献：OpenUAV 平台、1 万 2 千条轨迹的数据集加三级助导基准、以及分层轨迹生成的导航大模型，全部开源。展望：与人类 77 个点的差距、未见场景泛化和真机部署是未来方向。我的汇报到这里，谢谢大家，欢迎提问。",
 "Three contributions: the OpenUAV platform; the 12k-trajectory dataset with the three-tier benchmark; and the hierarchical navigation LLM — all open source. Looking ahead, the 77-point gap to humans, unseen-scene generalization, and real-UAV deployment are the frontiers. That's my presentation — thank you, and I'm happy to take questions."),
]

COMPETITION = [
# 1 封面
("尊敬的各位评委，大家好！我是北航 ColaLab 团队，今天带来的项目是天行 TravelUAV——面向真实世界的无人机视觉语言导航平台。一句话：让无人机听懂人话，在真实三维空域里自主搜索目标。项目已产出 6 自由度飞行动力学平台、一万两千条专家轨迹，核心指标超越基线五个百分点。",
 "Distinguished judges, good afternoon! We are the ColaLab team from Beihang University. Our project, TravelUAV, is a realistic vision-language navigation platform for UAVs — in one sentence, drones that understand language and search targets in real 3-D airspace. We've delivered a 6-DoF flight platform, twelve thousand expert trajectories, and performance five points above baselines."),
# 2 目录
("今天的汇报六个部分：行业痛点、解决方案、核心技术、数据成果、团队和规划愿景。整个项目的故事线就是：发现行业走不出去的三个坑，然后用一套全栈方案把它们一次填平。",
 "Six parts today: pain points, our solution, core technology, results, team, and roadmap. The storyline: three industry traps, and one full-stack solution that fills them all at once."),
# 3 章节01
("第一部分，行业痛点。",
 "Part one — the pain points."),
# 4 痛点
("三个痛点。第一，动作空间失真：现有方案沿用地面导航的离散动作，但无人机俯仰翻滚偏航是耦合发生的，硬拆的结果就是飞不真实。第二，真实数据空白：之前根本没有带真实飞行动力学的无人机导航数据集，轨迹都是改坐标改出来的。第三，指令能力不足：开阔场景视点剧变遮挡频发，纯文字描述撑不起精确搜索。左边这个数字很扎心：固定动作基线成功率 2.27%，人类飞手 94.51%。",
 "Three pain points. First, unrealistic action space: existing work reuses ground-based discrete actions, but pitch, roll and yaw happen together — forcing them apart produces fake flight. Second, no real data: before us there was no UAV navigation dataset with real flight dynamics; trajectories were teleported. Third, instructions alone are insufficient: shifting views and occlusions defeat pure text. The number stings: fixed actions succeed 2.27% of the time; human pilots, 94.51%."),
# 5 章节02
("第二部分，解决方案。",
 "Part two — our solution."),
# 6 方案总览
("我们的方案是四件套。OpenUAV 仿真平台：UE4 加 AirSim，22 场景 89 物体，物理级飞控。一万两千条专家轨迹数据集：飞手实飞加 GPT-4 描述。UAV-Need-Help 三级助导基准：模拟真实人机协作。最后是导航大模型：分层轨迹生成。四件套全部开源，社区可以直接复现扩展。",
 "Our solution is a four-piece stack. The OpenUAV platform: UE4 plus AirSim, 22 scenes, 89 objects, physics-level flight control. A 12,149-trajectory expert dataset: real pilots plus GPT-4 descriptions. The UAV-Need-Help three-tier benchmark mirroring real teamwork. And the navigation LLM with hierarchical trajectory generation. All four pieces are open source."),
# 7 应用场景
("这套技术往哪落？应急搜救：按描述在山区找失踪人员；电力巡检：长航时走廊飞行定位故障；安防监控：园区网格巡逻即时检索目标；物流配送：降落点视觉定位。特别说明，三级助导从全程引导到只避障，天然对应从地面站协作到全自主的落地路径。",
 "Where does it land? Emergency search and rescue by description; powerline inspection with fault localization; campus and city security patrol; logistics landing-point localization. Note that the three assistant tiers map naturally onto the deployment path from ground-station teamwork to full autonomy."),
# 8 章节03
("第三部分，核心技术。",
 "Part three — core technology."),
# 9 技术架构
("这是技术架构总图。指令和多视角图像编码进多模态大模型，一个可学习的查询 token 预测远距目标位姿，前视细化解码器输出六自由度精细轨迹。这套架构直接端到端吃图像和语言，不做人工规则映射。",
 "The architecture. Instructions and five-view images are encoded into the multimodal LLM; a learnable query token predicts the long-range target pose, and a front-view decoder outputs fine 6-DoF trajectories. It consumes images and language end to end — no hand-crafted rule mapping."),
# 10 关键技术一
("关键技术一：分层轨迹生成。先粗后细——第一步多模态 token 化，第二步解出远距目标位姿做全局规划，第三步前视细化解出精细轨迹，检测到目标就降落。分层的价值看右下角：成功率较单层 CMA 基线直接翻倍，8.37 到 16.10。",
 "Key technology one: hierarchical generation — plan coarse, then refine. Tokenize multimodal inputs; decode a long-range target pose for global planning; refine with front-view features into fine trajectories and land on detection. The payoff, bottom right: success rate doubles the single-level CMA baseline, 8.37 to 16.10."),
# 11 关键技术二
("关键技术二：回溯采样 DAgger。流程是：模型输出轨迹、闭环仿真飞行、一旦碰撞，平台把无人机回退两帧、改走教师轨迹继续飞，这样每场事故都变成了避障训练样本，零额外采集成本。效果：SR 从 16.10 提到 17.45，而且数据越多涨得越多。",
 "Key technology two: backtracking-sampling DAgger. The loop: the model flies in closed-loop simulation; on collision the platform reverts the UAV two frames and switches to the teacher — every crash becomes an avoidance sample at zero extra cost. Result: SR rises from 16.10 to 17.45, and keeps climbing with more data."),
# 12 章节04
("第四部分，数据与成果。",
 "Part four — data and results."),
# 13 大数字
("用数字说话：一万两千一百四十九条专家轨迹；22 个高保真场景、89 类物体；6 自由度真实动力学。下半区：仿真吞吐 160 到 1600 帧每秒，8 张 A100 并行 16 倍加速；平均轨迹 255 米，最长目标距离 400 米；指令词表 1 万零 8 百，平均每条指令 104 词。",
 "Let the numbers speak: 12,149 expert trajectories; 22 high-fidelity scenes and 89 object categories; 6-DoF realistic dynamics. Below: 160-to-1600 fps simulation, a 16x speedup on 8 A100s; 255-meter average trajectories with goals up to 400 meters; a 10.8k vocabulary at 104 words per instruction."),
# 14 性能对比
("性能对比。左图五根柱子：随机 0.14、固定动作 2.27、最强基线 CMA 8.37、我们 16.10、金色这根加了回溯 DAgger 17.45——较 CMA 提升 109%。右侧关键指标：OSR 48.87 说明近半任务能途经最优路径，NE 98.66 米对比人类 14.15 米。",
 "Performance. Five bars: random 0.14, fixed actions 2.27, the strongest baseline CMA 8.37, ours 16.10, and the gold bar with backtracking DAgger at 17.45 — a 109% gain over CMA. On the right: OSR 48.87 means nearly half the tasks touch the optimal path; final error 98.66 meters versus the human 14.15."),
# 15 泛化
("泛化能力和天花板。左图三个测试集：常规 16.10、未见物体 22.42——金色高亮，语言理解真的带来了类别迁移；但未见地图掉到 4.18。右边这个数字 94.5% 是人类飞手的成功率，和模型差 77 个点——我们如实呈现这个差距，它正是这个赛道的价值所在。",
 "Generalization and the ceiling. Three test sets: 16.10 on seen, 22.42 on unseen objects — the gold bar — language understanding genuinely transfers across categories; but 4.18 on unseen maps. And 94.5% is the human pilot rate, 77 points above the model. We present this gap honestly — it is exactly why this track matters."),
# 16 章节05
("第五部分，团队。",
 "Part five — the team."),
# 17 团队
("团队来自北航人工智能研究院 ColaLab，七位核心成员，王翔宇、杨东林、王子衿为共同一作，刘偲教授为通讯作者；联合指导方是香港中文大学 MMLab 的李嘉胜教授团队，多模态大模型方向顶尖力量。团队在具身智能与大模型方向有长期积累。",
 "The team comes from ColaLab at Beihang's Institute of AI — seven core members, with Wang Xiangyu, Yang Donglin and Ziqin Wang as equal contributors and Prof. Si Liu as corresponding author. Our co-advisors are Prof. Hongsheng Li's MMLab at CUHK, a top group in multimodal models. The team has long-standing depth in embodied AI and large models."),
# 18 章节06
("最后一部分，规划与愿景。",
 "Finally — roadmap and vision."),
# 19 规划
("路线图四步。2024 年 10 月已完成：平台、数据集、基准、模型全部开源发布。2025 年进行中：社区共建，更多场景和物体资产接入。2026 年下一步：Sim-to-Real，真机部署跨越仿真到现实的鸿沟。远期愿景：多机协同搜索，城市级低空智能导航网络。社会价值一句话：让应急救援、电力巡检、城市治理用上低成本会听的无人机。",
 "A four-step roadmap. Done, October 2024: platform, dataset, benchmark and model all open-sourced. Ongoing in 2025: community building with more scenes and assets. Next, 2026: Sim-to-Real — physical UAVs crossing the reality gap. Long term: swarm search and a city-scale low-altitude navigation network. In one sentence: affordable, listening drones for rescue, inspection and city governance."),
# 20 致谢
("我们的汇报到此结束，恳请各位评委专家批评指正，谢谢！",
 "That concludes our presentation. We sincerely welcome your feedback — thank you!"),
]

def apply(path, notes, lang_idx):
    prs = Presentation(path)
    slides = list(prs.slides)
    assert len(slides) == len(notes), f"{path}: {len(slides)} slides vs {len(notes)} notes"
    for sl, (zh, en) in zip(slides, notes):
        sl.notes_slide.notes_text_frame.text = zh if lang_idx == 0 else en
    prs.save(path)
    print("notes ->", os.path.basename(path))

def export_md(path, notes, title):
    lines = [f"# {title} 讲稿（中英对照）\n"]
    for i, (zh, en) in enumerate(notes, 1):
        lines.append(f"## 第 {i} 页\n\n**中文：** {zh}\n\n**English:** {en}\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("md ->", os.path.basename(path))

apply(os.path.join(BASE, "research", "TravelUAV_科研版组会汇报.pptx"), RESEARCH, 0)
apply(os.path.join(BASE, "research", "TravelUAV_Research_GroupMeeting_EN.pptx"), RESEARCH, 1)
apply(os.path.join(BASE, "competition", "TravelUAV_竞赛版路演.pptx"), COMPETITION, 0)
apply(os.path.join(BASE, "competition", "TravelUAV_Competition_Roadshow_EN.pptx"), COMPETITION, 1)
export_md(os.path.join(BASE, "research", "讲稿_科研版_中英对照.md"), RESEARCH, "TravelUAV 科研版（组会汇报）")
export_md(os.path.join(BASE, "competition", "讲稿_竞赛版_中英对照.md"), COMPETITION, "TravelUAV 竞赛版（路演）")
