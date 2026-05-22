#!/usr/bin/env python3
"""砚友 · 读用户画像（供 yanyu-dialogue grinding / fusion 两个 mode 共享）

调用 lark-cli base +record-search 拿当前用户的画像 JSON。
首次用户返回 {"user_id":..., "is_new": true}。

Schema 详见 ../references/profile-schema.md。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

# 默认 profile / app_token 走环境变量或 CLI 参数，避免硬编码
DEFAULT_PROFILE = os.environ.get("YANYU_PROFILE", "new_tenant")
DEFAULT_APP_TOKEN = os.environ.get("YANYU_PROFILE_APP_TOKEN", "")
DEFAULT_TABLE = os.environ.get("YANYU_PROFILE_TABLE", "yanyu_profile")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Read user profile from Bitable")
    p.add_argument("--user", required=True, help="飞书 open_id 或自定义 user_id")
    p.add_argument("--profile", default=DEFAULT_PROFILE)
    p.add_argument("--app-token", default=DEFAULT_APP_TOKEN, required=not DEFAULT_APP_TOKEN)
    p.add_argument("--table", default=DEFAULT_TABLE)
    return p.parse_args()


def search_profile(args: argparse.Namespace) -> dict:
    """用 lark-cli 在 Bitable 查 user_id == args.user 的记录。"""
    payload = json.dumps({"keyword": args.user, "search_fields": ["user_id"]}, ensure_ascii=False)
    cmd = [
        "lark-cli", "base", "+record-search",
        "--profile", args.profile, "--as", "bot",
        "--base-token", args.app_token,
        "--table-id", args.table,
        "--json", payload,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    raw = json.loads(proc.stdout)
    records = (raw.get("data", {}) or {}).get("records", []) or []
    # 精确匹配 user_id
    for r in records:
        fields = r.get("fields", {}) or {}
        if fields.get("user_id") == args.user:
            # lark-cli base 返回的 record 顶层一般有 record_id;部分版本叫 id,做兼容
            record_id = r.get("record_id") or r.get("id")
            return normalize(fields, record_id=record_id)
    return {"user_id": args.user, "is_new": True}


def normalize(fields: dict, record_id: str | None = None) -> dict:
    """把 Bitable 富文本字段反序列化成结构化 JSON。"""

    def parse_json_field(name: str, fallback):
        val = fields.get(name)
        if not val:
            return fallback
        try:
            return json.loads(val)
        except (TypeError, ValueError):
            return fallback

    def split_lines(name: str) -> list[str]:
        val = fields.get(name)
        if not val:
            return []
        return [line.strip() for line in str(val).splitlines() if line.strip()]

    return {
        "user_id": fields.get("user_id"),
        "record_id": record_id,  # profile_write 走 update 路径需要
        "display_name": fields.get("display_name"),
        "topic_mastery": parse_json_field("topic_mastery", {}),
        "stuck_points": split_lines("stuck_points"),
        "style_response": fields.get("style_response"),
        "methodology_quotes": split_lines("methodology_quotes"),
        "aha_moment_log": split_lines("aha_moment_log"),
        "last_session_at": fields.get("last_session_at"),
        "session_count": fields.get("session_count", 0),
        "domain_familiarity_tags": fields.get("domain_familiarity_tags") or [],
        "is_new": False,
    }


def main() -> int:
    args = parse_args()
    if not args.app_token:
        sys.stderr.write("ERROR: --app-token 必填，或设 YANYU_PROFILE_APP_TOKEN\n")
        return 2
    result = search_profile(args)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
