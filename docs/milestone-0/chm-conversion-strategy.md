# CHM → Knowledge Package 转换策略

状态：Draft / 尚未执行转换  
目标：建立可审计、可重跑、可扩展的知识工程流水线

## 1. 核心结论

转换不是：

```text
CHM → Markdown
```

而是：

```text
Acquire
→ Inventory
→ Preserve Source
→ Decode and Parse Evidence
→ Classify Works and Editions
→ Resolve Source References
→ Propose Knowledge Boundaries
→ Human Review
→ Render Library
→ Build Indexes
→ Validate
→ Release
```

每个阶段都必须保存输入摘要、工具版本、声明式决策和问题报告。任何阶段不得用推测掩盖歧义。

## 2. 转换对象模型

```text
Knowledge Node ──Provenance──> Fragment ──> Entry ──> Artifact
                                    │
                                    └──经审核的多对多来源映射──> Edition ──> Work
```

Work / Edition 是出版来源模型；Artifact / Entry / Fragment 是实际摄取证据。两条链通过可审核的多对多映射连接。一个 Artifact 可以聚合多个 Edition；同一 Edition 也可以由多个 Artifact 提供证据。一个 Fragment 可以被多个 Node 引用，Node 也可以在经过批准时引用多个 Fragment。

当前 CHM 是一个 Artifact，但不是一个 Edition。它的 Entry 可能分别声称来自多个 Work / Edition，也可能是社区原创、第三方、Playtest、模组或未知内容。

## 3. 阶段 0：设计与授权门禁

开始正式转换前必须确认：

- 知识包规范；
- Source 与 Library 边界；
- Node ID 和生命周期；
- Provenance Locator；
- Package 访问级别；
- 当前 CHM 的保存和再分发范围；
- 谁可以批准来源映射与节点边界。

未知授权不阻止在受限环境登记 Artifact，但阻止对外发布和把内容复制到公开 Package。

## 4. 阶段 1：Acquire

输入被视为不可信、不可变字节。

记录：

- 原始文件名；
- 大小；
- SHA-256；
- 获取渠道与时间；
- 提供者；
- MIME 与容器格式；
- 权利和访问状态；
- 恶意内容扫描结果；
- Artifact ID。

同一摘要可以复用字节存储，但不能自动合并 Acquisition Record。不同获取渠道可能具有不同证据和权利状态。

### 禁止

- 用新 CHM 覆盖旧 CHM；
- 解包前重命名后丢失原文件名；
- 只保存解包内容而不保存容器；
- 把文件修改时间当作唯一发布日期或编译时间。

## 5. 阶段 2：Inventory

在写出 Entry 前先读取容器目录，生成完整 Inventory：

```json
{
  "schema": "core.source-entry@0.1.0",
  "id": "urn:uuid:...",
  "artifact_id": "urn:uuid:...",
  "original_path": "...",
  "original_path_bytes": {"encoding": "base64", "value": "..."},
  "original_path_decoding": {"charset": "utf-8", "status": "exact"},
  "directory_record_digest": "sha256:...",
  "storage_path": "entries/...",
  "size": 123,
  "digest": "sha256:...",
  "container_location": {
    "section": 1,
    "section_logical_offset": 0,
    "uncompressed_length": 123
  },
  "path_safety": "safe",
  "extraction_status": "pending"
}
```

检查：

