# 砚友 · Forbidden Fruit：Trae SOLO 技能创作赛交付方案

> 项目代号：**禁果 / Forbidden Fruit**（致敬伊甸园那枚开智的果实）
> 产品名：**砚友**
> 美学意向：砚石与墨——必须经千百次按压与剧烈摩擦，才能研磨出最浓郁的墨汁，落笔成章

---

## Context · 重构动机

### 摩擦理论（产品根基）

人与人之间应该**降低**摩擦——这是协作效率问题。
人与知识之间应该**增加**摩擦——这是认知攀爬问题。

进一步把摩擦拆成两类：

| 类型 | 描述 | 处置 |
|---|---|---|
| **认知内摩擦**（低价值物理摩擦）| 找链接、跟反爬虫斗智斗勇、忍受营销号标题党、在飞书调排版对齐、手画表格…… 消耗精力但不产生智力增量 | **必须降到零**——这是工具应该吃掉的部分 |
| **深度认知摩擦**（高价值智力摩擦）| 对核心推导提出质疑、跨界概念碰撞、调动回忆作答、思考新理论如何解决自己实验室模型的难题 | **必须主动制造**——这才是产品真正的价值 |

### 为什么上一版方案没击中

回看上一版的"主动反哺"（推隐藏答案的面试卡片 / 推跨界论文创新大纲）——本质上是**把答案直接喂给用户**，用户处于被动接收态，知识摩擦近乎为零。哪怕 UI 再炫，也只是换种姿势把"答案"塞过去。

真正的产品形态应该是：**agent 以勾人参与的方式发起交互，通过精心设计的提问/质疑/碰撞，逼用户调动认知去攀爬，最后让用户自己体会到"我悟到了"的喜悦。** 而 agent 也在每次对话中沉淀对用户的理解，自我进化。

### 跟技能创作赛的契合

技能创作赛评审四维：**innovation / usability / completeness / community value**。新定位下：
- innovation：摩擦理论 + 苏格拉底对话引擎 + 跨界强制碰撞，社区独一份
- usability：用户做完一次对话有"我学到了"的真实感受，不是看到一堆 AI 生成的总结
- completeness：把核心对话引擎做稳，比铺多个半成品功能强
- community value：摩擦理论 + 砚友美学可以单独成文做方法论传播

---

## Skill 设计哲学（progressive disclosure）

按 Anthropic Claude Skills 官方设计哲学，砚友必须遵守以下铁律——这些不是建议，写错就等于 Skill 装了等于没装。

### 三层加载（L1 / L2 / L3）

| 层 | 内容 | 加载时机 | 砚友的具体落地 |
|---|---|---|---|
| **L1** | SKILL.md frontmatter（仅 name + description）| **始终被扫描** | 决定用户说"我想学这篇文章"时模型能不能想起来用砚友 |
| **L2** | SKILL.md 正文 | description 命中时才加载 | 苏格拉底引导师人设 + 核心提问策略 + 工作流 |
| **L3** | `references/` 和 `scripts/` 引用的外部资源 | L2 明确引用时才加载 | 详细 prompt 模板、用户画像 schema、跨界标签算法、4 色约束规则等 deep material |

**死线：每个 SKILL.md 正文 ≤ 500 行。** 超过就拆 Skill。

### description 字段是"检索词典"不是"说明文档"

模型按搜索引擎逻辑匹配 description 决定要不要触发——

❌ 错误：`description: 一个用于深度学习的对话 skill`
✅ 正确：`description: 当用户想要深度学习已入库的某篇文章/主题，希望被苏格拉底式提问引导自己悟到答案、而不是直接读 AI 总结时使用。触发词：研磨、深挖、引导提问、苏格拉底、自己想、被问住`

三条要求：① 触发场景明确 ② 用户最可能说出的高频关键词全铺 ③ 1-2 句话。

### SKILL.md / 系统 prompt / MCP 三者不可互替

