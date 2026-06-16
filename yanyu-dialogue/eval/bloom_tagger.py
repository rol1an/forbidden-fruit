"""砚友 · Bloom's taxonomy 自动标注器

把 agent 一回合的提问文本打成 Bloom's 六级标签：
remember / understand / apply / analyze / evaluate / create

依赖：anthropic（缺失则回退 stub，输出警告但不报错）。
API key 从环境变量 ANTHROPIC_API_KEY 读，--mock 模式不真调 API。

CLI：
    python3 -m eval.bloom_tagger --question "你觉得多向量索引能彻底解决长尾召回吗？"
    python3 -m eval.bloom_tagger --question "..." --mock

学术锚点：arXiv:2511.10903（GPT-4 在 Bloom's 6 层分类上 accuracy 0.72-0.73）。
"""
from __future__ import annotations

import argparse
import json
import os
import re
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

# 决策 7: 砚石痕迹 callout 消费的砚友动词标签 (避免 jargon leak)
# 详见 references/inkstone-trace.md §术语转译表
BLOOM_LABEL_CN = {
    "remember": "触碰",
    "understand": "看懂",
    "apply": "拆解",
    "analyze": "重构",
    "evaluate": "评判",
    "create": "创造",
}


def _attach_chinese_label(result: dict[str, Any]) -> dict[str, Any]:
    """给输出 dict 补 chinese_label 字段。不破坏 caller 兼容性 (旧 caller 不读这个字段)。"""
    level = result.get("level")
    if level in BLOOM_LABEL_CN:
        result["chinese_label"] = BLOOM_LABEL_CN[level]
    else:
        result["chinese_label"] = None
    return result

SYSTEM_PROMPT = """你是一个 Bloom's taxonomy 自动标注器。给定一个老师/agent 对学生抛出的提问，
判断它要求学生调动哪一级认知：

- remember: 回忆事实、定义、术语（"什么是 X""列出 Y"）
- understand: 解释、归纳、复述（"用自己的话讲讲 X""X 跟 Y 是什么关系"）
- apply: 在新情境用知识（"如果换成 X 怎么办""举一个 Y 的例子"）
- analyze: 拆分结构、找根因、比较（"哪一层是瓶颈""为什么会出 X 问题"）
- evaluate: 判断、评价、挑战（"你觉得 X 真的能解决 Y 吗""有什么反驳"）
- create: 设计、构造、合成（"重新设计 X""提出一个新方案"）

输出**严格 JSON**：{"level": "<one of six>", "confidence": 0.0-1.0, "reason": "<≤20 字>"}
不要其他字符。"""


def _stub_tag(question: str) -> dict[str, Any]:
    """无 anthropic 包 / mock 模式时的回退打标。

    用简单启发式关键词匹配，准度不高但保证 demo 不挂。
    """
    q = question.lower()
    rules: list[tuple[str, list[str]]] = [
        ("create", ["重新设计", "提出", "构造", "如果让你设计", "新方案"]),
        ("evaluate", ["你觉得", "真的能", "信吗", "反驳", "挑战", "好坏"]),
        ("analyze", ["瓶颈", "为什么", "根因", "哪一层", "拆解", "区别"]),
        ("apply", ["如果", "换成", "举例", "应用", "怎么办"]),
        ("understand", ["关系", "解释", "归纳", "复述", "用自己的话"]),
        ("remember", ["什么是", "定义", "列出", "背诵"]),
    ]
    for level, kws in rules:
        for kw in kws:
            if kw in q:
                return _attach_chinese_label({
                    "level": level,
                    "confidence": 0.55,
                    "reason": f"stub keyword: {kw}",
                })
    return _attach_chinese_label(
        {"level": "understand", "confidence": 0.30, "reason": "stub fallback"}
    )


def tag_question(question: str, mock: bool = False) -> dict[str, Any]:
    """主入口：给一句提问打 Bloom's 标签。

    真 LLM 调用通过 eval.llm_backend 路由, 支持 YANYU_LLM_BACKEND=anthropic|deepseek。
    Backend / API key / network 任一失败都 fallback 到 stub keyword tagger。
    """
    if mock:
        return _stub_tag(question)

    from . import llm_backend  # type: ignore

    if not llm_backend.has_credential():
        sys.stderr.write(
            f"[bloom_tagger] {llm_backend.backend_name()} credential not set; "
            "falling back to stub.\n"
        )
        return _stub_tag(question)

    try:
        text = llm_backend.call_llm(
            system=SYSTEM_PROMPT,
            user=f"提问：{question}",
            max_tokens=200,
        )
    except llm_backend.LLMError as e:
        sys.stderr.write(f"[bloom_tagger] {e}; falling back to stub.\n")
        return _stub_tag(question)

    # 防御性 JSON 解析 (DeepSeek 偶尔会包 ```json fence)
    text = _strip_json_fence(text)
    try:
        result = json.loads(text)
        # well-formed JSON 也可能是 list / 标量（model 没按指令吐 object）——
        # 不挡住会在 result.get() 抛 AttributeError，绕过下面的 fallback。
        if not isinstance(result, dict):
            raise ValueError(f"expected JSON object, got {type(result).__name__}")
        if result.get("level") not in BLOOM_LEVELS:
            raise ValueError(f"bad level: {result.get('level')}")
        return _attach_chinese_label(result)
    except (json.JSONDecodeError, ValueError) as e:
        sys.stderr.write(f"[bloom_tagger] LLM bad JSON ({e}); falling back to stub.\n")
        return _stub_tag(question)


def _strip_json_fence(text: str) -> str:
    """剥掉 ```json ... ``` 围栏 (DeepSeek / 某些 model 习惯包 fence)。

    同时兼容单行围栏（```json {...} ``` 整段在一行）——旧实现按换行切，
    单行时 len(lines)<2 直接放过，导致 json.loads 撞反引号失败。
    """
    t = text.strip()
    if not t.startswith("```"):
        return t
    t = re.sub(r"^```[A-Za-z0-9_-]*\s*", "", t)  # 开头 ```lang（同行或独立一行）
    t = re.sub(r"\s*```$", "", t)                # 结尾 ```
    return t.strip()


def main() -> None:
    p = argparse.ArgumentParser(description="Bloom's taxonomy 提问标注器")
    p.add_argument("--question", required=True, help="agent 的一句提问")
    p.add_argument("--mock", action="store_true", help="不调 API，纯启发式")
    args = p.parse_args()

    result = tag_question(args.question, mock=args.mock)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
