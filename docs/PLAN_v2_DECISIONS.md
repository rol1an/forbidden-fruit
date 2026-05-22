# PLAN v2 · 决策记录

> 2026-05-21 · 主指挥 agent · 基于 REVIEW_001 + BUSINESS 报告的方向修正
>
> 原 PLAN.md **不修改**——保留时间戳历史。本文是叠加的决策层。

---

## 触发原因（必读）

1. **REVIEW_001** 指出 3 个致命问题：
   - README 谎称"Trae CN 已验证兼容"（npx skills install target 不等于功能兼容）
   - 跨 Skill 相对路径 `../yanyu-grinding/scripts/profile_*.py` 在 symlink 部署后会崩
   - "用户悟到"主观成功标准 + 作者自评 = 双重幻觉

2. **BUSINESS** 报告的两大冲击：
   - **ChatGPT Study Mode（2025-07 上线、免费、8 亿周活）** 已经做了通用 Socratic AI 教学——砚友 innovation 上限被结构性压制
   - 砚友**真正独占的差异化只剩两条**：① 基于你自己的飞书知识库跑 Socratic（不是空白对话框）② 强制跨界 fusion
   - **冲一等奖 ROI 最高的补丁是 LocalFileBackend 最小版 3 天**，把 community value 从 3 拉到 5-6

---

## 决策 1 · 做 LocalFileBackend（最高 ROI 补丁）

### 为什么
- reviewer 给 community value: 3，扣分核心在"飞书锁死 = 9 成 Trae 评审复现不了"
- 商业 agent 测算：3 天工时把 community value 拉到 5-6 = 单位工时投入最高
- ROI 高于合并 grinding+fusion（后者解决工程坑但不解决评审复现问题）

### 范围（v1 最小可行）

支持的能力：

| 能力 | 飞书 backend | 本地 backend (v1) |
|---|---|---|
| 文章写入 | wiki + docs | `./yanyu_kb/articles/<slug>.md` + `<slug>.meta.json` |
| 文章读取 | docs +fetch | Path.read_text |
| 标签关联搜索 | base +record-search | 扫 meta.json + 标签集合交并 |
| 用户画像读写 | base +record-search/upsert | `./yanyu_kb/profiles/<user_id>.json` |
| 双向链接 | callout + append | 在 markdown 末尾用相对链接 |

**v1 不做**：
- 知识图谱可视化（飞书有现成 UI，本地版用 README 文字说明 v2 再做）
- 全文搜索（本地版 v1 用 ripgrep 兜底）
- 多用户隔离（本地版假定单用户）

### 接口设计

```python
# yanyu_core/backend.py（新建，三个 Skill 共享）
from abc import ABC, abstractmethod

class Backend(ABC):
    @abstractmethod
    def write_article(self, doc: Article) -> str:
        """返回文档 URL/path"""

    @abstractmethod
    def read_article(self, ref: str) -> Article: ...

    @abstractmethod
    def search_related(self, tags: list[str], min_overlap: int = 2) -> list[Article]: ...

    @abstractmethod
    def append_xref(self, target_ref: str, xref_html: str) -> None: ...

    @abstractmethod
    def read_profile(self, user_id: str) -> dict | None: ...

    @abstractmethod
    def upsert_profile(self, user_id: str, fields: dict) -> None: ...

class LarkBackend(Backend): ...        # 包装 lark-cli 调用
class LocalFileBackend(Backend): ...   # 纯 Python stdlib + Path
```

Skill 入口通过环境变量选 backend：`YANYU_BACKEND=lark|local`（默认 local——保证非飞书用户开箱即用）。

### 排期（3 天）

| 子任务 | 工时 |
|---|---|
| 抽 Backend 接口 + 重构 LarkBackend 包装现有 lark-cli 调用 | 1.0 天 |
| LocalFileBackend 实现 + 单元测试 | 1.5 天 |
| README 加"非飞书用户：5 分钟 quick start" + demo 视频脚本里加本地模式片段 | 0.5 天 |

