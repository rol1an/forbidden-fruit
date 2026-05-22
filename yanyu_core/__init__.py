"""砚友 · Core

三个 Skill 共享的存储抽象层。通过 `load_backend()` 按 env 选 local / lark。

典型用法::

    from yanyu_core import load_backend, Article
    backend = load_backend()
    url_or_path = backend.write_article(Article(title="...", body_xml="...", tags=[...]))
"""
from .backend import Article, Backend, BackendQuotaExceeded, Profile
from .factory import load_backend
from .lark_backend import LarkBackend
from .local_backend import LocalFileBackend

__all__ = [
    "Article",
    "Backend",
    "BackendQuotaExceeded",
    "Profile",
    "LarkBackend",
    "LocalFileBackend",
    "load_backend",
]
