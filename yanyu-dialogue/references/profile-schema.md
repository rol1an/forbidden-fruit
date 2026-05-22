# 用户画像 Bitable Schema

> **何时读**：首次运行 `scripts/profile_init.py` 创建 Bitable 表时；改 schema 时；调试 `profile_read.py` / `profile_write.py` 时。grinding 和 fusion 两个 mode 共用本表。

## 表结构

表名：`砚友用户画像`（或 `yanyu_profile`，单租户单表）

| 字段 | 类型 | 说明 |
|---|---|---|
| `user_id` | 主键 string | 飞书 open_id 或自定义；唯一索引 |
| `display_name` | string | 用户显示名（便于人工查表）|
| `topic_mastery` | 富文本（JSON 字符串）| `{"RAG":4, "Agent编排":2, ...}` 主题 → 掌握度 0-5 |
| `stuck_points` | 富文本（多行 string）| 累积的卡壳子问题列表，每行一条："<topic> :: <具体子问题>" |
| `style_response` | 单值 select | `prefers_challenge` / `prefers_guidance` / `prefers_affirmation` |
| `methodology_quotes` | 富文本 | 用户在辩护中说出的有创见的话，每行一条："<日期> :: <金句>" |
| `aha_moment_log` | 富文本 | 让用户悟到的高效提问，每行一条："<日期> :: <topic> :: <提问>" |
| `last_session_at` | 日期时间 | 上次对话时间（grinding 或 fusion）|
| `session_count` | number | 累计对话次数 |
| `domain_familiarity_tags` | 多值 select | 用户已涉足的领域标签（供 fusion mode 选已知 × 未知碰撞）|

## 为什么 mastery / stuck / quotes 用富文本而非展开表

砚友是单用户单表 + 多字段累积，不是高频结构化查询场景。富文本（JSON / 多行字符串）让：

1. 一次 record_search 拿全画像，不用 join
2. 字段数可控（< 15），便于在 Bitable UI 里人工 review
3. 写入逻辑简单——append 到字符串末尾即可

代价：不能直接在 Bitable 里按"X 主题掌握度排序"。这个分析需求由 `scripts/profile_analyze.py`（stretch goal）做，不在 MVP 范围。

## 初始化命令（scripts/profile_init.py 做的事）

```bash
# 1. 在用户飞书空间创建一张多维表格（lark-drive create + base create）
lark-cli drive +create --profile new_tenant --type bitable --name "砚友用户画像"
# → 返回 app_token

# 2. 创建表
lark-cli base +table-create --profile new_tenant --as bot \
  --base-token <app_token> --name yanyu_profile

# 3. 创建字段（按上表）
lark-cli base +field-create --profile new_tenant --as bot \
  --base-token <app_token> --table-id yanyu_profile \
  --json '{"field_name":"user_id","type":1}'
# ... 依次创建 9 个字段
```

详细字段类型代码见 [`../../yanyu-import/references/lark-cli-cheatsheet.md`](../../yanyu-import/references/lark-cli-cheatsheet.md) §Base。

## 读画像的返回 JSON 契约

`profile_read.py --user <user_id>` 输出：

```json
{
  "user_id": "ou_xxx",
  "display_name": "李四",
  "topic_mastery": {"RAG": 4, "Agent编排": 2},
  "stuck_points": [
    "RAG :: rerank 模型怎么选",
    "Agent编排 :: 多 agent 之间怎么传 context"
  ],
  "style_response": "prefers_challenge",
  "methodology_quotes": [
    "2026-05-15 :: 召回分层比单纯加 rerank 更重要"
  ],
  "aha_moment_log": [
    "2026-05-15 :: RAG :: 如果你的 chunking 是按段落切，跨段语义谁来保？"
  ],
  "last_session_at": "2026-05-21T14:00:00",
  "session_count": 7,
  "domain_familiarity_tags": ["RAG", "Agent", "LLM 微调"]
}
```

首次用户（无记录） → 返回 `{"user_id": "...", "is_new": true}`，agent 据此用通用开场。

## 写画像的输入契约

`profile_write.py --user <user_id> --session session.json` 输入：

```json
{
  "topic": "RAG",
  "mastery_delta": 1,
  "stuck_points_added": ["rerank 模型怎么选"],
  "style_response": "prefers_challenge",
  "aha_moment_question": "如果你的 chunking 是按段落切，跨段语义谁来保？",
  "user_methodology": "召回分层比单纯加 rerank 更重要",
  "session_summary": "本次研磨 RAG，用户在 chunk 跨段处卡壳，最终自己悟到动态窗口方向"
}
```

写入逻辑：
- `topic_mastery[topic] += mastery_delta`（clamp 0-5）
- `stuck_points` append
- `style_response` 覆盖（最新优先）
- `methodology_quotes` / `aha_moment_log` append（带日期）
- `last_session_at` 覆盖
- `session_count += 1`
- `domain_familiarity_tags` add topic if not in

## Mode 视图建议

虽然 schema 单表共享，对话时按 mode 关注不同字段：

| Mode | 必读字段 | 辅助字段 |
|---|---|---|
| grinding | `topic_mastery`, `stuck_points`, `style_response` | `methodology_quotes`（D 印证时引用）|
| fusion | `domain_familiarity_tags`, `methodology_quotes` | `topic_mastery`（避开掌握度过低的极陌生组合）|