**插入位置**：阶段 1 末（PLAN.md 原 5-25 ~ 5-28），与 yanyu-import 端到端验证并行。

---

## 决策 2 · 合并 yanyu-grinding + yanyu-fusion 成 yanyu-dialogue

### 为什么
- reviewer 工程角度：跨 Skill 相对路径 symlink 后失效
- 设计角度：grinding 和 fusion 本质是同一个对话引擎的两种 mode（共享 profile schema + 共享 scripts + 共享"绝不替用户思考"人设）
- 简化 prompt 维护负担 → 8 天调优窗口更容易调到位
- 商业 agent 也同意 reviewer 这条

### 改动清单

```
yanyu-dialogue/                    # 新建（合并 grinding + fusion）
├── SKILL.md                       # ≤600 行（两个 mode 工作流共一份）
├── references/
│   ├── socratic-method.md         # 原 grinding/
│   ├── anti-laziness-templates.md # 原 grinding/
│   ├── cross-domain-algorithm.md  # 原 fusion/
│   ├── devils-advocate-prompts.md # 原 fusion/
│   ├── profile-schema.md          # 共享
│   └── mode-selection.md          # 新：description 命中后怎么决定走 grinding 还是 fusion mode
└── scripts/
    ├── profile_read.py            # 原位置不变
    ├── profile_write.py           # 原位置不变
    └── profile_init.py            # 原位置不变
```

合并后 description（两组关键词共一份）：

> 当用户想深度学习已入库飞书/本地知识库的文章/主题，希望被苏格拉底式提问引导自己悟到答案（**研磨模式**）；或者抛出模糊创意/困惑，希望通过跨界强制碰撞 + devil's advocate 质疑收敛创新点（**研创模式**）时使用。两种 mode 由用户输入自然语言自动选择（"深挖/研磨/学透" → 研磨；"创意/跨界/碰撞" → 研创）。触发词：研磨、深挖、苏格拉底、被问住、自己想、学透、跨界、碰撞、灵感、收敛、devil's advocate、质疑我、砚友、yanyu-dialogue。

### 砍 fusion Step 5 喂答案

原 yanyu-fusion/SKILL.md Step 5 给"最小可行版本 / 失败模式 / 下一步验证假设"三段大纲——**砍掉**。改为：

```text
Step 5 收敛后：仅复述用户自己已经说出来的内容（"你刚才说的是：……"），最多加 1 句"你下一步想验证什么？"——把球踢回去。不主动产出方案。
```

理由：摩擦理论铁律——agent 接手扩展 = 摩擦消失。

### 排期（2 天）

| 子任务 | 工时 |
|---|---|
| 合并 SKILL.md + 写 mode-selection.md + 砍 Step 5 喂答案 | 1.0 天 |
| 测试两个 mode 切换的 description 触发率（10 条用户输入 × 2 mode = 20 测试用例）| 1.0 天 |

**插入位置**：阶段 2 开头（PLAN.md 原 5-26 ~ 5-27），在 grinding 8 天 prompt 调优窗口之内。

### 旧目录处理

`yanyu-grinding/` 和 `yanyu-fusion/` **物理保留**但只放一个 README 指向 `yanyu-dialogue/`，方便已经 follow 旧文档的人找过来。GitHub 仓库里两个旧目录不会被 npx skills install。

---

## 决策 3 · 叙事 reframe：把 ChatGPT Study Mode 当"市场存在性的官方背书"打

### 重大思考更新（用户主导）

**旧框架**（被动防御）：Study Mode 是威胁，砚友要避其锋芒
**新框架**（主动利用）：**Study Mode 是 OpenAI 亲自下场为"反喂答案 / 智力摩擦"这个市场做的背书**——荒野概念让评委怀疑市场存在，官方下场反而证明高级感

