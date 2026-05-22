# 砚友 · Ultimate Pitch

> 2026-05-21 · 主指挥 + 用户共同沉淀
>
> README 头图文案 / 论坛发帖叙事 / demo 视频脚本 / 答辩话术——**都从这里取材，不要在别处重新发明叙事**。

---

## 立场：Study Mode 不是威胁，是市场存在性的官方背书

2025-07 OpenAI 推出 ChatGPT Study Mode 全球免费上线，与砚友在三个核心点高度撞车：

| 维度 | ChatGPT Study Mode | 砚友 |
|---|---|---|
| 教育学内核 | 苏格拉底式 + 反喂答案 | 完全一致 |
| 用户画像 | ChatGPT Memory（全局） | Bitable 硬编码可视化画像 |
| 知识来源 | 用户上传课本/笔记/盲聊 | 用户自己脱水入库的飞书私有知识库 |

**关键认知翻转**：
- 在竞赛中，**"全网独一份"的荒野概念**会让评委怀疑市场是否存在
- 而现在 **OpenAI 亲自下场为我们论证了 "第二大脑不需要喂饭、人与知识需要智力摩擦" 这个市场的真实存在与高级感**
- 砚友不去碰瓷 OpenAI 的全能，而是利用 **飞书 CLI + 本地知识库** 的独占优势，打它绝对做不到的降维出彩点

**答辩第一句永远是**：
> "OpenAI 2025-07 推出 Study Mode 证明了 Socratic AI 是 AI 辅助学习的终极解。但 Study Mode 是阅后即焚的聊天框，砚友是把这个哲学嫁接到你私有知识库上的中式数字书院。"

---

## 四大降维出彩点（按答辩重要性排序）

### 🌟 出彩点 1 · 私有知识库的"物理占有权" vs 聊天框的"阅后即焚"

**Study Mode 的困境**：被动聊天会话。用户上传一篇微信文章或笔记跟它聊完，知识就**死在漫长的历史聊天记录里**。它**没有帮用户沉淀资产**。

**砚友的降维打击**：`yanyu-import` 是硬核底座——先帮用户在飞书里搭建去噪、严密排版、四色节奏的"个人数字书院"。每一场 Socratic 辩论都基于你**亲手打下的飞书私有资产**，知识在多文档间通过 lark-cli 缝合，是**会长大的神经网络**。

**答辩话术**：
> "ChatGPT 只负责陪练，砚友负责帮你建立江山。"

**物料落地点**：
- README hero 头图：左边一张 ChatGPT 聊天截图（标"阅后即焚"），右边一张飞书知识库截图（标"会长大的神经网络"）
- demo 视频 1:00-1:30：展示 yanyu-import 把一篇微信文章去噪入库 + 老文章自动 append xref 的全过程
- 飞书 wiki 节点的 14 篇相互关联文章 = 现成 demo 弹药

### 🌟 出彩点 2 · Bitable 活体画像 vs 黑盒 Memory

**Study Mode 的困境**：ChatGPT Memory 是黑盒。**用户看不见、摸不着、无法干预**——记住了什么 / 哪里卡壳 / 思维盲点全部不可观测。

**砚友的降维打击**：自进化建立在**公开、透明、用户可随时修改的 Bitable** 上：
- 辩论完后多维表格清晰登记："Luojian 在 RAG 召回分层主题掌握度 3 分；思维盲点：容易忽略 rerank 模型选型对长尾召回的影响"
- 下次对话前 agent 运行 `profile_read.py` 自动读取
- **最性感**：逆向吸纳人类的方法论金句，重塑 agent 自己的 prompt 库

**这是 ChatGPT 绝对做不到的"可干预、可可视化的双向共同进化"**。

**答辩话术**：
> "ChatGPT Memory 是黑盒，砚友画像是活体。你能打开飞书表格亲眼看到 agent 对你的理解，能改它、能加它、能让 agent 反向学习你的方法论。"

**物料落地点**：
- demo 视频 3:00-3:30：屏幕左侧跑研磨对话，右侧实时显示 Bitable 字段更新（掌握度 +1、卡壳点新增一行、aha-moment 金句落盘）
- README §4 "活体画像架构图"：画一张「对话 → profile_write → Bitable → profile_read → 下次对话起点调整」的循环图
- 论坛发帖配图 #2：Bitable 画像截图打码用户名