| 机制 | 在砚友里承担 |
|---|---|
| **系统 prompt**（性格基线，永远在上下文）| 用户在 Trae SOLO 顶层设的"砚友人设"——克制、不替用户思考、追问而非陈述 |
| **SKILL.md**（工作手册，触发时加载）| 三个独立 Skill 的具体流程 |
| **MCP / scripts**（外部能力）| `lark-cli` / `lark-oapi` 调用飞书读写、PySceneDetect 抽帧等——SKILL.md 引用 scripts 完成 |

`lark-cli` 调用归入 scripts/（"已有能力 + 一套流程"），不需要专门搞 MCP，除非 Trae SOLO 阶段 0 摸底发现强制要求。

---

## 砍掉与降级（明确范围）

### 砍掉
- 主动反哺 Cron + 飞书端侧推送（用户被动接收 = 零摩擦）
- 创意博主跨界灵感大纲 Agent（直接产出大纲 = 替代用户思考）
- 学术轨 C（WALL-X 论文创新点）
- Streamlit Web 大屏（技能创作赛不要 Web app）
- 4 角色 agent 编排（过度设计，且违反 Skill 单一职责）
- 自造 ASR / OpenCV 视觉理解
- **单 mega-Skill 架构**（违反 progressive disclosure，必须拆）

### 降级为"后台原料层"
- 微信脱水入库（保留现有 import-wechat 流程，但**不再当卖点宣传**，因为它只是消除低价值物理摩擦的基础设施）
- 4 色约束 + 反表格美学规则（继续用，但同样降为基础设施，放 L3 references/）

### Stretch goal（有时间再做，不进核心评审）
- B站/抖音视频源（用 `lark-minutes`，不自造 ASR）

---

## 核心产品形态：三个独立 Skill 组成的 Skill 包

按 Anthropic 设计哲学，砚友拆成三个独立 Skill，自进化是横切关注点放 scripts/。

### Skill 1：`yanyu-import`（原料层）

**description（草稿）**：当用户提供微信公众号文章 URL 想要去广告、剔除营销号噪音、按知识结构重组并入库到飞书知识库时使用。触发词：微信文章、公众号、收藏导入、知识入库、去广告

**L2 正文（≤300 行）**：8 步流程骨架（爬取 → 去噪 → 知识重构 → DocxXML → wiki+docs 写入 → Bitable 双向链接 → 索引登记 → 输出确认）

