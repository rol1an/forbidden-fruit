---
name: yanyu-fusion
version: 0.2.0-deprecated
description: "DEPRECATED — 本 Skill 已合并入 yanyu-dialogue（含 fusion mode）。Trae SOLO / Claude Code 应自动加载 yanyu-dialogue。本目录仅作历史保留与向后兼容，不会被自动触发。"
metadata:
  deprecated: true
  superseded_by: "yanyu-dialogue"
---

# yanyu-fusion · DEPRECATED

本 Skill 已与 `yanyu-grinding` 合并为单一 `yanyu-dialogue` Skill（含 grinding mode + fusion mode），原因见 [`../docs/PLAN_v2_DECISIONS.md`](../docs/PLAN_v2_DECISIONS.md) §决策 2。

**注意**：本 Skill 原 Step 5「agent 接手扩'最小可行版本 / 失败模式 / 下一步验证假设'三段大纲」**已砍**——理由见 [`../docs/PITCH.md`](../docs/PITCH.md) §出彩点 3 边界声明：那部分恰恰是用户最该自己想的，agent 接手 = 摩擦消失。

新 Step 5 仅复述用户已说出的内容 + 把球踢回去（"你下一步想验证什么？"），不主动产出方案。

请切换到 [`../yanyu-dialogue/SKILL.md`](../yanyu-dialogue/SKILL.md) Mode B。

本目录内的 `references/` 已迁移到 `yanyu-dialogue/`，本地副本仅作历史快照，**不要再修改**。
