# Hint laddering · 卡死时的三档脚手架（决策 7）

> **何时读**：执行 yanyu-dialogue 任何 mode 时——当用户**想答但卡死**（不是想躺平），先走 hint ladder 再考虑其他兜底。

## 设计动机

砚友早期版本只有两条规则：「绝不投降」（[`anti-laziness-templates.md`](anti-laziness-templates.md)）+ 「降密度」（[`pacing-detection.md`](pacing-detection.md)）。**5-22 真实用户实测**反馈：用户被问住时**想答但回忆不起来**（不是态度问题，是能力不到），于是绕开砚友、自己去飞书知识库看一眼文档再回来答——研磨摩擦被绕过。

这是 Wood, Bruner & Ross (1976) scaffolding 6 functions 里 **frustration control + marking critical features** 缺位的典型症状。Vygotsky ZPD 提示：hint 必须落在最近发展区内——"换更小的问题"（anti-laziness 做的）≠ hint，前者是问题降级，后者是脚手架。MathDial 的 **focus** move 给了一个不击穿 telling_rate ≤ 0.2 的合法 hint 形态。

## 与 anti-laziness / pacing 的分工

| 用户状态 | 走哪条 | 触发器关键词 |
|---|---|---|
| **想答但卡死 / 不记得 / 虚答** | 本文件 hint ladder | "想不起来 / 没看过 / 我忘了" / 虚答 |
| **想躺平 / 主动要答案** | [`anti-laziness-templates.md`](anti-laziness-templates.md) | "直接告诉我 / 我不想想 / 你讲吧" |
| **疲劳 / 情绪化** | [`pacing-detection.md`](pacing-detection.md) | "烦 / 算了 / 累" / 连续简短回复 |

**优先级**：hint laddering > anti-laziness。能力不到的卡死，先 ladder；ladder 走完用户仍躺平，再走 anti-laziness。pacing 是横切关注点，并联生效——pacing 模式下的 ladder 节奏放慢一档。

## 触发条件（至少满足 1 个）

| 信号 | 阈值 |
|---|---|
| 明确空白信号 | "想不起来 / 不记得 / 我忘了 / 我没看过这部分 / 这块我跳过了" 任一 |
| 虚答检测 | 单轮回复**形容词** ≥3 个但实质名词/动词 ≤1 个；典型："我觉得这个跟…有点关系吧大概" |
| 连续 ≥2 轮卡壳但用户**没要答案** | 区分于 anti-laziness（用户主动要答案）|

**实现提示**：agent 在生成回复前自然语言判断——不要硬编码字符串匹配，用户表达千变万化。

## 三档 Ladder（依次递进，**禁止跳级**）

### L1 · Focus move（只指位置 + 类型）

**给什么**：原料文章的**位置锚点** + **解决方案类型**。
**不给什么**：关键词、术语名、推理链、原文片段。

**MathDial 打标**：`focus`（不算 telling）；`ladder_level: 1`

**模板（5 条）**

| 用户卡点 | L1 话术 |
|---|---|
| 不记得文章某节怎么处理 X | "这答案在 <文章 X> '<某节>' 那一节——先回想那一节给的是**哪一类**解决方案？" |
| 跨界 fusion 卡在抽象层 | "你之前学的 <A 领域> 里有个**结构同构**的现象。你先想 A 领域里哪一个跟这个像？" |
| 不记得具体公式 / 数字 | "具体数字不用记。先想这个公式是**加项**多还是**乘项**多？" |
| 答得太抽象 | "回到具体——你**最近一次**遇到这个问题，是什么场景？" |
| 卡在判断方向 | "这问题有两个方向：一是 <方向 X>，二是 <方向 Y>。你的直觉先选哪一个？" |

### L2 · Recall trigger（反直觉锚点 + 弱形状提示）

**给什么**：①**反直觉锚点**（用户脑中默认答案 + agent 反向暗示）；②**弱形状提示**——只允许**中文范畴**（词性 / 侧 / 范畴 / 关系），如「是动词还是名词」「是用户侧还是 agent 侧」「跟 X 同一侧还是反侧」「是技术名词还是流程名词」。
**不给什么**：术语名、定义、推理结论。

**强形状提示禁令**（C2 修订）：

- ❌ 「英文缩写 N 个字母」 / 「6 个字母的英文词」 / 「以 L 开头」 / 任何**字母数 / 缩写位数 / 首字母**提示
- 原因 1：在专业语境里基本锁定答案（"6 字母英文词" 在 RAG 上下文几乎只指向 `window` / `chunk`，"L 开头"在排序场景几乎锁定 `LambdaRank` / `LTR`）——**击穿 telling_rate ≤ 0.2 红线**
- 原因 2：砚友对话主语言是中文，英文只用于无法直接翻译的专有名词——中文对话里突然问"英文缩写几个字母"是**语言断裂**

**关键约束**：agent 必须**先在内心反推用户脑中的默认答案是什么**，写入 `turns[].inferred_user_default` 字段供 judge.py 抽查。如果默认答案推不出来 → **退回 L1，不要给 L2**（盲猜的反直觉锚点会脱靶）。

**MathDial 打标**：`focus`（弱形状不锁定答案，不算 telling）；`ladder_level: 2`

**模板（5 条，全部走中文范畴弱形状）**

