# M1-C3：Obsidian Baseline Publisher

状态：**人工验收与自动验收完成 / PASS**

## 1. 目标与边界

M1-C3 把已通过 Release Gate 的 M1-C2A Build Root 投影为一个独立、可直接用 Obsidian 打开的 Baseline Vault。

Publisher 只消费显式传入的 Build Root，不读取 CHM、Acquisition、Release Gate 文档、Vault 配置、进程缓存或当前工作目录中的隐式状态。本阶段不生成 Fragment、Boundary、Knowledge Node、Relationship 或 Library，不访问用户现有 Vault。

## 2. 输入合同

唯一逐 Entry 枚举入口是 `markdown-manifest.jsonl`。Publisher 还显式读取：

- `.lorebuddy-m1c2a.json`；
- Manifest 声明的 Markdown；
- `reports/entries.jsonl`；
- Build、Encoding、Fidelity、Link、Asset、Navigation Report；
- `reports/navigation-tree.jsonl` 中的完整 HHC 节点树。

构建前必须先通过 M1-C2A Validator。Manifest、成功 Entry、Markdown 或 Asset 不闭合时拒绝发布。

## 3. 输出结构

```text
build/m1c3-obsidian-baseline/
├── README.md
├── Home.md
├── Books/
├── Notes/
├── Assets/
├── Reports/
└── .lorebuddy/
    ├── .lorebuddy-m1c3.json
    ├── publisher-manifest.jsonl
    ├── ownership-manifest.json
    └── publish-report.json
```

实际产物：

| 类型 | 数量 |
|---|---:|
| 正文 Note | 6,819 |
| Asset | 104 |
| HHC Navigation Node | 8,187 |
| 纯目录节点 | 471 |
| Books 分层导航索引 | 1,489 |
| Publisher 受控文件总数 | 8,427 |

每个物理 Entry 恰好生成一份 `Notes/` 正文。多个 Navigation Path 只产生多个索引引用，不复制正文。

## 4. Note 与导航投影

Note Front Matter 原样保留 `entry_id`、`source_path`、有序 `navigation_paths`、`source_sha256` 和检测编码，并增加：

- `publisher_profile`；
- `publisher_release`；
- `publisher_note_path`。

正文物理路径从同一 Entry 的全部 HHC Target Node 中选择与物理 `source_path` 组件亲和度最高的真实祖先路径，再投影到 `Notes/<顶层>/<章节>/.../<词条>.md`；HHC Source Order 仅作为亲和度相同的平局规则。该规则避免把较早出现的速查入口误当作内容主目录，例如 `第三方/拳斗士/拳斗士.htm` 现在落到 `Notes/拳斗士/拳斗士.md`，而不是 `Notes/本书速查/职业速查/拳斗士.md`。Navigation Path 缺失时进入 `Notes/_Unclassified/<标题>.md`。正常文件名不包含 Entry ID；只有多个 Entry 的 NFC、大小写不敏感规范化输出路径发生碰撞时，相关文件才追加稳定 Entry ID 短后缀。当前 6,819 份正文中有 2 份属于同一碰撞组，另有 6 份进入 `_Unclassified`。

采用 Source Path 亲和度是为了在多导航场景中确定一个更接近内容归属的单一物理位置；按全部路径复制正文会破坏“一 Entry 一正文”，机械采用第一次 HHC 出现则会把速查入口误作主目录。其他导航位置继续通过完整 `Books/` 树链接同一正文。稳定身份仍由 Front Matter、Publisher Manifest 和 Ownership Manifest 中的 Entry ID 承担，标题或路径变化不改变身份。

`Home.md` 提供 68 个 HHC 顶层节点和一个 `_Unclassified` 入口。`Books/` 按 HHC Parent / Child 关系生成多层 `_目录.md`：原始 `sibling_order` 决定同级显示顺序，471 个没有 `Local` 的纯目录节点仍生成目录索引；有正文的节点链接到唯一 `Notes/` 文件，同一 Entry 的多处导航节点只生成多个链接，不复制正文。

## 5. Link 与 Asset

Baseline 使用标准 Markdown 相对链接，不使用 Wikilink 或插件语法。

- 已解析本地页面 Link：7,890 次确定性投影；
- 成功本地图片引用：129 次重写，指向 104 个真实 Asset；
- External Link：保持外部 URL；
- Unresolved：4,710 次，继续以原正文可见形式和 Report 记录存在，不创建空 Note 或伪 Asset。

所有 Link 重写以 Link Report 的 `target_entry_id` 和 Publisher Manifest 为依据，不按标题猜测。页面内 Anchor 随目标 Note 路径一起保留。

## 6. Ownership 与安全发布

`publisher-manifest.jsonl` 每行记录一个正文 Note，包括 Entry ID、输入路径、输出路径、Source Path、Navigation Paths、Source 摘要和发布内容摘要。

`ownership-manifest.json` 记录 Publisher 拥有的全部生成或复制文件：

