"""砚友 · profile 脚本共享层

把"选哪个 backend / Profile ⇄ dict / session 合并"集中到一处，供
profile_read.py 与 profile_write.py 复用。**所有飞书 / 本地存储细节都在
yanyu_core 里**——本模块只做 CLI 适配，不再各自 shell out lark-cli（消除
旧版 profile_read/write 的重复 lark 逻辑 + 三层 subprocess 套娃）。

后端由 YANYU_BACKEND 选择（local 默认 / lark），见 yanyu_core/factory.py。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 允许 `python3 scripts/profile_*.py` 直接从仓库根 import yanyu_core
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from yanyu_core import Backend, Profile  # noqa: E402


def build_backend(
    *, profile: str | None = None, app_token: str | None = None, table: str | None = None
) -> Backend:
    """按 YANYU_BACKEND 构造后端。

    - local（默认）：纯文件存储，**无需飞书凭据**，开箱即用。
    - lark：lark-cli 查/写 Bitable；profile/app_token/table 可由 CLI 覆盖，
      缺省走 yanyu_core 的环境变量。
    """
    name = (os.environ.get("YANYU_BACKEND") or "local").lower()
    if name == "local":
        from yanyu_core.local_backend import LocalFileBackend

        return LocalFileBackend()
    if name == "lark":
        from yanyu_core.lark_backend import LarkBackend

        return LarkBackend(
            profile=profile,
            profile_app_token=app_token or None,
            profile_table=table,
        )
    # 其余值交给 factory 统一报错，保持单一出错口径
    from yanyu_core import load_backend

    return load_backend(name)


def profile_to_dict(p: Profile) -> dict[str, Any]:
    """Profile → 归一化 JSON（与历史 profile_read.py 输出形状一致）。"""
    return {
        "user_id": p.user_id,
        "record_id": p.record_id,
        "display_name": p.display_name,
        "topic_mastery": p.topic_mastery,
        "stuck_points": p.stuck_points,
        "style_response": p.style_response,
        "methodology_quotes": p.methodology_quotes,
        "aha_moment_log": p.aha_moment_log,
        "last_session_at": p.last_session_at,
        "session_count": p.session_count,
        "domain_familiarity_tags": p.domain_familiarity_tags,
        "is_new": p.is_new,
    }


def merge_session_into_profile(existing: Profile, session: dict[str, Any]) -> Profile:
    """按 ../references/profile-schema.md 的合并规则，把一次 session 并入现有画像。

    新用户（is_new=True）的 existing 各字段本就为空、session_count=0，合并后
    自然得到 session_count=1——无需像旧版那样特判 is_new。
    """
    today = datetime.now().strftime("%Y-%m-%d")
    topic = session.get("topic")

    # topic_mastery[topic] += mastery_delta，clamp 0-5
    mastery = dict(existing.topic_mastery)
    if topic:
        new_val = mastery.get(topic, 0) + session.get("mastery_delta", 0)
        mastery[topic] = max(0, min(5, new_val))

    # stuck_points：append "{topic} :: {sp}"，去重
    stuck = list(existing.stuck_points)
    for sp in session.get("stuck_points_added", []):
        line = f"{topic} :: {sp}" if topic else sp
        if line not in stuck:
            stuck.append(line)

    # methodology_quotes / aha_moment_log：带日期 append
    quotes = list(existing.methodology_quotes)
    q = session.get("user_methodology")
    if q:
        quotes.append(f"{today} :: {q}")

    aha = list(existing.aha_moment_log)
    a = session.get("aha_moment_question")
    if a and topic:
        aha.append(f"{today} :: {topic} :: {a}")

    domain_tags = list(existing.domain_familiarity_tags)
    if topic and topic not in domain_tags:
        domain_tags.append(topic)

    return Profile(
        user_id=existing.user_id,
        topic_mastery=mastery,
        stuck_points=stuck,
        style_response=session.get("style_response") or existing.style_response,
        methodology_quotes=quotes,
        aha_moment_log=aha,
        domain_familiarity_tags=domain_tags,
        session_count=existing.session_count + 1,
        last_session_at=datetime.now().strftime("%Y/%m/%d"),
        display_name=existing.display_name or session.get("display_name") or existing.user_id,
        record_id=existing.record_id,  # lark upsert 靠它定位行；local 忽略
    )
