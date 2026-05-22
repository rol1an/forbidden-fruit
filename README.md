# 砚友 · Forbidden Fruit

> 致敬伊甸园那枚开智的禁果。

砚友是一组为 Trae SOLO 技能创作赛打造的 Skill 包，由三个独立 Skill 组成，围绕一个核心信念：

**人与人之间应该降低摩擦——这是协作效率问题；人与知识之间应该增加摩擦——这是认知攀爬问题。**

低价值的物理摩擦（找链接、跟反爬虫斗智斗勇、忍受营销号标题党、调排版）必须由工具吃掉。高价值的智力摩擦（被问住时调动回忆、跨界概念碰撞、强行解释自己的直觉）必须由产品主动制造。

砚石与墨——必须经千百次按压与剧烈摩擦，才能研磨出最浓郁的墨汁，落笔成章。

## 三个 Skill

| Skill | 用途 | 摩擦类型 |
|---|---|---|
| `yanyu-import` | 微信公众号文章去广告、按知识结构重组、入库飞书知识库 | 消灭低价值物理摩擦（原料层）|
| `yanyu-grinding` | 苏格拉底式提问引导用户深度学习已入库知识，agent 绝不直接给答案 | 制造高价值智力摩擦（研磨模式）|
| `yanyu-fusion` | 跨界标签强制碰撞，devil's advocate 反复质疑，逼用户收敛创新点 | 制造高价值智力摩擦（研创模式）|

横切机制：每次对话后写用户画像 Bitable，下次对话开始前读取，agent 据此调起点难度、对话风格、跨界标签选择——**这本身就是 progressive disclosure 从静态文件扩展到动态对话状态的活体应用**。

## 仓库结构

```
forbiddenfruit/
├── README.md
├── docs/
│   └── PLAN.md                     # 完整的 22 天交付方案
├── probe/
│   └── TRAE_SOLO_PROBE.md          # Trae SOLO 平台兼容性摸底清单
├── yanyu-import/
│   ├── SKILL.md
│   ├── references/                 # L3 懒加载：美学规则、DocxXML 速查
│   └── scripts/                    # L3 懒加载：爬取、lark 写入封装
├── yanyu-grinding/
│   ├── SKILL.md
│   ├── references/                 # L3：按主题拆的提问模板库 + 画像 schema
│   └── scripts/                    # L3：profile_read.py / profile_write.py
└── yanyu-fusion/
    ├── SKILL.md
    ├── references/                 # L3：跨界算法 + devil's advocate 话术
    └── scripts/                    # 复用 yanyu-grinding 的 profile 脚本
```

## 设计哲学

每个 SKILL.md 严格遵守 Anthropic Claude Skills 的 **progressive disclosure** 三层加载：

- **L1**：frontmatter（仅 name + description），**始终扫描**
- **L2**：SKILL.md 正文，description 命中时才加载（300-500 行内）
- **L3**：`references/` 和 `scripts/`，L2 显式引用时才加载

`description` 字段按"检索词典"原则写——触发场景 + 用户高频关键词 + 1-2 句话内。

## 部署

砚友三个 Skill 都遵循 Anthropic Skills 协议。`npx skills` 工具会把它们 symlink 到 Claude Code / OpenClaw / Trae CN 等支持 Anthropic Skills 的 host。

详见 [docs/PLAN.md](docs/PLAN.md) 完整方案、[probe/TRAE_SOLO_PROBE.md](probe/TRAE_SOLO_PROBE.md) 平台摸底清单。