- `..` 与绝对路径；
- Windows 保留名；
- `/` 与 `\`；
- 大小写折叠冲突；
- Unicode NFC/NFD 冲突；
- 尾随空格或句点；
- 重复目录记录；
- 过长路径；
- 非 UTF-8 路径；
- 零长度与超大资源；
- 声明长度越界。

生成后的 `inventory.jsonl` 一行恰好一个完整 `core.source-entry@0.1.0`，是 Entry ID 与路径字段的唯一规范事实源；写出 Entry 后补齐 Digest 与最终提取状态，再封存并由 Extraction Receipt 固定摘要。原始路径不能直接作为安全宿主路径的唯一依据。`path-map.jsonl` 只能从 Inventory 确定性投影，并且必须能从存储路径还原同一 Entry 的原路径。

`original_path_bytes` 以 RFC 4648 Base64 保存 CHM Directory 名称原始 byte，并由 Directory Record 摘要佐证；它是路径身份的规范证据。`original_path` 是严格解码视图，必须记录 Charset 与成功/失败状态，禁止使用替换字符。若 UI 需要去除前导分隔符或生成 Breadcrumb，应另建显示字段，不能改写证据字段。

## 6. 阶段 3：Preserve Source

保存两类证据：

```text
sources/artifacts/<artifact-key>/original/input.chm
sources/artifacts/<artifact-key>/entries/...
```

原始 CHM 证明容器字节；解包 Entry 让未来工具无需再次理解 CHM 即可读取内容。二者都必须保留。

每个 Entry 记录：

- SHA-256 与长度；
- 原始和安全路径；
- Container Section、Section Logical Offset 与 Uncompressed Length；
- 初始 MIME / Charset 声明；检测 MIME 与实际 Decoder 结果在后续观察记录中补充；
- 提取工具及版本；
- 提取成功、失败或隔离状态。

### 6.1 解包验证

CHM 不提供可信的逐 Entry 内容摘要。首个正式摄取应该：

1. 用锁定版本的主解包器提取；
2. 用第二个独立实现全量交叉验证所有可提取 Entry 的长度与 SHA-256；
3. 验证所有非零目录 Stream 均已输出或被解释为内部控制 Stream；
4. 连续提取两次并比较 Inventory；
5. 禁止执行任何提取出的 Script 或二进制。

单一解包器更简单，但无法排除实现缺陷造成的静默错误，因此不作为首次长期归档的唯一证据。若第二实现只能抽样，Artifact 最多标记为 `source-provisional`，不能达到 `Source Complete`。

## 7. 阶段 4：Decode and Parse Evidence

这里的解析只用于建立证据，不修改 Source。来源分类依赖 HHC、首页、标题与路径，必须在安全解码这些证据后进行。

### 7.1 编码

Source 保留原始字节。Decoder 为每个 Entry 记录：

- BOM；
- HTTP/Container 声明（如有）；
- HTML `meta charset`；
- 注释声明；
- 检测候选；
- 实际采用编码；
- 严格解码错误；
- Decoder 与版本。

当前输入虽然普遍声明 GB2312，但存在大量超出严格 GB2312 的字节；因此不能只信声明。任何替换字符解码都必须阻塞，禁止使用 `errors=replace` 后继续转换。

### 7.2 HTML Parse

- 禁止执行 JavaScript、ActiveX、iframe 或外部请求；
- Parser 必须锁定版本和 Recover 配置；
- 原始 DOM 与恢复 DOM 分开，恢复行为进入报告；
- 注释、隐藏节点、脚注、边栏和模板元素先保留，后分类；
- CSS 只用于识别显示和结构候选，不自动决定删除；
- `display:none` 内容进入审核，不静默丢弃；
- Script 中可能生成的正文进入 `DYNAMIC_VISIBLE_CONTENT` 问题。

### 7.3 页面族

按 Generator、DOM Signature、CSS、目录和结构聚类页面模板，例如：

- WinCHM 普通页；
- Word / WPS 导出页；
- 2024 Stat Block；
- 大型速查页；
- 模组页面；
- Script 样式包装页。

每个页面族先人工确认：正文容器、边栏、导航噪声、脚注、表格和资产规则。未知页面族默认保留全文并阻塞自动清理。

### 7.4 Locator 坐标系

所有坐标必须声明空间和半开区间 `[start, end)`：

- `section_logical_offset`：CHM Section 解压逻辑流中的 Offset，不是原 CHM 文件物理位置；
- `entry_raw_byte_ranges[]`：解包后、尚未解码的 Entry 原始 byte；
- `decoded_text.ranges[]`：指定 Decoder 输出的 Unicode Scalar Value 序号；
- `dom`：记录 Parser、版本、Recover 配置、Selector Language 和 Selector；
- `text_quote`：保留 prefix / exact / suffix 原字符；
- `navigation_occurrence_ids[]`：引用 HHC 中一个或多个稳定挂载位置。

Fragment 必须有稳定 ID 和摘要。任何实现都不得把 Logical Offset、Entry Byte Offset、Unicode Code Point 和 DOM Node Index 混用。

阶段 2～4 达到门禁时，必须把工具/二进制摘要、脚本摘要、Parser/Decoder 配置、规则版本、输入参数、明细输出摘要和聚合统计写入 `sources/artifacts/<artifact-key>/receipts/extraction.json` 与 `analysis.json`。机器回执属于 Source Complete 证据并进入 Content Manifest；带绝对临时路径、性能和控制台输出的运行日志留在 `reports/`。

## 8. 阶段 5：Classify Works and Editions

这是当前 CHM 的关键人工门禁。

分类只使用阶段 4 产生的非执行证据视图，逐个 HHC 根区域和顶层路径建立候选：

- Work；
- Edition；
- 章节和导航映射；
- publisher / third-party / community / private 等来源关系；
- original / official-translation / licensed-translation / community-translation；
- normative / optional / playtest / legacy；
- ruleset、setting、campaign；
- Rights Claim、Access Policy 与目标 Visibility。

每项映射记录 `verified | claimed | inferred | unknown` 和证据。

### 为什么必须在生成 Node 前分类

如果先生成 Node，再补来源：

- 2014 与 2024 内容可能错误合并；
- 社区翻译可能被标成官方文本；
- 第三方和模组内容可能进入官方规则索引；
- Package 边界会被目录猜测固化；
- 后续拆包会造成大规模 ID 和路径迁移。

## 9. 阶段 6：建立 Source Reference Graph

先解析原始链接，再进行节点拆分和改写。

必须支持：

- `/` 与 `\`；
- 相对路径和 CHM 根路径；
- Fragment；
- Percent Encoding；
- 未编码空格；
- `mk:@MSITStore:`、`ms-its:` 等 CHM URI；
- Windows `file:///`；
- HTTP(S) 外链；
- CSS `url()`；
- HHC / HHK `Local`。