砚友不去碰瓷 OpenAI 全能，而是用 **飞书 CLI + 本地知识库** 的独占优势打它**绝对做不到**的降维出彩点。

### 四大降维出彩点（详细落地见 `PITCH.md`）

1. **私有知识库"物理占有权" vs 阅后即焚聊天框** — Study Mode 聊完知识死在历史记录，砚友帮你建数字书院
2. **Bitable 活体画像 vs 黑盒 Memory** — Study Mode Memory 不可观测，砚友画像可视化 + 可干预 + 可逆向吸纳用户金句
3. **yanyu-fusion 强制跨界碰撞** — OpenAI 严合规不敢做"具身智能 × 中医针灸"这种戏剧性认知冲突，砚友敢
4. **工程极简主义** — 不卷大模型底座，纯 Trae SOLO Skill + lark-cli 撬动飞书生态

### 物料落地规则

所有物料（README / 论坛帖 / demo 视频 / 答辩话术）**统一从 `PITCH.md` 取材**——不在别处重新发明叙事。

| 物料 | 取材自 PITCH.md 的章节 |
|---|---|
| README hero | "Ultimate Pitch" 段 + 四大出彩点 hero 一句话 |
| README §4-6 | 四大出彩点的"物料落地点"小节 |
| forum.trae.cn 发帖标题 | "为什么我让 AI 把具身智能跟中医针灸塞在一起逼问我" |
| demo 视频 6 分钟脚本 | 四大出彩点各 1 分钟 + 8 秒沉默 + ChatGPT 对比海报 |
| 答辩 Q&A | PITCH.md §"答辩 Q&A 预演" 5 个问题 |
| 方法论 blog | "为什么 Socratic AI 必须基于你自己的知识库（而不是 OpenAI 的）" |

### 英文产品名

**砚友 (InkMate)**——`InkMate` 作为英文 fallback 正式纳入 brand kit。所有 README / 论坛 / demo 英文字幕用 `InkMate`，中文场景用 `砚友`。

### 不能说的话（地雷清单）

- ❌ "我们比 ChatGPT 强"——对标可以，碾压姿态不专业
- ❌ "反 AI 摘要"——Study Mode 已抢，不要再用
- ❌ "苏格拉底 AI 第一个吃螃蟹"——前面有 Study Mode/Khanmigo/LearnLM
- ❌ "革命性""颠覆性"——评审听烦了

### 边界声明（防止内部矛盾）

**决策 2 砍 fusion Step 5 喂答案** 与 **出彩点 3 强制跨界碰撞是爆点** 不冲突：
- 砍的是 Step 5「agent 接手扩"最小可行版本 / 失败模式 / 下一步验证"大纲」
- 保留并强化的是 Step 1-4「跨界强制碰撞 + devil's advocate 质疑」
- 摩擦理论铁律：agent 制造摩擦但不替用户思考

---

## 决策 4 · 3 个真朋友测试提前到 5-30（reviewer + 商业一致建议）

原 PLAN 阶段 5 才让朋友试用。提前到阶段 2 结束（5-30）。

理由：22 天里**唯一能告诉你产品到底成不成立的信号源**。等到 6-10 才测，已经来不及调 prompt。

**测试设计**：3 个朋友（**至少 1 个非 AI 圈**），各做 1 次 yanyu-grinding 研磨对话 + 1 次 yanyu-fusion 研创对话。要求他们填一份 5 题问卷：
1. 你被问住过吗？被问住时是什么感觉？
2. agent 拒绝直接给答案，你想砸键盘吗？
3. 最后你有"我悟到了"的瞬间吗？发生在哪一轮？
4. agent 的提问，有没有让你想到自己之前没想过的角度？
5. 如果朋友跟你描述这个产品，你会推荐给谁？

---

## 决策 5 · 补未实现文件

reviewer 指出的"已引用但未实现"清单（除已经修的 4 个）：

