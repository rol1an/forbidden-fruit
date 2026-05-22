"""砚友 · Backend 抽象接口

三个 Skill（yanyu-import / yanyu-dialogue / yanyu-fusion）共享的存储抽象。
通过 `factory.load_backend()` 按 `YANYU_BACKEND` 环境变量选具体实现。

设计动机见 docs/PLAN_v2_DECISIONS.md §决策 1：飞书 API 额度耗尽时切到
LocalFileBackend 让评审在 5 分钟内复现砚友核心能力。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Article:
    """文章数据结构。

    - LarkBackend: body_xml 是 DocxXML
    - LocalFileBackend: body_xml 是 markdown（write 时 DocxXML 会被简化成 md）

    extra 装放灵活字段：复习元数据（next_review_at / round）、强力标记列表、
    作者公众号名、image_map 等不进入主 schema 的边缘信息。
    """

    title: str
    body_xml: str
    tags: list[str] = field(default_factory=list)
    source_url: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Profile:
    """用户画像。schema 与 yanyu-dialogue/references/profile-schema.md 一致。

    record_id 字段仅 LarkBackend 使用——Bitable upsert 需要它定位行；
    LocalFileBackend 一律忽略。
    """

    user_id: str
    topic_mastery: dict[str, int] = field(default_factory=dict)
    stuck_points: list[str] = field(default_factory=list)
    style_response: str | None = None
    methodology_quotes: list[str] = field(default_factory=list)
    aha_moment_log: list[str] = field(default_factory=list)
    domain_familiarity_tags: list[str] = field(default_factory=list)
    session_count: int = 0
    last_session_at: str | None = None
    is_new: bool = False
    record_id: str | None = None


class BackendQuotaExceeded(RuntimeError):
    """飞书 API 额度耗尽。捕获方应提示用户切到 LocalFileBackend。

    LarkBackend 在 lark-cli 返回额度类错误码（99991663 / quota / rate limited）
    时抛出此异常，避免被静默忽略。
    """


class Backend(ABC):
    """砚友存储后端接口。

    所有方法不接管 LLM 重写——LLM 加工在调用方（Skill 工作流）做，
    backend 只负责"把这个 Article/Profile 存到某处"和"按条件取回"。
    """

    @abstractmethod
    def write_article(self, doc: Article) -> str:
        """写入文章。返回文档 URL（LarkBackend）或文件路径（LocalFileBackend）。"""

    @abstractmethod
    def read_article(self, ref: str) -> Article:
        """按 ref 读取。ref 形态由 backend 决定：
        - LarkBackend: obj_token 或飞书文档 URL
        - LocalFileBackend: 文章 slug 或绝对/相对 path
        """

    @abstractmethod
    def search_related(self, tags: list[str], min_overlap: int = 2) -> list[Article]:
        """按标签交集 >= min_overlap 找相关文章，供双向链接缝合用。"""

    @abstractmethod
    def append_xref(self, target_ref: str, xref_html_or_md: str) -> None:
        """在已存在的 target 末尾追加一段交叉引用。

        实现需保证幂等：同样内容 append 多次只生效一次（避免重复入库时刷屏）。
        """

    @abstractmethod
    def read_profile(self, user_id: str) -> Profile:
        """读画像。无记录返回 Profile(user_id=..., is_new=True)，绝不返回 None。"""

    @abstractmethod
    def upsert_profile(self, profile: Profile) -> None:
        """覆盖写画像。合并语义由调用方负责（read → merge in memory → upsert）。"""
