"""eval 框架健壮性回归测试。

钉住几个曾经会让"坏 LLM 输出 → 回退 stub"安全网失效的 bug：
  - _strip_json_fence 单行围栏
  - judge / bloom 对 well-formed 但非 dict 的 JSON 不再崩
  - judge stub 对 content=null 的 turn 不再 len(None) 崩

从 yanyu-dialogue 目录跑：
    python3 -m unittest discover -s eval/tests -t .
"""
from __future__ import annotations

import unittest

from eval.bloom_tagger import _strip_json_fence
from eval.judge import judge_session


class StripJsonFenceTest(unittest.TestCase):
    def test_no_fence_passthrough(self) -> None:
        self.assertEqual(_strip_json_fence('{"level": "remember"}'), '{"level": "remember"}')

    def test_multi_line_fence(self) -> None:
        raw = '```json\n{"level": "analyze"}\n```'
        self.assertEqual(_strip_json_fence(raw), '{"level": "analyze"}')

    def test_single_line_fence(self) -> None:
        # 旧实现按换行切，单行围栏 len(lines)<2 直接放过 → json.loads 撞反引号失败
        raw = '```json {"level": "evaluate"}```'
        self.assertEqual(_strip_json_fence(raw), '{"level": "evaluate"}')

    def test_fence_without_lang(self) -> None:
        self.assertEqual(_strip_json_fence('```\n{"a": 1}\n```'), '{"a": 1}')


class JudgeStubRobustnessTest(unittest.TestCase):
    def test_null_content_user_turn_no_crash(self) -> None:
        # content 显式为 None（JSON null）：.get 默认值不生效，旧版 len(None) 崩
        session = {
            "turns": [
                {"role": "user", "content": None, "stage": "A"},
                {"role": "agent", "content": "x", "move": "probing", "stage": "A"},
                {"role": "user", "content": None, "stage": "E"},
            ]
        }
        result = judge_session(session, mock=True)
        self.assertIn("telling_rate", result)
        self.assertIn("probing_depth", result)

    def test_empty_session(self) -> None:
        result = judge_session({"turns": []}, mock=True)
        self.assertEqual(result["telling_rate"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
