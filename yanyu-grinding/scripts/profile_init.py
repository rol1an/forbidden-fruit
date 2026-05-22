#!/usr/bin/env python3
"""砚友 · 初始化用户画像 Bitable

第一次部署时跑一次:创建 "砚友用户画像" Bitable + yanyu_profile 表 + 9 个字段。

幂等保证:先用 `lark-cli drive +search --query "砚友用户画像" --doc-types bitable`
查重,已存在就跳过创建并打印现成 app_token。

字段定义来自 ../references/profile-schema.md (单一来源)。

输出:JSON 到 stdout,形如:
  {"app_token":"app_xxx","table_id":"tbl_xxx","action":"created"|"existed"}

用法:
  python3 profile_init.py --profile new_tenant            # 真跑
  python3 profile_init.py --profile new_tenant --dry-run  # 只打印命令,不执行

跑完后建议:
  export YANYU_PROFILE_APP_TOKEN=app_xxx
  供 profile_read.py / profile_write.py 使用。
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys

BASE_NAME = "砚友用户画像"
TABLE_NAME = "yanyu_profile"

# 字段定义按 profile-schema.md 表格顺序;首列(user_id) 由 +table-create 的 --fields 首元素改造
PRIMARY_FIELD = {"name": "user_id", "type": "text"}

EXTRA_FIELDS: list[dict] = [
    {"name": "display_name", "type": "text"},
    # 富文本字段在 base v3 里就是普通 text,JSON 字符串当字符串写
    {"name": "topic_mastery", "type": "text"},
    {"name": "stuck_points", "type": "text"},
    {
        "name": "style_response",
        "type": "select",
        "multiple": False,
        "options": [
            {"name": "prefers_challenge", "hue": "Red", "lightness": "Light"},
            {"name": "prefers_guidance", "hue": "Blue", "lightness": "Light"},
            {"name": "prefers_affirmation", "hue": "Green", "lightness": "Light"},
        ],
    },
    {"name": "methodology_quotes", "type": "text"},
    {"name": "aha_moment_log", "type": "text"},
    {
        "name": "last_session_at",
        "type": "datetime",
        "style": {"format": "yyyy-MM-dd HH:mm"},
    },
    {
        "name": "session_count",
        "type": "number",
        "style": {"type": "plain", "precision": 0},
    },
    # 多值 select,选项随用户实际涉足领域增长;首次不预置,允许平台自动追加
    {
        "name": "domain_familiarity_tags",
        "type": "select",
        "multiple": True,
        "options": [],
    },
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Init yanyu_profile Bitable (idempotent)")
    p.add_argument("--profile", default=os.environ.get("YANYU_PROFILE", "new_tenant"))
    p.add_argument(
        "--dry-run", action="store_true",
        help="只打印 lark-cli 命令,不执行(用于验证 CLI 调用正确性)",
    )
    return p.parse_args()


def run(cmd: list[str], dry_run: bool) -> dict:
    """跑一条 lark-cli 命令,返回解析后的 JSON;dry-run 模式只打印不执行。"""
    sys.stderr.write(f"[cmd] {shlex.join(cmd)}\n")
    if dry_run:
        return {}
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(f"WARN: 非 JSON 输出: {proc.stdout[:200]}\n")
        return {}


def find_existing_base(args: argparse.Namespace) -> str | None:
    """用 drive +search 查 "砚友用户画像" 是否已经存在;存在返回 app_token。"""
    cmd = [
        "lark-cli", "drive", "+search",
        "--profile", args.profile,
        "--query", BASE_NAME,
        "--doc-types", "bitable",
        "--only-title",
        "--format", "json",
    ]
    raw = run(cmd, args.dry_run)
    if args.dry_run:
        return None
    results = raw.get("results") or []
    for r in results:
        # search 返回的 title 可能带 <h> 高亮,简单 strip
        title = (r.get("title") or "").replace("<h>", "").replace("</h>", "")
        if title.strip() == BASE_NAME:
            # bitable 的 token 通常在 r["token"] 或 r["obj_token"]
            return r.get("token") or r.get("obj_token") or r.get("doc_token")
    return None


def create_base(args: argparse.Namespace) -> str:
    cmd = [
        "lark-cli", "base", "+base-create",
        "--profile", args.profile, "--as", "bot",
        "--name", BASE_NAME,
    ]
    raw = run(cmd, args.dry_run)
    if args.dry_run:
        return "<dry-run-app-token>"
    base = (raw.get("data") or raw).get("base") or raw.get("base") or {}
    token = base.get("app_token") or base.get("token")
    if not token:
        sys.stderr.write(f"ERROR: 创建 Base 后拿不到 app_token,raw={raw}\n")
        sys.exit(4)
    return token


def create_table(args: argparse.Namespace, app_token: str) -> str:
    cmd = [
        "lark-cli", "base", "+table-create",
        "--profile", args.profile, "--as", "bot",
        "--base-token", app_token,
        "--name", TABLE_NAME,
        # CLI 用 --fields 的首元素改写默认首列;这样 user_id 直接成为主列
        "--fields", json.dumps([PRIMARY_FIELD], ensure_ascii=False),
    ]
    raw = run(cmd, args.dry_run)
    if args.dry_run:
        return "<dry-run-table-id>"
    table = (raw.get("data") or raw).get("table") or raw.get("table") or {}
    table_id = table.get("table_id") or table.get("id")
    if not table_id:
        sys.stderr.write(f"ERROR: 建表后拿不到 table_id,raw={raw}\n")
        sys.exit(5)
    return table_id


def create_fields(args: argparse.Namespace, app_token: str, table_id: str) -> None:
    for fld in EXTRA_FIELDS:
        cmd = [
            "lark-cli", "base", "+field-create",
            "--profile", args.profile, "--as", "bot",
            "--base-token", app_token,
            "--table-id", table_id,
            "--json", json.dumps(fld, ensure_ascii=False),
        ]
        run(cmd, args.dry_run)


def main() -> int:
    args = parse_args()

    existing = find_existing_base(args)
    if existing and not args.dry_run:
        out = {"app_token": existing, "table_id": None, "action": "existed"}
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        sys.stderr.write(
            f"\n已存在 Base '{BASE_NAME}',跳过创建。\n"
            f"export YANYU_PROFILE_APP_TOKEN={existing}\n"
        )
        return 0

    app_token = create_base(args)
    table_id = create_table(args, app_token)
    create_fields(args, app_token, table_id)

    out = {"app_token": app_token, "table_id": table_id, "action": "created"}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if not args.dry_run:
        sys.stderr.write(
            f"\n初始化完成。请 export 下面两个环境变量供后续脚本使用:\n"
            f"export YANYU_PROFILE_APP_TOKEN={app_token}\n"
            f"export YANYU_PROFILE_TABLE={table_id}\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