### 🌟 出彩点 3 · yanyu-fusion 强制跨界碰撞（OpenAI 严合规不敢做）

**Study Mode 的困境**：极其被动。用户输入什么它就学什么。**绝对不会主动求变，更不会带你打破信息茧房**。

**砚友的降维打击**：`yanyu-fusion` 利用跨界标签算法，**强行从 Bitable 索引抽取两个互不相干的领域**（如"具身智能 × 中医针灸"），扮演 devil's advocate 主动对你发起怪趣交锋。

这种**强行制造戏剧性认知冲突**的算法，是 OpenAI 这种严合规、求稳的通用大模型**绝对不敢自带的爆点**。

**答辩话术**：
> "OpenAI 不敢逼用户跳出舒适区——通用大模型怕用户投诉。砚友敢——这是垂类工具的特权。"

**物料落地点**：
- demo 视频 4:00-5:00：研创模式高光——agent 抛出 "RAG 多向量索引 × 中医针灸取穴" 的挑衅性问题，用户从抗拒到收敛的全过程
- README §5 "跨界碰撞算法 V1.5"：embedding-distance + analogical-mapping 双阶段（决策 6a）
- 论坛发帖标题候选 #1："为什么我让 AI 把具身智能跟中医针灸塞在一起逼问我"

### 边界声明（避免被人挑战）

**决策 2 砍掉的是 fusion Step 5 "agent 接手扩大纲"**——
- 砍的：agent 主动给"最小可行版本 / 失败模式 / 下一步验证假设"三段
- 保留并强化的：Step 1-4 强制跨界碰撞 + devil's advocate 质疑

两者**不冲突**：摩擦理论铁律是 agent 制造摩擦但不替用户思考；fusion 的核心爆点是"制造跨界摩擦"，而非"给执行建议"。

### 🌟 出彩点 4 · 工程极简主义（Completeness 加分项）

**砚友不卷大模型底座**——不需要训练 / 微调 / 自有数据集 / 自有 inference server。

纯粹用 **Trae SOLO Skill 编排 + 本地 `lark-cli` 命令组合**，撬动飞书强大的 wiki / docs / Bitable 生态。

| 砚友需要的能力 | 怎么实现 |
|---|---|
| 文章入库 | `lark-cli wiki +node-create` + `docs +update --command overwrite` |
| 双向链接 | `base +record-search` + `docs +update --command append` |
| 用户画像 | `base +record-search/upsert` + 一对 Python 脚本 |
| LocalFileBackend | Python stdlib + Path |
| 整个 LLM 推理 | Trae SOLO 自带 Claude，零自建 |

**答辩话术**：
> "我们不用百亿参数训练，不需要 GPU 集群，不需要自建 vector DB。Trae SOLO 的 Skill 编排 + 本地 CLI 命令组合 = 极致的工程极简主义。这是评审会看到的'高工程素养'。"

**物料落地点**：
- README §6 "技术栈一览表"：把上面那张表搬过去
- demo 视频结尾 5:30-6:00：terminal 跑 `lark-cli` 命令的快剪 + 飞书文档实时更新

---

## Ultimate Pitch（README hero / 论坛发帖首段 / demo 开场白共用）

> **2025 年，OpenAI 推出 ChatGPT 学习模式，证明了苏格拉底式智力摩擦才是 AI 辅助人类学习的终极解。**
>
> **然而**，通用的 Study Mode 只是一个**阅后即焚的聊天框**——它无法帮你沉淀知识资产，你更无法看清它背后的 AI 记忆黑盒。
>
> **于是我们带来了砚友（InkMate）**。它是一个将 OpenAI 的摩擦治学哲学，与**飞书私有资产 + Bitable 可视化活体画像 + 跨界强制碰撞**完美缝合的**中式数字书院**。
>
> 我们利用 Trae SOLO 驱动飞书 CLI，**不卷大模型底座，只用极简的工程艺术**，把通用的聊天陪练，升级为了**专属于你、能与你共同双向进化的数字死党**。

### 关键短语词典（保持术语统一）