每个原始引用 Attribute 先保存不含解析结论的 Raw Record：

```yaml
schema: "core.source-reference-occurrence@0.1.0"
id: "urn:uuid:..."
occurrence_key: "sha256:..."
artifact_id: "urn:uuid:..."
entry_id: "urn:uuid:..."
reference_kind: "link | image | resource | anchor"
element: "a"
attribute: "href"
source_event_ordinal: 0
raw_value: "原始字符串"
lexical_evidence: {}
lifecycle:
  status: "active"
  revision: 1
```

解析结果另存为 Mapping，不得回写 Raw Record：

```yaml
schema: "core.link-mapping@0.1.0"
id: "urn:uuid:..."
source_reference:
  id: "urn:uuid:..."
  revision: 1
  digest: "sha256:..."
resolution:
  kind: "entry | fragment | external | missing | unsafe | ambiguous"
  target: null
  normalization_steps: []
issues: []
review: {}
lifecycle:
  status: "active"
  revision: 1
```

`reference_kind: image | resource` 必须使用 Link Mapping；`reference_kind: link` 只有在未被 `footnote-ref` Semantic Address Occurrence 消费时才使用 Link Mapping；Anchor 与 Footnote 使用后续 Semantic Address Occurrence / Mapping。原始 URL 永不被覆盖，规范化步骤只属于解析层；Entry、Ordinal 与 Raw Value 只从绑定的 Source Reference 读取，Mapping 不复制第二份。

Source Reference Occurrence 和 Navigation Occurrence 必须先写入规范 Metadata Record，再由 Index 消费；Index 不能成为 Occurrence ID 的唯一事实源。Reference Record 存放于 `metadata/references/occurrences/`；Key 与 UUID 的生成协议见[完整性与事件协议](integrity-protocols.md)。

