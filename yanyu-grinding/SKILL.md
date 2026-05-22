---
name: yanyu-grinding
version: 0.2.0-deprecated
description: "DEPRECATED — 本 Skill 已合并入 yanyu-dialogue。Trae SOLO / Claude Code 应自动加载 yanyu-dialogue。本目录仅作历史保留与向后兼容，不会被自动触发。"
metadata:
  deprecated: true
  superseded_by: "yanyu-dialogue"
---

# yanyu-grinding · DEPRECATED

本 Skill 已与 `yanyu-fusion` 合并为单一 `yanyu-dialogue` Skill（含 grinding mode + fusion mode），原因见 [`../docs/PLAN_v2_DECISIONS.md`](../docs/PLAN_v2_DECISIONS.md) §决策 2：

- 解决跨 Skill 相对路径 symlink 部署后失效问题（reviewer 致命问题 #2）
- 简化 prompt 维护负担——两个 mode 本质是同一个对话引擎
- 合并后 description 同时覆盖 grinding 与 fusion 关键词

请切换到 [`../yanyu-dialogue/SKILL.md`](../yanyu-dialogue/SKILL.md)。

本目录内的 `references/` 和 `scripts/` 已迁移到 `yanyu-dialogue/`，本地副本仅作历史快照，**不要再修改**——所有更新去 yanyu-dialogue/。
