# M1-C2A：全量 Markdown 构建

状态：**实现与自动验证完成；M1-C2B Release Gate 已通过**

## 1. 目标与边界

M1-C2A 将 M1-C1 已通过人工验收的 HTML → Markdown 管线应用于 M1-B Inventory 的全部 HTML Entry，形成确定、可追溯且可供后续发布层消费的全量输入。

本阶段不生成 Fragment、Boundary、Knowledge Node、Library 或 Relationship，不修复全部 Source 缺陷，不实现 Obsidian Publisher，也不访问 Vault。

## 2. 输入与输出

- Artifact ID：`urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408`
- 主输入：`build/acquisition-run-1/f1824e5ebdc3584ba98398335dbf1408/`
- 独立重跑输入：`build/acquisition-run-2/f1824e5ebdc3584ba98398335dbf1408/`
- 主输出：`build/m1c2a-full/`
- 对照输出：`build/m1c2a-full-rerun/`

输出接口：

```text
build/m1c2a-full/
├── README.md
├── markdown-manifest.jsonl
├── markdown/
├── assets/
└── reports/
    ├── entries.jsonl
    ├── build-report.json
    ├── encoding-report.json
    ├── fidelity-report.json
    ├── link-report.json
    ├── asset-report.json
    ├── navigation-report.json
    └── navigation-tree.jsonl
```

`markdown-manifest.jsonl` 是后续发布层的稳定逐 Entry 输入清单，不是 Publish Manifest。最终 Obsidian 目录结构不得从当前 `markdown/` 物理布局推断。

## 3. 路径、身份与导航

- 每个成功的物理 HTML Entry 恰好生成一份 Markdown。
- 文件名由可读标题和稳定 Entry ID 派生；标题不承担身份职责。
- `source_path` 逐字符复制 M1-B `Entry.original_path`，是相对 Link / Image 的解析基准。
- `navigation_paths` 按 HHC 出现顺序记录零条、一条或多条导航路径。
- `navigation-tree.jsonl` 逐节点保留 HHC Node ID、Parent、Depth、Sibling Order、Local、Target Entry 与完整 Path；没有 `Local` 的纯目录节点也不得丢弃。
- 多条导航路径不会复制正文。
- Front Matter 同时固定 Artifact ID、Entry ID、Source Path、Navigation Paths、Source SHA-256 和检测编码。

## 4. 失败隔离与报告

构建分为 Preflight 与 Conversion 两阶段。单页解码、Source 校验、解析、转换或写入失败只把该 Entry 标记为 `failed`，不会中止其他页面。非 HTML Entry 不进入正文转换，并单独计为非 HTML 跳过。

机器可读报告分别覆盖：

- 成功、失败、跳过和警告；
- 编码使用分布与声明冲突；
- 可见文本保留率、零正文和极短正文候选；
- Markdown Table 与最小 HTML Table；
- Link 解析、缺失目标和缺失 Anchor；
- Image 引用、唯一复制资产和缺失资源；
- HHC 导航覆盖、一对多导航关系、完整节点树、纯目录节点、兄弟顺序和导航来源。

## 5. 实际结果

| 指标 | 结果 |
|---|---:|
| Inventory Entry | 7,148 |
| HTML Entry | 6,819 |
| HTML 成功 | 6,819 |
| HTML 失败 | 0 |
| HTML 跳过 | 0 |
| 非 HTML 跳过 | 329 |
| Markdown Table | 3,944 |
| 最小 HTML Table | 1,721 |
| 已解析 Link | 8,052 |
| Unresolved Reference | 4,710 |
| Image Reference | 301 |
| 唯一复制资产 | 104 |
| 有警告 Entry | 81 |

编码结果：

- GB18030：6,817；
- UTF-8：2；
- 编码声明冲突：2。

Fidelity 候选：

- 可见文本保留率低于 `0.98`：6；
- 极短正文：74；
- 零正文：1。

Unresolved 分类：

- `target-not-found`：4,403；
- `asset-not-found`：134；
- `external-or-empty-image`：38；
- `missing-page-anchor`：135。

上述异常没有被静默修复或伪造成有效目标。

## 6. Validator

Validator 检查：

- Markdown 为 UTF-8 且无 CR；
- Markdown 不包含私人绝对路径；
- Front Matter 与 Manifest 的 Entry ID、Source Path、Navigation Paths、摘要和编码一致；
- 输出路径位于构建根目录内；
- 每个 Entry 只对应一份正文；
- Manifest 与实际 Markdown 文件闭合；
- 所有本地 Markdown / HTML Image 引用指向构建根目录内的真实普通文件；
- 资产摘要与 Source SHA-256 一致；
- 报告成功数与 Manifest 一致。

## 7. CLI

```bash
PYTHONPATH=src .venv/bin/python -m lorebuddy.cli markdown build <artifact-dir> --output build/m1c2a-full --json
PYTHONPATH=src .venv/bin/python -m lorebuddy.cli markdown validate build/m1c2a-full --json
PYTHONPATH=src .venv/bin/python -m lorebuddy.cli markdown report build/m1c2a-full --json
```

## 8. 确定性

两次构建分别读取两份独立、已验证的 M1-B 摄取产物。两份输出均通过 Validator，`diff -rq` 对完整目录返回零差异。

完整 HHC 树包含 8,187 个节点：7,716 个节点解析到 Entry，471 个节点没有 `Local`、仅表示目录，缺失目标为 0。两份当前构建目录树摘要均为 `115216460adf2fd86b6fb28006c48c400ea1c2a828490b7785e0308fb34b45b3`。

## 9. 后续门禁

M1-C2B 已以局部规则修复一个实质正文误删、56 个 Table Caption 遗漏和一个嵌套 List 遗漏。58 个受影响 Entry 已全部闭合；残余 6 个低保留率候选均为既有 HTML Entity 指标假阳性，74 个极短页面保留率均为 `1.000`，唯一零正文页面是 Source 本身为空的模板。详见 [M1-C2B Release Gate](m1c2b-release-gate.md)。缺失目标、缺失资产与缺失 Anchor 已完整报告，不要求批量修复。

下一阶段优先实现一个不拆 Fragment 的 Obsidian Baseline Publisher，消费 `markdown-manifest.jsonl`、`markdown/`、`assets/` 与报告，使用户尽快获得可直接打开、可浏览、图片和链接有效的完整 Vault。Publisher 必须自行定义 Vault 投影视图，不能把当前构建目录结构当成最终 Obsidian 目录结构。