### 9.1 外部资源

转换构建不访问网络。外部图片或网页如果需要长期保存，必须启动独立 Acquire 流程，生成新 Artifact，并记录：

- 原 URL；
- 重定向链；
- 获取时间；
- 响应 Header；
- 内容摘要；
- 权利状态；
- 获取失败。

网络不可达不应让 Source 转写失去原 URL，但可以阻止“资源完整”声明。

## 10. 阶段 7：Propose Knowledge Boundaries

节点边界由机器提出候选、人工批准。

### 10.1 候选信号

- HHC 层级、顺序与重复挂载；
- HTML 文件边界；
- `h1`～`h6`；
- `id` / `name` Anchor；
- 页面内链接目标；
- Stat Block、Spell、Condition、Equipment 等重复结构；
- 表格、边栏、脚注与定义列表；
- CSS 中经审核的语义约定；
- 标题、页面大小和相似内容；
- 来源 Edition 边界。

### 10.2 禁止的简单规则

- 一页一个 Node；
- 每个 Heading 一个 Node；
- 文件名或 `<title>` 生成 ID；
- HHC Object 数量等于 Node 数量；
- LLM 直接拆分并重写；
- 相同文本自动合并；
- 新版自动覆盖 Legacy。

### 10.3 Boundary Ledger

人工权威存储为声明式边界账本：

```yaml
schema: "core.boundary-decision@0.1.0"
id: "urn:uuid:..."
candidate_key: "sha256:..."
node_id: "urn:uuid:..."
entry_id: "urn:uuid:..."
locator: {}
title: "..."
kind: "..."
decision: "approved"
reviewer: "..."
reviewed_on: "2026-07-20"
reason: "独立规则主题。"
```

`candidate_key` 按以下字节计算：前缀 `lorebuddy-boundary-candidate-v1\n`，随后写入 JCS 对象 `{artifact_id, entry_id, locator, fragment_digest, proposal_algorithm}` 和一个 LF，再取 SHA-256。字段一律存在；未知值用 JSON `null`，数组顺序按来源顺序，禁止依赖 Map 插入顺序。这样重跑能匹配同一候选，提议算法升级则有意产生新 Key。

正式 Node ID 首次批准时分配，不能由 `candidate_key` 或正文摘要直接充当。来源轻微变化不应让语义身份自动漂移。

批准边界时还必须生成唯一的 `metadata/fragments/<shard>/<uuid>.yaml` Source Fragment Record。Boundary Ledger 保存“为何选择”，Fragment Record 保存“准确选择了什么”。多个 Node 可以引用同一 Fragment；范围发生变化时创建新 Fragment ID，不原地移动旧 ID。

## 11. 阶段 8：Human Review

### 11.1 来源审核

确认 Work、Edition、语言、版本、权威关系、Rights 和 Package 边界。

### 11.2 模板审核

确认每类页面的正文、边栏、脚注、隐藏内容、Script 和表格策略。

任何 `visible | hidden` 结论必须生成 `metadata/visibility-decisions/` 中的稳定 `core.visibility-decision@0.1.0` Record，固定页面族或具体 DOM 范围、CSS / Parser / Rule Version、证据、Reviewer 与失效条件。`unknown` 保持阻塞；转换器不得只把一次运行中的 CSS 计算结果写入临时 Report。

### 11.3 边界审核

审核工具应该并排展示：

- 原始 HTML 渲染；
- 原始字节/DOM 位置；
- 候选 Markdown；
- 可见文本差异；
- HHC Breadcrumb；
- 入链与出链；
- 相似或重复候选；
- Include / Exclude 范围。

### 11.4 版本与重复审核

确认相同标题、相似文本和跨书重复到底是：

- 同一表达的重复挂载；
- 相同字节的不同来源证据；
- 修订、勘误或再版；
- 不同系统/版本下的同名实体；
- 应保持独立的第三方变体。

