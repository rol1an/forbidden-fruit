"""砚友 · LLM-judge 三维度评估器

输入：session.json，含 turn list（user/agent 各回合内容 + agent 内部 move 标签）
输出：JSON 三维度分数 0-1
    - telling_rate: agent 直接给答案占比（应低）
    - probing_depth: A-E 5 阶段覆盖广度 + reasoning 引导深度（应高）
    - aha_moment_confidence: 是否有 D 阶段印证 + 用户在 E 完整复述

依赖：anthropic（缺失则回退 stub）。--mock 跳过真调。

CLI：
    python3 -m eval.judge --session session.json
    python3 -m eval.judge --session session.json --mock

学术锚点：RAGAS（arXiv:2309.15217）多维度 LLM-judge；MathDial（arXiv:2305.14536）
focus/probing/telling/generic teacher-move 分类（决策 6d 已纳入）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

MOVES_TELLING = {"telling"}
PROBING_STAGES = ["A", "B", "C", "D", "E"]
LADDER_LEVELS = [1, 2, 3]  # 决策 7: hint ladder 三档
L3_OVERUSE_THRESHOLD = 2  # L3 单 session 触发 ≥ 此值 = prompt 失败信号

JUDGE_SYSTEM = """你是一位**严厉**的教学评估官，专门审查 Socratic agent 的对话质量。

警告：**绝不要"自我祝贺"或溢美**。你的标准应该比生成 agent 更严厉——如果一次对话有任何
喂答案、跳过 reasoning、用户没真正自己悟到的迹象，必须扣分。Khanmigo 自己 pre-post 都
没显著差异——你看到的大概率不是真正的"悟到"。

**决策 7 新增**：hint ladder L1/L2 计入 focus 不算 telling；L3 (open original) 单独
标 ladder_level=3。如果同一 session 出现 ladder_level=3 ≥2 次, 视为 scaffolding
设计失败（L1/L2 应覆盖 ≥80% 卡死案例, L3 是兜底）, 扣 probing_depth 分。L2 必须带
inferred_user_default 字段, 缺字段视为 agent 盲猜反直觉锚点 → 扣分。

给定一段 user/agent 对话 + agent 内部 move 标签（focus/probing/telling/generic）,
输出**严格 JSON**：

{
  "telling_rate": 0.0-1.0,            # telling move 占比 + 即使标签非 telling 但实际给出了答案的情况
  "probing_depth": 0.0-1.0,           # A 探查→B 卡壳→C 假设挑战→D 印证→E 收尾覆盖广度 × 引导深度
  "aha_moment_confidence": 0.0-1.0,   # D 印证是否在用户自己悟到后才给 + E 用户是否完整复述
  "reason": "<≤80 字 简短说明扣分点>"
}

