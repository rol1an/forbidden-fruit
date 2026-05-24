"""砚友 · LLM backend 统一封装

支持两种 backend, 由环境变量 YANYU_LLM_BACKEND 选择:
- "anthropic" (默认): 用 ANTHROPIC_API_KEY + claude-haiku-4-5
- "deepseek": 用 DEEPSEEK_API_KEY + deepseek-chat (OpenAI-compatible, 用 requests 调 HTTP)

bloom_tagger.py / judge.py 共用本模块, 避免重复实现。

CLI 测试:
    DEEPSEEK_API_KEY=sk-... YANYU_LLM_BACKEND=deepseek python3 -c "
        from eval.llm_backend import call_llm
        print(call_llm(system='只回 ping', user='ping', max_tokens=50))
    "
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

DEFAULT_BACKEND = os.environ.get("YANYU_LLM_BACKEND", "anthropic")

ANTHROPIC_MODEL_DEFAULT = "claude-haiku-4-5"
DEEPSEEK_MODEL_DEFAULT = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1/chat/completions"


class LLMError(Exception):
    """LLM 调用失败 (network / auth / parse 等)"""


def _call_anthropic(
    system: str, user: str, max_tokens: int = 500, model: str | None = None
) -> str:
    """Anthropic claude API 调用。"""
    try:
        import anthropic  # type: ignore
    except ImportError as e:
        raise LLMError(f"anthropic package not installed: {e}")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model or ANTHROPIC_MODEL_DEFAULT,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text.strip()


def _call_deepseek(
    system: str, user: str, max_tokens: int = 500, model: str | None = None
) -> str:
    """DeepSeek OpenAI-compatible API 调用 (用 requests 直调 HTTP, 不依赖 openai SDK)。"""
    try:
        import requests  # type: ignore
    except ImportError as e:
        raise LLMError(f"requests package not installed: {e}")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise LLMError("DEEPSEEK_API_KEY not set")

    try:
        resp = requests.post(
            DEEPSEEK_BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model or DEEPSEEK_MODEL_DEFAULT,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.0,  # Bloom 标注 / judge 都要确定性
            },
            timeout=60,
        )
    except requests.RequestException as e:
        raise LLMError(f"DeepSeek HTTP failed: {e}")

    if resp.status_code != 200:
        raise LLMError(f"DeepSeek non-200: {resp.status_code} {resp.text[:200]}")

    try:
        body = resp.json()
        return body["choices"][0]["message"]["content"].strip()
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise LLMError(f"DeepSeek response parse failed: {e}: {resp.text[:200]}")


def call_llm(
    system: str,
    user: str,
    max_tokens: int = 500,
    model: str | None = None,
    backend: str | None = None,
) -> str:
    """统一入口。返回 model 输出文本 (已 strip)。

    backend: 不传则用 YANYU_LLM_BACKEND env var (默认 anthropic)。
    model: 不传则用 YANYU_LLM_MODEL env var, 再不传走 backend 默认。
        用例: YANYU_LLM_MODEL=deepseek-reasoner 切到 V4-Flash thinking 模式。
    raises LLMError on any failure—— caller 应该 catch 并 fallback 到 stub。
    """
    chosen = (backend or DEFAULT_BACKEND).lower()
    if model is None:
        model = os.environ.get("YANYU_LLM_MODEL") or None
    if chosen == "anthropic":
        return _call_anthropic(system, user, max_tokens, model)
    if chosen == "deepseek":
        return _call_deepseek(system, user, max_tokens, model)
    raise LLMError(f"unknown YANYU_LLM_BACKEND: {chosen} (expected anthropic | deepseek)")


def backend_name() -> str:
    """供 caller 在日志里报告当前用哪个 backend。"""
    return (DEFAULT_BACKEND or "anthropic").lower()


def has_credential(backend: str | None = None) -> bool:
    """检查 env var 是否设置好对应 backend 的 API key。"""
    chosen = (backend or DEFAULT_BACKEND).lower()
    if chosen == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    if chosen == "deepseek":
        return bool(os.environ.get("DEEPSEEK_API_KEY"))
    return False


if __name__ == "__main__":
    # 简单 smoke test: 跑当前 backend 一次 ping 调用
    if not has_credential():
        sys.stderr.write(
            f"[llm_backend] {backend_name()} credential not set; "
            "set ANTHROPIC_API_KEY or DEEPSEEK_API_KEY in env\n"
        )
        raise SystemExit(2)
    try:
        out = call_llm(system="回复'pong'", user="ping", max_tokens=20)
        print(f"[{backend_name()}] {out}")
    except LLMError as e:
        sys.stderr.write(f"[llm_backend] {e}\n")
        raise SystemExit(1)
