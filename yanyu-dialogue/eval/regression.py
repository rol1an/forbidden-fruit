"""砚友 · eval 框架回归测试

⚠️ 边界（务必读）：本测试**不调用真 agent，也不加载 SKILL.md 提示词**。
它从每条 fixture 的 `expected_moves` 反向拼出一份"理想 agent"虚拟 session
（见 `_mock_session`），再喂给 stub judge 打分。因此：

  ✅ 能捕获：eval 框架代码本身的退化（stub judge 评分逻辑 / ladder 计数 /
     砚石痕迹重复检测 / aha 关键词检查），以及 fixture 自洽性。
  ❌ 不能捕获：提示词（SKILL.md / references）层面的退化——改提示词对这里的
     分数**零影响**。真正的 prompt 回归需要接一个真 dialogue agent runner
     （见 `_mock_session` 的 TODO）。

输入：eval/fixtures/regression_set.json（固定测试用例）
每条：{
    "name": "...",
    "initial_user_input": "...",
    "topic": "...",
    "expected_moves": [...],          # 用于拼虚拟 session 的 agent move 序列
    "expected_aha_keywords": [...],   # E 阶段用户回复里应出现的关键词
    "expect_overuse": false           # 可选：是否预期触发 L3 ladder 滥用告警
}

行为：mock 跑（不真调 LLM）→ 生成虚拟 session → 跑 stub judge → 报告 pass/fail。
每条 case 的 pass 取决于三个信号同时满足：
    1. telling_rate 是否 ≤ 阈值（默认 0.2）
    2. expected_aha_keywords 是否都出现在 session 文本里
    3. ladder 滥用告警 (overuse_warning) 是否与 expect_overuse 一致

CLI：
    python3 -m eval.regression
    python3 -m eval.regression --threshold 0.15
    python3 -m eval.regression --fixtures path/to/set.json
    python3 -m eval.regression --mock     # 等价于默认行为；显式声明，便于脚本里挂保险
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

DEFAULT_FIXTURES = Path(__file__).parent / "fixtures" / "regression_set.json"


def _mock_session(case: dict[str, Any]) -> dict[str, Any]:
    """根据 expected_moves 拼一份"理想 agent"虚拟 session，用于 judge 跑通。

    真集成测试要换成真正的 dialogue agent runner——目前只验证 eval 框架本身。

    expected_moves 元素扩展（决策 7）:
        focus / probing / challenge / tell / summary  # 原有
        l1 / l2 / l3                                  # ladder 三档, move=focus, ladder_level=1/2/3
    """
    expected_moves = case.get("expected_moves", [])
    stage_map = {
        "focus": "A",
        "probing": "A",
        "challenge": "C",
        "tell": "D",
        "summary": "E",
        "l1": "B",  # 卡壳引导
        "l2": "B",
        "l3": "B",
    }
    # MathDial 四分类映射；l1/l2/l3 都打 focus，副标签 ladder_level 区分
    move_map = {
        "focus": "focus",
        "probing": "probing",
        "challenge": "probing",
        "tell": "telling",
        "summary": "generic",
        "l1": "focus",
        "l2": "focus",
        "l3": "focus",
    }
    ladder_level_map = {"l1": 1, "l2": 2, "l3": 3}

    turns: list[dict[str, Any]] = [
        {"role": "user", "content": case.get("initial_user_input", ""), "stage": "A"}
    ]
    for i, mv in enumerate(expected_moves):
        turn: dict[str, Any] = {
            "role": "agent",
            "content": f"[mock agent turn {i} · move={mv}]",
            "move": move_map.get(mv, "generic"),
            "stage": stage_map.get(mv, "A"),
        }
        if mv in ladder_level_map:
            turn["ladder_level"] = ladder_level_map[mv]
            if mv == "l2":
                turn["inferred_user_default"] = "<mock-default-answer>"
        turns.append(turn)
        # 用户应答（最后一回合放期望 aha keyword）
        if i == len(expected_moves) - 1:
            kws = " ".join(case.get("expected_aha_keywords", []))
            turns.append({"role": "user", "content": f"我悟到了：{kws}", "stage": "E"})
        else:
            turns.append({"role": "user", "content": "mock user reply", "stage": "A"})

    return {"topic": case.get("topic", ""), "turns": turns}


def _check_aha_keywords(session: dict[str, Any], keywords: list[str]) -> list[str]:
    """返回 session 文本里缺失的关键词列表。"""
    blob = "\n".join(t.get("content", "") for t in session.get("turns", []))
    return [kw for kw in keywords if kw not in blob]


def run_regression(
    fixtures_path: Path, threshold: float = 0.2, verbose: bool = False
) -> dict[str, Any]:
    from . import judge  # type: ignore

    with open(fixtures_path, encoding="utf-8") as f:
        cases = json.load(f)

    results: list[dict[str, Any]] = []
    pass_n = 0
    for case in cases:
        sess = _mock_session(case)
        jr = judge.judge_session(sess, mock=True)
        telling = jr.get("telling_rate", 0.0)
        missing_kws = _check_aha_keywords(sess, case.get("expected_aha_keywords", []))
        telling_ok = telling <= threshold
        kw_ok = len(missing_kws) == 0

        # 决策 7: ladder overuse 期望 (fixture 可选声明 expect_overuse)
        ladder_stats = jr.get("_ladder_stats", {}) or {}
        actual_overuse = bool(ladder_stats.get("overuse_warning", False))
        expected_overuse = bool(case.get("expect_overuse", False))
        overuse_ok = actual_overuse == expected_overuse

        ok = telling_ok and kw_ok and overuse_ok
        if ok:
            pass_n += 1
        results.append(
            {
                "name": case.get("name"),
                "pass": ok,
                "telling_rate": telling,
                "telling_ok": telling_ok,
                "missing_aha_keywords": missing_kws,
                "probing_depth": jr.get("probing_depth"),
                "aha_moment_confidence": jr.get("aha_moment_confidence"),
                "overuse_ok": overuse_ok,
                "actual_overuse": actual_overuse,
                "expected_overuse": expected_overuse,
                "ladder_stats": ladder_stats,
            }
        )

    summary = {
        "total": len(cases),
        "passed": pass_n,
        "failed": len(cases) - pass_n,
        "threshold_telling_rate": threshold,
        "cases": results,
    }
    if verbose:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        # 紧凑摘要
        print(f"regression: {pass_n}/{len(cases)} passed  (threshold={threshold})")
        for r in results:
            mark = "PASS" if r["pass"] else "FAIL"
            extras = []
            if not r["telling_ok"]:
                extras.append(f"telling={r['telling_rate']:.2f}>{threshold}")
            if r["missing_aha_keywords"]:
                extras.append(f"missing={r['missing_aha_keywords']}")
            if not r.get("overuse_ok", True):
                extras.append(
                    f"overuse={r.get('actual_overuse')} expected={r.get('expected_overuse')}"
                )
            extra = "  " + " ".join(extras) if extras else ""
            print(f"  [{mark}] {r['name']}{extra}")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="Prompt 回归测试")
    p.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES),
        help="测试集 JSON 路径",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=0.2,
        help="telling rate 阈值（默认 0.2）",
    )
    p.add_argument("--verbose", action="store_true", help="输出完整 JSON")
    p.add_argument(
        "--mock", action="store_true",
        help="兼容标志（regression 本来就走 mock judge）；显式声明用于 CI",
    )
    args = p.parse_args()

    fix_path = Path(args.fixtures)
    if not fix_path.exists():
        sys.stderr.write(f"[regression] fixtures not found: {fix_path}\n")
        raise SystemExit(2)

    summary = run_regression(fix_path, threshold=args.threshold, verbose=args.verbose)
    # 非零退出码方便 CI 判定
    if summary["failed"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