**L3 references/**：
- `aesthetic-rules.md`：4 色约束 + 反表格铁律 + 强力标记保留规则
- `lark-doc-xml-cheatsheet.md`：DocxXML 常用 block 速查

**L3 scripts/**：
- `wechat_scrape.py`：爬取去噪
- `lark_write.sh`：包装 lark-cli docs +update / wiki +node-create

### Skill 2：`yanyu-grinding`（研磨模式 · 核心 wow）

**description（草稿）**：当用户想要深度学习已入库的某篇文章/某个主题，希望被苏格拉底式提问引导自己悟到答案、而不是直接读 AI 总结时使用。触发词：研磨、深挖、引导提问、苏格拉底、自己想、被问住、学透

**L2 正文（≤500 行）**：
- 苏格拉底引导师人设（克制、追问、绝不直接给答案）
- 提问递进策略（钩子 → 探查 → 卡壳引导 → 关键点印证 → 收尾）
- 输出约束（每回合 ≤2-3 句，避免变成讲座）
- 反偷懒兜底（用户说"直接告诉我吧"时的应答模板）

**L3 references/**：
- `question-bank-rag.md`、`question-bank-agent.md`、`question-bank-llm.md`（按主题分文件的提问模板库——越按主题拆，单次加载越精准）
- `profile-schema.md`：Bitable 用户画像字段定义

**L3 scripts/**：
- `profile_read.py` / `profile_write.py`（自进化的横切脚本，三个 Skill 共享）

### Skill 3：`yanyu-fusion`（研创模式）

**description（草稿）**：当用户抛出一个模糊的创意、困惑、跨界灵感，想要通过 agent 反复质疑碰撞最终自己收敛到清晰创新点时使用。触发词：碰撞、跨界、灵感、收敛、创意、想做但说不清、有个想法

**L2 正文（≤400 行）**：
- 强制跨界规则（从用户画像挑一个已熟悉领域 × 一个完全陌生领域）
- devil's advocate 质疑模板
- 收敛判断（什么时候 agent 才能停止质疑接手扩展大纲）

**L3 references/**：
- `cross-domain-algorithm.md`：跨界标签碰撞算法（按领域聚类距离选标签的具体规则）
- `devils-advocate-prompts.md`：分场景的质疑话术库

**L3 scripts/**：复用 `yanyu-grinding` 的 profile 脚本

### 自进化：横切关注点

每次对话结束 → `profile_write.py` 调 `lark-cli base +record-upsert` 写画像：

| 字段 | 来源 |
|---|---|
| 用户在 X 主题上的掌握程度（0-5）| 模式 A 中用户的答题路径质量 |
| 用户的思维盲点 / 反复卡壳点 | 模式 A 中卡了哪几步 |
| 用户偏好的对话风格（被挑战 / 被引导 / 被肯定）| 用户对 agent 不同语气的回应正向程度 |
| 用户的方法论沉淀（用户自己说出来的金句）| 模式 B 中用户辩护时说出的有创见的话 |
| 关键启发时刻（让用户"悟到"的问题）| agent 自评哪句问题最有效 |

下次对话开始前 → `profile_read.py` 调 `lark-cli base +record-search` 取画像，agent 据此调起点难度、对话风格、跨界标签选择。

**这本身就是 progressive disclosure 的活体应用——熟悉的主题少展开、陌生的主题多展开。把 Anthropic 静态文件的设计哲学扩展到动态对话状态。** 这一句进发帖叙事。

---

## 阶段规划（5-21 ~ 6-12，22 天）

### 阶段 0（5-21 ~ 5-22，2 天）：Trae SOLO 摸底 · go/no-go

用户对 Trae SOLO 桌面端完全没碰过，是最高优先级风险。

任务：
1. 跑通 Trae SOLO 官方 Hello-World Skill
2. **重点验证四件事**：
   - Trae SOLO Skill 是否**兼容 Anthropic Skills 协议**（SKILL.md frontmatter + progressive disclosure 三层加载）？格式上是 Markdown + YAML frontmatter 还是 Trae 私有格式？
   - Skill 能不能做**多轮对话**（用户作答 → agent 追问 → 用户再答…）
   - Skill 能不能在对话过程中调用本地 shell（`lark-cli`）或 HTTP（`lark-oapi` Python SDK）
   - 多个 Skill 之间能否共享 scripts/ / 互相引用 / 编排
3. 摸清发布流程（GitHub repo 还是 TRAE 平台公开链接）
4. 输出 `TRAE_SOLO_PROBE.md`，明确 go/no-go

Go/No-Go 关键点：
- **如果 Trae SOLO 不能做多轮对话 Skill** → 整个产品定位无法落地，弃赛或换平台（Claude Code 沉淀自用）
- **如果 Trae SOLO 不能调 shell** → 备选 `lark-oapi` Python SDK（已装 1.3.5）
- **如果 Trae SOLO Skill 格式不兼容 Anthropic 规范** → 三层加载策略要换成 Trae 私有形态，工作量增加 1-2 天

### 阶段 1（5-23 ~ 5-25，3 天）：`yanyu-import` Skill

把现有 `~/.claude/commands/import-wechat.md` 8 步流程封装成第一个独立 Skill，**只追求能跑**，不追求美学完美——它现在只是为对话引擎提供素材。

任务：
- 写 SKILL.md（L2 正文 ≤300 行，骨架流程为主）
- 美学规则下沉到 `references/aesthetic-rules.md`（L3 懒加载）
- 复用现有 lark-cli 命令包装成 `scripts/lark_write.sh`
- description 按"检索词典"原则反复打磨

验证：跑 5 篇微信文章入库，Bitable 索引完整。

### 阶段 2（5-26 ~ 6-02，8 天）：`yanyu-grinding` Skill（核心 wow）

产品的命门。

任务：
1. **SKILL.md 正文设计**（占 50% 时间）：苏格拉底引导师人设 + 提问递进策略骨架，控制在 500 行内
2. **References 库构建**（占 25% 时间）：按主题拆分提问模板库（按主题分文件，避免单次加载过重）
3. **profile 读写脚本**（占 15% 时间）：scripts/profile_read.py / profile_write.py
4. **测试集**（占 10% 时间）：5 篇已入库文章 × 自己跑 20 轮对话，迭代 prompt

验证：自己跑一次对话，必须有真实的"被问住了 → 想了想 → 悟出来"的体验。如果跑完只觉得"agent 在装腔作势"，prompt 不合格。

### 阶段 3（6-03 ~ 6-07，5 天）：`yanyu-fusion` Skill + 自进化闭环

任务：
1. SKILL.md 正文：强制跨界规则 + devil's advocate 模板，控制在 400 行内
2. `references/cross-domain-algorithm.md`：跨界标签选择算法（基于画像偏好的"已知 × 未知"组合）
3. profile 字段完整化（阶段 2 写了基础字段，这里补全方法论沉淀和关键启发时刻）
4. 测试：自己跑 3 个真实模糊想法 → 2 个能收敛到清晰创新点

### 阶段 4（6-08 ~ 6-10，3 天）：Demo + 发布物料

任务：
1. **录 demo 视频**（5-7 分钟）：
   - 研磨模式跑一遍真实文章——展示"自己悟到"的高光时刻
   - 研创模式跑一遍真实想法——展示从模糊到清晰的收敛过程
   - 自进化展示：跑两次对话，第二次明显看到 agent 更懂用户
2. **README + 论坛发帖文案**：
   - 头图用砚石与墨的视觉
   - 核心叙事：禁果 / 摩擦理论 / 苏格拉底引擎 / 自进化即 progressive disclosure 的活体应用
   - 把"为什么不直接给答案"这件事讲清楚（这是反 AI 主流叙事的——大部分 AI 都在追求更快给答案，砚友反其道而行）
3. **方法论 blog**：摩擦理论 + 砚友美学 + Skill 设计哲学在砚友的活用（progressive disclosure 静态 → 动态），单独发一篇

### 阶段 5（6-11 ~ 6-12，2 天 buffer）：发布

- GitHub 仓库 public（三个 Skill 一个 monorepo）
- forum.trae.cn 发帖
- 给身边 1-2 个真朋友试用，收集真实"悟到"案例补进发帖

---

## 仓库目录结构（参考 Anthropic Skills 规范）

```
yanyu-skill-pack/
├── README.md
├── yanyu-import/
│   ├── SKILL.md                    # L1 frontmatter + L2 正文 ≤300 行
│   ├── references/
│   │   ├── aesthetic-rules.md      # 4 色约束 / 反表格 / 强力标记保留
│   │   └── lark-doc-xml-cheatsheet.md
│   └── scripts/
│       ├── wechat_scrape.py
│       └── lark_write.sh
├── yanyu-grinding/
│   ├── SKILL.md                    # ≤500 行
│   ├── references/
│   │   ├── question-bank-rag.md
│   │   ├── question-bank-agent.md
│   │   ├── question-bank-llm.md
│   │   └── profile-schema.md
│   └── scripts/
│       ├── profile_read.py         # 三 Skill 共享
│       └── profile_write.py
└── yanyu-fusion/
    ├── SKILL.md                    # ≤400 行
    ├── references/
    │   ├── cross-domain-algorithm.md
    │   └── devils-advocate-prompts.md
    └── scripts/
        └── (复用 yanyu-grinding/scripts/profile_*.py)
```

---

## 评审四维自评

| 维度 | 怎么得分 |
|---|---|
| **innovation** | "反喂答案"叙事 + 苏格拉底引擎 + 强制跨界碰撞 + agent 自进化 = 跟所有 AI 工具反向走 |
| **usability** | 用户跑完真有学到的感受，不是看一堆 AI 生成的字 |
| **completeness** | 三个 Skill 独立闭环，每个都符合 Anthropic 设计规范（300/500/400 行内），评审上手就能感觉到工程素养 |
| **community value** | 摩擦理论 + 砚友美学 + "progressive disclosure 从静态扩展到动态" 三层方法论叙事 |

---

## 关键风险与应对

| 风险 | 应对 |
|---|---|
| **Trae SOLO 不支持多轮对话 Skill** | 阶段 0 卡死 2 天必须验证。如不支持，弃赛或换平台 |
| **Trae SOLO Skill 格式与 Anthropic 规范不兼容** | 工作量+1-2 天，把三层加载思想用 Trae 私有格式重新表达；如果完全不能分层，单 mega-skill 也得控制在 500 行内 |
| **苏格拉底 prompt 调不出"悟到"的感觉** | 阶段 2 留 8 天就是给这个的。如果第 5 天还出不来效果，立刻砍研创模式，all-in 研磨模式 |
| **Demo 中"悟到"时刻难稳定复现** | 阶段 4 准备 3-5 个"已验证能跑出效果"的固定话题，录 demo 不即兴 |
| **agent 自进化效果在 2 次对话间不明显** | demo 用 5-10 次对话的压缩展示，时间跨度不真实但效果可见 |
| **description 写错导致 Skill 触发不准** | 每个 Skill 写完都用 10 条不同口吻的真实需求测一遍触发率，<80% 重写 description |
| **范围爆炸** | 视频源（B站/抖音）默认砍，只在阶段 3 提前完成时作 stretch goal |

---

## 关键文件路径速查

| 文件 | 用途 |
|---|---|
| `~/.claude/commands/import-wechat.md` | 阶段 1 原料层复用（90% 现成）|
| `~/.claude/projects/-Users-luojian-claudecode/memory/feedback_wechat_import.md` | 原料层美学规则参考（迁到 `yanyu-import/references/aesthetic-rules.md`）|
| `~/.claude/projects/-Users-luojian-claudecode/memory/methodology_rag_and_llm.md` | 对话引擎设计参考（LLM 角色化 / 两步提炼思想可借鉴到苏格拉底链路）|
| `~/.claude/skills/lark-base/` | Bitable 画像读写参考 |
| `~/.claude/skills/lark-doc/` | 知识库写入参考 |
| `~/.claude/skills/lark-skill-maker/` | Skill 结构参考（其内部就遵循 progressive disclosure）|
| `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/SKILL.md` | Anthropic 官方 Skill 创作脚手架（33KB，三层加载范例）|
| `/opt/homebrew/bin/lark-cli` | CLI 工具（阶段 0 验证后决定用 CLI 或 SDK）|

---

## 端到端验证清单

阶段 0：
- [ ] Trae SOLO 多轮对话 Skill Hello-World 跑通
- [ ] `TRAE_SOLO_PROBE.md` 明确 go/no-go + Skill 格式（兼容 Anthropic 与否）

阶段 1：
- [ ] 5 篇微信文章入库，Bitable 索引完整可查
- [ ] `yanyu-import/SKILL.md` ≤300 行；description 用 10 条不同口吻需求测，触发率 ≥80%

阶段 2：
- [ ] 自己跑研磨模式 3 篇文章 × 各 5 轮对话，至少 2 次出现真实"悟到"体验
- [ ] Bitable 画像基础字段（掌握程度 / 卡壳点）写入正常
- [ ] `yanyu-grinding/SKILL.md` ≤500 行；references/ 按主题拆 ≥3 个文件

阶段 3：
- [ ] 自己跑研创模式 3 个模糊想法，2 个能收敛到清晰创新点
- [ ] Bitable 画像方法论 / 偏好字段写入正常
- [ ] 第二轮对话能观察到 agent 起点 / 风格基于画像调整
- [ ] `yanyu-fusion/SKILL.md` ≤400 行

阶段 4：
- [ ] Demo 视频录完
- [ ] README + 论坛文案 + 方法论 blog 三件套就绪

阶段 5：
- [ ] GitHub 仓库 public
- [ ] forum.trae.cn 帖子发出
- [ ] 至少 1 个真实朋友试用反馈纳入 README

---

## 一份顺手的提醒

`lark-cli` 当前 1.0.27，最新 1.0.36，建议在阶段 0 之前先升级——`npm update -g @larksuite/cli && npx skills add larksuite/cli -g -y`，更新后**重启 AI agent** 让新 Skill 生效。
