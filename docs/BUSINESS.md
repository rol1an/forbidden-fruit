# 砚友 · 商业可行性与赛事得分评估

> 2026-05-21 · business-agent · 给作者的诚实评估，不替项目说好话

---

## 1. 目标用户画像

砚友定位（反 AI 摘要 + Socratic + 强依赖飞书 + Skill 形态）一上来就把用户池切得很窄。按"产品形态适配度 × 付费意愿 × 触达难度"过一遍：

| 细分 | 适配度 | 付费意愿 | 触达难度 | 评估 |
|---|---|---|---|---|
| K12 学生 | 高 | 家长付（Khanmigo $4/月已证明）| 极高（不在飞书生态）| 砚友够不到 |
| 大学生 / 研究生 | **中-高** | 低（白嫖 ChatGPT Study Mode 免费版）| 中（部分高校用飞书）| 主战场之一 |
| 知识工作者 / 内容创作者 | 中 | 中（Notion / Heptabase 已证明 $8-12/月可付）| 低（飞书个人版 ~1200 万 MAU）| **最 ready** |
| 面试备考者 | 高 | 高（地里 / 三节课等付费意愿强）| 低-中 | 高单价小池子 |
| 飞书企业内培训 | 中 | **高**（B 端预算大）| 低（已在飞书）| 隐藏机会 |

**最 ready 的细分是"已在飞书生态的知识工作者 + 重度内容创作者"**——他们已经为飞书付了沉没成本，对 Notion AI / Heptabase 类工具有付费习惯，且对"AI 让人变笨"有切身焦虑（创作者最怕自己的文风被 ChatGPT 平滑掉，参见爱范儿《我怀念我写得很烂的时候》）。但这个池子能精准触达砚友的，乐观估算也就万级量级。面试备考是 niche 但单价能撑到 ¥99-299，可作 v1.5 切入。

**推荐行动**：v1 demo 拍内容创作者画像（"导入收藏的公众号文章 → 砚友逼你说出自己的观点而不是复读"），赛后联系 1-2 个飞书重度用户的知识博主做共创案例。

---

## 2. 市场需求验证

"AI 让人变笨"焦虑是真实的，且 2025-2026 出现了顶级背书：

- **MIT Media Lab 2025-06 论文**《Your Brain on ChatGPT》用 EEG 量化证明：ChatGPT 组前额叶皮层活动显著低于 Search 组与 Brain-only 组，且"用得越多越懒"——这是砚友最锋利的叙事弹药。
- arXiv 2507.00181《ChatGPT produces more "lazy" thinkers》独立复现了 cognitive offloading 效应。
- 国内知乎、爱范儿、新华网均有大量讨论（"AI 让人变笨吗"是 2025 持续热点），但**讨论多 ≠ 付费意愿强**——绝大多数是焦虑型阅读，没人为"反 AI 摘要"产品付过钱。

**真需求强度评估**：
- **认知需求**：强。MIT 论文 + Time 报道 + 国内主流媒体已经把"AI 让人变笨"灌进了知识工作者的脑子。
- **付费需求**：弱-中。OpenAI 2025-07-29 上线的 **ChatGPT Study Mode 完全免费**（Free / Plus / Pro / Team 都给），Socratic + scaffolded + knowledge check 三件套已就位。砚友的"反 AI 摘要"叙事在产品层被 OpenAI 官方提前抢占。
- **行为需求**：很弱。"我应该让自己思考更多"和"我会切到一个故意让我难受的工具"之间隔了一条用户行为鸿沟——参考 Anki 用户基数对比 Notion 就明白。

**推荐行动**：发帖叙事不要硬碰 ChatGPT Study Mode，转而打"在你自己的知识库（飞书 wiki）上跑 Socratic，而不是在 OpenAI 的空白对话框里"——把战场从"通用 Socratic"切到"个人知识库 Socratic"，这才有差异化空间。