机器只排序候选，不做最终合并。

## 12. 阶段 9：Resolve Links、Addresses and Render Final Library

最终 Markdown 必须在保真验证前完成链接映射。验证候选不能在通过后再次改写正文。

### 12.1 Link 与 Address 映射

完成边界映射后：

- 指向已节点化 Fragment：改写为稳定 Node URI；
- 指向同 Node Anchor：保留本地 Anchor；
- 指向未节点化 Entry：在 Full Traceability Package 中改写为 `lorebuddy://source-entry/<entry-uuid>?fragment=<fragment-uuid>`；没有精确 Fragment 时省略 Query；公开投影无权披露 Entry 时改写为批准的 Provenance Receipt URI；
- 外链：保留原 URL；
- 多个候选目标：进入歧义清单；
- 坏链接：保留原证据，不猜测。

原始 Source Reference Graph、逐 Occurrence 映射和最终 Library Link Graph 都必须保留；其中 Link Graph 只是 `reference_kind: link` 的投影，不替代 Anchor / Image / Resource 的 Raw Reference Record。

同一阶段还必须生成并审核 `metadata/addresses/occurrences/` 与 `metadata/addresses/mappings/`。Address Occurrence 是 Semantic Wrapper：它以 `base_reference: {id,revision,digest}` 引用 `metadata/references/occurrences/` 中唯一的底层 `href`、`id` 或 `name`，再保存 `address_kind: anchor | footnote-ref | footnote-body`；Candidate Key 中的 `base_reference_occurrence_id` 取该对象的 `id`。Mapping 固定最终 Markdown ID、稳定 `address_occurrence_id`、`equivalence_id`、Ref → Body 配对和审核状态。Address 不能在 Markdown 渲染后临时按字符串猜测；丢失 Anchor、Footnote Ref 无 Body、多个未经合并批准的来源 ID 指向同一目标都必须阻塞。转换范围内每个 `<a href>` 必须恰好被一条 Active 普通 Link Mapping 或一条 Active `footnote-ref` Address Occurrence 消费；转换范围内每个 `id` / `name` 必须恰好被一条 Active `anchor` 或 `footnote-body` Address Occurrence 消费。

Source Entry URI 是交换层稳定标识，不依赖 Runtime。只有 `embedded-fragment` 模式的 Provenance / Navigation Index 把它映射回 Package 相对路径和 Locator；`external-public-receipt` 只能映射公开 Receipt，不能泄漏私有 Entry。

### 12.2 允许的转换

- 按浏览器显示语义解码 HTML Entity；
- 将 Heading、Paragraph、List、Blockquote、Link、Image 映射为 Markdown；
- 将可无损表达的简单表格映射为 GFM Table；
- 移除经页面族审核确认的纯展示 CSS 和导航外壳；
- Markdown 无法忠实表达时保留受限语义 HTML；
- 将 Library 编码统一为 UTF-8 与 LF。

### 12.3 禁止的转换

- 改写、总结或意译；
- 调整语序；
- 自动纠正错字、标点或单位；
- Unicode NFC/NFKC 回写正文；
- 自动合并重复段落；
- 为排版新增来源中不存在的标题；
- 根据模型判断删除“无关内容”；
- 执行 Script 或把 Script 执行结果直接并入转换正文；动态内容只能登记问题。未来如需恢复，必须建立独立、隔离且经确认的派生摄取流程；
- 下载远程图片并假装它原本在 CHM 中。

### 12.4 结构化抽取

Spell Level、Armor Class 等字段属于派生断言：

- 保留正文；
- 记录字段到 Fragment 的 Provenance；
- 记录抽取器与规则版本；
- 不推测缺失字段；
- 与正文冲突时阻塞发布。

## 13. 阶段 10：最终结构与文本保真验证

HTML 与 Markdown 字节不会相同，因此分开验证：

### 13.1 Source Integrity

- Artifact 字节摘要；
- Entry 字节摘要；
- Path Map；
- 容器目录长度和提取结果。

