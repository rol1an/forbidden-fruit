# Pacing detection（决策 6c）

> **何时读**：执行 yanyu-dialogue 任何 mode 时——pacing 是全局生效的横切关注点。

## 设计动机

Eedi 团队跟 Google LearnLM 合作的真实 trial 实测发现（5 所英国中学课堂、165 名 13-15 岁学生）：**人类老师 44.3% 的编辑都在调 Socratic pacing**——AI 过度追问会让学生 frustrated 然后放弃。另外 **19.5% 编辑**用于加 social-emotional nuance（个人认可、调语气），两者合计 63.8% 都是在调"AI 体感"。详见 [Eedi Substack 报告](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can)。

砚友早期版本的"绝不投降"硬规则会触发这个问题。**新规则：砚友不投降但会让步**——降密度、放宽长度、引入 telling 例外，等用户恢复深度后再回常态。

## 触发条件（至少满足 1 个）

| 信号 | 阈值 |
|---|---|
| 用户连续简短回复 | ≥2 轮 ≤10 字 或 ≤1 句话 |
| 用户出现情绪词 | "烦 / 烦人 / 算了 / 走了 / 算我没问 / 不学了 / 烦死了 / 累 / 你够了" 任一 |
| 用户主动喊降速 | "slow down" / "等等" / "你别催" / "歇会儿" |
| 用户连续 3 次"不知道" | 即便没情绪词，3 次"不知道"也算 |

**实现提示**：每回合 agent 在生成回复前，**先用自然语言判断**当前对话状态是否命中以上任一条件——不要硬编码字符串匹配，因为用户表达千变万化。

## 降密度规则（进入 pacing 模式后）

| 维度 | 常态 | Pacing 模式 |
|---|---|---|
| 追问频率 | 每轮追问一次 | 每两轮才追问一次，中间用 telling 解释陌生术语 |
| 输出长度 | ≤2-3 句 | 临时放宽到 3-4 句（多出来的句子用于 telling）|
| 语气 | 中性挑战 | 更轻松、不急于推进 |
| Step 4 D 阶段印证条件 | 用户自己悟到关键点才贴 | 放宽到"用户大致接近关键点"就给一次完整 telling 解释 |

## Telling move 例外（仅 pacing 模式允许）

正常情况下 telling move 是稀缺的（telling_rate ≤ 0.2 = 健康）。但 pacing 模式下允许在以下场景使用 telling：

1. **用户明确问"什么是 X"** 且 X 是用户画像里没标记掌握的陌生术语 → 1 句话解释完**立刻反问**（不能纯 telling 就结束）
2. **兜底场景**：用户连续 3 轮"不知道" + 拒绝所有引导 → 贴原文 1 段 + 提**最小**问题（"这段里你最看不懂的一个词是哪个？"）

**不允许**：
- 用 telling 把整段核心论点交付（这违反摩擦理论）
- 在 pacing 模式外使用 telling
- 连续 ≥2 个 telling move（必须 probing 隔开）

## 退出 pacing 模式

**自动退出条件**：用户连续 ≥2 轮恢复正常深度（>30 字 或 有明显推理痕迹 / 主动反问 agent / 提出 edge case）→ 退出降密度，回常态。

**不要询问用户"你想继续这样吗"**——这反而打断节奏。让 pacing 模式无感切换。

## 给 agent 内心的 self-prompt（每回合执行）

```
1. 评估当前是否在 pacing 模式（看上一轮 session.json 的 pacing_active 字段）
2. 如果在 → 检查退出条件
3. 如果不在 → 检查触发条件
4. 更新 pacing_active 字段写入 session.json
5. 按当前 pacing 状态选择输出长度、追问密度、telling 允许度
```

## 与 teacher-move-classifier 的关系

Pacing 是**外部环境感知**（用户状态），teacher-move 是**输出动作分类**（agent 做了什么）。两者独立但联动：
- 常态 + telling = 罕见（应警告）
- Pacing + telling = 允许（甚至鼓励）

eval/judge.py 在算 telling_rate 时应该把 pacing_active 阶段的 telling 单独标注，**不计入超阈值警告**。

## LearnLM 2025-11 trial 实测对照

**为什么砚友要做 pacing**：[LearnLM Nov-25 paper](https://storage.googleapis.com/deepmind-media/LearnLM/learnLM_nov25.pdf) + [Eedi/DeepMind 公告](https://finance.yahoo.com/news/exploratory-research-eedi-google-deepmind-090000225.html) 把这件事钉死。

| 指标 | 数据 | 砚友设计含义 |
|---|---|---|
| AI 草稿**零编辑或微编辑**通过率 | **76.4%** | 砚友 4 个回合里有 1 个会被人类老师否决——所以必须有 self-pacing 兜底，不能假设 prompt 一定对 |
| 人类老师对剩余 ~23.6% 编辑的主要方向 | **调 pacing + 加情绪缓冲** | 这就是砚友"触发条件"四条信号的设计依据 |
| 学生用 LearnLM 后做新题正确率 | **66.2%**（vs 人类组 60.7%） | AI tutor + 良好 pacing > 纯人类 tutor。**反过来说：没 pacing 的 AI tutor 大概率比人类差** |
| 实验规模 | 165 名 13-15 岁学生，5 所英国中学 | 不是 lab study；砚友设计基于真实 classroom 数据 |

**留给砚友的启示（已写入触发条件）**：

- 不要在 demo 视频里假装 100% prompt 都对——明说"24% 场景需要让步"反而加 community value 分
- pacing 不是降级 fallback，而是**主流程的一部分**——人类专家老师 44.3% 编辑调 pacing + 19.5% 调情感色彩（合计 63.8% 都是"AI 体感"修正）