- 文件类型；
- Entry ID 或 Asset Entry ID；
- 输入来源；
- 输出路径；
- 内容 SHA-256；
- Publisher 版本。

Ownership Manifest 自身不记录自身摘要，使用 `self_digest_policy: excluded-to-avoid-self-referential-digest` 明确处理不可解的自引用摘要；Validator 把 `self_path` 与其余声明文件共同纳入闭合检查。

发布流程：

1. 完整计算发布计划；
2. Dry Run 报告 create、rewrite、unchanged、remove；
3. 在同级受控 Staging 目录完整生成；
4. Publisher Validator 通过；
5. 原子切换输出目录；
6. 失败时保留上一份完整输出。

未知输出目录、未知 Staging 或未知 Backup 均拒绝覆盖或清理。

## 7. CLI

```bash
PYTHONPATH=src .venv/bin/python -m lorebuddy.cli obsidian publish \
  build/m1c2a-full \
  --output build/m1c3-obsidian-baseline \
  --dry-run \
  --json

PYTHONPATH=src .venv/bin/python -m lorebuddy.cli obsidian publish \
  build/m1c2a-full \
  --output build/m1c3-obsidian-baseline \
  --json

PYTHONPATH=src .venv/bin/python -m lorebuddy.cli obsidian validate \
  build/m1c3-obsidian-baseline \
  --json

PYTHONPATH=src .venv/bin/python -m lorebuddy.cli obsidian report \
  build/m1c3-obsidian-baseline \
  --json
```

## 8. Validator 与确定性

Publisher Validator 检查：

- Marker、Publisher Manifest、Ownership Manifest 与实际文件闭合；
- 每个 Entry 恰好一份正文；
- Front Matter 与 Publisher Manifest 一致；
- UTF-8、LF、无 Publisher 设备私人绝对路径；
- Note 与 Asset 摘要；
- 本地 Link、Image 和导航入口目标存在；
- HHC Navigation Node、目录索引数量和 Node ID 闭合；
- 输出路径不逃逸 Vault；
- 未声明或未知文件不能被 Publisher 冒充所有。

两次真实发布分别输出到：

- `build/m1c3-obsidian-baseline/`；
- `build/m1c3-obsidian-baseline-rerun/`。

两份 Validator 均为 `valid: true`，完整目录零差异。两份 M1-C2A 输入树摘要均为 `115216460adf2fd86b6fb28006c48c400ea1c2a828490b7785e0308fb34b45b3`；两份 Publisher 输出树摘要均为 `23bae8563e51a0a5db4b2b070fccc4483c31f531a1e460c50322c8f6042a9488`。CHM SHA-256 保持 `836eea8912cf6c068687e99db4a1b4b6b915aeb2ef8af35cfb040803184686f2`。

## 9. 产品样本验收

八类真实样本已检查：

| 类型 | 代表输出 | 结果 |
|---|---|---|
| 图片 | `Notes/歪曲之月/附录A：生物图集/魔宠/叮当锅.md` | HTML Image 指向真实 Asset |
| Caption | `Notes/珊娜萨的万事指南/附录：角色姓名（缺少翻译）/矮人姓名/灰矮人氏族名.md` | Caption 恰好一次，文件名可读 |
| 嵌套 List | `Notes/珊娜萨的万事指南/城主工具/奖励魔法物品.md` | 四条说明各保留一次 |
| 多 Navigation Path | `Notes/玩家手册2024/附录B：生物数据卡/野兽/CR0-1-4/蟹.md` | 两条路径保留，一份正文 |
| 已解析 Link | `Notes/写在前面.md` | 目标 Note 存在 |
| Unresolved | `Notes/本书速查/法术速查/万法大全速查表.md` | 未伪造成有效链接 |
| 极短正文 | `Notes/瓦罗的怪物指南（旧版）/图鉴/异怪/眼魔.md` | Source 短正文保持可读 |
| Intentional Blank | `Notes/_Unclassified/纯空白页模板.md` | 保持 Source Reality |

完整 HHC 树修正版的机器辅助结果保存在 Git 忽略的 `navigation-tree.jsonl`、构建产物及 Publisher Manifest 中。首页、69 个顶层入口、1,489 个 Books 索引、全部本地图片、已解析内部链接和正文唯一性均通过检查；两次完整目录树摘要一致。

## 10. Known Limitations

- 4,403 个 Source Missing / Broken Link；
- 135 个缺失 Anchor；
- 134 个缺失本地 Asset；
- 38 个 External Image Reference；
- 74 个 Source 极短页面；
- 1 个 Intentional Blank；
- 未实现 Fragment、Knowledge Node、Relationship 或人工维护的语义导航；
- 未向用户现有 Vault 执行增量发布。

上述限制不阻断把独立输出目录作为 Baseline Vault 打开。M1-C3 自动验收与用户
人工浏览均已完成，阶段结论为 **PASS**。验收证据见
`m1c3-acceptance.md`。
