"""砚友 · 对话质量可视化 dashboard

输入：session.json（含 turn list + judge 输出 + bloom 标注）
输出：PNG 四宫格 dashboard：
    左上：Bloom's 饼图（六色，按计数）
    右上：telling rate 折线（X=轮数，Y=0-1）
    左下：A-E 5 阶段 checkbox + 实际触达轮数
    右下：本次 aha_moment_confidence 大字 + 简短反馈

依赖：matplotlib（缺失时打印警告：`pip install matplotlib`）。
按需可与 judge.py / bloom_tagger.py 协同——本脚本也支持 --mock 重跑 judge + bloom。

CLI：
    python3 -m eval.dashboard --session session.json --output dashboard.png
    python3 -m eval.dashboard --session session.json --output dashboard.png --mock
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

BLOOM_LEVELS = [
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]
BLOOM_COLORS = ["#cdd9e3", "#a8c5da", "#6f9ec2", "#ec9a6a", "#d96a4a", "#a83232"]
STAGES = ["A", "B", "C", "D", "E"]
STAGE_LABELS = {
    "A": "A · 探查",
    "B": "B · 卡壳引导",
    "C": "C · 假设挑战",
    "D": "D · 印证",
    "E": "E · 收尾",
}


def _ensure_annotations(session: dict[str, Any], mock: bool) -> dict[str, Any]:
    """如果 session 没有 judge / bloom 字段，调用本地模块就地补齐。

    放在函数体内 import，避免顶层 import 循环 / 依赖。
    """
    from . import bloom_tagger, judge  # type: ignore

    if "judge" not in session:
        session["judge"] = judge.judge_session(session, mock=mock)

    if "bloom_tags" not in session:
        tags = []
        for t in session.get("turns", []):
            if t.get("role") == "agent":
                tags.append(bloom_tagger.tag_question(t.get("content", ""), mock=mock))
        session["bloom_tags"] = tags
    return session


def _bloom_distribution(tags: list[dict[str, Any]]) -> list[int]:
    counts = {lv: 0 for lv in BLOOM_LEVELS}
    for t in tags:
        lv = t.get("level")
        if lv in counts:
            counts[lv] += 1
    return [counts[lv] for lv in BLOOM_LEVELS]


def _telling_per_turn(turns: list[dict[str, Any]]) -> tuple[list[int], list[float]]:
    """累积 telling rate 折线。X=agent 回合编号，Y=截至该回合的 telling 累计占比。"""
    xs, ys = [], []
    telling_so_far = 0
    agent_so_far = 0
    for t in turns:
        if t.get("role") != "agent":
            continue
        agent_so_far += 1
        if t.get("move") == "telling":
            telling_so_far += 1
        xs.append(agent_so_far)
        ys.append(telling_so_far / agent_so_far)
    return xs, ys


def render(session: dict[str, Any], output: str) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
        from matplotlib import font_manager, rcParams  # type: ignore
    except ImportError:
        sys.stderr.write(
            "[dashboard] matplotlib not installed; run: pip install matplotlib\n"
        )
        raise SystemExit(2)

    # Best-effort CJK 字体兜底，避免标题/标签变方框（找不到就保持默认）
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for fname in ("PingFang SC", "Heiti SC", "Hiragino Sans GB",
                  "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC",
                  "Arial Unicode MS", "STHeiti"):
        if fname in installed:
            rcParams["font.family"] = [fname]
            break
    rcParams["axes.unicode_minus"] = False

    judge_out = session.get("judge", {})
    tags = session.get("bloom_tags", [])
    turns = session.get("turns", [])
    stage_cov = judge_out.get("_stage_coverage") or {s: 0 for s in STAGES}

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle(
        f"砚友对话 · 质量 Dashboard  ({session.get('topic','(未指定主题)')})",
        fontsize=14,
        fontweight="bold",
    )

    # 左上：Bloom 饼图
    ax = axes[0][0]
    dist = _bloom_distribution(tags)
    if sum(dist) == 0:
        ax.text(0.5, 0.5, "(no bloom tags)", ha="center", va="center")
        ax.axis("off")
    else:
        ax.pie(dist, labels=BLOOM_LEVELS, colors=BLOOM_COLORS,
               autopct=lambda p: f"{p:.0f}%" if p > 0 else "", startangle=90)
    ax.set_title("Bloom's taxonomy 提问分布")

    # 右上：telling rate 折线
    ax = axes[0][1]
    xs, ys = _telling_per_turn(turns)
    if xs:
        ax.plot(xs, ys, marker="o", color="#d96a4a", linewidth=2)
        ax.set_ylim(0, 1)
        ax.axhline(y=0.2, color="gray", linestyle="--", linewidth=0.8)
        ax.text(xs[-1], 0.21, "目标 ≤0.2", fontsize=8, color="gray")
    ax.set_xlabel("agent 回合数")
    ax.set_ylabel("累计 telling rate")
    ax.set_title("Telling rate 折线（应低）")

    # 左下：A-E checkbox + 触达轮数
    ax = axes[1][0]
    ax.axis("off")
    ax.set_title("5 阶段覆盖（A-E）")
    for i, s in enumerate(STAGES):
        cnt = stage_cov.get(s, 0)
        mark = "[x]" if cnt > 0 else "[ ]"
        c = "#2e7d32" if cnt > 0 else "#bdbdbd"
        ax.text(0.05, 0.85 - i * 0.18, f"{mark}  {STAGE_LABELS[s]}   ({cnt} 轮)",
                fontsize=12, color=c, transform=ax.transAxes)

    # 右下：aha-moment
    ax = axes[1][1]
    ax.axis("off")
    aha = judge_out.get("aha_moment_confidence", 0.0)
    color = "#2e7d32" if aha >= 0.6 else ("#e08e0b" if aha >= 0.3 else "#c62828")
    tx = ax.transAxes
    ax.text(0.5, 0.62, f"{aha:.2f}", fontsize=48, ha="center",
            color=color, fontweight="bold", transform=tx)
    ax.text(0.5, 0.42, "Aha-moment confidence", fontsize=12, ha="center", transform=tx)
    ax.text(0.5, 0.22, judge_out.get("reason", "")[:80], fontsize=9,
            ha="center", color="#555", wrap=True, transform=tx)
    telling = judge_out.get("telling_rate", 0.0)
    probing = judge_out.get("probing_depth", 0.0)
    ax.text(0.5, 0.08, f"telling={telling:.2f}  probing={probing:.2f}",
            fontsize=10, ha="center", color="#333", transform=tx)

    plt.tight_layout(rect=(0, 0, 1, 0.96))
    plt.savefig(output, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"dashboard saved: {output}")


def main() -> None:
    p = argparse.ArgumentParser(description="对话质量 dashboard 生成器")
    p.add_argument("--session", required=True, help="session.json 路径")
    p.add_argument("--output", required=True, help="输出 PNG 路径")
    p.add_argument("--mock", action="store_true", help="judge/bloom 走 stub")
    args = p.parse_args()

    with open(args.session, encoding="utf-8") as f:
        session = json.load(f)
    session = _ensure_annotations(session, mock=args.mock)
    render(session, args.output)


if __name__ == "__main__":
    main()