### 13.2 Library Fidelity

对 Source Fragment 与最终 Markdown 分别生成规范事件流。以下只是事件族摘要，完整序列化、空白规则、Link Projection 和测试向量见[完整性与事件协议](integrity-protocols.md)：

```text
ENTER(kind, attributes...)
EXIT(kind)
TEXT(value)
BLOCK_BREAK
LINE_BREAK
LIST_ITEM(depth, ordinal, item_role)
TABLE_CELL(row, column, rowspan, colspan, header_scope)
ANCHOR(address_occurrence_id, equivalence_id)
FOOTNOTE_REF_ENTER(address_occurrence_id, equivalence_id)
FOOTNOTE_REF_END
FOOTNOTE_BODY_ENTER(address_occurrence_id, equivalence_id)
FOOTNOTE_BODY_END
LINK_ENTER(occurrence_id, equivalence_target)
LINK_END
IMAGE(occurrence_id, equivalence_target, alt, title)
```

上表是比较投影的概览，不是另一套序列化语法。`ENTER / EXIT` 的允许 Kind、Table Row Group、Definition List Role、Block Break 位置与精确 JCS 形状全部以完整性协议为准。Fragment 的原始 Source Event Stream 另用 `source-link` / `source-image` / `source-resource` / `source-anchor` 保存未解析引用；Footnote 语义先由 Semantic Address Occurrence 包装底层 Link / Anchor Source Reference，再由 Address Mapping 派生，不存在 `source-footnote-*` 原始事件。最终 URI 不得写回来源摘要。

比较时只允许规范明确的 HTML 显示空白处理和 Entity 解码。禁止进行：

- Unicode 规范化；
- 标点替换；
- 大小写折叠；
- 文本排序；
- 同义词或翻译比较。

`pre`、`code`、强调/术语、列表类型与起始编号、表头 Scope、单元格 Span、Anchor、链接、图片、上标、下标和脚注必须有专门事件，不能压成普通段落文本。可见性（Visibility）不生成比较事件；它由锁定的 Visibility Decision 决定哪些 Source 子树参与比较，`unknown` 必须阻塞。

Source Link Graph 与 Library Link Graph 还要进行逐 Occurrence 等价检查：每个普通来源链接必须对应一个最终链接、经审核唯一选择的拆分后目标，或批准的排除项。底层 `<a href>` 若被唯一 Active Semantic Address Occurrence 消费为 `footnote-ref`，则不再生成普通 Link Mapping；同时出现 Link Mapping 与 Footnote 消费，或两者都没有，均阻塞。其余 Occurrence 映射保持一对一；多个候选必须保持 `ambiguous` 并阻塞，不能复制一条来源链接。原始 URL 与最终 URI 不直接做字符串相等比较；普通 Link 两边通过同一 Link Mapping Record 投影为相同 `occurrence_id + equivalence_target`。Address 两边通过同一 Address Mapping Record 投影为相同 `address_occurrence_id + equivalence_id`。删除链接、改错图片目标、丢失 Anchor 或破坏 Footnote Ref → Body 配对都必须阻塞。

转换器保存：

- Source 事件流文件的精确 Byte Count / `file_digest` 与带 Domain Prefix 的协议语义摘要；
- Markdown 往返事件流的文件摘要与协议语义摘要；
- 最终 `body_byte_digest`；
- 允许的差异；
- 不允许差异的精确位置。

最终 Pass / Fail、Node ID / Revision、Assertion ID、Body Digest 与完整 Fidelity Coverage Map 必须写入 `metadata/fidelity/` 的规范 Fidelity Record。Map 逐 Binding 固定 Provenance / Fragment，逐 Unit 固定正文 Byte Range、Source Fragment Event Record Range、Exception 前后的 Source / Library Event Descriptor，以及 Link / Address Mapping、Visibility Decision 和批准 Exception 的 `{id,revision,digest}`。每个 Event Descriptor 都固定 Record Count、精确 JSONL Byte Count、普通 File Digest 与带 Domain Prefix 的 Semantic Digest；最小形状见 Schema 提案。Source Fragment Event Stream 随 Fragment Record 保存；可重建的完整 Library Event Stream 和逐事件 Diff 可以进入 `reports/`，但删除报告后仍必须能从 Source Event、Node 和 Fidelity Record 重新验证每个 Unit 的结论。

