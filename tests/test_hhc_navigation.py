from lorebuddy.samples.hhc_navigation import (
    extract_navigation_paths,
    extract_navigation_tree,
    navigation_key,
)


def test_hhc_navigation_keeps_local_path_separate_from_name_hierarchy():
    source = '''
    <ul><li><object type="text/sitemap">
      <param name="Name" value="珊娜萨的万事指南"><param name="Local" value="book/index.htm">
    </object><ul><li><object type="text/sitemap">
      <param name="Name" value="附录：角色姓名（缺少翻译）"><param name="Local" value="book/names.htm">
    </object><ul><li><object type="text/sitemap">
      <param name="Name" value="侏儒姓名"><param name="Local" value="">
    </object><ul><li><object type="text/sitemap">
      <param name="Name" value="侏儒女性名"><param name="Local" value="book/gnome-female.htm">
    </object></ul></ul></ul></ul>
    '''
    paths = extract_navigation_paths(source)
    assert paths[navigation_key("book/gnome-female.htm")] == ["珊娜萨的万事指南/附录：角色姓名（缺少翻译）/侏儒姓名/侏儒女性名"]

    tree = extract_navigation_tree(source, source_entry_id="urn:uuid:source")
    assert [node["title"] for node in tree] == [
        "珊娜萨的万事指南",
        "附录：角色姓名（缺少翻译）",
        "侏儒姓名",
        "侏儒女性名",
    ]
    assert [node["source_order"] for node in tree] == [0, 1, 2, 3]
    assert [node["sibling_order"] for node in tree] == [0, 0, 0, 0]
    assert tree[2]["local"] is None
    assert tree[3]["parent_node_id"] == tree[2]["navigation_node_id"]
    assert tree[3]["depth"] == 4