参考链接：
- [MIT Media Lab：Your Brain on ChatGPT](https://www.media.mit.edu/publications/your-brain-on-chatgpt/)
- [arXiv 2507.00181：ChatGPT produces more "lazy" thinkers](https://arxiv.org/pdf/2507.00181)
- [OpenAI Study Mode 官方发布](https://openai.com/index/chatgpt-study-mode/)
- [知乎：没错，AI 会让我们变笨，但是还有救](https://zhuanlan.zhihu.com/p/79062943032)
- [爱范儿：ChatGPT 三周年之际，我怀念我写得很烂的时候](https://www.ifanr.com/1647583)

---

## 3. 竞品分析

| 竞品 | 一句话特色 | 砚友的差异点能不能站住 |
|---|---|---|
| **ChatGPT Study Mode**（免费）| OpenAI 官方 Socratic + scaffolded + 知识检查，全平台 8 亿周活触达 | **站不住**。同样是 Socratic，对方免费 + 触达高 100 倍。砚友唯一差异是"基于你自己的飞书知识库"和"跨界 fusion"——必须把这个差异讲透 |
| **Khanmigo** $4/月 | Khan Academy 全学科 Socratic AI，K12 强 | 砚友不切 K12，错开 |
| **Notion AI** $10/月 | 笔记内总结 / 改写 / 问答（**给答案型**）| 差异点站得住——Notion AI 是答案机，砚友是反答案机 |
| **Heptabase** $11.99/月 | 视觉卡片白板做研究学习，无 AI | 差异点站得住——视觉派 vs 对话派 |
| **Obsidian + AI 插件** 免费-$8 | 本地优先 + Copilot/Smart Connections 插件 | **差异点危险**。Obsidian 社区已经有人写 Socratic prompt 模板，且本地优先击中隐私敏感用户 |
| **RemNote** Pro+AI $18/月 | 笔记 → 自动 flashcard + spaced repetition + AI tutor | 间接竞争。RemNote 走 Anki 路线（间隔重复），砚友走 Socratic 路线，可错开但 RemNote 更成熟 |
| **Anki + AnkiBrain** 免费 | 经典间隔重复 + ChatGPT 出题插件 | 间接竞争。Anki 用户群高度自虐，是砚友潜在用户但搬迁成本高 |
| **SocratiQ / Socratic Mind** 实验型 | 学术界 Socratic AI demo，arXiv 多篇 | 学术 demo，不是商业品。砚友比它产品化 |

**残酷结论**：砚友真正独占的差异点只有两条——① 基于**你自己的飞书知识库**做 Socratic（不是空对空），② **forced cross-domain association**（fusion 模式）。其中 ② 是真原创，但效果难复现；① 是工程绑定不是产品创新。

**推荐行动**：放弃和 Khanmigo / Study Mode 比 Socratic 引擎本身的深度（你拼不过 Khan Academy 的教学法团队），全力强化"个人知识库 + 跨界碰撞"这两条 moat，README 头图直接对标 Study Mode 截图做差异化海报。

---

## 4. 商业模式

按现实可行性排序：

| 模式 | 可行性 | 备注 |
|---|---|---|
| **开源 + GitHub stars / 论坛声量**（短期）| 高 | 当前阶段唯一现实路径。砚友是 Skill 包不是 SaaS，赛事和社区曝光是真 ROI |
| **飞书插件市场上架免费版 + Pro 订阅**（中期）| 中 | 飞书有应用市场，个人版 ~1200 万 MAU 是池子，但飞书插件付费转化率国内行业普遍 <1% |
| **¥59-99/月知识付费课程伴侣**（中期）| 中-高 | 把砚友打包给"得到 / 三节课 / 飞书课程"的课主，让他们的学员用砚友做课后内化。B2B2C 模式更现实 |
| **企业版 / 飞书企培 SaaS**（长期）| 中 | 飞书企业客户用砚友做新员工知识入职、技术分享后内化。客单 ¥3000-10000/年/团队，但销售周期长 |
| **个人订阅 $4-8/月**（参考 Khanmigo $4 / Notion $10）| 低 | 砚友差异化不够强支撑独立订阅。Khanmigo 有 Khan Academy 课程库，砚友没有自有内容库 |
| **API / Skill 协议授权**（远期）| 极低 | Anthropic Skills 是开源协议，没人会为 Skill 付授权费 |

**Khanmigo 定价锚点**：$4/月 / $44/年 / 家庭版覆盖 10 个孩子。**砚友的独立订阅没法对标这个价位**——Khanmigo 背后是 Khan Academy 全学科内容库 + 几十人教学团队，砚友的 Skill 包没有内容资产护城河。

**推荐行动**：放弃个人订阅幻想，**做开源 + 飞书企培 B2B 双轨**。短期通过赛事拿声量，中期主动接触 1-2 家用飞书的教培 / 咨询公司做定制案例（"用砚友帮你的咨询师消化客户访谈"），客单 ¥1-3 万。

---

## 5. 飞书强依赖的代价

REVIEW_001 给 community value 打 3 分的核心理由就是"飞书锁死 = 9 成评审复现不了"，这条必须算总账。

**当前依赖面**：
- **画像存储**：Bitable（替换需重写 profile_read/write.py）
- **知识库**：飞书 wiki + docs（替换需重写整个 yanyu-import 的 lark_write.sh）
- **运行时**：lark-cli / lark-oapi（替换需切到目标平台 SDK）
- **微信文章导入终点**：飞书 docs（替换需切到 Markdown / Notion API）

**抽象 storage 层的工时估算**（按主程序员效率）：

| 层 | 工作量 | 备注 |
|---|---|---|
| 定义 `StorageBackend` interface（read_profile / write_profile / write_doc / search_doc）| 0.5 天 | |
| FeishuBackend 实现（封装现有代码）| 0.5 天 | |
| LocalFileBackend 实现（profile 存 JSON，doc 存 Markdown 到本地文件夹）| 1-2 天 | 最快落地，覆盖 Obsidian + Logseq 用户 |
| NotionBackend 实现 | 3-5 天 | Notion API 限速 + 富文本 schema 复杂 |
| 各 Skill 改用 backend interface | 1-2 天 | 改 scripts 引用，SKILL.md 文案 |
| 文档 + backend 选择机制（env var or config）| 1 天 | |
| **总计** | **7-12 天** | LocalFile 最小版 3 天能跑通 |

**核心判断**：在 22 天 deadline 内补完抽象层来不及，**但 LocalFileBackend 最小版（3 天）必须做**，且在赛事提交前完成——这一条直接把 community value 从 3 分拉到 5-6 分，是 ROI 最高的单笔投入。Notion backend 留到 v2 赛后做。

**额外现实**：飞书个人版 ~1200 万 MAU 看似不少，但 Trae 全球累计 600 万用户 / 月活 1.6 万，**Trae 用户 ∩ 飞书重度用户**才是赛事评审的真实复现池子，估计两位数到三位数量级。这就是 community value 必然偏低的结构性原因。

**推荐行动**：今天就在 PLAN.md 里加阶段 0.5——"3 天做 LocalFileBackend，让 Skill 在没有飞书的电脑上也能跑"，**这是阻止 community value 翻车的最便宜手段**。

---

## 6. 短期赛事得分潜力

### 评审四维当前预估

基于 REVIEW_001 的基线 + 22 天剩余可行动作：

| 维度 | REVIEW_001 基线 | 22 天可达上限 | 一等奖所需 |
|---|---|---|---|
| innovation | 5 | **6-7** | 8+ |
| usability | 4 | **6-7**（加 LocalFileBackend）| 8+ |
| completeness | 6 | **7-8**（按 REVIEW 修 bug + 实现缺失文件）| 8+ |
| community value | 3 | **5-6**（去飞书锁 + 真朋友测试反馈）| 8+ |

### 合理预期档位

赛事档位（推测，未在官方页明确分级）：特等 / 一等 / 二等 / 三等 / 入围 / 落选

**砚友合理预期：二等到三等之间**，乐观情况摸到一等门槛。理由：

1. **innovation 上限被 ChatGPT Study Mode 卡住**——OpenAI 2025-07 已经把"Socratic AI"做成官方功能且免费，评审会问"为什么不用 Study Mode"，砚友需要把"个人知识库 Socratic + 跨界 fusion"的差异讲到评审听完就懂的程度。
2. **completeness 受 REVIEW_001 列出的 3 个 bug 拖累**（profile_write 不传 record_id / EmphasisCollector 嵌套 / wechat_scrape 无 timeout）——这些必须先修，否则演示翻车直接掉档。
3. **community value 是天花板**——飞书强依赖在 Trae 社区评审视角下天然刺眼，做 LocalFileBackend 是必须的。
4. **usability 实测会被"用户必须先有飞书 wiki 才能用"卡掉一档**。

### 冲一等奖需要补什么

按 ROI 排序：

1. **LocalFileBackend 最小版**（3 天，community value +2、usability +1）—— 最高 ROI
2. **修 REVIEW_001 列的 3 个 bug + 实现缺失的 profile_init.py / lark_oapi_fallback.py**（1-2 天，completeness +1）
3. **真用户测试 ≥3 人 × 1 次研磨，把"悟到"反馈截图放进 README**（提前到 5-30 前，usability +1，破"作者自评"质疑）
4. **方法论 blog 单独发**——"progressive disclosure 从静态文件扩展到动态对话状态"+ "摩擦理论"，独立成文比塞 README 强，**community value 评审会按可独立传播的内容资产打分**（+1）
5. **demo 视频里加一段"在没装飞书的电脑上用 LocalFileBackend 跑"**——直接堵住评审"飞书锁死"的嘴
6. **删 yanyu-fusion 或合并进 grinding**（REVIEW_001 也建议过）——三个半成品 Skill 不如两个完整的 Skill，completeness 评审更吃硬指标

### 不推荐的行动

- 临阵增加视频源 / B 站抖音功能（范围爆炸，PLAN.md 已正确砍掉）
- 临阵转 Notion backend（工时不够）
- 临阵切换平台（Trae SOLO 是赛事硬要求，必须用）

### 一句话评估

**砚友的产品定位足够有想法，但与 ChatGPT Study Mode 的正面竞争 + 飞书锁死 + 22 天 deadline 的复合压力下，二等奖是合理预期、一等奖需要严格执行上面的 6 条补丁、特等基本不可能（特等通常给社区 high-leverage 工具，砚友不具备）。**

**推荐行动（终局）**：把 22 天剩余资源按 50% 砸 grinding 引擎打磨 + 30% 砸 LocalFileBackend + 20% 砸真用户测试和方法论 blog。三个 Skill 不要硬铺，必要时合并 grinding+fusion，集中火力。

---

## 引用与数据来源

- [Trae SOLO 技能创作赛官方帖](https://forum.trae.cn/t/topic/16860)
- [MIT Media Lab：Your Brain on ChatGPT](https://www.media.mit.edu/publications/your-brain-on-chatgpt/)
- [arXiv 2507.00181 cognitive engagement decline](https://arxiv.org/pdf/2507.00181)
- [OpenAI ChatGPT Study Mode](https://openai.com/index/chatgpt-study-mode/)
- [Khanmigo Pricing $4/月](https://www.khanmigo.ai/pricing)
- [RemNote Pricing Pro+AI $18/月](https://www.remnote.com/pricing)
- [Heptabase vs Obsidian 2026 对比](https://www.sollmannkann.com/project-management-and-notes/obsidian-vs-heptabase/)
- [知乎：AI 会让我们变笨吗](https://zhuanlan.zhihu.com/p/79062943032)
- [爱范儿：我怀念我写得很烂的时候](https://www.ifanr.com/1647583)
- [Trae 600 万开发者 / 1.6M MAU](https://www.geekpark.net/news/358722)
- [飞书 MAU ~1200 万估算](https://sino-manager.com/detail/9620)
- **未找到具体数据，建议人工调研**：飞书插件市场付费转化率、Trae 社区评审复现飞书 Skill 的实际比例、面试备考用户群对 Socratic 工具的付费弹性

---

## 附录 · 2026-05-21 用户主导的市场 reframe

> 原报告把 ChatGPT Study Mode 定性为"砚友 innovation 上限被结构性压制"——这个判断**部分错位**。本附录由用户主导修订，作为对原 §3 §5 §6 的补充而非替换（decision records over rewrites）。

### 核心 reframe

| 维度 | 原报告（被动防御视角）| 修订后（主动利用视角）|
|---|---|---|
| Study Mode 对砚友的意义 | innovation 上限被压制 / 抢通用赛道 | **OpenAI 亲自下场为"反喂答案 + 智力摩擦"市场做官方背书**——荒野概念会让评委怀疑市场存在性，官方下场反而证明市场高级感 |
| 答辩第一句 | 避开 Study Mode 比较 / 强调差异化 | **主动以 Study Mode 起头**："OpenAI 2025-07 证明了 Socratic AI 是终极解。但..."（把对手作背书 + 引出降维出彩点）|
| innovation 评分上限 | 6-7（被压制）| **7-8**（重新自评——四大降维出彩点中至少 2 条（活体画像、强制跨界）是 Study Mode 绝对做不到的）|

### 四大降维出彩点（详见 PITCH.md）

砚友相对 Study Mode 的真正壁垒，不是"我们也做 Socratic"，而是**做 Study Mode 不能做的事**：

1. **私有知识库的物理占有权 vs 聊天框阅后即焚** — Study Mode 没有 yanyu-import 这种"帮你建数字书院"的硬核底座
2. **Bitable 活体画像 vs 黑盒 Memory** — Study Mode 的 Memory 不可观测、不可干预；砚友的 Bitable 画像可视化、可改、可逆向吸纳用户方法论金句
3. **yanyu-fusion 强制跨界碰撞** — OpenAI 严合规不敢自带"具身智能 × 中医针灸"这种戏剧性认知冲突；砚友这种垂类工具有特权
4. **工程极简主义** — 不卷大模型底座，纯 Trae SOLO Skill + lark-cli 撬动飞书生态，Completeness 加分项

### 对原报告关键结论的修正

| 原报告 §X | 原结论 | 修订 |
|---|---|---|
| §3 竞品分析 | "ChatGPT Study Mode 站不住" → 推断 innovation 没空间 | "Study Mode 是市场背书"，innovation 空间反而**因为有官方加持而更安全** |
| §6 一句话评估 | "二等奖是合理预期" | **改为**："二等奖是保底，一等奖是合理目标，前提是 PITCH.md 四大出彩点在 demo 视频中 1 分钟内被看到" |
| §6 推荐行动终局 | "三个 Skill 不要硬铺，必要时合并 grinding+fusion 集中火力" | **强化**："必合并；并且 fusion 是杀手锏不能砍——OpenAI 不敢做就是我们最大的护城河" |

### 对赛事得分的复评

| 维度 | 原 22 天可达上限 | 修订后上限（基于本附录 reframe + 决策 6a/6b 落地后）|
|---|---|---|
| innovation | 6-7 | **7-8** |
| usability | 6-7 | 6-7（不变，LocalFileBackend 决策已纳入）|
| completeness | 7-8 | 7-8（不变）|
| community value | 5-6 | **6-7**（PITCH.md "中式数字书院"叙事 + 对标 Study Mode 差异化海报给社区传播力加分）|

四维全部 7+ 即一等奖门槛，砚友现在站在那条线上——**严格执行 PITCH.md 落地 + 决策 6a/6b 工程升级即可摸到**。

### 推荐行动（修订版）

砍掉原 §6 "残酷结论"的"特等基本不可能"——保留这条但加一条：**如果 PITCH.md 的 Ultimate Pitch 在评审 1 分钟内被传达成功 + Bloom dashboard demo 让评审看到工程透明度，特等不是不可能**——它取决于 Trae 评审是否真的有人愿意为"工程极简主义 + 中式数字书院"叙事买单。

