# 5-30 朋友测试 · 数据回收

> **回收方式**：本地 markdown 兜底（5-22 ~ 5-31 飞书 API 配额异常期）→ 6-1 配额回来后迁移到 Bitable。
>
> 模板配套 [`USER_TEST_PROTOCOL.md`](USER_TEST_PROTOCOL.md) + [`USER_TEST_SCRIPT.md`](USER_TEST_SCRIPT.md)。

---

## 使用说明

每个朋友测一次（含 grinding + fusion 两个 mode）→ **加一个 §朋友 N 章节**到本文件 → 按下方模板填。

- 朋友昵称用化名（"朋友 A / B / C"），避免泄露隐私
- **5 题问卷原话录入**（不润色）
- 主持人观察笔录与朋友原话**分开记**——朋友说啥是朋友说啥，你看到啥是你看到啥
- session.json 路径写进来（如果自动落地了），跑 `python3 -m eval.judge --mock` 把 metrics 摘要也粘进来

---

## 朋友测试记录模板（复制到下方章节用）

````markdown
## 朋友 [A/B/C] · [yyyy-mm-dd hh:mm]

### Meta

- **化名**：朋友 X
- **AI 圈**？yes / no
- **关系熟度**：（1-5, 5 = 室友 / 配偶级）
- **测试时长**：实际多少分钟（buffer 内 vs 超时）
- **session.json 路径**：`~/.agents/sessions/<...>` 或 N/A
- **录音/录屏**：yes / no / N/A

### Grinding 段记录

- **朋友选的主题**：（朋友自己抛的）
- **轮数**：约 X 轮
- **被问住次数**：X 次
- **主动放弃次数**：X 次（"直接告诉我吧" / "我不想想" 等）
- **agent 触发的 ladder 档位**（看 session.json `_ladder_stats`）：L1=? L2=? L3=?
- **L3 触发后朋友的反应**：去飞书看了 / 没去 / 看了但回来直接复制原文（不算复述）/ 看了且用自己的话复述
- **砚石痕迹 callout 出现时朋友的反应**：笑 / 困惑 / 忽略 / 主动追问"我现在到第几了" / N/A
- **主持人观察的情绪节点**（按时间顺序）：
  - 第 X 轮：朋友 [笑 / 皱眉 / 翻白眼 / 长时间沉默 / 主动叹气]
  - ...

### Fusion 段记录

- **朋友抛的模糊想法**：（朋友原话）
- **agent 强制跨界抛的 A 领域**：（看 agent 第一轮选了哪个 A）
- **朋友第一反应**：（朋友原话, 例："这俩有啥关系" / "有意思" / "..."）
- **收敛了吗**：yes / no / 假收敛（"懂了懂了" 但讲不出方案）
- **收敛信号**：朋友是否用具体动词（"先做 X 再做 Y"）？是否能说出最小可行版本？是否主动列了已知失败模式？
- **agent 是否把朋友自己说过的金句甩回脸上**：yes / no（这是决策 2 砍掉 Step 5 喂答案后 agent 唯一能用的手段）
- **主持人观察的情绪节点**：
  - 第 X 轮：...

### 5 题问卷（朋友原话 + 你的追问及回答）

**Q1: 你被问住过吗? 被问住时是什么感觉?**

> 朋友原话：

> 追问 + 朋友回答：

**Q2: agent 拒绝直接给答案, 你想砸键盘吗?**

> 朋友原话：

> 追问 + 朋友回答：

**Q3: 最后你有"我悟到了"的瞬间吗? 发生在哪一轮?**

> 朋友原话：

> 追问 + 朋友回答：

**Q4: agent 的提问, 有没有让你想到自己之前没想过的角度?**

> 朋友原话：

> 追问 + 朋友回答：

**Q5: 如果朋友跟你描述这个产品, 你会推荐给谁?**

> 朋友原话：

> 追问 + 朋友回答：

