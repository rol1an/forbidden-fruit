# 砚石痕迹 · 进度感即时反馈（决策 7）

> **何时读**：执行 yanyu-dialogue 任何 mode 时——这是横切关注点，每次 stage 切换 + 每 5 轮强制盘点触发。

## 设计动机

5-22 真实用户实测反馈 2：研磨过程漫长，缺乏成就感 / 学到东西的小点。用户提议"进度条 + 80-100% 阈值自动放答案"——直接破 telling_rate ≤ 0.2 红线（铁律 4）+ SDT 外驱反噬。

**真实解法不是进度条，是 informational feedback**——Deci, Koestner & Ryan (1999) 128 项实验 meta-analysis 留的关键口子：tangible + task-contingent + expected 的外部奖励才挤压内驱；**informational feedback（告诉你做对了什么、能力如何增长）不构成挤压**。

砚石美学契合：研磨是按压留下痕迹，不是百分比条。

## 与用户原始提议的差异

| | 用户提议（进度条 + 阈值放答案）| 砚石痕迹 |
|---|---|---|
| 形态 | 进度条 % | 文字 callout |
| 内容 | 还差多少（remaining %）| 已走多远（stage / 跃升）|
| 阈值触发 | agent 自动放答案 | 仅作为 prompt 失败信号供 judge.py 采集 |
| SDT 分类 | controlling reward | informational feedback |
| 击穿 telling_rate ≤ 0.2 | 是 | 否 |

## 触发协议（MVP）

**MVP 范围**：仅靠 stage transition + every-5-rounds 触发（无 LLM 误判风险）。Bloom 跨级跃升触发列入 **P1 闸门**——必须先通过 `eval/bloom_agreement.py` agreement ≥85%。

| 触发器 | 频率 |
|---|---|
| Stage transition（A→B / B→C / C→D / D→E）| 每次 stage 切换都触发 |
| 每 5 轮强制盘点 | agent 回合数 % 5 == 0 且本轮无 stage transition 时触发 |
| pacing 模式 | 降密到每 8 轮一次（避免 frustrated 状态下打扰）|
| 用户明确关闭 | session.json `inkstone_disabled: true` 后不再触发 |

**实现提示**：agent 内心检测 stage 切换或回合计数命中，立即在常规回复之后**追加一行** callout（不替代回复）。

## Callout 格式

stage 切换专用：

```
🪨 第 X 阶段 → 第 Y 阶段。<一句 observation>。
```

每 5 轮强制盘点：

```
📿 砚石痕迹：<观察句, 含情感锚点>。
```

**情感锚点必要性**：Eedi/LearnLM 报告 63.8% 真人编辑用于 pacing + 情感节奏调整，纯认知反馈（"你到 X 阶段了"）会冷峻像考试评分。砚石痕迹必须像同行点头，不像评分员盖章。

## 文案样例（5 条 + 反例）

| 触发场景 | callout 文案 |
|---|---|
| A → B（探查转卡壳）| 🪨 A → B：你这一问触到了真实的卡点，从这里开始挖。 |
| B → C（卡壳引导转假设挑战）| 🪨 B → C：基础站稳了，往下走——边角案例上场。 |
| C → D（假设挑战转印证）| 🪨 C → D：你刚才那一步已经在推作者的骨架。 |
| D → E（印证转收尾）| 🪨 D → E：你说出来的版本比原文多了一层——记住这层。 |
| 每 5 轮强制盘点 | 📿 砚石痕迹：5 轮里你**自己提出了 2 个反例**——你这一会儿在做的就是研磨。 |

**反例（不要这样写）**：

- ❌ 「📿 你完成了 60%」—— SDT 外驱反噬（Deci & Ryan 1999 直接预测会挤压内驱）
- ❌ 「📿 你触达 Bloom 第 4 层（分析）」—— jargon leak，用户不学认知科学
- ❌ 「📿 还差 2 个关键洞察就印证」——给"还差多少"暗示，破内驱
- ❌ 「📿 加油！」 / 「📿 太棒了！」—— cheerleading 腔，CLAUDE.md 风格铁律明令禁止
- ❌ 在同一 session 重复同一句 callout ≥3 次（设计上 5 条样例应轮换，不复用）

