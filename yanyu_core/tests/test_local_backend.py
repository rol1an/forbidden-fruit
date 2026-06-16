"""LocalFileBackend 单测。

无 pytest 时直接 `python3 test_local_backend.py` 跑 stdlib 兜底；
有 pytest 时 pytest 自动发现并跑——同样的 case 名。
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# 允许从仓库根目录直接 `python3 yanyu_core/tests/test_local_backend.py`
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from yanyu_core import Article, LocalFileBackend, Profile  # noqa: E402


class LocalBackendArticleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.backend = LocalFileBackend(root=self._tmp.name)

    def test_write_read_roundtrip(self) -> None:
        doc = Article(
            title="RAG 评估方法论",
            body_xml=(
                "<h1>RAG 评估方法论</h1>"
                "<p>核心是 <b>recall@k</b> 与 nDCG。</p>"
                "<callout emoji=\"📌\">章节要点：评估比加 rerank 重要</callout>"
                "<code language=\"python\">print('hi')</code>"
            ),
            tags=["RAG", "评估", "LLM"],
            source_url="https://example.com/x",
            extra={"author": "山月"},
        )
        path = self.backend.write_article(doc)
        self.assertTrue(Path(path).exists())
        meta_path = Path(path).with_suffix(".meta.json")
        self.assertTrue(meta_path.exists())

        # 路径与文件名 slug 验证
        self.assertIn("RAG-评估方法论", path)

        # 读回——按 slug 而非全路径
        slug = Path(path).stem
        back = self.backend.read_article(slug)
        self.assertEqual(back.title, "RAG 评估方法论")
        self.assertEqual(set(back.tags), {"RAG", "评估", "LLM"})
        self.assertEqual(back.source_url, "https://example.com/x")
        self.assertEqual(back.extra.get("author"), "山月")

        # markdown 简化验证
        self.assertIn("# RAG 评估方法论", back.body_xml)
        self.assertIn("**recall@k**", back.body_xml)
        self.assertIn("```python", back.body_xml)
        # callout 退化成 > emoji 内容
        self.assertIn("> 📌", back.body_xml)
        # HTML 标签全部清掉
        self.assertNotIn("<p>", back.body_xml)
        self.assertNotIn("<callout", back.body_xml)

    def test_search_related_overlap(self) -> None:
        self.backend.write_article(Article(
            title="A", body_xml="<p>a</p>", tags=["RAG", "评估"]))
        self.backend.write_article(Article(
            title="B", body_xml="<p>b</p>", tags=["RAG", "Agent"]))
        self.backend.write_article(Article(
            title="C", body_xml="<p>c</p>", tags=["RAG", "评估", "LLM"]))
        self.backend.write_article(Article(
            title="D", body_xml="<p>d</p>", tags=["Web3"]))

        # 找与 [RAG, 评估] 重叠 ≥2 的：A, C
        hits = self.backend.search_related(["RAG", "评估"], min_overlap=2)
        titles = {a.title for a in hits}
        self.assertEqual(titles, {"A", "C"})

        # 重叠 ≥1 = A, B, C
        hits = self.backend.search_related(["RAG", "评估"], min_overlap=1)
        self.assertEqual({a.title for a in hits}, {"A", "B", "C"})

        # 空标签 = 空结果
        self.assertEqual(self.backend.search_related([], min_overlap=1), [])

    def test_append_xref_idempotent(self) -> None:
        path = self.backend.write_article(Article(
            title="主文", body_xml="<p>正文</p>", tags=["RAG"]))
        slug = Path(path).stem
        xref = "- [相似] 见 ./B.md"

        self.backend.append_xref(slug, xref)
        self.backend.append_xref(slug, xref)  # 重复调用
        self.backend.append_xref(slug, xref)

        body = Path(path).read_text(encoding="utf-8")
        # "## 相关知识" 只应出现一次
        self.assertEqual(body.count("## 相关知识"), 1)
        # xref 内容只应出现一次
        self.assertEqual(body.count("[相似]"), 1)

        # 追加不同 xref 应正常累加
        self.backend.append_xref(slug, "- [另一] 见 ./C.md")
        body = Path(path).read_text(encoding="utf-8")
        self.assertEqual(body.count("[相似]"), 1)
        self.assertEqual(body.count("[另一]"), 1)


class LocalBackendProfileTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.backend = LocalFileBackend(root=self._tmp.name)

    def test_new_user_returns_is_new(self) -> None:
        p = self.backend.read_profile("ou_unknown")
        self.assertTrue(p.is_new)
        self.assertEqual(p.user_id, "ou_unknown")
        self.assertEqual(p.topic_mastery, {})
        self.assertEqual(p.session_count, 0)

    def test_upsert_read_roundtrip(self) -> None:
        prof = Profile(
            user_id="ou_xx",
            topic_mastery={"RAG": 3, "Agent": 1},
            stuck_points=["RAG :: rerank 模型怎么选"],
            style_response="prefers_challenge",
            methodology_quotes=["2026-05-21 :: 召回分层比加 rerank 重要"],
            aha_moment_log=["2026-05-21 :: RAG :: chunk 跨段语义谁来保？"],
            domain_familiarity_tags=["RAG", "Agent"],
            session_count=3,
            last_session_at="2026/05/21",
            display_name="罗健",
        )
        self.backend.upsert_profile(prof)
        back = self.backend.read_profile("ou_xx")
        self.assertFalse(back.is_new)
        self.assertEqual(back.topic_mastery, {"RAG": 3, "Agent": 1})
        self.assertEqual(back.stuck_points, ["RAG :: rerank 模型怎么选"])
        self.assertEqual(back.style_response, "prefers_challenge")
        self.assertEqual(back.session_count, 3)
        self.assertEqual(set(back.domain_familiarity_tags), {"RAG", "Agent"})
        self.assertEqual(back.display_name, "罗健")

        # 第二次 upsert 应覆盖（不累加）
        prof.session_count = 5
        prof.topic_mastery = {"RAG": 4}
        self.backend.upsert_profile(prof)
        back2 = self.backend.read_profile("ou_xx")
        self.assertEqual(back2.session_count, 5)
        self.assertEqual(back2.topic_mastery, {"RAG": 4})

    def test_profile_json_on_disk(self) -> None:
        prof = Profile(user_id="ou_disk", topic_mastery={"X": 1}, session_count=1)
        self.backend.upsert_profile(prof)
        path = Path(self._tmp.name) / "profiles" / "ou_disk.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["topic_mastery"], {"X": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
