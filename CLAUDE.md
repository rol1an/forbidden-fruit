# 砚友 · Forbidden Fruit — Claude Code 项目指南

> 这份 CLAUDE.md 是给**你**（未来对话里的 Claude）看的，让你 0 摩擦接续这个项目。
>
> 看完一遍即可上手；细节按需 deep-dive 到 `docs/` 里。

---

## 一句话项目身份

砚友（InkMate / Forbidden Fruit）= **基于 Anthropic Claude Skills 协议、Trae SOLO + Claude Code 双 host 兼容的中式数字书院**。

参赛 Trae SOLO 技能创作赛（投稿期 2026-05-12 ~ 2026-06-12）。

## 哲学根基（必内化，不要忘）

**摩擦理论**——
- 人与人之间应该**降低**摩擦（沟通效率）
- 人与知识之间应该**增加**高价值智力摩擦（认知攀爬）

低价值物理摩擦（找文章、调排版、跟反爬虫斗）必须由工具吃掉；
高价值智力摩擦（被问住、跨界碰撞、调动回忆）必须由 agent 主动制造。

**反对 AI 喂答案**。砚友绝不直接给答案——而是用苏格拉底提问让用户**自己**悟到。

**美学意向**：砚石与墨——必须经千百次按压与剧烈摩擦，才能研磨出最浓郁的墨汁，落笔成章。

## Brand kit

| 场景 | 用 |
|---|---|
| 中文 | 砚友 |
| 英文 | InkMate |
| 项目代号 | 禁果 / Forbidden Fruit |
| GitHub repo | `rol1an/forbidden-fruit` |
| 仓库本地路径 | `/Users/luojian/claudecode/forbiddenfruit/` |
| 部署路径 | `~/.agents/skills/yanyu-dialogue` + `yanyu-import`（symlink）|

---

## 仓库架构鸟瞰

```
forbiddenfruit/
├── CLAUDE.md                ← 你正在读
├── README.md                ← 给人看的（GitHub 首页）
├── .gitignore
│
├── yanyu-import/            ← Skill #1：微信文章→飞书入库（原料层）
├── yanyu-dialogue/          ← Skill #2：苏格拉底研磨 + 跨界研创（核心 wow）
├── yanyu-grinding/          ← DEPRECATED（合并到 yanyu-dialogue）
├── yanyu-fusion/            ← DEPRECATED（合并到 yanyu-dialogue）
│
├── yanyu_core/              ← 共享后端抽象（Backend ABC + Lark/Local 双实现）
│   ├── backend.py
│   ├── lark_backend.py
│   ├── local_backend.py
│   ├── factory.py           ← YANYU_BACKEND=local|lark 环境变量
│   └── tests/               ← 14/14 PASS
│
├── docs/                    ← 给 agent / reviewer / 评审 / 未来你看的
│   ├── PLAN.md              ← 原始 22 天交付方案（不动 · 时间戳锚）
│   ├── PLAN_v2_DECISIONS.md ← 7 大决策叠加层（active, 含决策 7 hint laddering + 砚石痕迹）
│   ├── PITCH.md             ← README/答辩/blog 所有物料的取材源 ⭐
│   ├── BUSINESS.md          ← 商业可行性 + Study Mode reframe 附录
│   ├── DESIGN.md            ← 视觉规范（朱砂 / 砚石与墨）
│   ├── TECH_RESEARCH.md     ← 6 方向 SOTA 调研（Khanmigo/LearnLM/MathDial）
│   └── REVIEW_001.md        ← 首轮 reviewer 评估（4 维基线分）
│
└── probe/
    └── TRAE_SOLO_PROBE.md   ← Trae SOLO 兼容性实测记录（A/B/C 全通过）
```

---

## 文档地图（按"什么场景读什么"组织）

