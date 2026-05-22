"""砚友 · LocalFileBackend

纯本地 Markdown + JSON 实现，零飞书依赖，开箱即用。

存储布局（root 默认 ~/.yanyu_kb/，环境变量 YANYU_KB_ROOT 覆盖）::

    <root>/
    ├── articles/
    │   ├── 20260521-rag-evaluation.md         主体 markdown
    │   └── 20260521-rag-evaluation.meta.json  {title,tags,source_url,...}
    └── profiles/
        └── <user_id>.json                     整个 Profile 序列化
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .backend import Article, Backend, Profile

XREF_SECTION_HEADING = "## 相关知识"


def _slugify(title: str) -> str:
    """生成 filesystem-safe slug。保留 ASCII 字母数字与中划线，其余统一替换。

    中文/日文等 CJK 字符直接保留——本地存储无需 ASCII-only，反而保留原标题方便人肉浏览。
    """
    # 去掉 markdown 强调与不可见字符
    s = title.strip()
    # 把空白与连续标点压成 -
    s = re.sub(r"[\s/\\:*?\"<>|]+", "-", s)
    # 砍掉行首行尾的 -
    s = s.strip("-")
    if not s:
        s = "untitled"
    # 限长，避免 macOS 255 字节文件名上限
    return s[:80]


def _docxxml_to_markdown(body_xml: str) -> str:
    """把 DocxXML 简化转 markdown。

    保留 h1/h2/h3/p/li/code 元素的语义；丢弃 callout / table / 复杂样式。
    实现思路是正则替换而非完整 HTML 解析——这是 v1 简化方案：
    DocxXML 标签集合有限且砚友 yanyu-import 模板高度结构化，正则够用。

    保留：标题、段落、列表、代码块、行内代码、粗体、斜体、链接
    丢弃：callout、table、span 样式（颜色）、image_block（用占位符）、emoji 装饰
    """
    s = body_xml

    # 1. 代码块（先处理避免内部内容被其他规则吃掉）
    def _code_block(m: "re.Match[str]") -> str:
        lang = m.group(1) or ""
        content = m.group(2)
        # 解 HTML 实体（&lt; &gt; &amp;）
        content = (content.replace("&lt;", "<")
                          .replace("&gt;", ">")
                          .replace("&amp;", "&"))
        return f"\n```{lang}\n{content.rstrip()}\n```\n"

    s = re.sub(
        r"<code(?:\s+language=[\"']?(\w+)[\"']?)?[^>]*>([\s\S]*?)</code>",
        _code_block, s,
    )

    # 2. 标题
    for level in (1, 2, 3, 4, 5):
        prefix = "#" * level
        s = re.sub(rf"<h{level}[^>]*>([\s\S]*?)</h{level}>",
                   rf"\n{prefix} \1\n", s)

    # 3. 列表
    s = re.sub(r"<li[^>]*>([\s\S]*?)</li>", r"- \1\n", s)
    s = re.sub(r"</?(?:ul|ol)[^>]*>", "", s)

    # 4. 段落、换行
    s = re.sub(r"<p[^>]*>([\s\S]*?)</p>", r"\1\n\n", s)
    s = re.sub(r"<br\s*/?>", "\n", s)

    # 5. 强调（粗体 / 斜体）
    s = re.sub(r"<(?:b|strong)[^>]*>([\s\S]*?)</(?:b|strong)>", r"**\1**", s)
    s = re.sub(r"<(?:i|em)[^>]*>([\s\S]*?)</(?:i|em)>", r"*\1*", s)

    # 6. 链接
    s = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', r"[\2](\1)", s)

    # 7. callout 退化：emoji + 内容（保留信息但去 box）
    def _callout(m: "re.Match[str]") -> str:
        attrs = m.group(1) or ""
        body = m.group(2)
        emoji_m = re.search(r'emoji="([^"]+)"', attrs)
        emoji = emoji_m.group(1) if emoji_m else ""
        return f"> {emoji} {body.strip()}\n"

    s = re.sub(
        r"<callout([^>]*)>([\s\S]*?)</callout>",
        _callout, s,
    )

    # 8. 图片：转 markdown 图片占位（src 可能在 image_block 或 img 标签）
    s = re.sub(
        r'<(?:img|image_block)[^>]*(?:src|file_token)="([^"]+)"[^>]*/?>',
        r"![](\1)", s,
    )

    # 9. span 等剩余标签直接剥掉，保留文字
    s = re.sub(r"<[^>]+>", "", s)

    # 10. HTML 实体
    s = (s.replace("&lt;", "<")
          .replace("&gt;", ">")
          .replace("&amp;", "&")
          .replace("&nbsp;", " "))

    # 11. 收紧空白
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


class LocalFileBackend(Backend):
    """文件系统后端。所有路径均封装在 root 之下，不污染外部。"""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or os.environ.get("YANYU_KB_ROOT") or
                         Path.home() / ".yanyu_kb").expanduser()
        self.articles_dir = self.root / "articles"
        self.profiles_dir = self.root / "profiles"
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    # -------- 内部工具 --------

    def _resolve_article_paths(self, slug: str) -> tuple[Path, Path]:
        """slug 可能是裸 slug、`xx.md`、绝对路径——都规范化。"""
        p = Path(slug)
        if p.is_absolute() and p.exists():
            base = p.with_suffix("")
        else:
            stem = p.stem if p.suffix == ".md" else slug
            base = self.articles_dir / stem
        return base.with_suffix(".md"), base.with_suffix(".meta.json")

    def _scan_meta(self) -> list[tuple[Path, dict[str, Any]]]:
        out: list[tuple[Path, dict[str, Any]]] = []
        for meta_path in self.articles_dir.glob("*.meta.json"):
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            out.append((meta_path, meta))
        return out

    # -------- write_article --------

    def write_article(self, doc: Article) -> str:
        date = datetime.now().strftime("%Y%m%d")
        slug = f"{date}-{_slugify(doc.title)}"
        md_path, meta_path = self._resolve_article_paths(slug)

        # 若同名已存在，加 -2 -3 ... 后缀避免覆盖
        n = 2
        while md_path.exists():
            new_slug = f"{slug}-{n}"
            md_path, meta_path = self._resolve_article_paths(new_slug)
            slug = new_slug
            n += 1

        body_md = _docxxml_to_markdown(doc.body_xml)
        md_path.write_text(body_md, encoding="utf-8")

        meta = {
            "title": doc.title,
            "tags": list(doc.tags),
            "source_url": doc.source_url,
            "slug": slug,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "xref_targets": [],  # 维护已注入的 xref，append_xref 用于去重
            "extra": doc.extra,
        }
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8",
        )
        return str(md_path)

    # -------- read_article --------

    def read_article(self, ref: str) -> Article:
        md_path, meta_path = self._resolve_article_paths(ref)
        if not md_path.exists():
            raise FileNotFoundError(f"article not found: {ref} (looked at {md_path})")
        body = md_path.read_text(encoding="utf-8")
        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
        return Article(
            title=meta.get("title") or md_path.stem,
            body_xml=body,
            tags=list(meta.get("tags") or []),
            source_url=meta.get("source_url"),
            extra=dict(meta.get("extra") or {}),
        )

    # -------- search_related --------

    def search_related(self, tags: list[str], min_overlap: int = 2) -> list[Article]:
        if not tags:
            return []
        tag_set = set(tags)
        hits: list[tuple[int, str]] = []
        for meta_path, meta in self._scan_meta():
            article_tags = set(meta.get("tags") or [])
            overlap = len(tag_set & article_tags)
            if overlap >= min_overlap:
                hits.append((overlap, meta.get("slug") or meta_path.stem.replace(".meta", "")))
        # 重叠度高优先
        hits.sort(key=lambda x: -x[0])
        return [self.read_article(slug) for _, slug in hits]

    # -------- append_xref --------

    def append_xref(self, target_ref: str, xref_html_or_md: str) -> None:
        md_path, meta_path = self._resolve_article_paths(target_ref)
        if not md_path.exists():
            raise FileNotFoundError(f"xref target not found: {target_ref}")

        # 幂等检查：meta.xref_targets 装去重指纹
        snippet = xref_html_or_md.strip()
        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
        xref_targets: list[str] = list(meta.get("xref_targets") or [])
        if snippet in xref_targets:
            return  # 已 append 过，跳过

        body = md_path.read_text(encoding="utf-8")
        if XREF_SECTION_HEADING in body:
            # 已有相关知识小节，append 到末尾即可（小节就在文档尾部）
            new_body = body.rstrip() + "\n\n" + snippet + "\n"
        else:
            new_body = (
                body.rstrip() + "\n\n" + XREF_SECTION_HEADING + "\n\n" + snippet + "\n"
            )
        md_path.write_text(new_body, encoding="utf-8")

        xref_targets.append(snippet)
        meta["xref_targets"] = xref_targets
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8",
        )

    # -------- profile --------

    def _profile_path(self, user_id: str) -> Path:
        safe = _slugify(user_id)
        return self.profiles_dir / f"{safe}.json"

    def read_profile(self, user_id: str) -> Profile:
        path = self._profile_path(user_id)
        if not path.exists():
            return Profile(user_id=user_id, is_new=True)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return Profile(user_id=user_id, is_new=True)
        return Profile(
            user_id=data.get("user_id") or user_id,
            topic_mastery=dict(data.get("topic_mastery") or {}),
            stuck_points=list(data.get("stuck_points") or []),
            style_response=data.get("style_response"),
            methodology_quotes=list(data.get("methodology_quotes") or []),
            aha_moment_log=list(data.get("aha_moment_log") or []),
            domain_familiarity_tags=list(data.get("domain_familiarity_tags") or []),
            session_count=int(data.get("session_count") or 0),
            last_session_at=data.get("last_session_at"),
            is_new=False,
        )

    def upsert_profile(self, profile: Profile) -> None:
        path = self._profile_path(profile.user_id)
        data = {
            "user_id": profile.user_id,
            "topic_mastery": profile.topic_mastery,
            "stuck_points": profile.stuck_points,
            "style_response": profile.style_response,
            "methodology_quotes": profile.methodology_quotes,
            "aha_moment_log": profile.aha_moment_log,
            "domain_familiarity_tags": profile.domain_familiarity_tags,
            "session_count": profile.session_count,
            "last_session_at": profile.last_session_at,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
