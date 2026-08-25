from pathlib import Path

from lorebuddy.samples.html_to_markdown import MarkdownRenderer, collect_anchors, parse_html


def _render_fixture(project_root: Path, name: str) -> tuple[str, MarkdownRenderer]:
    source = (project_root / "fixtures" / "m1c2b" / name).read_text(encoding="utf-8")
    renderer = MarkdownRenderer(link_callback=lambda *_: None, image_callback=lambda *_: None)
    return renderer.render(parse_html(source)), renderer


def test_converter_preserves_structure_and_cleans_noise():
    source = """
    <html><head><title>测试页</title><style>.x{}</style><script>bad()</script></head>
    <body><nav>导航噪声</nav><div id="winchm_template_content"><h1 id="top">标题</h1><p>正文 <b>加粗</b></p></div>
    <ul><li>甲</li><li>乙</li></ul>
    <table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>
    <p><a href="other.htm#part">目标</a><img src="image.png" alt="图"></p></body></html>
    """
    root = parse_html(source)
    assert collect_anchors(root) == {"top"}
    renderer = MarkdownRenderer(
        link_callback=lambda raw, label: "other.md#part" if raw else None,
        image_callback=lambda raw, alt: "../assets/image.png" if raw else None,
    )
    markdown = renderer.render(root)
    assert '# 标题' in markdown
    assert '<a id="top"></a>' in markdown
    assert "- 甲\n- 乙" in markdown
    assert "| A | B |" in markdown
    assert "[目标](other.md#part)" in markdown
    assert "![图](../assets/image.png)" in markdown
    assert "bad()" not in markdown
    assert "导航噪声" not in markdown
    assert "winchm_template_content" not in markdown
    assert renderer.stats.noise_nodes_removed >= 1


def test_complex_table_is_preserved_as_minimal_html():
    root = parse_html('<table class="layout"><tr>\r\n<td rowspan="2" style="x">A</td><td>B</td></tr><tr><td>C</td></tr></table>')
    renderer = MarkdownRenderer(link_callback=lambda *_: None, image_callback=lambda *_: None)
    markdown = renderer.render(root)
    assert '<table>' in markdown
    assert '<td rowspan="2">A</td>' in markdown
    assert 'class=' not in markdown and 'style=' not in markdown
    assert "\r" not in markdown
    assert renderer.stats.html_tables == 1


def test_orphaned_winchm_top_preserves_substantive_content_but_template_top_remains_noise(project_root: Path):
    substantive, _ = _render_fixture(project_root, "substantive-template-top.html")
    template, renderer = _render_fixture(project_root, "template-top-with-content.html")

    assert "这是唯一的实质正文。" in substantive
    assert "- 正文项目" in substantive
    assert "独立正文容器中的内容。" in template
    assert "上一页" not in template
    assert "Help > 示例" not in template
    assert "重复页眉标题" not in template
    assert renderer.stats.noise_nodes_removed >= 1


def test_visible_table_caption_is_emitted_once_and_empty_caption_is_ignored(project_root: Path):
    markdown, _ = _render_fixture(project_root, "table-caption.html")

    caption_position = markdown.index("**可见表格标题**")
    table_position = markdown.index("| 骰值 | 结果 |")
    assert caption_position < table_position
    assert markdown.count("可见表格标题") == 1
    assert "**空标题**" not in markdown
    assert "&nbsp;" not in markdown
    assert markdown.count("**复杂表格标题**") == 1
    assert markdown.index("**复杂表格标题**") < markdown.index("<table>")


def test_directly_nested_list_is_traversed_without_breaking_normal_nesting(project_root: Path):
    markdown, _ = _render_fixture(project_root, "nested-list.html")

    assert "- 挑战等级 0–4：掷骰七次" in markdown
    assert "- 挑战等级 5–10：掷骰十八次" in markdown
    assert "1. 普通有序项" in markdown
    assert "  - 普通嵌套项" in markdown