| 场景 | 用这个短语 | 不用 |
|---|---|---|
| 整体定位 | 中式数字书院 | "知识管理工具""学习助手" |
| Study Mode 对比 | 阅后即焚的聊天框 | "通用 AI""ChatGPT 竞品" |
| 用户感受 | 共同双向进化的数字死党 | "AI tutor""学习伙伴" |
| 画像 | Bitable 活体画像 | "用户配置""个性化设置" |
| 知识库 | 飞书私有资产 / 数字书院 | "知识库""笔记本" |
| Fusion | 跨界强制碰撞 / 怪趣交锋 | "脑暴""灵感生成" |
| 工程定位 | 工程极简主义 / 极简工程艺术 | "轻量级""MVP" |
| 哲学叙事 | 摩擦治学 / 砚石与墨 / 禁果 | "Socratic AI"（除非答辩第一句对标）|

---

## 物料生成路径（PITCH.md → 各物料）

```
PITCH.md
   │
   ├─→ README hero / §4-6                          (设计 agent DESIGN.md 已规划好版面)
   ├─→ forum.trae.cn 发帖正文 + 4 张配图节奏       (DESIGN §4)
   ├─→ 6 分钟 demo 视频脚本 (按 4 大出彩点分段)    (DESIGN §5 加 8 秒沉默)
   ├─→ 方法论 blog "为什么 Socratic AI 必须基于你自己的知识库"
   └─→ 答辩 Q&A 应答 (5 个常见问题预演)
```

---

## 答辩 Q&A 预演（提前准备 5 个最可能被问的问题）

### Q1 · "ChatGPT Study Mode 也能做这个，为什么用砚友？"

**答**：Study Mode 是聊天框陪练，砚友是给你建数字书院。Study Mode 跟你聊完知识就死了，砚友帮你把它沉淀到飞书私有资产里、跟其他文章自动缝合、下次研磨时复用。Study Mode 的 Memory 是黑盒你看不见，砚友的画像是 Bitable 你能打开看能改能让 agent 反向学。

### Q2 · "为什么强依赖飞书？"

**答**：v1 在飞书生态可以做到工程极简（lark-cli 一行命令 = 一个能力）。但我们已经做了 LocalFileBackend 抽象（决策 1），非飞书用户用本地文件夹也能跑，demo 视频里我专门留了 30 秒展示。Notion / Obsidian backend 是 v2 路线图。

### Q3 · "跨界碰撞算法是不是 random？"

**答**：V1 是手写簇 + random（已交付 MVP），V1.5 升级为 embedding-distance + analogical-mapping 双阶段（已落入决策 6a），3 天可落地。学术依据是 Gentner SME + Fauconnier 4-space。

### Q4 · "怎么证明用户真的'悟到了'，不是你自己感觉良好？"

**答**：(1) 5-30 已经请 3 个真朋友测过，问卷数据在 README §X；(2) demo 视频里有 Bloom's taxonomy dashboard（决策 6b），每轮提问按记忆/理解/应用/分析/评价/创造打标，telling rate / probing depth 折线图实时展示。这是 ChatGPT Study Mode 没有的工程透明度。

### Q5 · "砚友会让用户觉得 frustrated 吗？"

**答**：会，所以我们加了 pacing detection（决策 6c）。Eedi/LearnLM 真实 trial 实测人类老师 **44.3% 编辑都在调 pacing + 19.5% 加情感缓冲**（合计 63.8% 在调"AI 体感"，[Eedi Substack 报告](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can)）——这是我们正面回应的设计点。用户连续 2 轮简短回复或情绪词出现 → agent 自动降密度。绝不投降不等于绝不让步。

---

## 不要在物料里说的话（地雷清单）

- ❌ "我们比 ChatGPT 强"——对标可以，碾压不行（OpenAI 体量 vs 个人项目，碾压姿态不专业）
- ❌ "反 AI 摘要"——这是 Study Mode 之前的旧叙事，已被它抢，不要再用
- ❌ "苏格拉底 AI 第一个吃螃蟹"——Study Mode + Khanmigo + LearnLM 都在前
- ❌ "AI 让人变笨"——这个叙事 MIT 论文已说过，再说一遍弱化你的独到性
- ❌ 任何提到 "革命性""颠覆性" 的形容词——评审听烦了
