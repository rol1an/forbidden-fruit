#!/usr/bin/env python3
"""砚友 · 微信文章爬取与结构化器

输入：微信公众号文章 URL
输出：JSON 到 stdout，包含 title / author / publish_date / parts / emphases

parts 是按原文顺序排列的「文字块 + 图片 + 公式」有序列表，供后续 LLM 重构。
emphases 是原文加粗/彩色强力标记 list，Step 4 渲染完用作自检表。

依赖：python3 标准库 + curl（系统命令）。无第三方依赖。
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def curl_fetch(url: str) -> str:
    """模拟浏览器 UA 抓取，绕过微信轻量反爬。"""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        out_path = f.name
    try:
        try:
            subprocess.run(
                [
                    "curl", "-sL", "-o", out_path,
                    "--max-time", "30",
                    "-H", f"User-Agent: {UA}",
                    "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "-H", "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8",
                    url,
                ],
                check=True, capture_output=True, timeout=30,
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                f"微信 curl 30s 超时,URL 是否有效? url={url}"
            ) from e
        except subprocess.CalledProcessError as e:
            stderr_tail = (e.stderr or b"").decode("utf-8", errors="replace")[-200:]
            raise RuntimeError(
                f"微信 curl 失败(exit={e.returncode}),url={url}\nstderr 尾: {stderr_tail}"
            ) from e
        return Path(out_path).read_text(encoding="utf-8", errors="replace")
    finally:
        Path(out_path).unlink(missing_ok=True)


def extract_meta(html_text: str) -> dict:
    """从微信 HTML 提取标题 / 公众号 / 发布日期。"""
    def first(pattern: str) -> str | None:
        m = re.search(pattern, html_text)
        return m.group(1) if m else None

    title = (
        first(r'var msg_title = ["\']([^"\']+)["\']')
        or first(r'<meta property="og:title" content="([^"]+)"')
        or first(r'<title>([^<]+)</title>')
    )
    author = (
        first(r'var nickname = ["\']([^"\']+)["\']')
        or first(r'<meta property="og:article:author" content="([^"]+)"')
    )
    ct = first(r'var ct = ["\'](\d+)["\']')
    publish_date = None
    if ct:
        from datetime import datetime
        publish_date = datetime.fromtimestamp(int(ct)).strftime("%Y-%m-%d")

    return {
        "title": html.unescape(title) if title else None,
        "author": html.unescape(author) if author else None,
        "publish_date": publish_date,
    }


def extract_body(html_text: str) -> str:
    """提取 id="js_content" 容器内的 HTML（微信正文标准位置）。"""
    m = re.search(
        r'<div[^>]*id=["\']js_content["\'][^>]*>(.*?)</div>\s*(?:<script|<!--end)',
        html_text, re.DOTALL,
    )
    return m.group(1) if m else html_text  # 兜底返全文，让上层报警


def _parse_color(color: str) -> tuple[int, int, int] | None:
    c = color.lower().strip().rstrip(";")
    if c in ("inherit", "initial", "transparent"):
        return None
    if c == "black":
        return (0, 0, 0)
    if c == "white":
        return (255, 255, 255)
    if c.startswith("#") and len(c) in (4, 7):
        h = c[1:]
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        try:
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except ValueError:
            return None
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", c)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


def _is_real_emphasis_color(color: str) -> bool:
    """过滤掉默认黑、表格白、代码高亮灰、章节灰等"弱视觉色"——
    它们是模板/语法高亮设的，不是作者真强调。用 HSV 饱和度判别。"""
    rgb = _parse_color(color)
    if rgb is None:
        return True  # 无法解析，宁可保留交给后续 LLM 判断
    r, g, b = rgb
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == 0:  # 纯黑
        return False
    saturation = (mx - mn) / mx
    # 饱和度 < 0.15 = 灰度家族（含黑/白/各种灰）
    return saturation >= 0.15


class EmphasisCollector(HTMLParser):
    """收集 <strong>/<b>/style=color:... 标记的文本片段（已过滤黑灰噪音色）。"""

    def __init__(self) -> None:
        super().__init__()
        self._stack: list[dict] = []
        self.emphases: list[dict] = []

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag in ("strong", "b"):
            # 记录开标签的具体 tag,方便 endtag 严格匹配 pop
            self._stack.append({"kind": "bold", "tag": tag, "buf": []})
        else:
            style = attrs_d.get("style", "")
            color_m = re.search(r"color\s*:\s*([^;]+)", style)
            if color_m and _is_real_emphasis_color(color_m.group(1)):
                self._stack.append({
                    "kind": "color",
                    "tag": tag,
                    "color": color_m.group(1).strip(),
                    "buf": [],
                })

    def _pop_match(self, predicate):
        """从栈顶向下找第一个满足 predicate 的 frame 并 pop。
        其上层未闭合的 frame 也一起弹出(HTML 容错:错配嵌套)。"""
        for i in range(len(self._stack) - 1, -1, -1):
            if predicate(self._stack[i]):
                frame = self._stack[i]
                # i 之上的 frame 视作隐式闭合,一起 pop
                del self._stack[i:]
                return frame
        return None

    def handle_endtag(self, tag):
        if tag in ("strong", "b"):
            frame = self._pop_match(lambda f: f["kind"] == "bold")
            if frame:
                text = "".join(frame["buf"]).strip()
                if text:
                    self.emphases.append({"kind": "bold", "text": text})
        else:
            # 任意带 color style 的标签结束都可能闭合一个 color frame
            # (不止 span:微信里 <p style="color:..."> / <section style="color:...">  也常见)
            frame = self._pop_match(lambda f: f["kind"] == "color" and f.get("tag") == tag)
            if frame:
                text = "".join(frame["buf"]).strip()
                if text:
                    self.emphases.append({"kind": "color", "color": frame["color"], "text": text})

    def handle_data(self, data):
        # 关键:同时写入所有打开的 frame buf,避免内层 frame pop 后外层 buf 还是空的
        for frame in self._stack:
            frame["buf"].append(data)


def _clean_prose(s: str) -> str:
    """正文清洗：<br>→换行，去标签，HTML 实体解码，规整空白。"""
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</p>\s*<p[^>]*>", "\n\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)  # &nbsp; / &amp; / &#x00A0; 等
    s = s.replace("\xa0", " ")  # nbsp 字面
    # 多空格压一个，但保留换行
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _extract_code(pre_html: str) -> dict:
    """从 <pre>...</pre> 提取代码块，保留换行和语言提示。"""
    lang_m = re.search(r'class="[^"]*(?:lang|language)-(\w+)', pre_html, re.IGNORECASE)
    lang = lang_m.group(1) if lang_m else None
    # 部分微信编辑器把代码每行装在 <code><span>...</span></code>，<br> 分隔
    inner = re.sub(r"<br\s*/?>", "\n", pre_html, flags=re.IGNORECASE)
    inner = re.sub(r"</li>\s*<li[^>]*>", "\n", inner, flags=re.IGNORECASE)
    inner = re.sub(r"<[^>]+>", "", inner)
    inner = html.unescape(inner).replace("\xa0", " ")
    inner = re.sub(r"[ \t]+\n", "\n", inner)
    inner = re.sub(r"\n{3,}", "\n\n", inner).strip("\n")
    return {"type": "code", "lang": lang, "content": inner}


def split_parts(body_html: str) -> list[dict]:
    """按 <pre> 和 <img> 切分，建立「文字 / 代码 / 图片」有序列表。

    每张图带 ctx_before / ctx_after（脱标签后的前 100 / 后 100 字符），供 LLM 判类型。
    代码块作为 atomic part，保留换行和语言标签。
    """
    # 先切代码块（贪婪保整段），剩下的再切图片
    pre_split = re.split(r"(<pre[\s\S]*?</pre>)", body_html, flags=re.IGNORECASE)
    parts: list[dict] = []
    img_n = 0

    def add_text(s: str) -> None:
        text = _clean_prose(s)
        if text:
            parts.append({"type": "text", "content": text})

    def add_image(piece: str, prev: str, nxt: str) -> None:
        nonlocal img_n
        src_m = re.search(r'data-src="([^"]+)"', piece) or re.search(r'src="([^"]+)"', piece)
        if not src_m:
            return
        img_n += 1
        parts.append({
            "type": "image",
            "n": img_n,
            "url": html.unescape(src_m.group(1)),
            "ctx_before": _clean_prose(prev)[-100:],
            "ctx_after": _clean_prose(nxt)[:100],
        })

    for seg in pre_split:
        if seg.lower().startswith("<pre"):
            parts.append(_extract_code(seg))
            continue
        pieces = re.split(r"(<img[^>]+>)", seg)
        for i, piece in enumerate(pieces):
            if piece.startswith("<img"):
                add_image(
                    piece,
                    pieces[i - 1] if i > 0 else "",
                    pieces[i + 1] if i + 1 < len(pieces) else "",
                )
            else:
                add_text(piece)
    return parts


def scrape(url: str) -> dict:
    raw = curl_fetch(url)
    meta = extract_meta(raw)
    body = extract_body(raw)

    collector = EmphasisCollector()
    collector.feed(body)

    return {
        "url": url,
        **meta,
        "parts": split_parts(body),
        "emphases": collector.emphases,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: wechat_scrape.py <wechat-article-url>", file=sys.stderr)
        return 1
    result = scrape(sys.argv[1])
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
