# M1-C1：真实 Markdown 样本验证

状态：**人工验收通过（2026-07-23）**

## 1. 目标与边界

M1-C1 从 M1-B 已验证的 Entry Inventory 中选择 10 个真实页面，生成 UTF-8 Markdown、必要资产和机器可读报告，用于验证编码、结构、链接和基础可见文本保真。产物位于 Git 忽略的 `build/m1c1-samples/`，不是正式 Package 或 Library。

本阶段未执行全量转换，未生成 Fragment、Boundary、Knowledge Node 或 Relationship，也未实现 Publisher、写入 Obsidian Vault 或进入 M1-C2。

## 2. 输入与输出

- Artifact ID：`urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408`
- 输入：`build/acquisition-run-1/f1824e5ebdc3584ba98398335dbf1408/`
- 独立重跑输入：`build/acquisition-run-2/f1824e5ebdc3584ba98398335dbf1408/`
- 主输出：`build/m1c1-samples/`
- 对照输出：`build/m1c1-samples-rerun/`

输出包含 `README.md`、`sample-selection.json`、`markdown/`、`assets/` 和 `reports/`。每份 Markdown 的 Front Matter 仅包含 Artifact ID、Entry ID、Source Path、Navigation Paths、Source SHA-256 和检测编码。

### 路径语义

- `source_path` 直接复制 M1-B `Entry.original_path`，表示物理 CHM Entry 路径，逐字符保留并用于相对 Link / Image 解析。
- `navigation_paths` 从 `DND五版不全书.hhc` 的 `Name` 层级派生；HHC 的 `Local` 用于把导航节点关联到物理 Entry。一个 Entry 可以有零条、一条或多条导航路径。
- HHC Entry 为 `urn:uuid:fc940c37-a607-5d34-ba4d-b828e7afce55`，摘要为 `sha256:c126ee732d00d73ce7fb0937bd7e8cdf14b45006930bc560c6fa818d33288249`。
- 报告和 Markdown 不再把 HHC 面包屑称为 HTML Source Path，也不使用导航层级作为 Link 解析基准。

两个已核对样本的事实分别是：

| 标题 | Source Path（物理 Entry） | Navigation Path（HHC Name 层级） |
|---|---|---|
| 工匠工具 | `玩家手册2024/装备/工匠工具.htm` | `玩家手册2024/第六章：装备/工具/工匠工具` |
| 侏儒女性名 | `珊娜萨的万事指南/角色姓名/侏儒女性名.htm` | `珊娜萨的万事指南/附录：角色姓名（缺少翻译）/侏儒姓名/侏儒女性名` |

上述两个 Source Path 已分别通过 SevenZip `l -slt` 对原始 CHM 直接列举复核；其字节长度 `6966` 与 `33392` 也与 M1-B Inventory 一致。Navigation Path 则由 HHC 的嵌套 `Name` 值构成，叶节点 `Local` 仍指向对应的简短物理 Source Path。

## 3. 样本覆盖

| Entry ID 短标识 | 标题 | 主要验证点 |
|---|---|---|
| `5c782775` | 侏儒女性名 | 声明 GB2312、实际 UTF-8 的编码冲突，大型简单表格，缺失 HTML title |
| `993a9467` | 法术详述 | 长正文、多级标题、列表和表格 |
| `6a7341e5` | 非玩家角色 | 大量表格行、列表和长正文 |
| `8b7af327` | 帆船和战舰 | 标题、列表、表格和两张本地图片 |
| `8d4e8ddc` | 巴洛维亚 | 长正文、内部链接、页面内锚点和表格 |
| `107cca4c` | 魔法物品 | 同名消歧、WinCHM 导航噪声清理和简单表格 |
| `39f56ef5` | 魔法物品 | 同名不同内容、长正文和表格 |
| `40015881` | DND五版不全书 | HHK 导航索引、非规范 HTML 和跨页链接 |
| `d04d55e1` | 叛神武具 | 导航索引已选目标、长正文、列表和表格 |
| `6441be68` | 工匠工具 | `rowspan` / `colspan` 复杂表格的最小 HTML 回退 |

同名页面使用“可读标题 + Entry ID 短标识”确定性消歧，标题变化不承担身份职责。

## 4. 转换行为

- 解码采用 M1-B 编码候选，并进行严格解码；不修改 Source 字节。
- 简单矩形表格转换为 Markdown；跨行、跨列或嵌套等复杂表格保留最小 HTML。
- `script`、`style`、`nav` 和识别出的 WinCHM 导航节点不进入正文。
- 已选页面间链接改写为相对 Markdown Link；未选页面和不存在的页面内锚点进入 unresolved 报告。
- 本地图片按 Entry ID 分目录复制，并校验 Source SHA-256；不跟随符号链接。
- 可见文本保留率是候选检查，不构成 Full Fidelity Coverage Map；人工验收以 `reports/fidelity-review.md` 为准。

## 5. 实际结果

- 样本：10
- Markdown 表格：24
- 最小 HTML 表格：17
- 复制资产：2
- unresolved：25，其中未选择目标 20、缺失页面内锚点 5
- 编码：9 个 GB18030，1 个 UTF-8；确认 1 个编码声明冲突
- 自动可见文本保留率：9 页为 `1.000`；“侏儒女性名”为 `0.971`，需人工重点检查

unresolved 不会被伪造成可用链接。HHK 索引到“叛神武具”的链接已成功映射到所选 Markdown 页面。

## 6. 命令与确定性

```bash
PYTHONPATH=src .venv/bin/python -m lorebuddy.cli samples build <artifact-dir> --output build/m1c1-samples --json
PYTHONPATH=src .venv/bin/python -m lorebuddy.cli samples validate build/m1c1-samples --json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -p no:cacheprovider
.venv/bin/pip check
```

两次构建分别使用 M1-B 的两份确定性摄取产物，`diff -rq` 对完整输出目录返回零差异。两份输出均通过 `samples validate`。

## 7. 已知限制与人工门禁

- 未选择页面的 20 条链接只保留在报告中；后续阶段需先确定链接投影策略。
- “巴洛维亚”的 5 个锚点引用在来源页中找不到对应锚点，当前按 unresolved 处理。
- 自动文本保留率不验证版式语义、表格视觉对应关系或图片语义。
- 复杂表格依赖普通 Markdown 阅读器对内嵌 HTML 的支持。
- M1-C2 之前必须完成人工阅读，尤其检查编码冲突页、复杂表格、图片、锚点和同名文件体验。

人工验收文件：`build/m1c1-samples/reports/fidelity-review.md`。

## 8. 人工验收结论

用户已于 2026-07-23 确认样本通过人工审查，包括 unresolved 未伪造为有效链接、编码冲突页无乱码，以及 script、style 和明显导航噪声已移除。该结论授权进入 M1-C2A 全量 Markdown 构建，不授权 M1-C2B、Obsidian Publisher 或 Vault 写入。
