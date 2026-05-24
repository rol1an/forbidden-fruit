# 研磨结晶卡 · 决策 7 P2 Spike

> 2026-05-24 · **评估专用 spike, 不实施**。基于 5-22 用户反馈 2 + reviewer 调研 Nielsen 路线。
>
> 配套：[`PLAN_v2_DECISIONS.md`](PLAN_v2_DECISIONS.md) §决策 7 P2 / [`../yanyu-dialogue/references/inkstone-trace.md`](../yanyu-dialogue/references/inkstone-trace.md)

---

## 1. 背景与触发

**5-22 用户反馈 2** 拆成两层痛点：

| 层 | 痛点 | 现状 |
|---|---|---|
| 对话内 | 缺 small win, 不知道学到了什么 | ✅ 砚石痕迹 MVP 解决（stage transition + every-5-rounds callout）|
| 对话外 | 学完不知道沉淀去哪了, 7 天后忘光 | ❌ **本 spike 评估对象** |

**哲学锚点**：Michael Nielsen [Augmenting Long-term Memory](https://augmentingcognition.com/ltm.html) ——「进度感不必来自实时 UI feedback, 可以来自**沉淀物的积累**」。Anki SRS 哲学。

**PITCH.md 兼容性**：

- 强化 **出彩点 1**（私有知识库物理占有权 vs Study Mode 阅后即焚）—— 结晶卡是 Study Mode 物理上不可能做的（飞书 Bitable 私有库）
- 强化 **出彩点 2**（Bitable 活体画像 vs 黑盒 Memory）—— 用户能**看见、编辑、回放**自己的 aha-moment 卡片
- 不冲突任何决策铁律（agent 不替用户思考 / 不喂答案）—— 卡片是用户**自己悟到的内容**沉淀, agent 只负责检测时机 + 写入

## 2. 三个核心能力点（按工程难度排序）

### 2.1 aha-moment 检测（最难点）

**信号源 — 现状盘点**

`judge.py _stub_judge` 已有 `aha_moment_confidence` 字段：

```python
has_d = cov.get("D", 0) > 0          # D 印证阶段触达
has_e = cov.get("E", 0) > 0          # E 收尾阶段触达
aha = 0.6 if (has_d and has_e) else (0.3 if has_d or has_e else 0.0)
if has_d and has_e and last_user_len >= 40:
    aha = 0.75                        # 加用户复述完整度信号
```

**当前精度**：不调 LLM, 仅用 stage 标签 + 长度。**够用** for 单维度检测（D+E + 长复述 = 印证型 aha）。

**三类 aha-moment 该被分别检测**：

| 类型 | 信号 | 现状 | 检测难度 |
|---|---|---|---|
| **类型 1 印证型** | D 阶段贴原文 + E 用户复述 | ✅ judge.py 已有 | 低（已有 stage 标签）|
| **类型 2 反例型** | C 阶段用户**主动**提反例 / edge case | ❌ 缺信号 | 中（需新 prompt 判别）|
| **类型 3 跨界型** | fusion mode 用户连接 A/B 领域时的"哦"瞬间 | ❌ 缺信号 | 高（需 LLM-judge）|

**风险**（套用 5-24 学到的 [[llm-judge-multi-run-required]] 教训）：

- 类型 2/3 都需要 LLM-judge → 跟 bloom_tagger 同病：**单次跑不稳, mean ± std 估计不出来 5-30 之前来不及**
- 假阳性 = 用户复习无效卡片 → 卡片库污染 → **长期信任崩盘**, 比 P1 砚石痕迹误奖励更严重（因为长程沉淀）
- 类型 1 用 stage 标签 + 长度是 **deterministic**, 没有 LLM variance 问题

**Mitigation**：MVP 阶段**只做类型 1**, 完全不调 LLM。类型 2/3 列入 P3, 跟 P1 reasoner 工程债（JSON mode + N-shot majority vote）一起做。

### 2.2 Bitable 写入（最简单）

**yanyu-import 已有完整链路可复用**：

| 参数 | 复用值 |
|---|---|
| profile | `new_tenant` |
| base_token | `RZeFbv8rCaoDoosMvqmcvBupnXg`（同"文章索引"那张 base）|
| 命令 | `lark-cli base +record-upsert --as bot --base-token ... --table-id "研磨结晶卡"` |
| 权限 | 写 base 必须 `--as bot`, 读用 user/bot 都行 |

**结晶卡表 schema 草案**（10 个字段）：

| 字段 | 类型 | 含义 |
|---|---|---|
| 卡 ID | text (自增) | crystal_001 / crystal_002 ... |
| 创建日期 | date | session 结束时间 |
| 主题 | text | session.topic（已有字段）|
| 模式 | select | grinding / fusion |
| 用户原话 | long text | E 阶段用户复述的最后一句话 |
| 被问住的问题 | long text | agent 在 D 阶段印证前抛的最后一个问题 |
| agent 引导金句 | long text | session.json 里 probing 类 move 最长的一句 |
| 关联原文 obj_token | text | wiki node 链接 |
| aha 类型 | select | 印证型 / 反例型 / 跨界型 |
| SRS 下次复习 | date | 创建日期 + 7 天（MVP 不 push, 字段留空）|

**工时**：0.5 天（schema 设计 + lark-cli base create + write stub）

**依赖**：飞书 API 配额。5-22~5-31 异常期, 6-1 重置。

### 2.3 SRS 复盘 push（最不急）

**设计**：7 天后飞书机器人 push 「你 7 天前研磨的 <主题>, 现在用一句话复述给我听」, 用户回复 → 写回结晶卡的"7 天后复述质量"字段。

**依赖**：

- 飞书机器人长 cron 任务（macOS launchd / Linux cron）
- 飞书 API 配额（写消息）

**风险**：

- launchd 在用户不开机时不跑, 用户手动 trigger 体验差
- 配额异常期会 fail
- **跟朋友测试 5-30 这条线不冲突**（朋友测试时无 7 天历史卡片）—— 这个能力**完全可以 5-30 之后做**

**工时**：1 天

**结论**：MVP 不做, P3 推迟。

## 3. 五种部署形态对比

| 形态 | 范围 | 工时 | 风险 |
|---|---|---|---|
| **A · 不做** | 无 | 0 | 错失 demo 杀手镜头, 但 PITCH.md 出彩点 1 已有 yanyu-import 双向链接论据 |
| **B · MVP 上 5-30 前** | 类型 1 检测 + Bitable 写入 + 对话内"沉淀第 N 张"callout | 0.5-1 天 | 5-26~5-29 时间已紧（5-27 自测 + 5-28 ping 朋友）；飞书配额可能仍紧；朋友视角"沉淀第 N 张"可能不 wow |
| **C · 完整版上 6-2 后** | 三类 aha 检测全做 + Bitable + SRS push | 3-4 天 | 错过 6-8 demo 视频拍摄窗口（PLAN_v2 排期）|
| **D · 占位 schema 不接入** | 仅建 Bitable 表 + 写 stub, 不接对话 | 15 分钟 | 0；占位让未来 0 摩擦扩展 |
| **E · PITCH.md 叙事补强** | 加一节"未来路线: 研磨结晶卡（Nielsen 沉淀物路线）" | 1 小时 | 0；答辩时多一个 future work 论据 |

## 4. 推荐：形态 D + E 组合（1.5 小时）

理由按重要性：

1. **5-30 朋友测试是当前最高 ROI 单一活动**。任何 ≥0.5 天的工程改动应该让位——一次朋友反馈胜过 10 个工程师 wow。
2. **形态 D 留扩展接口**：Bitable schema 沉淀在飞书, 未来 6-2 后扩展只需要接 judge.py 输出, 不动 schema, 0 摩擦。
3. **形态 E 给答辩论据**：PITCH.md 加一节"未来工作: 研磨结晶卡"——明说"已建 schema 留 P2 实施"——答辩 / 投帖时有"路线图证据", 不假装已实施。
4. **形态 B 看似诱人但有三重风险**（**反 over-promise**）：
   - 5-26~5-29 时间紧（5-27 自测 + 5-28 ping 朋友, 还要修 5-27 自测发现的问题）
   - 类型 1 检测勉强 MVP 的 callout "沉淀第 N 张" 是**工程师视角 wow**——非 AI 圈朋友看到可能"so what"
   - 飞书配额异常期, 写入崩溃比没有更糟（朋友看到 error 比看不到 callout 更损伤）
5. **形态 C 5-30 后做**：朋友反馈确认这是真痛点再投入 3-4 天, 否则可能做完"工程师 wow / 用户冷漠"的功能。
6. **方法论**（依据 [[reviewer-nice-to-have-pushback]] + [[llm-judge-multi-run-required]]）：
   - 不要让作者自评（"这个功能朋友一定喜欢"）驱动工程投入——5-30 朋友反馈是 ground truth
   - aha-moment 检测如果上 LLM-judge, 必须先解 P3 工程债（JSON mode + multi-run）—— MVP 阶段强制类型 1 deterministic 路径

## 5. 排期更新建议（写进 PLAN_v2 §决策 7）

```diff
- | P2 研磨结晶卡（Anki SRS 哲学路线, 长程沉淀感）| 3-4 天 | 🔵 5-30 朋友反馈后决定 |
+ | P2-D 结晶卡 Bitable schema 占位（形态 D）| 15 min | ✅ 5-25 可立即做 |
+ | P2-E PITCH.md 加"未来工作: 研磨结晶卡"叙事（形态 E）| 1 小时 | ✅ 5-25 可立即做 |
+ | P2-C 结晶卡完整版（aha 三类检测 + Bitable + SRS）| 3-4 天 | 🔵 5-30 朋友反馈后决定 |
+ | P2-B MVP（类型 1 检测 + Bitable 写入 + 对话 callout）| 0.5-1 天 | ❌ 不推荐独立做, B 是 C 的子集 |
```

## 6. 如果用户最终选形态 B（详细排期, 备查）

不推荐, 但准备好供选：

| 子任务 | 工时 | 谁做 |
|---|---|---|
| Bitable 创建"研磨结晶卡"表 + 10 字段 schema | 1 小时 | 我（用户 export 飞书 user open_id 即可）|
| `yanyu_core/crystal_card_backend.py` 抽象 | 1 小时 | 我（复用 lark_backend 现成调用）|
| `yanyu-dialogue/SKILL.md` Step 5 加"E 阶段后自动写结晶卡"协议 | 0.5 小时 | 我 |
| 对话内"沉淀第 N 张" callout 集成砚石痕迹 | 1 小时 | 我（callout 第 6 种触发器: session 结束）|
| 端到端 self-test：跑一次研磨, 看卡片是否写入 | 0.5 小时 | 我 + 用户验证飞书表 |
| regression test 加 fixture（验证类型 1 aha 检测）| 0.5 小时 | 我 |
| **合计** | **0.5-1 天** | |

**B 路径硬条件**：
- 5-25 内做完, 5-26 ~ 5-27 buffer 修 bug, 5-28 ping 朋友前必须稳定
- 飞书 API 配额至少能连续写 5 次（5-22~5-31 异常期是赌博）
- 朋友测试时砚石痕迹 + 结晶卡两个新功能同时上 = **测试信号互相 confound**（朋友吐槽是因为哪个？）

## 7. 风险登记

| 风险 | 严重度 | 缓解 |
|---|---|---|
| aha-moment 检测假阳性污染卡片库 | 高 | 类型 1 deterministic 检测限定 D+E+复述 ≥40 字, 假阳性率天然低 |
| 飞书 API 配额异常期写入失败 | 中 | LocalFileBackend MVP 兜底（决策 1 已落地）, 配额回来后迁移 |
| 朋友测试 confound 信号 | 高 | 形态 D + E 不接入对话, 朋友测试零暴露 → 信号纯净 |
| 工程师 vs 非 AI 圈用户视角差 | 中 | 5-30 朋友反馈定生死, 不在自评阶段加塞功能 |
| Bitable schema 设计偏（10 字段哪个其实没用）| 低 | 形态 D 写空 schema, 6-2 后接入时按朋友反馈调整 |

## 8. SOTA 锚点

- **Michael Nielsen** [Augmenting Long-term Memory](https://augmentingcognition.com/ltm.html) —— Anki / SRS 哲学：进度感来自沉淀物
- **Ebbinghaus forgetting curve** —— 7 天后复述质量是记忆强度的标准探针
- **MathDial 印证型 aha** —— D 阶段贴原文后用户复述是合法的"用户自己悟到"信号（决策 6d 已 align）
- **PITCH.md 出彩点 1/2** —— 私有知识库 + 活体画像 = Study Mode 物理不可能做的差异化

---

## 决策记录

**主对话总指挥 5-24 拍板**：推荐**形态 D + E（1.5 小时）**, 立即可做, 5-25 内完成。形态 C 完整版 **5-30 朋友反馈后** 评估是否上 6-2~6-5。形态 B 不独立做。

**等用户拍板后**：

- 若用户同意 → TaskCreate 形态 D + E 执行清单
- 若用户改 B → 走 §6 的详细排期, 但记录决策理由（用户自评驱动 vs 朋友反馈驱动）
- 若用户改 A → spike doc 归档, P2 完全不做
