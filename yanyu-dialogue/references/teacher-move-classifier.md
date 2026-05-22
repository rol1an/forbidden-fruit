# Teacher-move 四分类（决策 6d）

> **何时读**：执行 yanyu-dialogue 任何 mode 时——每回合 agent 生成回复后必做内心 self-classification。

## 设计动机

MathDial（EMNLP-2023, arXiv:2305.14536）建立了 3000 条人类教师 × LLM 学生对话语料，明确编码 teacher-move 四分类。它给砚友带来两个直接价值：

1. **可观测**：原本"5 阶段 A-E"是流程描述，没法量化。四分类是离散标签，可以打到每一回合，喂 eval/judge.py 算 telling_rate / probing_depth
2. **可调优**：分类阈值（telling_rate ≤ 0.2 = 健康）给 prompt 调优一个明确的优化目标，破"8 天瞎调"死局

## 四分类定义

| 类别 | 定义 | 示例 |
|---|---|---|
| **focus** | 把用户注意力从跑题/边角拉回主线; **决策 7 后包含 hint ladder L1/L2** | "你刚提到 X，跟我们讨论的 Y 是什么关系？" / "我们回到 Step 3——你刚才说的方案对 chunk 跨段的情况怎么处理？" / L1: "答案在 <文章 X> '<某节>' 那一节——先回想那一节给的是哪类解决方案？" / L2: "反直觉之处在于不是 X，而是另一个机制——英文缩写 3 个字母。" |
| **probing** | 追问深一层，要求用户给出更多 reasoning | "为什么？" / "如果换成 Z 呢？" / "这个推理基于哪个前提？" / "你怎么证明这一步成立？" |
| **telling** | 直接告知信息 / 解释术语 / 贴原文片段 | "RAGAS 是基于 LLM-judge 的开源评估框架，包含 Faithfulness、Answer Relevancy 等指标。" |
| **generic** | 通用 backchannel，不增加信息也不推进 reasoning | "嗯" / "对" / "好的" / "我懂了" / "继续说" |

