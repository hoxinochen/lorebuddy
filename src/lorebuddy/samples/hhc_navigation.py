"""从 CHM HHC 的 Name 层级提取导航路径，不把它伪装成物理 Entry 路径。"""

from __future__ import annotations

import posixpath
import unicodedata
import uuid
from collections import defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit


NAVIGATION_NODE_NAMESPACE = uuid.UUID("39539723-4754-5fec-8912-8cce87445a15")


def _local_key(value: str) -> str:
    path = urlsplit(unquote(value).replace("\\", "/")).path.lstrip("/")
    return unicodedata.normalize("NFC", posixpath.normpath(path)).casefold()


@dataclass(frozen=True, slots=True)
class RawNavigationNode:
    source_order: int
    parent_source_order: int | None
    sibling_order: int
    depth: int
    title: str
    local: str | None
    navigation_path: str


class _HHCParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parents: list[str | None] = []
        self.last_name_by_depth: dict[int, str] = {}
        self.params: dict[str, str] | None = None
        self.paths: dict[str, list[str]] = defaultdict(list)
        self.nodes: list[RawNavigationNode] = []
        self.parent_orders: list[int | None] = []
        self.last_order_by_depth: dict[int, int] = {}
        self.sibling_counts: defaultdict[int | None, int] = defaultdict(int)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        values = {key.casefold(): value or "" for key, value in attrs}
        if tag == "ul":
            self.parents.append(self.last_name_by_depth.get(len(self.parents)))
            self.parent_orders.append(self.last_order_by_depth.get(len(self.parent_orders)))
        elif tag == "object" and values.get("type", "").casefold() == "text/sitemap":
            self.params = {}
        elif tag == "param" and self.params is not None:
            self.params[values.get("name", "").casefold()] = values.get("value", "")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag == "object" and self.params is not None:
            name = self.params.get("name", "").strip()
            local = self.params.get("local", "").strip()
            if name:
                depth = len(self.parents)
                source_order = len(self.nodes)
                parent_source_order = (
                    self.parent_orders[-1] if self.parent_orders else None
                )
                sibling_order = self.sibling_counts[parent_source_order]
                self.sibling_counts[parent_source_order] += 1
                navigation_path = "/".join(
                    [parent for parent in self.parents if parent] + [name]
                )
                self.nodes.append(
                    RawNavigationNode(
                        source_order=source_order,
                        parent_source_order=parent_source_order,
                        sibling_order=sibling_order,
                        depth=depth,
                        title=name,
                        local=local or None,
                        navigation_path=navigation_path,
                    )
                )
                self.last_name_by_depth[depth] = name
                self.last_order_by_depth[depth] = source_order
            if name and local:
                key = _local_key(local)
                if key and navigation_path not in self.paths[key]:
                    self.paths[key].append(navigation_path)
            self.params = None
        elif tag == "ul" and self.parents:
            depth = len(self.parents)
            self.parents.pop()
            self.parent_orders.pop()
            for key in [key for key in self.last_name_by_depth if key >= depth]:
                del self.last_name_by_depth[key]
            for key in [key for key in self.last_order_by_depth if key >= depth]:
                del self.last_order_by_depth[key]


def extract_navigation_paths(text: str) -> dict[str, list[str]]:
    """返回以规范化 HHC Local 为键、按 HHC 出现顺序排列的导航面包屑。"""

    parser = _HHCParser()
    parser.feed(text)
    parser.close()
    return dict(parser.paths)


def extract_navigation_tree(
    text: str,
    *,
    source_entry_id: str,
) -> list[dict[str, object]]:
    """保留 HHC 全部有名称节点、父子关系和原始兄弟顺序。"""

    parser = _HHCParser()
    parser.feed(text)
    parser.close()
    ids = {
        node.source_order: f"urn:uuid:{uuid.uuid5(NAVIGATION_NODE_NAMESPACE, f'{source_entry_id}:{node.source_order}')}"
        for node in parser.nodes
    }
    return [
        {
            "schema": "m1c2a.navigation-node@0.1.0",
            "navigation_node_id": ids[node.source_order],
            "source_entry_id": source_entry_id,
            "source_order": node.source_order,
            "parent_node_id": (
                ids[node.parent_source_order]
                if node.parent_source_order is not None
                else None
            ),
            "sibling_order": node.sibling_order,
            "depth": node.depth,
            "title": node.title,
            "local": node.local,
            "navigation_path": node.navigation_path,
        }
        for node in parser.nodes
    ]


def navigation_key(source_path: str) -> str:
    """将物理 Entry 路径转换为仅用于 HHC Local 匹配的键。"""

    return _local_key(source_path)
