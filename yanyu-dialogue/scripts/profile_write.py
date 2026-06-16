#!/usr/bin/env python3
"""砚友 · 写用户画像（research / fusion 两个 mode 共享）

读取 session.json，与现有画像合并，通过 yanyu_core 的 Backend 抽象写回。
后端由 YANYU_BACKEND 选择：

- local（默认）：写 ~/.yanyu_kb/profiles/<user>.json，**无需飞书**，开箱即用。
- lark：lark-cli upsert Bitable（需 --app-token 或 YANYU_PROFILE_APP_TOKEN）。

合并规则见 ../references/profile-schema.md（实现于 _profile_backend.merge_session_into_profile）：
- topic_mastery[topic] += mastery_delta (clamp 0-5)
- stuck_points / methodology_quotes / aha_moment_log: append (带日期)
- style_response: 覆盖；session_count += 1；domain_familiarity_tags: add topic

历史变化：旧版各自 shell out lark-cli，且 profile_write 通过 subprocess 再调
profile_read 取 record_id（三层进程套娃）；现在全部走 in-process backend，record_id
由 backend 自身维护——lark 更新定位更稳，且不再有"缺 record_id 直接报错"的失败态。

CLI：
    python3 scripts/profile_write.py --user <user_id> --session <session.json>
    YANYU_BACKEND=lark python3 scripts/profile_write.py --user <u> --session <s> --app-token <tok>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from _profile_backend import build_backend, merge_session_into_profile, profile_to_dict

DEFAULT_PROFILE = os.environ.get("YANYU_PROFILE", "new_tenant")
DEFAULT_APP_TOKEN = os.environ.get("YANYU_PROFILE_APP_TOKEN", "")
DEFAULT_TABLE = os.environ.get("YANYU_PROFILE_TABLE", "yanyu_profile")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write/upsert user profile via yanyu_core backend")
    p.add_argument("--user", required=True)
    p.add_argument("--session", required=True, help="path to session.json")
    p.add_argument("--profile", default=DEFAULT_PROFILE, help="lark backend: lark-cli profile")
    p.add_argument("--app-token", default=DEFAULT_APP_TOKEN, help="lark backend: Bitable app_token")
    p.add_argument("--table", default=DEFAULT_TABLE, help="lark backend: 画像表 table id")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    session = json.loads(Path(args.session).read_text(encoding="utf-8"))

    backend = build_backend(profile=args.profile, app_token=args.app_token, table=args.table)
    existing = backend.read_profile(args.user)
    merged = merge_session_into_profile(existing, session)
    backend.upsert_profile(merged)

    # 回显写入后的画像，便于调用方 / 测试核对
    json.dump(profile_to_dict(merged), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