不要任何其他字符。"""


def _count_moves(turns: list[dict[str, Any]]) -> dict[str, int]:
    """统计 agent 各 move 类型回合数。"""
    counts: dict[str, int] = {}
    for t in turns:
        if t.get("role") != "agent":
            continue
        mv = t.get("move", "generic")
        counts[mv] = counts.get(mv, 0) + 1
    return counts


def _stage_coverage(turns: list[dict[str, Any]]) -> dict[str, int]:
    """统计 A-E 5 阶段实际触达回合数。"""
    cov = {s: 0 for s in PROBING_STAGES}
    for t in turns:
        if t.get("role") != "agent":
            continue
        st = t.get("stage")
        if st in cov:
            cov[st] += 1
    return cov


def _count_ladder(turns: list[dict[str, Any]]) -> dict[str, Any]:
    """统计决策 7 的 hint ladder L1/L2/L3 触发次数。

    返回:
        {
            "l1_count": int,
            "l2_count": int,
            "l3_count": int,
            "overuse_warning": bool,             # L3 ≥ L3_OVERUSE_THRESHOLD
            "l2_missing_default": int,           # L2 但没写 inferred_user_default 的次数 (盲猜反直觉锚点)
        }
    """
    counts = {lv: 0 for lv in LADDER_LEVELS}
    l2_missing = 0
    for t in turns:
        if t.get("role") != "agent":
            continue
        lv = t.get("ladder_level")
        if lv in counts:
            counts[lv] += 1
            if lv == 2 and not t.get("inferred_user_default"):
                l2_missing += 1
    return {
        "l1_count": counts[1],
        "l2_count": counts[2],
        "l3_count": counts[3],
        "overuse_warning": counts[3] >= L3_OVERUSE_THRESHOLD,
        "l2_missing_default": l2_missing,
    }


def _stub_judge(turns: list[dict[str, Any]]) -> dict[str, Any]:
    """无 API / mock 时的回退评估，靠 move 标签 + 阶段标签算。"""
    move_counts = _count_moves(turns)
    agent_total = sum(move_counts.values()) or 1
    telling = move_counts.get("telling", 0)
    telling_rate = telling / agent_total

    cov = _stage_coverage(turns)
    stages_hit = sum(1 for v in cov.values() if v > 0)
    probing_depth = stages_hit / len(PROBING_STAGES)

    # aha-moment：必须 D 至少 1 次 且 E 至少 1 次
    has_d = cov.get("D", 0) > 0
    has_e = cov.get("E", 0) > 0
    aha = 0.6 if (has_d and has_e) else (0.3 if has_d or has_e else 0.0)

    # 用户最后一回合长度作为"复述完整度"的弱信号
    last_user_turns = [t for t in turns if t.get("role") == "user"]
    if last_user_turns:
        last_len = len(last_user_turns[-1].get("content", ""))
        if has_d and has_e and last_len >= 40:
            aha = 0.75

    ladder_stats = _count_ladder(turns)
    reason = f"stub: stages_hit={stages_hit}/5, telling={telling}/{agent_total}"
    if ladder_stats["overuse_warning"]:
        reason += f" | L3 overuse ({ladder_stats['l3_count']} times) — scaffolding 设计失败"
        # L3 滥用同时扣 probing_depth (兜底用太多 = 主路径设计差)
        probing_depth *= 0.7
    if ladder_stats["l2_missing_default"] > 0:
        reason += f" | {ladder_stats['l2_missing_default']} 个 L2 未填 inferred_user_default (盲猜)"

    return {
        "telling_rate": round(telling_rate, 2),
        "probing_depth": round(probing_depth, 2),
        "aha_moment_confidence": round(aha, 2),
        "reason": reason,
        "_move_counts": move_counts,
        "_stage_coverage": cov,
        "_ladder_stats": ladder_stats,
    }


def judge_session(session: dict[str, Any], mock: bool = False) -> dict[str, Any]:
    """主入口：评估一次完整对话。"""
    turns = session.get("turns", [])
    if not turns:
        return {
            "telling_rate": 0.0,
            "probing_depth": 0.0,
            "aha_moment_confidence": 0.0,
            "reason": "empty session",
        }

    # 总是先算 stub 版（提供辅助统计字段给 dashboard）
    stub_result = _stub_judge(turns)

    if mock:
        return stub_result

    try:
        import anthropic  # type: ignore
    except ImportError:
        sys.stderr.write(
            "[judge] anthropic package not installed; falling back to stub.\n"
        )
        return stub_result

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.stderr.write("[judge] ANTHROPIC_API_KEY not set; falling back to stub.\n")
        return stub_result

    # 真调：拼一份 readable 对话
    convo = "\n".join(
        f"[{t.get('role','?')}|move={t.get('move','-')}|stage={t.get('stage','-')}] "
        f"{t.get('content','')}"
        for t in turns
    )
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": convo}],
    )
    text = msg.content[0].text.strip()
    try:
        result = json.loads(text)
        # 合并 stub 的辅助字段供 dashboard 用
        result["_move_counts"] = stub_result["_move_counts"]
        result["_stage_coverage"] = stub_result["_stage_coverage"]
        result["_ladder_stats"] = stub_result["_ladder_stats"]
        return result
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[judge] LLM bad JSON ({e}); falling back to stub.\n")
        return stub_result


def main() -> None:
    p = argparse.ArgumentParser(description="LLM-judge 三维度评估器")
    p.add_argument("--session", required=True, help="session.json 路径")
    p.add_argument("--mock", action="store_true", help="不调 API，纯启发式")
    args = p.parse_args()

    with open(args.session, encoding="utf-8") as f:
        session = json.load(f)
    result = judge_session(session, mock=args.mock)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