## 14. 阶段 11：Build Indexes

生成：

- Content Manifest；
- Node Index；
- Alias Index；
- Forward / Reverse Relationship Index；
- Source / Semantic Navigation Index；
- Provenance 与 Coverage Index；
- Asset Record / Usage Index；
- Output Manifest 与根级 Release Manifest。

HHC 生成 Source Navigation 候选；HHK 只生成 Alias 候选；`$FIftiMain` 不作为 LoreBuddy Index 输入真相。

## 15. 问题检测与稳定键

自动检测结果先写入 `reports/<run>/detected-issues.jsonl`，每行至少包含：

```yaml
issue_key: "sha256:..."
code: "CHARSET_CONFLICT"
severity: "error"
rule_version: "core.charset-check@0.1.0"
artifact_id: "urn:uuid:..."
entry_id: "urn:uuid:..."
locator: null
evidence: {}
suggested_actions: []
```

`issue_key` 不是随机 UUID。它按以下字节计算：前缀 `lorebuddy-issue-key-v1\n`，随后是 JCS 对象 `{code, artifact_id, entry_id, locator, rule_version}` 和一个 LF，再取 SHA-256。这样不同运行可以匹配同一检测结果；规则变化则有意生成新 Key。

稳定错误代码至少包括：

- `UNKNOWN_SOURCE_AUTHORITY`
- `RIGHTS_UNKNOWN`
- `AMBIGUOUS_DOCUMENT_BOUNDARY`
- `CHARSET_CONFLICT`
- `DECODE_ERROR`
- `HTML_PARSE_RECOVERY`
- `DYNAMIC_VISIBLE_CONTENT`
- `UNREVIEWED_HIDDEN_TEXT`
- `UNSUPPORTED_TABLE`
- `UNSUPPORTED_RESPONSIVE_IMAGE`
- `UNSUPPORTED_REFERENCE_ELEMENT`
- `UNSUPPORTED_REFERENCE_ATTRIBUTE`
- `REFERENCE_CONSUMPTION_CONFLICT`
- `IMAGE_ONLY_RULE_TEXT`
- `AMBIGUOUS_NODE_BOUNDARY`
- `DUPLICATE_TITLE`
- `POSSIBLE_DUPLICATE_CONTENT`
- `VERSION_CONFLICT`
- `BROKEN_INTERNAL_LINK`
- `MISSING_FRAGMENT`
- `AMBIGUOUS_LINK_TARGET`
- `EXTERNAL_ASSET`
- `MISSING_ASSET`
- `MIME_EXTENSION_MISMATCH`
- `UNSAFE_OR_COLLIDING_PATH`
- `VISIBLE_TEXT_MISMATCH`
- `ORPHAN_SOURCE_FRAGMENT`
- `OVERLAPPING_SOURCE_FRAGMENT`
- `UNTRACEABLE_NODE`
- `MANUAL_EDIT_CONFLICT`
- `NON_DETERMINISTIC_OUTPUT`

## 16. 审计事实

检测报告不是人工治理事实。问题一旦被接受、驳回、延期或批准为例外，必须写入 Content Manifest 覆盖的规范元数据：

- `metadata/issues/`：分配稳定 UUID `issue_id`，引用一个或多个 `issue_key`，保存状态与证据；
- `metadata/exceptions/`：保存批准人、适用 Artifact / Entry / Fragment、精确例外规则、理由和失效条件；
- `metadata/reviews/`：保存来源分类、边界、忠实度或发布审核结论。