| 文件 | 何时补 |
|---|---|
| `yanyu-grinding/references/description-tuning-grinding.md` | 阶段 2 grinding 调优开始前——可以复用 yanyu-import 的 description-tuning.md 加几条 grinding-specific 例子，30 分钟 |
| `yanyu-import/scripts/lark_oapi_fallback.py` | 阶段 0 摸底如果发现 Trae SOLO 不能调 shell 才补 |

---

## 修订后的关键日期表

| 日期 | 里程碑 | 状态 |
|---|---|---|
| 5-21（今天）| 仓库骨架 + 3 SKILL + 1 篇真实文章 import demo | 🟢 进行中 |
| 5-22 | Trae SOLO 桌面端摸底 + Hello World Skill 跑通 | 🔵 阶段 0（待用户做）|
| 5-25 | yanyu-import 端到端 5 篇 + LocalFileBackend 接口抽象完 | 🔵 |
| 5-28 | LocalFileBackend 实现 + 端到端跑通双后端 | 🔵 |
| 5-29 | yanyu-dialogue 合并完成 + 砍 fusion Step 5 | 🔵 |
| **5-30** | **3 个真朋友测试 ⚡ 全项目最关键节点** | 🔵 |
| 6-02 | grinding mode prompt 调到合格（朋友测试反馈 in） | 🔵 |
| 6-05 | fusion mode 调通 + 跨界算法 V2（如果技术调研 agent 给方案）| 🔵 |
| 6-08 | Demo 视频录制 | 🔵 |
| 6-10 | 方法论 blog 写完 + README 头图 + DESIGN.md 落地到实物 | 🔵 |
| 6-12 | GitHub public + forum.trae.cn 发帖 | 🔵 |

---

## 决策 6 · 技术调研驱动的具体升级（基于 TECH_RESEARCH.md）

技术调研给了 6 个 actionable 升级方向，按 ROI 排序挑 4 个必做、2 个降级 v2 backlog。

### 6a · 跨界 V1.5：embedding-distance + analogical-mapping 双阶段（**必做 · 3 天**）

**为什么**：砚友相对 Study Mode 真正的 moat 就是跨界 fusion。V1 `random.choice` 距离 SOTA 太远；Gentner SME systematicity 与 Fauconnier 4-space 学术锚点明确；3 天可落地。Concept Vectors 论文警告 LLM 对抽象关系无稳定内部表示——必须显式 prompt 引导用户做 structure mapping。

**改动**：`yanyu-fusion`（合并后是 `yanyu-dialogue` 的 fusion mode）的 `cross-domain-algorithm.md` V1 手写簇 + random，升级为：
- 离线：用 sentence-embedding（Anthropic `claude-embed` 或 OpenAI `text-embedding-3-small`）对所有 Bitable 标签做向量化
- 在线：抽 A 时按用户 `domain_familiarity_tags` 抽一个已熟悉的；抽 B 时按"与 A 余弦距离 ≥ 0.6 + 用户陌生"过滤后加权随机
- prompt 显式 generic-space 提问（让用户自己说"A 和 B 在什么抽象层面上结构相似"），不让 LLM 自己脑补

**插入位置**：阶段 3（PLAN.md 原 6-03 ~ 6-05），与 fusion mode 调优并行。

### 6b · LLM-judge 自动评估 + Bloom's dashboard（**必做 · 3 天**）

**为什么**：REVIEW_001 "没自动化 eval = 8 天瞎调"+"作者自评双重幻觉"两大致命问题的解药。**Khanmigo 自己 pre-post test 都没显著差异**（TECH_RESEARCH §6 实证）——证明纯 learning gain 路径行业内都做不出来，**砚友做工程透明度 dashboard 反而是 Study Mode 没有的杀手锏**。