## 术语转译表（Bloom 英文 → 砚友动词标签）

Khan Academy 用 named tier（Attempted / Familiar / Proficient / Mastered）不用 raw % 已经验证 SOTA 路径。砚友把 Bloom 6 层翻译成砚友风格的动词标签——P1 Bloom 跨级跃升触发时消费这套词汇：

| Bloom 英文层级 | 砚友动词标签 | 说明 |
|---|---|---|
| remember | 触碰 | 用户刚意识到这个概念存在 |
| understand | 看懂 | 用户能复述 |
| apply | 拆解 | 用户能在新场景套用 |
| analyze | 重构 | 用户能拆作者推理骨架 |
| evaluate | 评判 | 用户能挑战作者论点 |
| create | 创造 | 用户能给出超出原文的新方案 |

P1 callout 示例（agreement test ≥85% 解锁后）：

```
📿 砚石痕迹：你这一问从「看懂」推到「重构」—— 3 轮前你还在复述原文，现在已经在拆作者的推理骨架。
```

## P1 Bloom 跨级跃升触发的闸门

**为什么 MVP 不上这个触发器**：Bloom tagger 误判率即体验天花板。若误判 >15%，用户被"你到第 5 层"误奖励然后下轮被打回第 2 层 → **信任崩盘比不显示更糟**。

**解锁条件**：`python3 -m eval.bloom_agreement` 在 20 条人工标注 fixture 上 agreement ≥85%。详见 [`../eval/bloom_agreement.py`](../eval/bloom_agreement.py)。

agreement < 85% 时砚石痕迹**仅允许** stage transition + every-5-rounds 触发，不允许消费 bloom_tagger 输出。

## 失败处理

| 症状 | 应对 |
|---|---|
| 用户回复"少跟我说这些客套话" / "别加 emoji" | 立刻关闭本次 session 的砚石痕迹（session.json `inkstone_disabled: true`），不再追加 callout |
| 用户问"我现在到第几了" | 不报百分比，反问"你刚才那一步比 3 轮前是更深还是更浅？" |
| 频率被吐槽太密 | 跳到 pacing 模式的 every-8 频率 |
| 同 callout 文案重复出现 ≥3 次 | session.json 标 `inkstone_repetition_warning`，喂 judge.py 作为 prompt 失败信号 |
| stage 转移检测出错（A→C 跳过 B）| 不输出 callout——stage 跳跃本身可能是 prompt bug，先看 session 再说 |

## 与 eval/dashboard.py 的契约

session.json 增加字段：

```json
{
  "inkstone_traces": [
    {"turn_idx": 3, "trigger": "stage_transition", "from": "A", "to": "B", "callout": "🪨 A → B：..."},
    {"turn_idx": 8, "trigger": "every_5_rounds", "callout": "📿 砚石痕迹：..."}
  ],
  "inkstone_disabled": false
}
```

dashboard.py 可在 P1 加一个 callout 时间线小图（MVP 不强求）。

## SOTA 锚点

- **Deci, Koestner & Ryan (1999)** "A Meta-Analytic Review of Experiments Examining the Effects of Extrinsic Rewards on Intrinsic Motivation"——128 项实验证明 task-contingent + expected 的 tangible reward 系统性挤压内驱，但 **informational feedback 不挤压**。砚石痕迹只显示"已走多远"恰好落在 informational 一侧，理论合法
- **Khan Academy Mastery Levels**（[support.khanacademy.org](https://support.khanacademy.org/hc/en-us/articles/5548760867853--How-do-Khan-Academy-s-Mastery-levels-work)）—— Attempted / Familiar / Proficient / Mastered 四级 named tier 替代 raw %，行业 SOTA 验证
- **Michael Nielsen, Augmenting Long-term Memory**（[augmentingcognition.com/ltm.html](https://augmentingcognition.com/ltm.html)）——进度感可来自沉淀物积累而非 UI feedback。这是砚友 P2 「研磨结晶卡」方案的理论基础
- **Eedi/LearnLM 报告**（[eedi.substack.com](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can)）—— 44.3% pacing + 19.5% 情感缓冲 = 63.8% 真人编辑量，提示砚石痕迹必须有情感锚点不能纯认知
