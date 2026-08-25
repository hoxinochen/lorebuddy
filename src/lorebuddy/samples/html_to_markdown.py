"""无第三方依赖的保守 HTML → Markdown 样本转换器。"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Callable


VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})
BLOCK_TAGS = frozenset({"address", "article", "aside", "blockquote", "div", "dl", "fieldset", "figcaption", "figure", "footer", "form", "header", "main", "nav", "p", "section"})
NOISE_TOKENS = frozenset({"navbar", "breadcrumbs", "breadcrumb", "toc-nav", "page-nav"})
WINCHM_TEMPLATE_TOP_ID = "winchm_template_top"
WINCHM_CONTENT_ID = "winchm_template_content"
WINCHM_NOISE_IDS = frozenset({"winchm_template_button", "winchm_template_navigation", "winchm_template_title"})


@dataclass(slots=True)
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        folded = tag.casefold()
        self._auto_close(folded)
        node = Node(folded, {key.casefold(): value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if node.tag not in VOID_TAGS:
            self.stack.append(node)

    def _auto_close(self, incoming: str) -> None:
        if incoming == "li":
            for index in range(len(self.stack) - 1, 0, -1):
                if self.stack[index].tag in {"ul", "ol"}:
                    break
                if self.stack[index].tag == "li":
                    del self.stack[index:]
                    return
        if incoming == "p":
            self._close_nearest({"p"})
        elif incoming == "tr":
            self._close_nearest({"td", "th", "tr"})
        elif incoming in {"td", "th"}:
            self._close_nearest({"td", "th"})
        elif incoming in {f"h{level}" for level in range(1, 7)}:
            self._close_nearest({"p", *(f"h{level}" for level in range(1, 7))})

    def _close_nearest(self, tags: set[str]) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag in tags:
                del self.stack[index:]
                return
            if self.stack[index].tag in {"body", "table", "ul", "ol"}:
                return

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.casefold() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        folded = tag.casefold()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == folded:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def parse_html(text: str) -> Node:
    parser = TreeParser()
    parser.feed(text)
    parser.close()
    return parser.root


def _walk(node: Node):
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from _walk(child)


def first_text(root: Node, tag: str) -> str | None:
    for node in _walk(root):
        if node.tag == tag:
            value = normalize_inline(plain_text(node))
            if value:
                return value
    return None


def plain_text(node: Node, *, exclude_noise: bool = True) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif not (exclude_noise and is_noise(child)):
            parts.append(plain_text(child, exclude_noise=exclude_noise))
    return " ".join(parts)


def normalize_inline(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def is_noise(node: Node, *, preserve_winchm_top: bool = False) -> bool:
    if node.tag in {"script", "style", "noscript", "template"}:
        return True
    if node.tag == "nav":
        return True
    node_id = node.attrs.get("id", "").casefold()
    if node_id == WINCHM_TEMPLATE_TOP_ID:
        return not preserve_winchm_top
    if node_id in WINCHM_NOISE_IDS:
        return True
    tokens = set(re.split(r"\s+", f"{node.attrs.get('class', '')} {node.attrs.get('id', '')}".casefold()))
    return bool(tokens & NOISE_TOKENS)


def collect_anchors(root: Node) -> set[str]:
    result: set[str] = set()
    for node in _walk(root):
        for key in ("id", "name"):
            value = node.attrs.get(key)
            if value and not value.casefold().startswith("winchm_"):
                result.add(value)
    return result


@dataclass(slots=True)
class RenderStats:
    headings: int = 0
    lists: int = 0
    markdown_tables: int = 0
    html_tables: int = 0
    images: int = 0
    links: int = 0
    anchors: int = 0
    noise_nodes_removed: int = 0


LinkCallback = Callable[[str, str], str | None]
ImageCallback = Callable[[str, str], str | None]


class MarkdownRenderer:
    def __init__(self, *, link_callback: LinkCallback, image_callback: ImageCallback) -> None:
        self.link_callback = link_callback
        self.image_callback = image_callback
        self.stats = RenderStats()
        self._preserved_winchm_top_ids: set[int] = set()

    def render(self, root: Node) -> str:
        has_separate_content = any(
            node.attrs.get("id", "").casefold() == WINCHM_CONTENT_ID
            for node in _walk(root)
        )
        self._preserved_winchm_top_ids = {
            id(node)
            for node in _walk(root)
            if node.attrs.get("id", "").casefold() == WINCHM_TEMPLATE_TOP_ID
            and not has_separate_content
        }
        body = next((node for node in _walk(root) if node.tag == "body"), root)
        value = self._render_children(body)
        value = re.sub(r"[ \t]+\n", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip() + "\n"

    def _anchor(self, node: Node) -> str:
        value = node.attrs.get("id") or node.attrs.get("name")
        if not value:
            return ""
        if value.casefold().startswith("winchm_"):
            return ""
        self.stats.anchors += 1
        return f'<a id="{html.escape(value, quote=True)}"></a>\n'

    def _render_children(self, node: Node, *, inline: bool = False) -> str:
        return "".join(self._render(child, inline=inline) for child in node.children)

    def _render(self, item: Node | str, *, inline: bool = False) -> str:
        if isinstance(item, str):
            return re.sub(r"\s+", " ", item)
        node = item
        if is_noise(node, preserve_winchm_top=id(node) in self._preserved_winchm_top_ids):
            self.stats.noise_nodes_removed += 1
            return ""
        tag = node.tag
        if tag in {"document", "html", "body"}:
            return self._render_children(node, inline=inline)
        if tag in {"head", "title", "meta", "link", "base"}:
            return ""
        anchor = self._anchor(node)
        if re.fullmatch(r"h[1-6]", tag):
            self.stats.headings += 1
            level = int(tag[1])
            text = normalize_inline(self._render_children(node, inline=True))
            return f"\n\n{anchor}{'#' * level} {text}\n\n" if text else anchor
        if tag == "br":
            return "\n" if not inline else "  \n"
        if tag == "hr":
            return "\n\n---\n\n"
        if tag in {"strong", "b"}:
            text = normalize_inline(self._render_children(node, inline=True))
            return f"**{text}**" if text else ""
        if tag in {"em", "i"}:
            text = normalize_inline(self._render_children(node, inline=True))
            return f"*{text}*" if text else ""
        if tag == "code":
            text = normalize_inline(plain_text(node))
            return f"`{text.replace('`', '``')}`"
        if tag == "pre":
            return f"\n\n```\n{plain_text(node, exclude_noise=False).strip()}\n```\n\n"
        if tag == "blockquote":
            text = self._render_children(node).strip()
            return "\n\n" + "\n".join(f"> {line}" for line in text.splitlines()) + "\n\n"
        if tag in {"ul", "ol"}:
            return self._render_list(node, ordered=tag == "ol")
        if tag == "li":
            return normalize_inline(self._render_children(node, inline=True))
        if tag == "a":
            label = normalize_inline(self._render_children(node, inline=True))
            href = node.attrs.get("href")
            if not href:
                return anchor + label
            target = self.link_callback(href, label or href)
            if target is None:
                return anchor + (label or href)
            self.stats.links += 1
            return anchor + f"[{label or href}]({target})"
        if tag == "img":
            source = node.attrs.get("src", "")
            alt = node.attrs.get("alt") or node.attrs.get("title") or "image"
            target = self.image_callback(source, alt)
            if target is None:
                return f"\n\n<!-- unresolved image: {html.escape(source)} -->\n\n"
            self.stats.images += 1
            return f"![{alt}]({target})"
        if tag == "table":
            return self._render_table(node)
        if tag == "object":
            return self._render_sitemap_object(node)
        if tag == "param":
            return ""
        content = self._render_children(node, inline=inline or tag in {"span", "font", "small", "sup", "sub", "label"})
        if tag in BLOCK_TAGS:
            return f"\n\n{anchor}{content.strip()}\n\n" if content.strip() else anchor
        return anchor + content

    def _render_list(self, node: Node, *, ordered: bool) -> str:
        self.stats.lists += 1
        lines: list[str] = []
        index = 1
        for child in node.children:
            if isinstance(child, Node) and child.tag in {"ul", "ol"}:
                nested_text = self._render_list(child, ordered=child.tag == "ol").strip()
                # 缺少父 LI 的嵌套列表没有可表达的父项；按当前层级保留其项目，
                # 避免丢失内容或制造一个不存在的空父项目。
                lines.extend(nested_text.splitlines())
                continue
            if not isinstance(child, Node) or child.tag != "li":
                continue
            inline_parts: list[str] = []
            nested: list[Node] = []
            for part in child.children:
                if isinstance(part, Node) and part.tag in {"ul", "ol"}:
                    nested.append(part)
                else:
                    inline_parts.append(self._render(part, inline=True))
            marker = f"{index}." if ordered else "-"
            text = normalize_inline("".join(inline_parts))
            lines.append(f"{marker} {text}".rstrip())
            for nested_list in nested:
                nested_text = self._render_list(nested_list, ordered=nested_list.tag == "ol").strip()
                lines.extend(f"  {line}" for line in nested_text.splitlines())
            index += 1
        return "\n\n" + "\n".join(lines) + "\n\n"

    def _table_rows(self, table: Node) -> tuple[list[list[Node]], bool]:
        rows: list[list[Node]] = []
        complex_table = False
        for node in _walk(table):
            if node is not table and node.tag == "table":
                complex_table = True
            if node.tag != "tr":
                continue
            cells = [child for child in node.children if isinstance(child, Node) and child.tag in {"th", "td"}]
            if cells:
                rows.append(cells)
                if any(cell.attrs.get("rowspan", "1") != "1" or cell.attrs.get("colspan", "1") != "1" for cell in cells):
                    complex_table = True
        widths = {len(row) for row in rows}
        if not rows or len(widths) != 1 or max(widths, default=0) > 8:
            complex_table = True
        return rows, complex_table

    def _render_table(self, table: Node) -> str:
        caption_node = next(
            (child for child in table.children if isinstance(child, Node) and child.tag == "caption"),
            None,
        )
        caption = normalize_inline(self._render_children(caption_node, inline=True)) if caption_node else ""
        caption_prefix = f"\n\n**{caption}**\n\n" if caption else "\n\n"
        rows, complex_table = self._table_rows(table)
        if complex_table:
            self.stats.html_tables += 1
            return caption_prefix + self._minimal_table_html(table) + "\n\n"
        self.stats.markdown_tables += 1
        rendered = [[normalize_inline(self._render_children(cell, inline=True)).replace("|", "\\|") for cell in row] for row in rows]
        header = rendered[0]
        lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
        lines.extend("| " + " | ".join(row) + " |" for row in rendered[1:])
        return caption_prefix + "\n".join(lines) + "\n\n"

    def _minimal_table_html(self, table: Node) -> str:
        allowed = {"table", "thead", "tbody", "tfoot", "tr", "th", "td", "br", "strong", "b", "em", "i", "a", "img"}
        def serialize(item: Node | str) -> str:
            if isinstance(item, str):
                return html.escape(re.sub(r"\s+", " ", item))
            if is_noise(item):
                return ""
            if item.tag == "caption":
                return ""
            if item.tag not in allowed:
                return "".join(serialize(child) for child in item.children)
            attrs = ""
            if item.tag in {"td", "th"}:
                kept = [(key, value) for key, value in item.attrs.items() if key in {"rowspan", "colspan"} and value]
                attrs = "".join(f' {key}="{html.escape(value, quote=True)}"' for key, value in kept)
            if item.tag == "br":
                return "<br>"
            if item.tag == "a":
                label = normalize_inline(plain_text(item))
                href = item.attrs.get("href", "")
                target = self.link_callback(href, label or href) if href else None
                return f'<a href="{html.escape(target, quote=True)}">{html.escape(label)}</a>' if target else html.escape(label)
            if item.tag == "img":
                alt = item.attrs.get("alt") or "image"
                target = self.image_callback(item.attrs.get("src", ""), alt)
                return f'<img src="{html.escape(target, quote=True)}" alt="{html.escape(alt, quote=True)}">' if target else ""
            content = "".join(serialize(child) for child in item.children)
            return f"<{item.tag}{attrs}>{content}</{item.tag}>"
        return serialize(table)

    def _render_sitemap_object(self, node: Node) -> str:
        params = {
            child.attrs.get("name", "").casefold(): child.attrs.get("value", "")
            for child in node.children if isinstance(child, Node) and child.tag == "param"
        }
        label = params.get("name", "")
        local = params.get("local", "")
        if not label and not local:
            return ""
        if local:
            target = self.link_callback(local, label or local)
            return f"[{label or local}]({target})" if target else (label or local)
        return label


def source_visible_segments(root: Node) -> list[str]:
    segments: list[str] = []
    has_separate_content = any(
        node.attrs.get("id", "").casefold() == WINCHM_CONTENT_ID
        for node in _walk(root)
    )
    preserved_winchm_top_ids = {
        id(node)
        for node in _walk(root)
        if node.attrs.get("id", "").casefold() == WINCHM_TEMPLATE_TOP_ID
        and not has_separate_content
    }

    def collect(node: Node) -> None:
        if is_noise(node, preserve_winchm_top=id(node) in preserved_winchm_top_ids):
            return
        for child in node.children:
            if isinstance(child, str):
                value = normalize_inline(child)
                if value:
                    segments.append(value)
            else:
                collect(child)
    collect(root)
    return segments
