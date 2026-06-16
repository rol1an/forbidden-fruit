# 砚友 · Forbidden Fruit

> 致敬伊甸园那枚开智的禁果。

砚友是一组为 Trae SOLO 技能创作赛打造的 Skill 包，由两个 Skill 组成（其中 `yanyu-dialogue` 内含研磨 / 研创双 mode），围绕一个核心信念：

**人与人之间应该降低摩擦——这是协作效率问题；人与知识之间应该增加摩擦——这是认知攀爬问题。**

低价值的物理摩擦（找链接、跟反爬虫斗智斗勇、忍受营销号标题党、调排版）必须由工具吃掉。高价值的智力摩擦（被问住时调动回忆、跨界概念碰撞、强行解释自己的直觉）必须由产品主动制造。

砚石与墨——必须经千百次按压与剧烈摩擦，才能研磨出最浓郁的墨汁，落笔成章。

## 两个 Skill

| Skill | 用途 | 摩擦类型 |
|---|---|---|
| `yanyu-import` | 微信公众号文章去广告、按知识结构重组、入库飞书知识库 | 消灭低价值物理摩擦（原料层）|
| `yanyu-dialogue` · 研磨模式 | 苏格拉底式提问引导用户深度学习已入库知识，agent 绝不直接给答案 | 制造高价值智力摩擦（研磨模式）|
| `yanyu-dialogue` · 研创模式 | 跨界标签强制碰撞，devil's advocate 反复质疑，逼用户收敛创新点 | 制造高价值智力摩擦（研创模式）|

> `yanyu-grinding` / `yanyu-fusion` 是早期的两个独立 Skill，已合并进 `yanyu-dialogue`（研磨 + 研创双 mode），目录仅保留废弃声明的 `SKILL.md` 作向后兼容。合并动机见 [docs/PLAN_v2_DECISIONS.md](docs/PLAN_v2_DECISIONS.md) §决策 2。

横切机制：每次对话后写用户画像 Bitable，下次对话开始前读取，agent 据此调起点难度、对话风格、跨界标签选择——**这本身就是 progressive disclosure 从静态文件扩展到动态对话状态的活体应用**。

存储统一走 `yanyu_core`（`Backend` ABC + `LarkBackend` / `LocalFileBackend` 双实现），由 `YANYU_BACKEND` 环境变量切换；默认 `local`，开箱即用、零飞书依赖。

## 仓库结构

```
forbiddenfruit/
├── README.md
├── CLAUDE.md                       # 给接续对话的 Claude 看的项目指南
├── docs/                           # 方案 / 决策 / 调研 / 答辩物料
│   ├── PLAN.md                     # 原始 22 天交付方案（时间戳锚，不动）
│   └── PLAN_v2_DECISIONS.md        # 7 大决策叠加层（active）
├── probe/
│   └── TRAE_SOLO_PROBE.md          # Trae SOLO 平台兼容性摸底清单
├── yanyu-import/                   # Skill：微信文章 → 飞书入库（原料层）
│   ├── SKILL.md
│   ├── references/                 # L3 懒加载：美学规则、DocxXML 速查
│   └── scripts/                    # L3 懒加载：wechat_scrape.py
├── yanyu-dialogue/                 # Skill：苏格拉底研磨 + 跨界研创（双 mode）
│   ├── SKILL.md
│   ├── references/                 # L3：提问模板 / 跨界算法 / 画像 schema / hint laddering
│   ├── scripts/                    # L3：profile_read.py / profile_write.py / profile_init.py
│   └── eval/                       # LLM-judge / Bloom 打标 / 回归 / dashboard
├── yanyu_core/                     # 共享存储抽象：Backend ABC + Lark/Local 双实现 + factory
│   ├── backend.py · lark_backend.py · local_backend.py · factory.py
│   └── tests/                      # 14 个 unittest（stdlib，无 pytest 也能跑）
├── yanyu-grinding/  (DEPRECATED)   # 仅留 SKILL.md 废弃声明，已合并入 yanyu-dialogue
└── yanyu-fusion/    (DEPRECATED)   # 仅留 SKILL.md 废弃声明，已合并入 yanyu-dialogue
```

## 设计哲学

每个 SKILL.md 严格遵守 Anthropic Claude Skills 的 **progressive disclosure** 三层加载：

- **L1**：frontmatter（仅 name + description），**始终扫描**
- **L2**：SKILL.md 正文，description 命中时才加载（300-500 行内）
- **L3**：`references/` 和 `scripts/`，L2 显式引用时才加载

`description` 字段按"检索词典"原则写——触发场景 + 用户高频关键词 + 1-2 句话内。

## 部署

砚友的 Skill 都遵循 Anthropic Skills 协议。`npx skills` 工具会把它们 symlink 到 Claude Code / OpenClaw / Trae CN 等支持 Anthropic Skills 的 host。

详见 [docs/PLAN.md](docs/PLAN.md) 完整方案、[probe/TRAE_SOLO_PROBE.md](probe/TRAE_SOLO_PROBE.md) 平台摸底清单。
