#!/usr/bin/env python3
"""砚友 · 读用户画像（research / fusion 两个 mode 共享）

通过 yanyu_core 的 Backend 抽象读取画像，归一化 JSON 输出到 stdout。
后端由 YANYU_BACKEND 选择：

- local（默认）：从 ~/.yanyu_kb/profiles/<user>.json 读，**无需飞书**，开箱即用。
- lark：lark-cli 查 Bitable（需 --app-token 或 YANYU_PROFILE_APP_TOKEN）。

首次用户输出 {"user_id":..., "is_new": true, ...}。
Schema 详见 ../references/profile-schema.md。

CLI：
    python3 scripts/profile_read.py --user <user_id>
    YANYU_BACKEND=lark python3 scripts/profile_read.py --user <user_id> --app-token <tok>
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from _profile_backend import build_backend, profile_to_dict

DEFAULT_PROFILE = os.environ.get("YANYU_PROFILE", "new_tenant")
DEFAULT_APP_TOKEN = os.environ.get("YANYU_PROFILE_APP_TOKEN", "")
DEFAULT_TABLE = os.environ.get("YANYU_PROFILE_TABLE", "yanyu_profile")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Read user profile via yanyu_core backend")
    p.add_argument("--user", required=True, help="飞书 open_id 或自定义 user_id")
    p.add_argument("--profile", default=DEFAULT_PROFILE, help="lark backend: lark-cli profile")
    p.add_argument("--app-token", default=DEFAULT_APP_TOKEN, help="lark backend: Bitable app_token")
    p.add_argument("--table", default=DEFAULT_TABLE, help="lark backend: 画像表 table id")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    backend = build_backend(profile=args.profile, app_token=args.app_token, table=args.table)
    profile = backend.read_profile(args.user)
    json.dump(profile_to_dict(profile), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
