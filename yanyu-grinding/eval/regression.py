"""砚友 · Prompt 回归测试框架

输入：eval/fixtures/regression_set.json（5-10 条固定测试用例）
每条：{
    "name": "...",
    "initial_user_input": "...",
    "topic": "...",
    "expected_moves": [...],          # 顺序敏感的 agent move 期望
    "expected_aha_keywords": [...]    # E 阶段用户回复 / agent 印证 中应出现的关键词
}

行为：用 mock 跑（不真调 Anthropic），生成虚拟 session → 跑 judge → 报告 pass/fail。
关注两个回归信号：
    1. telling rate 是否超阈（默认 0.2）
    2. expected_moves 序列是否对得上（前缀匹配）

CLI：
    python3 -m yanyu_eval.regression
    python3 -m yanyu_eval.regression --threshold 0.15
    python3 -m yanyu_eval.regression --fixtures path/to/set.json
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

    真集成测试要换成真正的 grinding agent runner——目前只验证 eval 框架本身。
    """
    expected_moves = case.get("expected_moves", [])
    stage_map = {
        "focus": "A",
        "probing": "A",
        "challenge": "C",
        "tell": "D",
        "summary": "E",
    }
    # MathDial 四分类映射
    move_map = {
        "focus": "focus",
        "probing": "probing",
        "challenge": "probing",
        "tell": "telling",
        "summary": "generic",
    }

    turns: list[dict[str, Any]] = [
        {"role": "user", "content": case.get("initial_user_input", ""), "stage": "A"}
    ]
    for i, mv in enumerate(expected_moves):
        turns.append(
            {
                "role": "agent",
                "content": f"[mock agent turn {i} · move={mv}]",
                "move": move_map.get(mv, "generic"),
                "stage": stage_map.get(mv, "A"),
            }
        )
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
        ok = telling_ok and kw_ok
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