### 主持人事后笔录（5 分钟内写完, 不要让记忆衰减）

- 整体感觉这次测试**信号强不强**：（1-5）
- 朋友给我**最不爽的一句话**：
- 朋友给我**最意外的一句话**：
- 我**忍不住为 agent 辩护**了吗：yes / no（如果 yes, 哪里？）
- 我**最想立刻改 agent prompt 的一处**：

### Eval metrics 摘要（朋友走后跑 judge.py + bloom_tagger）

```bash
python3 -m eval.judge --session <path> --mock
```

```json
// 粘贴 judge 输出
```

- **telling_rate**：（应该 ≤ 0.2; 如果 > 0.2 是 prompt failure）
- **probing_depth**：
- **aha_moment_confidence**：
- **_ladder_stats**：l1=? l2=? l3=? overuse=true/false
- **_inkstone_stats**：warning=true/false, duplicates=?

### 主客观对齐验证（决策 7 测点）

- 朋友说"被问住 N 次" vs session.json 实际 L1/L2/L3 触发 N 次：**对齐 / 不对齐**
- 朋友说"agent 让我觉得它在给答案" vs telling_rate：**对齐 / 不对齐**（如果朋友主观觉得 telling 多但 metric 低 = prompt 有 false-negative 漏标）
- 朋友说"看到进度提示" vs `_inkstone_stats` 有 callout 触发：**对齐 / 不对齐**

---
````

## 朋友测试记录

<!-- 5-30 当天起把每个朋友的测试记录粘到下方, 用上面模板 -->

### 朋友 A · YYYY-MM-DD HH:MM

（待填）

### 朋友 B · YYYY-MM-DD HH:MM

（待填）

### 朋友 C · YYYY-MM-DD HH:MM

（待填）

---

## 6-1 之后迁移到飞书 Bitable

配额回来后跑：

```bash
# 1. 创建 Bitable
lark-cli base +create --profile new_tenant --as bot --name "5-30 朋友测试问卷"

# 2. 表 schema（参考下方字段定义）
#    - 主表 "朋友测试" 字段:
#      * 化名 (text)
#      * AI 圈 (checkbox)
#      * 测试日期 (date)
#      * 测试时长 (number, 分钟)
#      * Q1 / Q2 / Q3 / Q4 / Q5 (text, 各对应 5 题问卷答案)
#      * telling_rate / probing_depth / aha_moment_confidence (number)
#      * ladder_l1_count / l2_count / l3_count (number)
#      * ladder_overuse (checkbox)
#      * inkstone_callout_count (number)
#      * 主持人最不爽 / 最意外 / 最想改 (text)
#      * session_json_path (text)

# 3. 把本文件每个 §朋友 N 章节导入 Bitable 一行
#    (后续可写一个 docs/MIGRATE_TEST_RESPONSES.py 脚本)
```

迁移后本文件**保留**作为永久 backup, 不删除。

## 6-1 数据分析模板

3 个朋友数据齐了之后, 用以下框架分析:

1. **三个朋友最一致的 1 条反馈**（共鸣点 = 真信号）
2. **三个朋友最不一致的 1 条反馈**（个体差异点）
3. **非 AI 圈朋友 vs AI 圈朋友的反馈差异**（产品定位指引）
4. **主客观对齐的 3 个 metric 跟朋友体感不一致的地方**（prompt failure 信号）
5. **3 个朋友是否都"被问住过"**——如果有人完全没被问住, prompt 太软 / hook 不够具体
6. **3 个朋友是否都有 aha moment**——如果有人完全没有, D 阶段印证机制可能失效
7. **3 个朋友是否都"想砸键盘"**——如果都没砸键盘的冲动, 摩擦力度不够（砚友的存在就是制造摩擦）

把上述 7 点分析写入 [`docs/REVIEW_002.md`](REVIEW_002.md)（待建, 5-31 之后由二轮 reviewer agent 主导评估）。