**改动**：新建 `yanyu-dialogue/eval/`：
- `judge.py`：LLM-judge 三维度（telling rate / probing depth / aha-moment confidence）
- `bloom_tagger.py`：自动把每轮提问按 Bloom's taxonomy（记忆/理解/应用/分析/评价/创造）打标
- `dashboard.py`：跑完一次对话生成 Bloom's 饼图 + telling rate 折线 + 知识点 checkbox（matplotlib，保存为 PNG）
- `regression.py`：5 条固定 prompt 输入跑回归，给 prompt 调优一个可观测指标

**这个 dashboard 直接放 demo 视频里**——让评审看到"砚友比 ChatGPT Study Mode 多了工程透明度"，是 community value 杀手锏。

**插入位置**：阶段 2 开头（5-25 ~ 5-27），先于 grinding prompt 调优——让调优有数据驱动。

### 6c · pacing detection + telling move 例外（**必做 · 0.5 天**）

**为什么**：Eedi/LearnLM 真实 trial 实测 **人类老师 44.3% 编辑都在调 Socratic pacing + 19.5% 加情感缓冲**（合计 63.8% 在调"AI 体感"，[Eedi Substack 报告](https://eedi.substack.com/p/ai-empowers-the-teacher-so-they-can)）——砚友"绝不投降"+"绝不直接给答案"硬规则会让用户 frustrated。MathDial 证明 telling move 在解释陌生术语场景是正确策略，禁掉它会让对话卡死。

**改动**：`yanyu-dialogue/SKILL.md` 工作流增加：
- 用户连续 ≥2 轮简短回复（≤10 字）或出现情绪词（"烦/烦人/算了/走了"）→ 降密度（每两轮才追问一次，中间用 telling move 解释陌生术语）
- 出现陌生术语且用户明确问"什么是 X" → 允许 telling，但用 ≤ 1 句话解释完后立刻反问

砍 `anti-laziness-templates.md` 的"绝不投降"绝对化措辞，改为"由 pacing 模型决定"。

### 6d · MathDial teacher-move 四分类做 agent 自评（**必做 · 1 天**）

**为什么**：砚友 SKILL.md 5 阶段（A-E）是流程不是可观测 move 类型。MathDial 的四分类（**focus / probing / telling / generic**）有学术依据 + 可直接做 LLM-judge 评估维度。

**改动**：
- `socratic-method.md` 增加 §4 "teacher-move 四分类"
- 每轮 agent 输出时在内心打标（focus / probing / telling / generic），不输出给用户但记到 session.json，喂给 6b 的 judge.py
- `judge.py` 用 move 分布算 telling-rate 等指标

### 降级为 v2 backlog（不做）

| 6e Memory Tool 协议升级 | 2 天 | 吃 Anthropic 官方话语红利，但不改产品本质，v2 再做 |
| 6f Devil's Advocate 多 agent judge | 1 天 | 决策 2 砍 fusion Step 5 已部分解决"自我说服"风险，剩余风险走 v2 |

---

## 修订后的工时分配（22 天总账）

| 类别 | 工时 | 已纳入决策 |
|---|---|---|
| LocalFileBackend（决策 1）| 3 天 | ✓ |
| 合并 yanyu-dialogue（决策 2）| 2 天 | ✓ |
| 跨界 V1.5（决策 6a）| 3 天 | ✓ |
| LLM-judge eval + Bloom dashboard（决策 6b）| 3 天 | ✓ |
| pacing + telling（决策 6c）| 0.5 天 | ✓ |
| MathDial teacher-move（决策 6d）| 1 天 | ✓ |
| **核心引擎打磨 + Prompt 调优** | **5 天**（剩余）| —— |
| 真朋友测试（决策 4）| 1 天 | ✓ |
| Demo 视频 + README + 方法论 blog | 2 天 | —— |
| 仓库初始化 / 修 bug 等已完成项 | 1.5 天 | 已发生 |
| **合计** | **22 天** | 100% |

**警告**：Prompt 调优只剩 5 天，必须靠 6b 的 LLM-judge eval 数据驱动调优（避免瞎调）。如果 6b 落地不顺，立即砍 6c+6d 把那 1.5 天还给 prompt 调优。

---

## 整合到关键日期表

| 日期 | 里程碑（含本轮新增） |
|---|---|
| 5-21（已发生）| 仓库骨架 / 3 SKILL / 1 篇真实 import / 6 个 agent 完成首轮 |
| 5-22 | Trae SOLO 摸底（用户实测）|
| 5-25 | yanyu-import 5 篇入库 + LocalFileBackend 接口抽象 |
| 5-27 | LocalFileBackend 实现完 + LLM-judge eval 框架（6b）|
| 5-28 | 合并 yanyu-dialogue 完成 + pacing detection（6c）+ teacher-move 分类（6d）|
| **5-30** | **3 个真朋友测试 ⚡ 全项目最关键节点** |
| 6-02 | grinding mode prompt 调到合格（用 judge.py 跑回归）|
| 6-05 | fusion mode 跨界 V1.5（6a）调通 |
| 6-07 | demo dashboard 生成 + 录视频 |
| 6-09 | 方法论 blog 写完 + 二轮 reviewer 评估 |
| 6-12 | GitHub public + forum.trae.cn 发帖 |

---

## 二轮 reviewer 评估时机

**5-30 真朋友测试后** + **6b LLM-judge eval 第一次跑完** → 派二轮 reviewer，让它评估：
- 三个致命问题是否真的解决了
- pacing/teacher-move/V1.5 三个升级是否真的提升了对话质量
- 22 天剩余 12 天给出 final 冲刺建议

---

## 决策 7 · hint laddering + 砚石痕迹（用户反馈驱动 · 5-22 当日落地）

> 2026-05-22 · 真实用户实测反馈触发的非计划决策。一气呵成 P0 14 个 commit 入库, regression 7/7 PASS。

### 触发原因

5-22 用户在 Trae SOLO 桌面端**实测**砚友后给出两条反馈：

1. **scaffolding 不足**：研友提问时给的提示太少；用户被卡住时**绕开砚友**自己去飞书查阅文档再回来答 → 研磨摩擦被绕过
2. **缺成就感 + 过程漫长**：整个使用过程缺乏 small win；用户提议"进度条 + 80-100% 阈值触发放答案"

### 用户提议"阈值放答案"的风险（不可采纳）

直接击穿三处：

- agent 主动给答案 = 破 telling_rate ≤ 0.2 红线（铁律 1, 4）
- 外驱挤压内驱（Deci & Ryan 1999 meta-analysis 实证）
- 剥夺 D 阶段 aha-moment 所有权（"我自己悟到了" 变成 "系统判定我合格"）

### 范围（一气呵成 P0, 1 天内完成）

**A · scaffolding hint laddering**（响应反馈 1）

三档脚手架，区分于 anti-laziness（态度问题）和 pacing（情绪问题）。优先级 ladder > anti-laziness, pacing 并联生效：

| 档位 | 给什么 | 打标 |
|---|---|---|
| L1 Focus | 位置 + 类型 | `move=focus`, `ladder_level=1` |
| L2 Recall trigger | 反直觉锚点 + **中文范畴弱形状**（词性 / 侧 / 关系） | `move=focus`, `ladder_level=2`, 必填 `inferred_user_default` |
| L3 Open original | 允许用户去飞书查阅 30 秒, 回来必须**自己复述**, 单 session 上限 1 次 | `ladder_level=3` |

**关键设计**（经 reviewer C2 修订）：

- L2 形状提示**仅允许中文范畴**（「是动词还是名词」「是用户侧还是 agent 侧」「跟 X 同一侧还是反侧」）
- **禁止英文字母数 / 缩写位数 / 首字母**——在专业语境基本锁定答案（击穿 telling 红线 + 中文对话语言断裂）
- L3 把用户"绕路看文档"**正名为合法 ladder**, 加"自己复述"约束确保不退化为搬运

**B · 砚石痕迹 informational feedback**（响应反馈 2）

对话内嵌轻量 callout，给"已走多远"不给"还差多少"：

- MVP 触发：stage transition（A→B / B→C 等）+ every-5-rounds 强制盘点
- pacing 模式下降密到 every-8-rounds
- 格式：`🪨 第 X 阶段 → 第 Y 阶段。<情感锚点观察>。` 或 `📿 砚石痕迹：<observation>。`
- **禁止**：百分比 / 进度条 / "还差多少" / "Bloom 第 X 层"（jargon leak）/ cheerleading 腔
- 高频失败处理：用户问「我现在到第几了」→ 反问「你刚才那一步比 3 轮前是更深还是更浅？」
- **P1 闸门**：Bloom 跨级跃升触发必须先通过 `eval/bloom_agreement.py` agreement ≥ 85%（20 条人工标注 fixture 已建好）

### 改动清单（14 个 commit, bd471b3 → c777c4f）

| 文件 | 改动 |
|---|---|
| `yanyu-dialogue/references/hint-laddering.md` | **新建** (135 行, 决策 7 主协议) |
| `yanyu-dialogue/references/inkstone-trace.md` | **新建** (128 行, 砚石痕迹协议) |
| `yanyu-dialogue/SKILL.md` | 加 §3.x §3.y 挂载 + §3.y 高频失败处理 |
| `yanyu-dialogue/references/anti-laziness-templates.md` | 顶部加分流指引（能力问题→ladder / 态度问题→本文件）|
| `yanyu-dialogue/references/teacher-move-classifier.md` | 加 ladder 副标签契约 + 示例 schema 对齐 `role/content/move` |
| `yanyu-dialogue/eval/judge.py` | `_count_ladder` + L3 overuse 扣分 + `l2_missing` 软扣 + `_check_inkstone_repetition` |
| `yanyu-dialogue/eval/bloom_tagger.py` | 加 `chinese_label` 字段（触碰 / 看懂 / 拆解 / 重构 / 评判 / 创造）|
| `yanyu-dialogue/eval/fixtures/bloom_agreement_set.json` | **新建** (20 条砚友风格人工标注, stratified) |
| `yanyu-dialogue/eval/bloom_agreement.py` | **新建** (CLI 跑 agreement test, ≥85% 闸门) |
| `yanyu-dialogue/eval/regression.py` | `_mock_session` 支持 `l1/l2/l3` 标识 + `overuse_ok` 验证 |
| `yanyu-dialogue/eval/fixtures/regression_set.json` | 加 2 条 ladder fixture 覆盖决策 7 代码路径 |

### Reviewer 三项 critical 修复（commit f6f377e / 96797ad / 48b7ede）

- **C1**：teacher-move-classifier 示例 schema 从 `speaker/text/agent_move` 对齐 `role/content/move`（否则 ladder 监控空转）
- **C2**：L2 形状提示删强保弱（中文范畴），守住 telling_rate + 语言一致性
- **C3**：regression 加 2 条 ladder fixture，决策 7 代码路径首次被覆盖

### Nice-to-have 四项（commit 085790c / b58463f / c777c4f）

- N1：`l2_missing_default > 0` → telling_rate 软扣 0.05 / each（agent 盲猜反直觉锚点 ≈ telling 行为）
- N2：bloom_003 标注 remember → understand（"作者用 ColBERT 还是另一种"有比对成分）
- N3：`_check_inkstone_repetition` 检测同 callout 出现 ≥3 次 = prompt 失败信号
- N4：SKILL.md §3.y 升"我现在到第几了"高频失败处理

### 排期与最终验证

| 阶段 | 工时 | 状态 |
|---|---|---|
| P0 全部（主线 8 项 + reviewer 3 项 + nice-to-have 4 项）| 1 天 | ✅ 5-22 当日完成 |
| P1 Bloom 跨级跃升触发（依赖 `bloom_agreement.py` ≥85%）| 0.5 天 | 🔵 5-30 之后 |
| P2 研磨结晶卡（Anki SRS 哲学路线, 长程沉淀感）| 3-4 天 | 🔵 5-30 朋友反馈后决定 |

**最终回归**：`python3 -m eval.regression --mock --verbose` 7/7 PASS，telling_rate 全部 ≤ 0.2 守住红线。新增的 `ladder_normal_l1_l2` 和 `ladder_l3_overuse_scaffolding_fail` 两条 fixture 真触发了 `_count_ladder` + `overuse_warning` + `probing_depth × 0.7` 扣分逻辑。

### SOTA 锚点

- **Wood, Bruner & Ross (1976)** scaffolding 6 functions —— *frustration control* + *marking critical features* 是 hint laddering 的设计根据
- **Vygotsky ZPD** —— hint 必须落在最近发展区内；"换更小的问题"是问题降级而非 hint
- **MathDial focus move**（[arXiv:2305.14536](https://arxiv.org/abs/2305.14536)）—— telling 和 probing 之间存在不击穿红线的合法 hint 形态
- **Deci, Koestner & Ryan (1999)** 128 项实验 meta-analysis —— informational feedback **不构成**内驱挤压, 砚石痕迹只显示"已走多远"恰好落在 informational 一侧, 理论合法
- **Khan Academy Mastery Levels** —— named tier 替代 raw % 行业 SOTA 验证；砚友 Bloom 中文转译表（触碰/看懂/拆解/重构/评判/创造）借鉴这条路径
- **Michael Nielsen, Augmenting Long-term Memory**（[augmentingcognition.com/ltm.html](https://augmentingcognition.com/ltm.html)）—— 进度感可来自沉淀物积累而非 UI feedback（启发 P2 研磨结晶卡）
- **Eedi/LearnLM 报告**——44.3% pacing + 19.5% 情感缓冲 = 63.8% 真人编辑量, 砚石痕迹 callout 必须有情感锚点
- **arXiv:2511.10903** —— GPT-4 在 Bloom 6 层 accuracy 0.72-0.73, 砚友 agreement ≥ 85% 阈值有意拔高一截（Bloom 误判信任崩盘代价 > telling 红线违规）

### 决策 7 与其他决策的关系

- **决策 2**（合并 yanyu-dialogue）：完全兼容, 在合并后的 SKILL.md 上加 §3.x §3.y
- **决策 6b**（LLM-judge eval + Bloom dashboard）：强复用基建, 加 `_ladder_stats` + `_inkstone_stats` 字段, dashboard P1 可视化复用
- **决策 6c**（pacing detection）：优先级 ladder > anti-laziness, pacing 并联生效（pacing 模式下 ladder 节奏放慢一档）
- **决策 6d**（MathDial 四分类）：L1/L2 计入 focus, L3 单独副标签——首次让"内心打标 focus 类目"有实际使用场景

### 关键文件链接

- 主协议：[`../yanyu-dialogue/references/hint-laddering.md`](../yanyu-dialogue/references/hint-laddering.md)
- 砚石痕迹：[`../yanyu-dialogue/references/inkstone-trace.md`](../yanyu-dialogue/references/inkstone-trace.md)
- 挂载点：[`../yanyu-dialogue/SKILL.md`](../yanyu-dialogue/SKILL.md) §3.x §3.y
- 评估契约：[`../yanyu-dialogue/references/teacher-move-classifier.md`](../yanyu-dialogue/references/teacher-move-classifier.md) §Ladder level 副标签
- P1 闸门：[`../yanyu-dialogue/eval/bloom_agreement.py`](../yanyu-dialogue/eval/bloom_agreement.py)
