"""砚友 · Backend 工厂

按环境变量 YANYU_BACKEND 选具体实现。默认 local——保证非飞书用户开箱即用，
也保证飞书 API 额度耗尽时一行 env 即可降级。
"""
from __future__ import annotations

import os

from .backend import Backend


def load_backend(name: str | None = None) -> Backend:
    """加载 backend 实例。

    name 优先级：函数参数 > YANYU_BACKEND 环境变量 > 默认 "local"。
    支持值：`local` / `lark`。
    """
    resolved = (name or os.environ.get("YANYU_BACKEND") or "local").lower()
    if resolved == "lark":
        from .lark_backend import LarkBackend
        return LarkBackend()
    if resolved == "local":
        from .local_backend import LocalFileBackend
        return LocalFileBackend()
    raise ValueError(
        f"Unknown YANYU_BACKEND={resolved!r}; expected 'local' or 'lark'"
    )
