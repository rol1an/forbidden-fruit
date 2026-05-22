#!/usr/bin/env python3
"""砚友 · 写用户画像（供 yanyu-grinding / yanyu-fusion 共享）

读取 session.json，与现有画像合并，调用 lark-cli base +record-upsert 写回 Bitable。

合并规则见 ../references/profile-schema.md：
- topic_mastery[topic] += mastery_delta (clamp 0-5)
- stuck_points / methodology_quotes / aha_moment_log: append (带日期)
- style_response: 覆盖
- session_count += 1
- domain_familiarity_tags: add topic if not in
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_PROFILE = os.environ.get("YANYU_PROFILE", "new_tenant")
DEFAULT_APP_TOKEN = os.environ.get("YANYU_PROFILE_APP_TOKEN", "")
DEFAULT_TABLE = os.environ.get("YANYU_PROFILE_TABLE", "yanyu_profile")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write/upsert user profile to Bitable")
    p.add_argument("--user", required=True)
    p.add_argument("--session", required=True, help="path to session.json")
    p.add_argument("--profile", default=DEFAULT_PROFILE)
    p.add_argument("--app-token", default=DEFAULT_APP_TOKEN, required=not DEFAULT_APP_TOKEN)
    p.add_argument("--table", default=DEFAULT_TABLE)
    return p.parse_args()


def read_existing(args: argparse.Namespace) -> dict:
    """复用 profile_read 逻辑取现有画像（如果有）。"""
    here = Path(__file__).parent
    cmd = [
        sys.executable, str(here / "profile_read.py"),
        "--user", args.user,
        "--profile", args.profile,
        "--app-token", args.app_token,
        "--table", args.table,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    return json.loads(proc.stdout)


def merge(existing: dict, session: dict) -> dict:
    """按 schema 合并规则产出待写回的 fields dict。"""
    today = datetime.now().strftime("%Y-%m-%d")
    topic = session.get("topic")

    # mastery clamp 0-5
    mastery = dict(existing.get("topic_mastery", {}))
    if topic:
        new_val = mastery.get(topic, 0) + session.get("mastery_delta", 0)
        mastery[topic] = max(0, min(5, new_val))

    stuck = list(existing.get("stuck_points", []))
    for sp in session.get("stuck_points_added", []):
        line = f"{topic} :: {sp}" if topic else sp
        if line not in stuck:
            stuck.append(line)

    quotes = list(existing.get("methodology_quotes", []))
    q = session.get("user_methodology")
    if q:
        quotes.append(f"{today} :: {q}")

    aha = list(existing.get("aha_moment_log", []))
    a = session.get("aha_moment_question")
    if a and topic:
        aha.append(f"{today} :: {topic} :: {a}")

    domain_tags = list(existing.get("domain_familiarity_tags", []))
    if topic and topic not in domain_tags:
        domain_tags.append(topic)

    return {
        "user_id": existing["user_id"],
        "display_name": existing.get("display_name") or session.get("display_name") or existing["user_id"],
        "topic_mastery": json.dumps(mastery, ensure_ascii=False),
        "stuck_points": "\n".join(stuck),
        "style_response": session.get("style_response") or existing.get("style_response"),
        "methodology_quotes": "\n".join(quotes),
        "aha_moment_log": "\n".join(aha),
        "last_session_at": datetime.now().strftime("%Y/%m/%d"),
        "session_count": int(existing.get("session_count") or 0) + 1,
        "domain_familiarity_tags": domain_tags,
    }


def write_record(args: argparse.Namespace, fields: dict, record_id: str | None) -> None:
    """写入画像。

    lark-cli base +record-upsert 不会按业务键(user_id)自动 upsert:
    - 不传 --record-id => 新建一行
    - 传 --record-id   => 更新该 record_id

    所以这里依赖上游 profile_read 给出的 record_id 决定走哪条路径,
    避免每次都新建脏行。
    """
    payload = json.dumps(fields, ensure_ascii=False)
    cmd = [
        "lark-cli", "base", "+record-upsert",
        "--profile", args.profile, "--as", "bot",
        "--base-token", args.app_token,
        "--table-id", args.table,
        "--json", payload,
    ]
    if record_id:
        cmd.extend(["--record-id", record_id])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    sys.stdout.write(proc.stdout)


def main() -> int:
    args = parse_args()
    if not args.app_token:
        sys.stderr.write("ERROR: --app-token 必填，或设 YANYU_PROFILE_APP_TOKEN\n")
        return 2
    session = json.loads(Path(args.session).read_text(encoding="utf-8"))
    existing = read_existing(args)
    record_id: str | None = None
    if existing.get("is_new"):
        existing = {"user_id": args.user, "topic_mastery": {}, "stuck_points": [], "session_count": 0}
    else:
        record_id = existing.get("record_id")
        if not record_id:
            sys.stderr.write(
                "ERROR: 现有画像缺 record_id,无法定位更新目标。"
                "请确认 profile_read.py 返回里带 record_id;否则会重复新建脏行。\n"
            )
            return 3
    fields = merge(existing, session)
    write_record(args, fields, record_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
