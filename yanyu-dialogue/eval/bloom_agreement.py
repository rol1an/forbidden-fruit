"""砚友 · Bloom tagger agreement test（决策 7 砚石痕迹 P1 闸门）

跑 bloom_tagger.py 在 fixture 上的标注 vs 人工标注，输出 agreement % +
per-level confusion。≥85% 才允许上 Bloom 跨级跃升触发砚石痕迹（避免误奖励
用户后下轮被打回的信任崩盘——见 references/inkstone-trace.md）。

学术锚点：arXiv:2511.10903 报告 GPT-4 在 Bloom 6 层 accuracy 0.72-0.73，
所以 85% 阈值是有意拔高一截—— Bloom 误判的代价（UX 信任崩盘）高于一次
telling 违规，必须严格于 telling_rate ≤ 0.2 红线。

CLI：
    python3 -m eval.bloom_agreement                          # 默认 fixture + 真 API
    python3 -m eval.bloom_agreement --mock                   # 走 stub keyword tagger
    python3 -m eval.bloom_agreement --threshold 0.85 --verbose
    python3 -m eval.bloom_agreement --fixtures path/to/set.json

退出码：0=PASS / 1=agreement < threshold / 2=fixture 路径不存在
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_FIXTURES = Path(__file__).parent / "fixtures" / "bloom_agreement_set.json"
DEFAULT_THRESHOLD = 0.85
BLOOM_LEVELS = [
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]


def run_agreement(
    fixtures_path: Path,
    threshold: float = DEFAULT_THRESHOLD,
    mock: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    from . import bloom_tagger  # type: ignore

    with open(fixtures_path, encoding="utf-8") as f:
        cases = json.load(f)

    agree_n = 0
    confusion: dict[str, dict[str, int]] = {
        lv: {lv2: 0 for lv2 in BLOOM_LEVELS} for lv in BLOOM_LEVELS
    }
    disagreements: list[dict[str, Any]] = []

    for case in cases:
        question = case["question"]
        human = case["human_label"]
        if human not in BLOOM_LEVELS:
            sys.stderr.write(f"[bloom_agreement] bad human_label in {case.get('id')}: {human}\n")
            continue
        llm_out = bloom_tagger.tag_question(question, mock=mock)
        llm_label = llm_out.get("level", "?")
        if llm_label == human:
            agree_n += 1
        else:
            disagreements.append(
                {
                    "id": case.get("id", "?"),
                    "question": question,
                    "human": human,
                    "llm": llm_label,
                    "llm_reason": llm_out.get("reason", ""),
                }
            )
        if llm_label in confusion[human]:
            confusion[human][llm_label] += 1

    total = len(cases)
    agreement_rate = agree_n / total if total > 0 else 0.0
    passed = agreement_rate >= threshold

    summary = {
        "total": total,
        "agreed": agree_n,
        "agreement_rate": round(agreement_rate, 3),
        "threshold": threshold,
        "passed": passed,
        "mock": mock,
        "disagreements": disagreements,
        "confusion": confusion,
    }

    if verbose:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        mark = "PASS" if passed else "FAIL"
        mock_note = " [mock=stub keyword tagger]" if mock else ""
        print(
            f"agreement: {agree_n}/{total} ({agreement_rate * 100:.1f}%) "
            f"{mark} (threshold={threshold:.2f}){mock_note}"
        )
        if disagreements:
            print(f"  {len(disagreements)} disagreements:")
            for d in disagreements:
                q_preview = d["question"][:60]
                print(
                    f"    [{d['id']}] human={d['human']:>10} "
                    f"llm={d['llm']:>10}  {q_preview}..."
                )
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="Bloom tagger agreement test (决策 7)")
    p.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES),
        help="JSON fixture 路径",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"agreement 阈值 (默认 {DEFAULT_THRESHOLD})",
    )
    p.add_argument(
        "--mock", action="store_true", help="bloom_tagger 走 stub keyword tagger"
    )
    p.add_argument(
        "--verbose", action="store_true", help="输出完整 JSON + confusion matrix"
    )
    args = p.parse_args()

    fix_path = Path(args.fixtures)
    if not fix_path.exists():
        sys.stderr.write(f"[bloom_agreement] fixtures not found: {fix_path}\n")
        raise SystemExit(2)

    summary = run_agreement(
        fix_path, threshold=args.threshold, mock=args.mock, verbose=args.verbose
    )
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
