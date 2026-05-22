"""factory.load_backend 测试。

也顺便覆盖 LarkBackend 的额度耗尽分支（mock subprocess.run）。
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from yanyu_core import (  # noqa: E402
    BackendQuotaExceeded,
    LarkBackend,
    LocalFileBackend,
    load_backend,
)


class FactoryTest(unittest.TestCase):
    def test_default_is_local(self) -> None:
        env = dict(os.environ)
        env.pop("YANYU_BACKEND", None)
        with mock.patch.dict(os.environ, env, clear=True):
            b = load_backend()
        self.assertIsInstance(b, LocalFileBackend)

    def test_explicit_local(self) -> None:
        b = load_backend("local")
        self.assertIsInstance(b, LocalFileBackend)

    def test_explicit_lark(self) -> None:
        b = load_backend("lark")
        self.assertIsInstance(b, LarkBackend)

    def test_env_lark(self) -> None:
        with mock.patch.dict(os.environ, {"YANYU_BACKEND": "lark"}):
            b = load_backend()
        self.assertIsInstance(b, LarkBackend)

    def test_unknown_raises(self) -> None:
        with self.assertRaises(ValueError):
            load_backend("postgres")


class LarkBackendQuotaTest(unittest.TestCase):
    def test_quota_error_raises_backend_quota_exceeded(self) -> None:
        backend = LarkBackend(
            profile="t", space_id="s", base_token="b", dry_run=False,
        )
        fake = mock.Mock()
        fake.returncode = 1
        fake.stdout = ""
        fake.stderr = "Error: 99991663 rate limit exceeded for tenant"
        with mock.patch("yanyu_core.lark_backend.subprocess.run", return_value=fake):
            with self.assertRaises(BackendQuotaExceeded):
                backend.read_article("some_token")

    def test_non_quota_error_raises_runtime(self) -> None:
        backend = LarkBackend(
            profile="t", space_id="s", base_token="b", dry_run=False,
        )
        fake = mock.Mock()
        fake.returncode = 2
        fake.stdout = ""
        fake.stderr = "auth failed: token expired"
        with mock.patch("yanyu_core.lark_backend.subprocess.run", return_value=fake):
            with self.assertRaises(RuntimeError) as ctx:
                backend.read_article("some_token")
            self.assertNotIsInstance(ctx.exception, BackendQuotaExceeded)

    def test_dry_run_constructs_command(self) -> None:
        backend = LarkBackend(
            profile="np", space_id="sp", base_token="bt", dry_run=True,
        )
        # dry_run 不应抛错——内部短路返回
        backend.append_xref("doctoken123", "- [x] xref body")
        # search_related 在 dry_run 下返回 []
        self.assertEqual(backend.search_related(["RAG"], min_overlap=2), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