随机 UUID 用于人工裁决实体的长期身份，确定性 `issue_key` 用于重跑匹配；二者职责不能互换。已关闭 Issue、Exception 和 Review 不得删除，必须保留 Resolution、Reviewer 与证据。报告中的执行时间、主机和性能数据不进入规范摘要；人工裁决进入其所属 Access Domain Package 的 `content_root_digest`。公开 Package 只携带经过 Disclosure Approval 的最小 Attestation，完整 Reviewer、合同或私有 Fragment 证据保留在受限 Audit Package。

## 17. 质量门禁

| Gate | 阻塞条件 |
|---|---|
| G0 Artifact | Header 无法解析、摘要不一致、权限状态缺失 |
| G1 Inventory | 目录记录重复、危险路径未隔离、长度越界 |
| G2 Extraction | 非零 Stream 丢失、长度/摘要不稳定、Path Map 不可逆 |
| G3 Classification | Work / Edition 边界未审核、未知内容被标记为官方 |
| G4 Decode | 替换字符、编码不确定、关键页面无法解析 |
| G5 Boundary | Candidate 未批准、Node ID 冲突、跨版本错误合并 |
| G6 Fidelity | 可见文本事件流不一致、静默丢失或新增正文 |
| G7 Provenance | Node 无法追溯到 Fragment / Entry / Artifact |
| G8 Links / Assets | 已转换范围内的链接或必需资产静默丢失 |
| G9 Schema | Node、Source、Relationship 或 Manifest 无效 |
| G10 Index | Alias 被覆盖、悬空 ID、Index 不可重建 |
| G11 Determinism | 同输入重跑产生未解释 Diff |
| G12 Release | Rights 任一所需权限不是 `allowed`、Access Policy 不允许目标受众、Disclosure Approval 缺失、Public Lock 泄漏受限指纹、Payload 出现额外文件或私有信息隔离测试失败 |

来源自身已有的坏链接可以作为批准例外保留，但必须明确标记为 Source Defect，不能修正后伪装成原始事实。

## 18. 幂等与人工修改

同一 Artifact、工具链、Schema、Registry、Package Lock 和 Boundary Ledger 必须生成相同结果。确定性测试至少要改变临时目录、文件系统枚举顺序、Locale 和 Timezone；这些环境变化不得改变规范输出。

- 新 CHM 创建新的 Artifact ID；若需要表达前后关系，使用显式 `revises` / `derived_from` Relationship，不引入未定义的 Artifact Revision 身份层；
- 人工决策写入 Ledger，不直接修改临时生成物；
- Index 可以随时删除重建；
- 若生成 Node 被手工修改，重跑必须检测 `body_byte_digest` 冲突并停止；
- 转换器修复必须通过显式迁移或重建报告处理；
- 当前时间不得进入规范输出。

## 19. 首批样本策略

在全量转换前选取 5～10 个覆盖不同复杂度的页面：

1. 简单独立规则页；
2. 同页多个规则主题；
3. 2024 Stat Block；
4. 复杂 `rowspan` / `colspan` 表格；
5. Word / WPS Office 导出页；
6. 含脚注、边栏、上标和内链的页面；
7. 含 Script 的大型速查页；
8. 含远程或缺失图片的页面；
9. 2014 / 2024 同名规则；
10. 官方声称来源与第三方/社区内容各一页。

样本必须完成：Source 保存、来源分类、Boundary Ledger、Markdown、Provenance、链接改写、Index 和全部质量门禁。样本暴露的问题应先反向修正规范，不能用页面特例绕过。

## 20. 全量转换启动条件

只有以下条件同时成立，才允许全量转换：

- Milestone 0 架构决策已确认；
- Core Schema 与注册表已冻结到可测试版本；
- 当前 CHM 已达到 Source Complete；
- 来源分类账本覆盖所有顶层区域；
- 样本通过文本保真和确定性重建；
- 权利与访问策略足以确定输出 Package 位置；
- 所有自动规则都有版本、测试和回滚方案；
- 人工审核容量与责任人明确。