| 场景 | 优先读 |
|---|---|
| **刚接手项目，先理解全貌** | 本文件 → `docs/PITCH.md` → `docs/PLAN_v2_DECISIONS.md` |
| **要写发帖/README/答辩话术** | **必读 `docs/PITCH.md`**（含四大出彩点 + Ultimate Pitch + Q&A + 短语词典 + 地雷清单），不要在别处重新发明叙事 |
| **要改 SKILL.md / references/** | 先读 `yanyu-dialogue/SKILL.md` + 相关 reference + `docs/TECH_RESEARCH.md` 对应方向 |
| **要做工程实施** | `docs/PLAN_v2_DECISIONS.md` § 决策 1-7（每条都有完整接口设计 + 范围 + 排期）|
| **要改 hint laddering / 砚石痕迹** | `yanyu-dialogue/references/hint-laddering.md` + `inkstone-trace.md` + PLAN_v2 §决策 7 |
| **要做视觉/排版** | `docs/DESIGN.md`（朱砂 #A0322C 全篇 ≤3 处 / 标题宋体正文黑体）|
| **想知道为什么这么决定** | `docs/REVIEW_001.md` + `docs/BUSINESS.md` + `docs/TECH_RESEARCH.md` 风险提示 |
| **要跟评审解释飞书锁死** | `docs/BUSINESS.md` §5 + 决策 1 LocalFileBackend |
| **要回应"ChatGPT Study Mode 也能做" 质疑** | `docs/PITCH.md` 四大出彩点 + Q&A Q1 |

---

## 当前状态（截至 2026-05-22）

### ✅ 已完成

- 仓库骨架 + 3 Skill 完整（含合并 dialogue + deprecation 旧目录）
- yanyu-import **真实端到端 1 篇飞书入库** + 3 篇老文章双向链接缝合
- yanyu_core LocalFileBackend MVP（8 文件 / 14/14 单测 / 飞书额度耗尽自动 catch）
- eval/ 完整框架（judge / bloom_tagger / dashboard / regression，全支持 --mock）
- 7 个 docs 全部就位（44.3% 数据风险已修复 + Eedi Substack 真实出处验证）
- Trae SOLO 兼容性实测：A（自动选 skill）/ B（调 shell）/ C（返回真实数据）全 ✅
- GitHub 仓库已 push（public）
- **决策 7 P0 完成**（5-22 用户实测反馈驱动）: hint laddering L1/L2/L3 + 砚石痕迹 MVP（stage transition + every-5-rounds 触发） + Bloom agreement test P1 闸门脚手架 + reviewer 三项 critical 修复 + 4 项 nice-to-have。14 commits（bd471b3..c777c4f）+ 1 commit PLAN_v2 章节追加。regression 7/7 PASS, telling_rate 全部 ≤ 0.2 守住红线

### 🔄 待办（按优先级）

| 优先级 | 任务 | 何时做 |
|---|---|---|
| 🔴 P0 | yanyu-dialogue 在 Trae SOLO 实测触发率（20 条测试用例已在 SKILL.md 末尾）| 用户随时 |
| 🔴 P0 | 5-30 真朋友测试（≥3 人，至少 1 个非 AI 圈）grinding + fusion 各 1 次 | 5-30 卡死节点 |
| 🟡 P1 | 决策 6a 跨界 V1.5（embedding distance + analogical-mapping，3 天）| 5-30 之后 |
| 🟡 P1 | LocalFileBackend 接力：重构 yanyu-import / yanyu-dialogue 走 backend（~250 行改动）| 5-30 之前完成更好 |
| 🟢 P2 | Demo 视频（6 分钟，按 PITCH.md 四出彩点分段 + 8 秒沉默）| 6-08 |
| 🟢 P2 | 方法论 blog（"为什么 Socratic AI 必须基于你自己的知识库"）| 6-10 |
| 🟢 P2 | forum.trae.cn 发帖 + GitHub README 升级（按 DESIGN.md §2）| 6-12 |

---

## 7 大决策摘要（一句话版）

| 决策 | 一句话 | 详见 |
|---|---|---|
| 1 | **LocalFileBackend** 让砚友能在无飞书时跑（评审复现旁路 + 共享接口）| PLAN_v2 §决策 1 |
| 2 | **合并 grinding + fusion 为 yanyu-dialogue**（解决跨 Skill 路径 symlink 失效 + 共享 profile/scripts/人设）| PLAN_v2 §决策 2 |
| 3 | **叙事 reframe**：把 ChatGPT Study Mode 当"市场存在性官方背书"打，不再用"反 AI 摘要"旧叙事 | PITCH.md + PLAN_v2 §决策 3 |
| 4 | 5-30 真朋友测试提前到阶段 2 末（破"作者自评双重幻觉"）| PLAN_v2 §决策 4 |
| 6a | 跨界 V1.5：embedding distance + analogical-mapping 双阶段（V1 random.choice 是 placeholder）| PLAN_v2 §决策 6a |
| 6b | **LLM-judge eval + Bloom dashboard**（破"8 天 prompt 瞎调"+ demo 视频里的工程透明度杀手锏）| PLAN_v2 §决策 6b ✅ |
| 6c | **Pacing detection**（LearnLM 44.3% 编辑都在调 pacing → 砚友"不投降但会让步"）| PLAN_v2 §决策 6c ✅ |
| 6d | MathDial **focus/probing/telling/generic 四分类**（agent 内心打标 + judge.py 算 telling_rate）| PLAN_v2 §决策 6d ✅ |
| 7 | **hint laddering L1/L2/L3 + 砚石痕迹**（5-22 用户实测驱动: 反 scaffolding 不足 + 反 SDT 外驱反噬, 拒绝"阈值放答案"）| PLAN_v2 §决策 7 ✅ |

---

## 已知风险与陷阱（不要重新踩）

| 风险 | 状态 | 处理 |
|---|---|---|
| **44.3% 数据归因错误** | ✅ 已修复 | 真实来源是 [Eedi Substack 报告](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can)，不是 LearnLM Nov-25 paper（彩蛋：还有 19.5% 编辑用于情感缓冲，合计 63.8%）|
| **飞书 API 额度耗尽** | ⚠️ 5-22 ~ 5-31 期间 lark-cli 写操作可能 fail | 用户本月异常用量；月初 6-1 重置；LocalFileBackend 作为后备 |
| **跨 Skill 相对路径 symlink 后失效** | ✅ 已解决 | 合并 dialogue 消除了 fusion → grinding/scripts 引用 |
| **lark-cli auth scope 不足** | ⚠️ 偶发 | 跑 `lark-cli auth login --profile new_tenant --scope "<missing_scope>"` 增量授权 |
| **Trae SOLO 不自动重扫 ~/.agents/skills/** | ⚠️ 偶发 | 设置 → 技能与命令 → 关掉再开 `.agents` 开关；或重启 SOLO |
| **session limit 击穿 background agent** | ⚠️ 频发 | 每个 agent prompt 都要"高频写文件防止结果丢失"|
| **agent 引用编造数据风险** | ⚠️ 系统性 | 任何关键数据点上 demo / 答辩前必须 fetch 原始出处复核 |

---

## 关键决策铁律（违反 = 项目崩）

1. **agent 不替用户思考**（绝不给最小可行版本/失败模式/下一步验证假设，这些是用户该自己想的）
2. **每回合输出 ≤ 2-3 句**（pacing 模式下放宽到 3-4）
3. **D 阶段印证之前不贴原文**（用户自己悟到才能贴）
4. **fusion Step 5 仅复述 + 踢球**（不主动产出方案——决策 2 砍掉的核心）
5. **fusion 强制跨界算法保留**（这是砚友独占 moat，对应 PITCH.md 出彩点 3）
6. **不在物料里说**：反 AI 摘要 / 我们比 ChatGPT 强 / 革命性/颠覆性 / "苏格拉底 AI 第一个吃螃蟹"（地雷清单见 PITCH.md）
7. **每改 SKILL.md / references/**：跑 `cd yanyu-dialogue && python3 -m eval.regression` 验回归（telling_rate ≤ 0.2）

---

## 常用命令速查

### 部署 Skill 到 Trae SOLO / Claude Code

```bash
# Skill 已 symlink 到 ~/.agents/skills/，改本地文件即生效
ls -la ~/.agents/skills/ | grep yanyu

# 如果 Trae SOLO 没扫到新 skill：
# 设置 → 技能与命令 → 关掉再开 `.agents 技能目录` 开关
```

### 跑 eval（mock 模式不烧 token）

```bash
cd /Users/luojian/claudecode/forbiddenfruit/yanyu-dialogue

# 单句 Bloom's 打标
python3 -m eval.bloom_tagger --question "为什么不是 chunking？" --mock

# 对话 session 评分
python3 -m eval.judge --session session.json --mock

# 生成 dashboard PNG
python3 -m eval.dashboard --session session.json --output /tmp/dashboard.png --mock

# Prompt 回归（每次改 prompt 必跑）
python3 -m eval.regression --mock              # 默认 telling_rate ≤ 0.2
python3 -m eval.regression --threshold 0.15 --verbose
```

### 飞书 lark-cli 关键命令

```bash
# 微信文章爬取（产物 → /tmp/yanyu_scrape.json）
python3 yanyu-import/scripts/wechat_scrape.py "https://mp.weixin.qq.com/s/..."

# 飞书写入
lark-cli wiki +node-create --profile new_tenant --space-id 7638158720962202573 --title "..."
lark-cli docs +update --profile new_tenant --api-version v2 --doc <obj_token> --command overwrite --content @./xx.xml

# Bitable 搜索（必 --as bot）
lark-cli base +record-search --profile new_tenant --as bot --base-token RZeFbv8rCaoDoosMvqmcvBupnXg --table-id "文章索引" --json '{"keyword":"RAG"}'

# 身份说明
#   --as user：docs 编辑（bot 没文档权限）
#   --as bot：base 写（user 报 91403）
```

### LocalFileBackend 切换

```bash
# 默认 local（开箱即用）
export YANYU_BACKEND=local
python3 -c "from yanyu_core import load_backend; print(load_backend())"

# 切回飞书
export YANYU_BACKEND=lark
```

### Git workflow

```bash
cd /Users/luojian/claudecode/forbiddenfruit
git status
git add . && git commit -m "..." && git push
# GitHub: https://github.com/rol1an/forbidden-fruit
```

---

## 配置常量（硬编码在多处）

| 项 | 值 | 出现位置 |
|---|---|---|
| 飞书 profile | `new_tenant` | 所有 lark-cli 命令 |
| 知识空间 space_id | `7638158720962202573`（"大模型 Agent 面试"）| yanyu-import / yanyu-dialogue SKILL.md |
| 文章索引 Bitable | `RZeFbv8rCaoDoosMvqmcvBupnXg`（owner = user 604098）| 同上 |
| user open_id | `ou_2421972325f0fc0b8dfbe417776647d2`（用户 604098）| 仅历史命令 |
| user 数字 ID | `604098` | brand 内部识别 |

⚠️ Bitable app_token **不是 secret**（是飞书表的 unique identifier，有权限保护）。Fork 仓库的人需要自行替换为自己的 token。

---

## 与用户协作的偏好

来自用户的 working style：

- **诚实大于安抚**：当用户做得不好就直说，不要软化
- **决策记录优于重写**：原 plan 不动，叠加新决策到 v2/v3——时间戳历史本身有价值
- **中文 prose / 英文 jargon**（RRF / trace_id / Skills 协议 等术语不翻译）
- **短答案**：1-2 句完成的不要 3 段
- **不要尾部总结**："让我知道有什么需要" 类无内容句一律删

---

## 我（前一任 Claude）留给你的提示

1. **不要从头重新理解项目**——读 PITCH.md 就够了，深的去 PLAN_v2
2. **用户已经在 Trae SOLO 桌面端实测过架构**——A/B/C 全通过，不要再质疑兼容性
3. **22 天里最关键节点是 5-30 真朋友测试**——这是唯一能告诉项目成不成立的信号
4. **PITCH.md 是物料圣经**——任何对外内容都从那里取材，不要重新发明叙事
5. **如果飞书 API 报 99991663 之类的限额错误**：不是 bug，是 5-22~5-31 异常配额耗尽期。建议建议切 `YANYU_BACKEND=local`
6. **当用户说 "继续推进砚友" 时**：检查待办清单 → 选最高优先级动手；当用户说 "我有个想法" 时：先确认是不是 fusion mode 适用 → 再决策
