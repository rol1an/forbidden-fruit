"""砚友 · LarkBackend

包装 lark-cli subprocess 调用。**不引 lark-oapi SDK**，保持单二进制依赖。

额度耗尽兜底：lark-cli 返回 quota / rate-limited 类错误时抛 BackendQuotaExceeded，
调用方应捕获并提示用户切到 LocalFileBackend（`YANYU_BACKEND=local`）。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any

from .backend import Article, Backend, BackendQuotaExceeded, Profile

# 飞书额度类错误码 / 关键字（任意命中即认为额度耗尽）
QUOTA_ERROR_PATTERNS = (
    "99991663",          # 飞书官方频控码
    "rate limit",
    "rate_limit",
    "quota exceeded",
    "api quota",
    "QPS limit",
    "frequency limit",
)

# 默认配置（与 yanyu-import / yanyu-dialogue 当前硬编码一致；可由环境变量覆盖）
DEFAULT_PROFILE = os.environ.get("YANYU_LARK_PROFILE", "new_tenant")
DEFAULT_SPACE_ID = os.environ.get("YANYU_WIKI_SPACE_ID", "")
DEFAULT_BASE_TOKEN = os.environ.get("YANYU_BASE_TOKEN", "")
DEFAULT_ARTICLE_TABLE = os.environ.get("YANYU_ARTICLE_TABLE", "文章索引")
DEFAULT_PROFILE_TABLE = os.environ.get("YANYU_PROFILE_TABLE", "yanyu_profile")
DEFAULT_PROFILE_APP_TOKEN = os.environ.get("YANYU_PROFILE_APP_TOKEN", DEFAULT_BASE_TOKEN)


def _is_quota_error(stderr: str, stdout: str) -> bool:
    blob = (stderr + "\n" + stdout).lower()
    return any(p.lower() in blob for p in QUOTA_ERROR_PATTERNS)


def _run(cmd: list[str], *, dry_run: bool = False) -> tuple[int, str, str]:
    """跑 lark-cli。dry_run=True 时只打印命令、返回 (0, "", "")，便于测试。"""
    if dry_run:
        return 0, json.dumps({"dry_run": True, "cmd": cmd}), ""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


class LarkBackend(Backend):
    """lark-cli 包装。每个公开方法都做 quota 检查。

    dry_run=True 时所有调用都不真发 subprocess，方便：
    1. 单测验证命令构造正确
    2. 飞书额度耗尽时通过 env 强制开启 dry_run 抓现场
    """

    def __init__(
        self,
        *,
        profile: str | None = None,
        space_id: str | None = None,
        base_token: str | None = None,
        article_table: str | None = None,
        profile_table: str | None = None,
        profile_app_token: str | None = None,
        dry_run: bool | None = None,
    ) -> None:
        self.profile = profile or DEFAULT_PROFILE
        self.space_id = space_id or DEFAULT_SPACE_ID
        self.base_token = base_token or DEFAULT_BASE_TOKEN
        self.article_table = article_table or DEFAULT_ARTICLE_TABLE
        self.profile_table = profile_table or DEFAULT_PROFILE_TABLE
        self.profile_app_token = profile_app_token or DEFAULT_PROFILE_APP_TOKEN
        if dry_run is None:
            self.dry_run = os.environ.get("YANYU_LARK_DRY_RUN", "").lower() in ("1", "true", "yes")
        else:
            self.dry_run = dry_run

    # -------- 工具 --------

    def _exec(self, cmd: list[str]) -> str:
        code, out, err = _run(cmd, dry_run=self.dry_run)
        if code != 0:
            if _is_quota_error(err, out):
                raise BackendQuotaExceeded(
                    "飞书 API 额度耗尽。建议设 YANYU_BACKEND=local 切到 LocalFileBackend。\n"
                    f"原始 stderr: {err.strip()[-300:]}"
                )
            raise RuntimeError(f"lark-cli failed (exit={code}): {err.strip()[-500:]}")
        return out

    # -------- write_article --------

    def write_article(self, doc: Article) -> str:
        if not self.space_id:
            raise RuntimeError("LarkBackend 需要 space_id（YANYU_WIKI_SPACE_ID）")

        # Step A: 创建 wiki 节点
        create_out = self._exec([
            "lark-cli", "wiki", "+node-create",
            "--profile", self.profile,
            "--space-id", self.space_id,
            "--title", doc.title,
        ])
        obj_token, doc_url = self._parse_wiki_create(create_out)

        # Step B: overwrite 写入 DocxXML
        # 用 stdin 传 content 避免临时文件清理负担
        write_cmd = [
            "lark-cli", "docs", "+update",
            "--profile", self.profile,
            "--api-version", "v2",
            "--doc", obj_token,
            "--command", "overwrite",
            "--content", "-",  # 从 stdin 读
        ]
        if self.dry_run:
            self._exec(write_cmd)
        else:
            proc = subprocess.run(
                write_cmd, input=doc.body_xml, capture_output=True, text=True,
            )
            if proc.returncode != 0:
                if _is_quota_error(proc.stderr, proc.stdout):
                    raise BackendQuotaExceeded(
                        f"docs +update 触发额度上限。切 YANYU_BACKEND=local。\n"
                        f"stderr: {proc.stderr.strip()[-300:]}"
                    )
                raise RuntimeError(
                    f"docs +update failed (exit={proc.returncode}): "
                    f"{proc.stderr.strip()[-500:]}"
                )

        # Step C: 写 Bitable 索引（轻量字段，复习元数据在 extra）
        if self.base_token:
            self._write_index_record(doc, obj_token, doc_url)

        return doc_url or obj_token

    def _parse_wiki_create(self, out: str) -> tuple[str, str]:
        """lark-cli wiki +node-create 输出可能是 JSON 或文本，做容错解析。"""
        try:
            data = json.loads(out)
            node = (data.get("data") or {}).get("node") or data.get("node") or data
            obj_token = node.get("obj_token") or node.get("token") or ""
            url = node.get("url") or ""
            if obj_token:
                return obj_token, url
        except (json.JSONDecodeError, AttributeError):
            pass
        # 文本兜底正则
        token_m = re.search(r"obj_token[\":\s]+([A-Za-z0-9_-]{16,})", out)
        url_m = re.search(r"(https?://[^\s\"]+/wiki/[^\s\"]+)", out)
        if not token_m:
            raise RuntimeError(
                f"无法从 wiki +node-create 输出解析 obj_token；输出尾: {out[-300:]}"
            )
        return token_m.group(1), (url_m.group(1) if url_m else "")

    def _write_index_record(self, doc: Article, obj_token: str, doc_url: str) -> None:
        record = {
            "标题": doc.title,
            "原文链接": doc.source_url or "",
            "文档链接": doc_url,
            "知识标签": doc.tags[0] if doc.tags else "",  # 单值 select
            "文档Token": obj_token,
        }
        record.update({k: v for k, v in doc.extra.items() if k in (
            "导入日期", "复习状态", "复习轮次", "下次复习",
        )})
        self._exec([
            "lark-cli", "base", "+record-upsert",
            "--profile", self.profile, "--as", "bot",
            "--base-token", self.base_token,
            "--table-id", self.article_table,
            "--json", json.dumps(record, ensure_ascii=False),
        ])

    # -------- read_article --------

    def read_article(self, ref: str) -> Article:
        # ref 可能是 obj_token 或完整 URL，lark-cli 自适应
        out = self._exec([
            "lark-cli", "docs", "+fetch",
            "--profile", self.profile,
            "--api-version", "v2",
            "--doc", ref,
        ])
        title = ""
        body_xml = out
        try:
            data = json.loads(out)
            title = data.get("title") or (data.get("data") or {}).get("title") or ""
            body_xml = data.get("content") or (data.get("data") or {}).get("content") or out
        except json.JSONDecodeError:
            pass
        return Article(title=title or ref, body_xml=body_xml, tags=[], source_url=None, extra={})

    # -------- search_related --------

    def search_related(self, tags: list[str], min_overlap: int = 2) -> list[Article]:
        if not (self.base_token and tags):
            return []
        # lark-cli base +record-search 按关键词搜，砚友 SKILL.md 用 search_fields 限定列
        keyword = " ".join(tags)
        out = self._exec([
            "lark-cli", "base", "+record-search",
            "--profile", self.profile, "--as", "bot",
            "--base-token", self.base_token,
            "--table-id", self.article_table,
            "--json", json.dumps(
                {"keyword": keyword, "search_fields": ["知识标签", "标题"]},
                ensure_ascii=False,
            ),
        ])
        if self.dry_run:
            return []
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return []
        records = ((data.get("data") or {}).get("records") or [])
        results: list[Article] = []
        tag_set = set(tags)
        for r in records:
            fields = r.get("fields") or {}
            row_tags = fields.get("知识标签")
            row_tag_list = (
                row_tags if isinstance(row_tags, list)
                else [row_tags] if row_tags else []
            )
            if len(tag_set & set(row_tag_list)) < min_overlap:
                continue
            results.append(Article(
                title=fields.get("标题") or "",
                body_xml="",  # 索引不带正文；调用方按 obj_token 再 read_article
                tags=row_tag_list,
                source_url=fields.get("原文链接"),
                extra={"obj_token": fields.get("文档Token"), "url": fields.get("文档链接")},
            ))
        return results

    # -------- append_xref --------

    def append_xref(self, target_ref: str, xref_html_or_md: str) -> None:
        cmd = [
            "lark-cli", "docs", "+update",
            "--profile", self.profile,
            "--api-version", "v2",
            "--doc", target_ref,
            "--command", "append",
            "--content", "-",
        ]
        if self.dry_run:
            self._exec(cmd)
            return
        proc = subprocess.run(cmd, input=xref_html_or_md, capture_output=True, text=True)
        if proc.returncode != 0:
            if _is_quota_error(proc.stderr, proc.stdout):
                raise BackendQuotaExceeded(
                    f"append_xref 触发额度上限。stderr: {proc.stderr.strip()[-300:]}"
                )
            raise RuntimeError(
                f"append_xref failed (exit={proc.returncode}): "
                f"{proc.stderr.strip()[-500:]}"
            )

    # -------- profile --------

    def read_profile(self, user_id: str) -> Profile:
        if not self.profile_app_token:
            raise RuntimeError(
                "LarkBackend.read_profile 需要 YANYU_PROFILE_APP_TOKEN"
            )
        out = self._exec([
            "lark-cli", "base", "+record-search",
            "--profile", self.profile, "--as", "bot",
            "--base-token", self.profile_app_token,
            "--table-id", self.profile_table,
            "--json", json.dumps(
                {"keyword": user_id, "search_fields": ["user_id"]},
                ensure_ascii=False,
            ),
        ])
        if self.dry_run:
            return Profile(user_id=user_id, is_new=True)
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return Profile(user_id=user_id, is_new=True)
        records = ((data.get("data") or {}).get("records") or [])
        for r in records:
            fields = r.get("fields") or {}
            if fields.get("user_id") != user_id:
                continue
            return self._normalize_profile(fields, r.get("record_id") or r.get("id"))
        return Profile(user_id=user_id, is_new=True)

    @staticmethod
    def _normalize_profile(fields: dict[str, Any], record_id: str | None) -> Profile:
        def parse_json(name: str, fallback: Any) -> Any:
            v = fields.get(name)
            if not v:
                return fallback
            try:
                return json.loads(v)
            except (TypeError, ValueError):
                return fallback

        def split_lines(name: str) -> list[str]:
            v = fields.get(name)
            return [s.strip() for s in str(v or "").splitlines() if s.strip()]

        return Profile(
            user_id=fields.get("user_id") or "",
            topic_mastery=parse_json("topic_mastery", {}),
            stuck_points=split_lines("stuck_points"),
            style_response=fields.get("style_response"),
            methodology_quotes=split_lines("methodology_quotes"),
            aha_moment_log=split_lines("aha_moment_log"),
            domain_familiarity_tags=list(fields.get("domain_familiarity_tags") or []),
            session_count=int(fields.get("session_count") or 0),
            last_session_at=fields.get("last_session_at"),
            display_name=fields.get("display_name"),
            is_new=False,
            record_id=record_id,
        )

    def upsert_profile(self, profile: Profile) -> None:
        if not self.profile_app_token:
            raise RuntimeError("LarkBackend.upsert_profile 需要 YANYU_PROFILE_APP_TOKEN")
        fields = {
            "user_id": profile.user_id,
            "topic_mastery": json.dumps(profile.topic_mastery, ensure_ascii=False),
            "stuck_points": "\n".join(profile.stuck_points),
            "style_response": profile.style_response or "",
            "methodology_quotes": "\n".join(profile.methodology_quotes),
            "aha_moment_log": "\n".join(profile.aha_moment_log),
            "domain_familiarity_tags": profile.domain_familiarity_tags,
            "session_count": profile.session_count,
            "last_session_at": profile.last_session_at or "",
        }
        if profile.display_name:
            fields["display_name"] = profile.display_name
        cmd = [
            "lark-cli", "base", "+record-upsert",
            "--profile", self.profile, "--as", "bot",
            "--base-token", self.profile_app_token,
            "--table-id", self.profile_table,
            "--json", json.dumps(fields, ensure_ascii=False),
        ]
        if profile.record_id:
            cmd.extend(["--record-id", profile.record_id])
        self._exec(cmd)