**决策 7 ladder 副标签**：[`hint-laddering.md`](hint-laddering.md) 的 L1/L2 hint 在主标签上计入 `focus`（**不算 telling**，不影响 telling_rate）；L3 (open original) 不计入主标签四分类，单独走 `ladder_level=3` 副字段。详见下方 [§Ladder level 副标签](#ladder-level-副标签决策-7) 章节。

## Ladder level 副标签（决策 7）

[`hint-laddering.md`](hint-laddering.md) 把"用户卡死"的脚手架拆成三档：

| 档位 | 主标签 `move` | 副标签 `ladder_level` | 计 telling_rate？ |
|---|---|---|---|
| L1 · Focus | `focus` | `1` | 否 |
| L2 · Recall trigger | `focus` | `2` | 否 |
| L3 · Open original | `focus`（不实质给信息）| `3` | 否, 但单独统计频次 |

`turns[]` 字段：

- `ladder_level: 1 | 2 | 3 | null`（null = 非 ladder 回合）
- `inferred_user_default: str | null`（仅 L2 必填；agent 必须先在内心反推用户脑中的默认答案）

**eval/judge.py 期望统计**：

- `ladder_l3_count`：单 session L3 触发次数
- `ladder_overuse_warning`：`ladder_l3_count ≥ 2` → 视为 prompt 失败信号（L1/L2 应覆盖 ≥80% 卡死案例，L3 是兜底）
- L1/L2 的 focus 不触发 over-focus 警告（与下方期望分布的 focus > 30% 警告分开记账）

## 期望分布（健康对话）

| 类别 | 期望占比 | 阈值 |
|---|---|---|
| probing | 50-70% | < 40% 警告 |
| focus | 10-20% | > 30% 警告（说明用户经常跑题） |
| telling | 5-20% | **> 40% = prompt 失败必须重写** |
| generic | < 15% | > 25% 警告（agent 像在敷衍）|

Pacing 模式下 telling 阈值放宽到 0.35（见 [`pacing-detection.md`](pacing-detection.md)）。

## 每回合 agent 内心 self-classification

agent 生成回复后，**内心**用以下 prompt 做四分类（不输出给用户）：

```text
你刚才输出的这条回复，属于以下四类哪一类？

- focus: 把用户注意力拉回主线
- probing: 追问深一层
- telling: 直接告知信息或解释术语
- generic: 通用 backchannel

回复：<上一句>

只回答 JSON：{"move": "focus|probing|telling|generic", "reason": "<10 字内>"}
```

输出落 session.json 的 `turns[].agent_move` 字段。

## session.json 中的 move 序列示例

```json
{
  "topic": "RAG 召回分层",
  "mode": "grinding",
  "pacing_active": false,
  "turns": [
    {"speaker": "agent", "text": "你觉得 RAG 召回率瓶颈在哪一层——embedding / chunking / rerank？", "agent_move": "probing", "stage": "A"},
    {"speaker": "user", "text": "embedding 模型本身吧"},
    {"speaker": "agent", "text": "为什么不是 chunking？你的项目里 chunk 跨段语义断裂的情况怎么处理？", "agent_move": "probing", "stage": "A"},
    {"speaker": "user", "text": "嗯……跨段断裂确实没考虑"},
    {"speaker": "agent", "text": "你刚才意识到的这个 gap，正是大多数 RAG 项目的 silent failure。", "agent_move": "telling", "stage": "C", "pacing_telling": false},
    {"speaker": "user", "text": "嗯……我想不起来作者那一节具体怎么处理跨段的"},
    {"speaker": "agent", "text": "这答案在《RAG 召回分层实战》的 '跨段语义保留' 那一节——先回想那一节给的是哪类解决方案？", "agent_move": "focus", "stage": "B", "ladder_level": 1},
    {"speaker": "user", "text": "嗯我还是想不起来"},
    {"speaker": "agent", "text": "反直觉之处在于不是 chunking 大小, 在 chunk 的**边界**——一个 6 个字母的英文词。", "agent_move": "focus", "stage": "B", "ladder_level": 2, "inferred_user_default": "chunking 大小"}
  ]
}
```

注意 L1 / L2 两条都打 `move=focus`，副标签 `ladder_level` 区分档位；L2 必带 `inferred_user_default` 字段。

注意最后一条 `telling` 在 stage C（假设挑战 → 印证），属于"用户自己悟到后才贴的印证 telling"——这是被允许的。eval/judge.py 会区分。

## 与 eval/judge.py 的契约

`judge.py` 期望读 session.json 的：
- `turns[].agent_move` ∈ {focus, probing, telling, generic}
- `turns[].stage` ∈ {A, B, C, D, E, fusion-碰撞, fusion-质疑, fusion-收敛}
- `turns[].ladder_level` ∈ {1, 2, 3, null}（决策 7）
- `turns[].inferred_user_default` ∈ {str, null}（仅 L2 必填，供 judge.py 抽查 agent 默认答案推断是否合理）
- `pacing_active` boolean（影响 telling 阈值）

算出来的 metrics：

```python
telling_rate = count(move=telling) / count(all_agent_turns)
probing_depth = count(unique_stage_visited) / total_stages   # A-E 覆盖广度
aha_moment_confidence = LLM-judge 看 D + E 阶段有没有"用户自己悟到 + 复述"
```

## 调 prompt 时的优化目标

每次改 SKILL.md 或 socratic-method.md：

```bash
python3 -m eval.regression --verbose
# 看哪条 fixture 触发了 telling > 0.2
# 那些 fixture 对应的 system prompt 段落就是要重写的
```

**禁止**：通过修改 fixture 把 telling_rate 调下来。fixture 是 ground truth，要改的是 prompt。

## 反例（agent 应该警觉自己做了什么）

❌ 用户说"我不知道" → agent 立刻贴原文 = 错误 telling（应该 probing 拆小问题）
❌ 用户说"对吧？" → agent 答"对" = generic + 失去引导机会（应该 probing 反问"你为什么觉得对"）
❌ agent 连续 3 轮都是 probing 且用户卡壳 = 缺 focus / pacing detection 没工作（应该转 focus 或进 pacing 模式）

## 四分类真实样本 few-shot 锚点

来源：MathDial 论文（[aclanthology 全文 PDF](https://aclanthology.org/2023.findings-emnlp.372.pdf) / [arXiv:2305.14536](https://arxiv.org/abs/2305.14536)）+ Eth-NLPed 公开数据集。每类贴 2 条**真人教师在数学辅导场景的真实表述**，agent 做 self-classification 时拿来当 few-shot 对照：

| 类 | 真实英文样本（MathDial） | 砚友中文等价样本 |
|---|---|---|
| **focus** | "Can you reread the question and tell me what is being asked?" | "回到原题——你要解的具体是哪个量，先重述一遍。" |
| **focus** | "Can you calculate how many items he had at the start?" | "我们先不管整段——光算第一步，你的数字是几？" |
| **probing** | "How would things change if they had 12 items instead of 10?" | "如果不是 10 个而是 12 个，你刚才的推理链哪一步会变？" |
| **probing** | "Why did you choose to divide here?" | "为什么这一步是除而不是减？你的判断依据是什么？" |
| **telling** | "You need to add 5 to both sides to isolate x." | "这里要两边同加 5——但记住下一步的方向，是你**自己**要选的。" |
| **telling** | "Actually, he had 7 items, not 9." | "正确数字是 7——你算成 9 是因为漏了哪一步？" |
| **generic** | "Yes." / "Good." / "OK." | "嗯。" / "对。" / "继续说。" |
| **generic** | "Got it." | "知道了，往下推。" |

**agent self-classification 时的 few-shot 用法**：把上表 8 条作为 prompt 例子塞进 self-classifier 的 system prompt（[`profile-schema.md`](profile-schema.md) `agent_move` 字段写入前调用），能把分类 accuracy 从无 few-shot 的 ~70% 提升——MathDial 论文 §5 报告纯 prompted GPT-4 在该任务上 ~75%，加 few-shot 可达 ~85%。