| 用户默认答案 | L2 话术 |
|---|---|
| 用户以为是 embedding 模型 | 「反直觉之处在于**不是 embedding 模型**——是另一个机制，它不靠模型权重，是个**纯算法**。」 |
| 用户以为是 chunk 大小 | 「不在 chunk 大小，在 chunk 的**另一个属性**——这属性跟 rerank 同一侧。」 |
| 用户以为是 cosine similarity | 「不是 cosine，而是**另一种排序逻辑**——它不基于相似度数值，是基于一组样本之间的对比。」 |
| 用户以为是 fine-tune | 「是 fine-tune 的**反面**——一个**用户侧**做的操作，不动模型。」 |
| 用户以为是数据量 | 「不在数据量，在数据**采集**那一步——这一步本质是一个**动作**，跟模型训练完全无关。」 |

每条都用了中文范畴（"纯算法 / 跟 rerank 同一侧 / 不基于数值 / 用户侧 / 动作"）作为形状, **没有任何**字母数或缩写位数。

### L3 · Open the original（开放查阅原文权）

**给什么**：允许用户**自己**去飞书知识库查阅那一节原文 30 秒，但**回来必须用自己的话复述**。
**不给什么**：agent 主动贴原文片段（违反 D 阶段铁律）。

**关键约束**：

- 每次研磨 session **最多 1 次 L3**——硬规则
- L3 后用户必须用自己的话复述，**不允许直接复制原文**
- 复述完才进入 D 阶段印证，不允许跳过 D 直接收尾
- L3 **不计 telling_rate**（不是 agent 给的）但 session.json 标 `ladder_level: 3`，judge.py 统计单 session L3 频次，≥2 视为 prompt 失败信号

**MathDial 打标**：不算 telling，也不算 focus——单独 `ladder_level: 3`，move 字段留 `focus`

**模板（5 条）**

| 用户已尝试 L1/L2 仍卡 | L3 话术 |
|---|---|
| 通用 | "你已经卡住 3 轮——这次去看 <文章 X> '<某节>' 那一段，30 秒后回来用**你自己的话**告诉我：作者为什么觉得 <用户默认答案> 不够？" |
| 跨界 fusion | "去看一眼 <A 领域文章> 关于 <某节> 那段——回来不要复制原话，用你自己的话告诉我那段逻辑能不能搬到 <B 领域>。" |
| 卡在具体数字 / 事实 | "查一下 <文章 X> 的数字，30 秒。回来不要光报数字，告诉我这数字让你**重新想到了什么**。" |
| 怀疑自己理解错了 | "去对一下原文 <某节>。回来告诉我**你刚才哪一步推错了**，不是告诉我答案。" |
| 跑题但有潜力 | "去查 <跑到的话题> 的原文 30 秒。回来告诉我它跟我们刚才讨论的 <主线> 是什么关系——这关系才是答案的入口。" |

**为什么 L3 这样设计**：用户绕路看知识库本来是反馈 1 的痛点；L3 把这个行为**正名为合法 ladder**——不再是绕路，是被 agent 主动批准的查阅。但加上"用自己的话复述"约束，确保主动学习不退化为搬运。

## 失败处理

| 症状 | 应对 |
|---|---|
| L1 给完用户仍空白 | 升 L2 |
| L2 给完用户仍空白 | 升 L3 |
| L3 给完用户**直接复制原文**回话 | 不算复述。反问"用你自己的话再说一遍，不要用原文措辞" |
| L3 给完用户**仍说不出** | 进入 anti-laziness 兜底 + 终极兜底（"今天到这，下次换角度"）|
| 同 session 触发 ≥2 次 L3 | session.json 自动标 `ladder_overuse: true`，喂 judge.py → prompt 失败信号（L1/L2 应该覆盖 ≥80% 卡死案例，L3 是兜底）|

## 与 eval/judge.py 的契约

session.json `turns[]` 新增字段：

```json
{
  "role": "agent",
  "content": "...",
  "move": "focus",
  "stage": "B",
  "ladder_level": 2,
  "inferred_user_default": "embedding 模型"
}
```

- `ladder_level: 1 | 2 | 3 | null`（null = 非 ladder 回合）
- `inferred_user_default: str | null`（仅 L2 必填，agent 内心反推用户脑中默认答案）

`judge.py` 期望读取并：

- L1/L2 计入 `focus`，**不计 telling**（不影响 telling_rate）
- L3 单独统计 `ladder_l3_count`，≥2 触发 `ladder_overuse_warning`
- `_ladder_stats` 字段返回供 dashboard 复用

## SOTA 锚点

- **Wood, Bruner & Ross (1976)** "The Role of Tutoring in Problem Solving"——scaffolding 6 functions（recruitment / reduction in degrees of freedom / direction maintenance / **marking critical features** / **frustration control** / demonstration），其中粗体两项直接对应 hint laddering 设计
- **Vygotsky ZPD**（zone of proximal development）—— hint 必须落在 ZPD 内：太抽象等于没给，太具体剥夺学习
- **MathDial** [arXiv:2305.14536](https://arxiv.org/abs/2305.14536) `focus` move 定义——在 telling 和 probing 之间存在不击穿 telling_rate ≤ 0.2 红线的合法 hint 形态
- **Eedi/LearnLM 报告**（[eedi.substack.com](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can)）—— 44.3% pacing edits + 19.5% 情感缓冲, 提示砚友需要主动调节奏 + 主动指方向, 不只是被动等用户答
- **Khanmigo 渐进式 hint** 4 步链（指领域 → 触发回忆 → 自检 → 例题），砚友简化为 L1/L2/L3 三档，全程不击穿 telling 红线
