# 砚友技术调研报告

> 2026-05-21 · tech-research-agent · 第二次派
> 目标：正面回应 reviewer "苏格拉底 AI 不空白" + business agent "ChatGPT Study Mode 抢通用 Socratic 赛道" 两个挑战

## TL;DR 给砚友最有价值的 3 条技术升级

1. **把 V1 跨界算法升级为 embedding-distance + analogical-mapping 双阶段**——砚友相对 Study Mode 真正的 moat，技术上有 Gentner SME / Fauconnier 概念整合学术依据，工程上 3 天可落地。
2. **在 Step 5 加 RAGAS / LearnLM 风格的 LLM-judge 自动评估**——破 REVIEW_001 "没自动化 eval = 8 天瞎调" 死局；demo 视频里"用户悟到"有量化数据背书，破"作者自评幻觉"。
3. **把 profile 富文本字段升级为 Anthropic Memory Tool 协议形态**——2025-09 Memory Tool 官方范式已就位，砚友的"progressive disclosure 静态扩展到动态"叙事直接对接 Anthropic 话语体系。

---

## 1. 苏格拉底式 AI 教学

### SOTA

- **ChatGPT Study Mode**（2025-07-29 全免费上线）：custom system instructions 层叠在基座模型上、不换模型；做 Socratic questioning + scaffolded responses + 跨会话记忆个性化。[OpenAI 官方介绍](https://openai.com/index/chatgpt-study-mode/)
- **Khanmigo**（GPT-4 底座，$4/月）：核心是"不直接答题，先问学生 first step 是什么"；2024-25 用户从 6.8 万涨到 70 万；Microsoft 合作免费给 40+ 国家教师。[Khanmigo 官网](https://www.khanmigo.ai/)
- **Google LearnLM**（2024-05 v1 / 2025-11 v2）：pedagogical 专用模型，专家盲评胜过 GPT-4o / Claude 3.5 / Gemini 1.5 Pro；2025 暑期 Eedi 5 个英国中学课堂真实 trial（165 名 13-15 岁学生），AI+人类组合在"修正错误"维度 93.0% vs 人类 91.2%；**关键发现：人类老师 44.3% 的编辑都在调 Socratic pacing**（防止学生 frustrated）+ **另外 19.5% 编辑用于加 social-emotional nuance**（个人认可、调语气）——加起来 63.8% 的编辑都是在调"AI 体感"。[Eedi Substack 报告](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can) · [LearnLM Nov-25 论文](https://storage.googleapis.com/deepmind-media/LearnLM/learnLM_nov25.pdf)
- **MathDial（EMNLP-2023, arXiv:2305.14536）**：3000 条人类教师 × LLM 学生的对话语料；明确编码 teacher-move 分类（focus / probing / telling / generic）；证明 GPT-3 是好 solver 但坏 tutor，premature solution disclosure 是头号失败模式。[arXiv:2305.14536](https://arxiv.org/abs/2305.14536)
- **SocraticLM**（NeurIPS-2024）：把"Socratic 教学"显式建模为多 agent（thought partner / cognitive director / pedagogical expert）协作，再用 SFT+DPO 训练。[USTC 论文 PDF](http://staff.ustc.edu.cn/~huangzhy/files/papers/JiayuLiu-NeurIPS2024.pdf)

### 砚友差距

1. 砚友 "每回合 ≤2-3 句、绝不投降" 是硬规则——LearnLM 实测告诉你，硬规则会让用户 frustrated，**必须引入 pacing detection**（用户连续 ≥2 轮简短回复 / 情绪词出现时降密度）。
2. teacher-move 没有分类体系——`socratic-method.md` 5 阶段 A-E 是流程而非可观测的 move 类型，没法做评估也没法 fine-tune。直接借 MathDial 的 focus / probing / telling / generic 四分类。
3. "绝不直接给答案"是过于绝对的口号——MathDial 的 telling move 在某些场景（解释陌生术语）反而是正确策略，禁掉它会让对话卡死。

### 立刻可吸收的升级

- **引入 MathDial teacher-move 分类**作为 agent 自评信号：每回合自标注 move 类型，写进 session.json 的新字段 `move_sequence`。后续可做"move distribution 健康度"指标（probing 占比 ≥60% 算健康）。
- **增加 pacing 兜底**：连续 ≥2 轮用户回复 <10 字 → 切到 "降密度" 模板（直接讲一点 + 抛一个非常具体的小问题），灵感来自 LearnLM 人类编辑日志。
- **README 战术叙事调整**：不打"我们 Socratic 比 Study Mode 更好"——打不过。打"我们是 *你私人知识库* 上的 Socratic，跨界 fusion 是 Study Mode 没有的"。


---

## 2. 多轮对话状态管理

### SOTA

- **Anthropic Memory Tool（2025-09 beta，beta header `context-management-2025-06-27`）**：放弃 RAG/向量库，改用文件目录 + create/read/update/delete 原语；Anthropic 自报 **84% token 减少**。设计哲学：just-in-time retrieval，agent 学到什么存起来、用到再 pull。[Memory Tool 文档](https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool) / [Context Management 公告](https://www.anthropic.com/news/context-management)
- **Anthropic "Context Engineering" 范式**（2025 全年推）：context = prompts + memory + tools + data 的统一设计学；四类操作 write / select / compress / isolate。被业界标记为 "the #1 job" of agent engineers。
- **LangGraph checkpointing**：thread-scoped memory + long-term memory 双层；agent 任意时刻 read/write state，配合断点恢复。[LangGraph 官方介绍可参考](https://blog.langchain.dev/langgraph/)
- **Mem0 / Letta（前 MemGPT）**：把 conversation 拆成 hot / warm / cold tier，借鉴 OS 分页思想；适合 unbounded 对话历史。

### 砚友差距

1. 砚友 profile 当前是"一次性读全表 + 一次性写回"——这是 2023 范式。Memory Tool 范式是 agent 在对话中**随时** read/write/update 多个 memory file，**对话期间** profile 也能演化（用户金句一冒出来就写，不等到 Step 5）。
2. `profile-schema.md` 的富文本字段（topic_mastery JSON / methodology_quotes 多行字符串）等同于"把所有 memory 压在单个文件"——Memory Tool 推荐每条记忆独立文件、便于人类 review 和版本控制。
3. 没有 context isolation：grinding 和 fusion 共享同一 profile，但场景需要的视图不同（grinding 关心 stuck_points，fusion 关心 methodology_quotes + domain_tags）。Anthropic 的 isolate 操作建议按场景做 view。

### 立刻可吸收的升级

- **profile 切分为多文件结构**，对应 Memory Tool 形态：`/memories/topic_mastery.md`（按主题分章节）/ `/memories/methodology_quotes.md` / `/memories/stuck_points.md` / `/memories/fusion_history.md`。Bitable 当 backend，但 schema 层做成 Memory Tool 兼容——叙事直接对接 Anthropic 官方话语。
- **对话期间增量写**：用户金句一冒出来，agent 立刻调 `profile_append_quote.py`，不等到 Step 5。降低 session crash 数据丢失风险（你这次跑挂就是真案例）。
- **per-skill view**：`profile_read.py --view grinding` 只返 topic_mastery + stuck_points + style；`--view fusion` 只返 domain_tags + methodology + fusion_history。少加载 = context 干净 + token 省。
- **README 加一句"砚友 profile 是 Anthropic Memory Tool 协议的活体应用"**——community value 直接吃 Anthropic 生态红利。


---

## 3. 个性化对话（用户画像驱动）

### SOTA

- **Apollonion: Profile-centric Dialog Agent**（arXiv:2404.08692）：把 profile 拆成 static / dynamic 两层；static = 显式声明的偏好与背景，dynamic = 对话过程中归纳的隐式偏好（用户每说一句都触发 profile 更新候选，agent 用 LLM-as-judge 决定要不要持久化）。[arXiv:2404.08692](https://arxiv.org/abs/2404.08692)
- **PersonaLLM（ICLR 2025）**：把 personalization 定义为"alignment 的精细化"——不是对齐普遍偏好，是对齐"这个用户在这个场景下的偏好"。
- **PersonaLens（ACL 2025 Findings）**：personalization 评估基准，明确给出"个性化是否真的让回复变好"的对照评估方法论——破"agent 自评幻觉"。[PersonaLens 论文](https://aclanthology.org/2025.findings-acl.927.pdf)
- **Persistent Memory + User Profiles**（arXiv:2510.07925, 2025-10）：综述 profile 驱动 long-term interaction 的 4 个能力——profile modeling / memory / planning / action execution——强调 cross-session consistency 是头号挑战。[arXiv:2510.07925](https://arxiv.org/pdf/2510.07925)
- **Towards Proactive Personalization**（arXiv:2512.15302, 2025-12）：主动学习用户的 implicit preference，不等用户显式说出来。

### 砚友差距

1. 砚友 profile 只有 dynamic 层（全部从对话归纳）——**缺 static 层**。新用户首次进来 profile 为空，agent 没有任何 prior，只能用"通用开场"。Apollonion 的 static 层（如"我是 RAG 工程师 / 我偏好被挑战"用户主动填）可以解 cold start。
2. profile 写入是回合粒度（每次 session 结束写一次），不是 turn 粒度——错过了 Apollonion 强调的 "user 每说一句都是 profile signal" 的精细度。
3. `style_response` 只有 3 个 enum（challenge/guidance/affirmation）——粒度太粗。PersonaLLM 用 Big-Five + 学习偏好向量（visual/verbal, sequential/global）这种连续/多维表示，避免"被挑战 + 被引导"同时存在的用户被强行二选一。
4. 没有评估对照机制——按 PersonaLens，个性化的价值必须用 "with-profile vs without-profile" A/B 才能证明。砚友 demo 视频里"第二次明显比第一次个性化"的叙事，没有量化支撑。

### 立刻可吸收的升级

- **profile 加 static 层 schema**：新建 `profile_static.md`（用户首次进来填一次的表单：身份、目标主题、偏好风格、知识边界），fusion 的 `domain_familiarity_tags` 也可以从 static 初始化而非等积累。代码工作量 1 天。
- **金句即时落盘**：用户说出"召回分层比单纯加 rerank 更重要"这种判断时，agent 立刻调 `profile_append_quote.py`——不等 Step 5。这同时解了 REVIEW_001 的 record_id bug（每次 append 而不是 upsert 整行）。
- **style_response 升级为 4 维向量**：`{"challenge_tolerance": 0-5, "guidance_density": 0-5, "affirmation_need": 0-5, "humor_acceptance": 0-5}`——4 个连续维度可以同时存在，agent 按向量调语气而不是 enum switch。
- **demo 视频加 A/B 段落**：同一用户跑 2 次（一次有 profile / 一次无 profile），录"差异"——破 REVIEW_001 "作者自评幻觉"指控。


---

## 4. 跨界 forced association 算法

### SOTA

- **Fauconnier & Turner · Conceptual Blending / Conceptual Integration Networks**（1998 Cognitive Science）：跨界不是两概念简单并列，而是 **两个输入空间 → generic space（共享结构）→ blended space（涌现新结构）** 四空间模型。砚友 V1 的 "A × B 抛挑衅性问题" 只做了 input1+input2，没有显式让用户构建 generic space 和 blend space。[Conceptual Integration Networks 1998 论文](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog2202_1)
- **Gentner Structure-Mapping Engine (SME)**（Falkenhainer/Forbus/Gentner 1989）：analogy = 把 base domain 的**关系结构**而非表面特征映射到 target domain；核心原则 systematicity——优先映射高阶关系而非孤立 predicate。砚友想要"用 RAG 解决中医取穴"这种碰撞产生质量，得让用户显式说出 "源域的哪个关系结构" 而不只是 "源域里的哪个概念词"。[SME 算法论文](https://groups.psych.northwestern.edu/gentner/papers/FalkenhainerForbusGentner89.pdf) / [Gentner & Forbus 2025 多十年回顾](https://journals.sagepub.com/doi/abs/10.1177/09637214251395678)
- **LLM × analogical reasoning（2024-2025 Design Science）**：LLM-assisted analogical reasoning 让设计 ideation 组的 novel idea 评分显著高于 baseline；用 cosine similarity over encoder embedding 做 analog 动态选取已经是标准做法。[Cambridge Design Science 论文](https://www.cambridge.org/core/journals/design-science/article/analogical-reasoning-with-large-language-models-a-cocreative-framework-and-benchmarking-of-llms-in-design-ideation/0B8149CCF53C45E1E1B78C4CA93E5BDC) / [Fluid Transformers arXiv:2302.12832](https://arxiv.org/pdf/2302.12832)
- **Concept Vectors in LLMs**（arXiv:2503.03666, 2025）：诚实告诉你坏消息——LLM 内部对"上下位、反义"这类**词汇关系**有稳定 concept vector，但对**抽象关系**没有稳定表示。即砚友想让 LLM 自动找"跨界 + 高阶关系映射"，光靠 embedding 距离不够，必须显式 prompt 引导用户做 structure mapping。[arXiv:2503.03666](https://arxiv.org/pdf/2503.03666)

### 砚友差距

1. **V1 = `random.choice` + 手写簇黑名单**——按 Concept Vectors 论文 + SME 理论双重提示：纯距离选 B 不够，需要的是 **distance + relational structure overlap potential** 的联合打分。
2. `pick_cross_domain` 算法生成 (A,B) 后只抛"A 的方法论解 B 的问题"——这等同于 Fauconnier 四空间里只触发了 input space。**用户没被引导去构建 generic space**（A 和 B 共享的抽象关系是什么？），生成的 blend 会很表层。
3. SAME_CLUSTER 是硬编码——A 字典每加 1 个新主题就要补；不可扩展。任何稍微"AI 簇"外的标签都无簇可查，退化为纯 random。
4. 没有"碰撞质量"反馈——用户给出的"荒谬 + 有道理"分析质量没被评估，下次抽 B 时无法用历史强化（高质量 B 应该被加权）。

### 立刻可吸收的升级

- **V1.5 算法（2-3 天可落地）**：用 OpenAI `text-embedding-3-small` 一次性 embed 所有 Bitable 标签 → 缓存到 `data/tag_embeddings.npy` → 选 B 时按 `(1 - cosine(A, B))` 做 softmax 加权。**直接砍掉 SAME_CLUSTER 字典**——这是 fusion-reference 里 V2 stretch goal，提前到 V1.5 做完全可行（embedding API 调用一次几分钱）。
- **加 generic-space 提问步骤**：抽到 (A,B) 后不直接抛"荒谬/有道理"，先问用户 **"A 和 B 在最抽象的层面，可能共享什么样的结构关系？"**——逼用户做 SME 式的 structure mapping。等他给出结构后，再问 blend 怎么涌现。这步如果让用户做不出来，再降级到现有 V1 模板。
- **加 blend 质量自评**：每次 fusion 结束时，agent 用 LLM-judge 对 blend 输出打三个分（novelty 0-5 / feasibility 0-5 / user-engagement 0-5），写进 `fusion_history`。下次抽 B 时按历史质量做 explore-exploit 加权（高分组合相邻的 B 加权）。
- **README "fusion 是我们相对 Study Mode 真正的 moat" 这句话要给硬支撑**：把 Fauconnier 4-space + SME systematicity 两个学术锚点写进发帖叙事——评审一看就知道你不是拍脑袋"random 配对"。


---

## 5. Devil's advocate / 多 agent 辩论

### SOTA

- **Anthropic Debate Safety Case Sketch**（arXiv:2505.03989, 2025-05）：debate 作为 scalable oversight 核心技术，理论上"诚实是唯一均衡点"。但 Anthropic 自己也承认前提是 judge 足够强——judge 弱时整个 debate 崩塌。[arXiv:2505.03989](https://arxiv.org/pdf/2505.03989)
- **CW-POR · Confidence-Weighted Persuasion Override Rate**（arXiv:2504.00374, 2025-04）：单轮多 agent debate 里，LLM judge 频繁被"vivid 但错误的论点"说服选错——给出量化指标。[arXiv:2504.00374](https://arxiv.org/pdf/2504.00374)
- **Devil's Advocate: Anticipatory Reflection for LLM Agents**：单 agent 自己扮演 devil's advocate 在生成答案前自反思——可以提升 problem-solving 能力 + 减少 bias。和砚友 fusion 的设计完全同构。
- **LLM-Powered Devil's Advocate for Group Decision**（ACM CHI 2024, dl.acm.org/doi/fullHtml/10.1145/3640543.3645199）：明确发现 AI 扮演 devil's advocate 在小组决策中能有效避免 confirmation bias 和 groupthink，且参与者主观满意度不降。[ACM 论文](https://dl.acm.org/doi/fullHtml/10.1145/3640543.3645199)
- **Minority Voices via Devil's Advocate**（arXiv:2502.06251, 2025-02）：进一步证明 AI devil's advocate 还能放大少数派观点。
- **Persuasion Driven Adversarial Influence**（Nature Sci Rep, 2026）：多 agent debate 中**一个 agent 恶意持续说服**就能拐走整个共识——单 agent 自我说服理论上风险等价（"自己劝服自己" 的内在闭环）。[Nature 论文](https://www.nature.com/articles/s41598-026-42705-7)

### 砚友差距 + 风险

1. fusion 的 devil's advocate 是**单 agent 扮演**（system prompt 写"你是 devil's advocate"），没有外部 judge——按 CW-POR 论文，存在"agent 自己说服自己用户走偏"的风险（agent 持续质疑 → 用户被压服 → agent 收尾时反而强化错误结论）。
2. fusion Step 4 的"收敛信号"判定是 agent 自己做的——按 Anthropic Debate Safety 框架，这等于"既是辩手又是裁判"，没有 sanity check。
3. fusion 里 agent 持续质疑模式如果遇到用户**真的有正确观点**，agent 的质疑会推用户偏离正确方向——这是 CW-POR 论文最警告的失败模式。
4. Step 5 "禁止在大纲里塞用户没自己想到的新点子"是好规则，但 reviewer 指出现有 Step 5 模板里的"最小可行版本"段落本身就是 agent 在替用户想——已经踩坑。

### 立刻可吸收的升级

- **加 "steel-man + devil's advocate" 双角色切换**：单 agent 在每个回合**先 steel-man 用户最强版本（"如果你的观点对，最强的支撑论证是什么"）再 devil's advocate**。Anticipatory Reflection 论文证明这种自反思能减偏。代码工作量为零（只改 prompt）。
- **引入外部 judge agent（轻量版）**：每 3-5 个回合调一次 `judge_call`（独立 system prompt：你是教学评估官，只评估 agent 是否在做有效的引导而非压服），输出"是否需要 agent 收敛"信号——破"既是辩手又是裁判"问题。这个 judge 在 demo 里**不展示给用户**，仅当作内部 governor。
- **加 "users right" 兜底**：当用户连续 2-3 轮坚持同一观点 + 给出新证据 → agent 必须切到 steel-man 模式而非继续质疑。`devils-advocate-prompts.md` 现在缺这条话术。
- **Step 5 大纲精简到"复述 + 用户已说过的失败模式"**——把"我建议的下一步" 段落整段砍掉。这条同时回应 REVIEW_001 § F2。
- **README 加风险声明**：明确写"fusion 模式有 *自我说服* 风险（CW-POR）；如果用户感觉被压服，砚友会切到 steel-man 模式 + judge agent 介入"——主动暴露技术风险反而加 community value 分。


---

## 6. 对话效果可量化评估

### SOTA

- **Khan Academy 2024-11 Efficacy Results + 2024-25 Khanmigo pre-post 研究**：Khanmigo 用 pre-post test 测 learning gain；公开的 2024-25 研究**坏消息**——量化分析显示各组都有 learning gain，**但组间无显著差异**；定性数据显示学生主观满意度高。即 Khan Academy 自己也没能用 pre-post 证明 Khanmigo 显著优于无 Khanmigo。[Khan Academy Efficacy Nov-2024](https://blog.khanacademy.org/khan-academy-efficacy-results-november-2024/) / [Khanmigo pre-post 研究](https://jtl.uwindsor.ca/index.php/jtl/article/view/10052)
- **LearnLM Eedi trial** ：用真实学生 + classroom 数据测 misconception resolution rate（95.4% AI+人类 vs 94.9% 单人类）——这是当前最严谨的 AI tutor 评估范式。
- **RAGAS**（Es et al. 2024, arXiv:2309.15217）：LLM-as-judge 的开源标准化方案；核心思想是把"主观质量"拆成多个可独立打分的子维度（faithfulness / relevance / context-precision）。可类比迁移到 Socratic 评估。[RAGAS arXiv](https://arxiv.org/pdf/2309.15217)
- **Bloom's Taxonomy 自动分类**（arXiv:2511.10903, 2025-11）：GPT-4 / Gemini 在 Bloom's 6 层认知分类上 accuracy 0.72-0.73——足以用来 **自动标注 agent 提问所触发的认知层次**（remember/understand/apply/analyze/evaluate/create）。[arXiv:2511.10903](https://arxiv.org/html/2511.10903)
- **MathDial teacher-move taxonomy**（前述）：把 tutor 行为分类后做评估的范式，砚友可以直接套。

### 砚友差距

1. PLAN.md 阶段 2 给了 8 天调 prompt，**完全没自动化 eval**——按 REVIEW_001 §D 的指控这就是"8 天瞎调"。没有 eval = 调完不知道有没有变好 = 阶段 4 demo 翻车风险高。
2. "用户悟到了"的成功标准是作者主观判断——这是 REVIEW_001 §A3 的"双重幻觉"指控。Khanmigo 自己 pre-post 都搞不出显著差异，砚友凭作者自评说"悟到了"完全站不住。
3. profile 的 `mastery_delta` 是 agent 自己打的（-1/0/+1/+2），等于 LLM 既是出题人又是阅卷人，没有外部锚点。
4. 没有 agent 提问质量本身的评估——`aha_moment_question` 字段只有 agent 自评"哪句最有效"，没有对比基线。

### 立刻可吸收的升级

- **3 天搭最小 eval 框架**（阶段 2 的前 3 天必须做）：5 篇文章 × 各准备 5 个 ground-truth 知识点 → 用 LLM-judge（独立 prompt，给原文 + agent 对话 + 用户回复）打三个分：① user_reasoning_quality（用户推理是否独立推进）② agent_telling_rate（agent 是否过度直接给答案 / MathDial telling move 占比应 ≤20%）③ knowledge_coverage（5 个知识点用户在对话中触达几个）。RAGAS 风格的可独立打分子维度。
- **加 Bloom's level 自动标注**：用 GPT-4 把 agent 每个提问自动打 Bloom's 标签（accuracy 0.73 已经够 demo 用），统计 distribution——好的 Socratic 对话 analyze/evaluate/create 占比应远高于 remember/understand。这是 demo 视频里**最有说服力的可视化**。
- **3-5 个真朋友 pre-post 微量测试**：每个朋友选一篇陌生文章 → 让他口头说出对该主题的理解（5 个开放题）→ 跑砚友 → 再问相同 5 题 → 用 LLM-judge 对比答案变化。这是 Khanmigo 都没真正搞定的事——但你只需要 N=3-5 演示在 demo 里有显著感即可，不需要统计显著性。REVIEW_001 §F3 已经推荐过早期真朋友测试，此处给评估方法。
- **demo 视频里加一张"对话质量 dashboard"**：Bloom's level 分布饼图 + telling move rate 折线图 + 触达知识点 checkbox——把"agent 是不是真在做 Socratic"这件事可视化、不靠用户主观感受。完全可以用 matplotlib 一张图搞定，工作量 0.5 天，但给 completeness / community value 双重加分。
- **README 加一句"我们用 RAGAS + Bloom's 自动评估 Socratic 质量，自带 eval framework"**——这是 ChatGPT Study Mode 公开材料里没有的工程透明度，是真正能让 reviewer 改观的差异点。


---

## 风险提示

按踩坑概率与杀伤力排序：

1. **苏格拉底硬规则 = 用户 frustrated 流失**（Eedi/LearnLM trial 实测，人类老师 **44.3% 编辑都在调 pacing + 19.5% 加情感缓冲**，合计 63.8% 在调"AI 体感"，[Eedi Substack 报告](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can)）。砚友"每回合 ≤2-3 句、绝不投降"如果不加 pacing detection，demo 时大概率出现"用户被反复追问到放弃"的尴尬场面。**对策见 §1 升级建议**。
2. **fusion 单 agent 自我说服**（CW-POR arXiv:2504.00374）。devil's advocate 持续质疑 + 用户最终"被说服收敛"——很可能是错的方向。**对策见 §5 双角色 + 外部 judge**。
3. **没自动 eval = 阶段 2 八天瞎调**（REVIEW_001 §D + Khan Academy 自己 pre-post 都没显著差异）。砚友想用"作者自评"扛过 22 天，赛事 demo 必翻车。**对策见 §6 RAGAS 风格 LLM-judge + Bloom's 自动标注**。
4. **跨界 V1 算法距离学术 SOTA 太远**——Fauconnier 4-space + Gentner SME 是 1990s 就有的经典，砚友 V1 还在 `random.choice` 阶段，reviewer 一眼看穿"未读相关学术"。**对策见 §4 V1.5 embedding + generic-space 引导**。
5. **profile 不是 turn 粒度增量写 = session crash 全丢**（你这次跑挂就是真案例 + REVIEW_001 §C1 record_id bug 双重原因）。**对策见 §2 + §3 即时落盘 + Memory Tool 协议**。
6. **Concept Vectors 论文（arXiv:2503.03666）警告**：LLM 内部对抽象关系无稳定表示——意味着 fusion 想让 LLM "自己找出 A 和 B 的高阶共享结构" 大概率失败，必须显式 prompt 让用户来做这一步。**已纳入 §4 升级建议**。
7. **ChatGPT Study Mode 全免费 + 8 亿周活**——innovation 维度天花板已被 OpenAI 钉死。砚友所有 README/demo 叙事必须把战场转到"个人知识库 Socratic + 跨界 fusion 双驱"两条砚友独有的能力上，不要硬碰通用 Socratic。
8. **未找到具体出处**：① 国内"Socratic AI 在中文语境下的 cultural pacing 偏好"研究 ② Trae SOLO 平台对 Anthropic Memory Tool beta header 的具体支持情况 ③ 飞书 Bitable 富文本字段 JSON-as-string 在 high-frequency append 写入下的性能上限。这三项 22 天内能自测就自测、否则在 README 标"未验证"。

