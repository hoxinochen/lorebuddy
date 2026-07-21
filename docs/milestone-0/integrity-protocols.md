# 完整性与事件协议草案

状态：Draft  
规范版本：`0.1.0`

## 1. 目标

本文定义 Milestone 0 中承担跨实现比较职责的三个独立协议：

1. 可见文本事件（Visible Text Events）：证明来源与 Library 的文字、顺序和可见换行没有静默变化；
2. 结构保真事件（Structure Fidelity Events）：证明 Heading、List、Table、Link、Image、强调和脚注等结构得到等价表达；
3. 来源片段事件（Source Fragment Events）：为一个已批准 Source Fragment 的内容选择计算稳定摘要。

三者不能共用一个含义模糊的“文本摘要”。可见文字相同不代表结构相同；结构等价也不代表两个 Fragment 具有同一身份。

本文只定义规范事件和摘要字节。HTML Recovery、Markdown Parser、页面族规则和 CSS 可见性判断仍必须锁定在 Extraction / Analysis Receipt 中；实现不得声称仅凭一个摘要就消除了 Parser 差异。

## 2. 共用记录流

所有协议使用相同记录流规则：

- 每条事件是 JSON Object；
- 每个 Object 按 JSON Canonicalization Scheme（JCS，RFC 8785）编码为 UTF-8；
- 禁止 BOM；
- 规范 `.jsonl` 文件只保存事件，每条事件后写一个 LF；
- 协议语义摘要在计算时把 Domain Prefix 虚拟前置于完整 JSONL file bytes，Prefix 不写入 JSONL 文件；
- 字符串不做 NFC、NFKC、大小写、标点或全半角规范化；
- 数组顺序是语义顺序；
- 未知值用 JSON `null`，禁止通过省略字段改变 Key 或摘要语义；
- 摘要使用 SHA-256，表示为 `sha256:<lowercase-hex>`。

生成器必须同时保存事件流文件、事件数、文件字节数、普通文件 SHA-256 和带 Domain Prefix 的协议语义摘要。只保存摘要不足以审计差异。

## 3. 可见文本事件

协议 ID：`core.visible-text-events@0.1.0`  
Domain Prefix：UTF-8 `lorebuddy-visible-text-v1\n`

### 3.1 事件

```jsonl
{"t":"text","v":"原字符"}
{"t":"block-break"}
{"t":"line-break"}
{"t":"image-alt","v":"替代文字"}
```

- `text`：按阅读顺序出现的一个或多个 Unicode Scalar Value 组成的最大连续序列；
- `block-break`：规范块容器结束后的阅读分隔；
- `line-break`：`br`、Markdown Hard Break 或预格式文本中的显式换行；
- `image-alt`：每个 Image 在其阅读位置恰好发出一次；`v` 为来源中实际存在的替代文字 String，Alt 缺失时为 JSON `null`，显式空 Alt 为 `""`。三者不能与普通正文或彼此静默互换。

### 3.2 空白与可见性

可见文本流的处理固定为：

1. 解码 HTML Entity；
2. 普通文本把 U+0009、U+000A、U+000C、U+000D、U+0020 的一个或多个连续字符折叠为一个 U+0020；不折叠 U+00A0、U+3000 等非 ASCII 空白；
3. `pre`、Code Block 和显式保留空白的页面族只跳过第 2 步：先把 CRLF 与孤立 CR 转为 LF，再把每个 LF 从 `text.v` 中移出并按原位置发出一个 `line-break`；
4. 遍历时按下述固定触发集合生成候选 `block-break`；完成全流后，删除 Stream 开头/结尾的 `block-break`，删除其两侧 `text.v` 中的 U+0020，并把连续 `block-break` 折叠为一个；该全流步骤同样作用于 Pre / Code 外围边界；
5. 不执行 Unicode Normalization。

普通流的折叠作用于同一可见 Block 内按 DOM / AST 顺序拼接后的逻辑字符流，不以 Text Node 边界重置；因此两个实现不能因为切分 Text Node 的方式不同而产生不同摘要。

`block-break` 的触发集合固定为 `paragraph`、`heading`、`blockquote`、`list-item`、`table-caption`、`table-row`、`pre`、`code-block`、`figure`、`figcaption`、`details` 与 `summary`。生成器在相应可见 Container 的 `exit` 后生成一次候选；Nested Exit 可能产生连续候选，再由第 4 步折叠。最终规范流绝不以 `block-break` 开头或结尾。未知块级 Element 不能自行归入该集合，必须由新协议版本或已审核页面族规则处理。

事件分块也是规范的一部分：在完成上述处理后，每个 Block 内两个非文本事件之间的最大连续字符序列必须合并为恰好一个 `text` 事件；空字符串不发事件。Pre / Code 中每个 `line-break` 之间的最大序列同样只发一个 `text` 事件。禁止把 `"ab"` 任意表示为两个 `"a"`、`"b"` 事件。

只有页面族审核明确判定为 `hidden` 的节点才从可见文本流排除。`visibility: unknown`、Script 可能生成正文、外部请求或无法求值的 CSS 必须生成阻塞 Issue，不能靠猜测得到通过摘要。

Source 与最终 Markdown 必须产生字节相同的可见文本事件流和摘要。Link URL、Anchor ID、CSS Class 等不进入本协议。

### 3.3 测试向量

摘要输入（下列每一显示行后都有一个 LF，包括最后一行；不包含字面量反斜杠与 `n`）：

```text
lorebuddy-visible-text-v1
{"t":"text","v":"专注"}
{"t":"block-break"}
{"t":"text","v":"Concentration"}
```

期望 SHA-256：

```text
49856ea37eb6813354939a172f221b7d607061166252b2a5c166c731a7e0d968
```

## 4. 结构保真事件

协议 ID：`core.structure-events@0.1.0`  
Domain Prefix：UTF-8 `lorebuddy-structure-events-v1\n`

### 4.1 事件族

所有容器结构使用 `enter` / `exit` 成对事件；属性必须在 `enter` 上完整给出。

| 事件族 | 必需语义 |
|---|---|
| Block | `paragraph`、`heading(level)`、`blockquote`、`figure`、`figcaption`、`details`、`summary` |
| List | `list(type,start)`、`list-item(depth,ordinal,item_role)` |
| Table | `table`、`table-caption`、`table-head`、`table-body`、`table-foot`、`table-row`、`table-cell(row,column,rowspan,colspan,header_scope)` |
| Preformatted | `pre`、`code-block(language-or-null)` |
| Inline | `emphasis(kind)`、`inline-code`、`term`、`sup`、`sub`、`ruby` |
| Addressable | `anchor(address_occurrence_id,equivalence_id)`、`footnote-ref(address_occurrence_id,equivalence_id)`、`footnote-body(address_occurrence_id,equivalence_id)` |
| Link | `link(occurrence_id,equivalence_target)` Container |
| Image | `image(occurrence_id,equivalence_target,alt,title)` |
| Text | 第 3 节定义的 `text`、`line-break`；Image Alt 由 `image.alt` 表达 |

规范 JSON 形状如下。未列字段禁止出现；可空字段必须显式写 JSON `null`。

```jsonl
{"kind":"paragraph","t":"enter"}
{"kind":"paragraph","t":"exit"}
{"kind":"heading","level":2,"t":"enter"}
{"kind":"heading","t":"exit"}
{"kind":"list","list_type":"ordered","start":1,"t":"enter"}
{"depth":0,"item_role":"item","kind":"list-item","ordinal":0,"t":"enter"}
{"kind":"list-item","t":"exit"}
{"kind":"list","t":"exit"}
{"kind":"table","t":"enter"}
{"kind":"table-body","t":"enter"}
{"kind":"table-row","t":"enter"}
{"colspan":1,"column":0,"header_scope":"column","kind":"table-cell","row":0,"rowspan":1,"t":"enter"}
{"kind":"table-cell","t":"exit"}
{"kind":"table-row","t":"exit"}
{"kind":"table-body","t":"exit"}
{"kind":"table","t":"exit"}
{"kind":"code-block","language":null,"t":"enter"}
{"kind":"code-block","t":"exit"}
{"emphasis_kind":"strong","kind":"emphasis","t":"enter"}
{"kind":"emphasis","t":"exit"}
{"address_occurrence_id":"urn:uuid:...","equivalence_id":"urn:uuid:...","t":"anchor"}
{"address_occurrence_id":"urn:uuid:...","equivalence_id":"urn:uuid:...","kind":"footnote-ref","t":"enter"}
{"kind":"footnote-ref","t":"exit"}
{"equivalence_target":"lorebuddy://node/...","kind":"link","occurrence_id":"urn:uuid:...","t":"enter"}
{"kind":"link","t":"exit"}
{"alt":"...","equivalence_target":"lorebuddy://asset/sha256:...","occurrence_id":"urn:uuid:...","t":"image","title":null}
{"t":"line-break"}
{"t":"text","v":"专注"}
```

Container 的 `exit` 只允许 `kind`、`t`; `t` 固定为 `exit`，不得重复 Enter Attribute。允许的 `kind` 与 Enter Attribute 为：

- 无附加属性：`paragraph`、`blockquote`、`figure`、`figcaption`、`details`、`summary`、`table`、`table-caption`、`table-head`、`table-body`、`table-foot`、`table-row`、`pre`、`inline-code`、`term`、`sup`、`sub`、`ruby`；
- `heading`：整数 `level`，范围 1～6；
- `list`：`list_type: ordered | unordered | definition`，有序列表的 `start` 为整数，其他为 `null`；
- `list-item`：非负整数 `depth`、`ordinal`；`item_role: item | term | definition`，Definition List 必须使用后两者，其他 List 必须使用 `item`；
- `table-cell`：非负 `row` / `column`，正整数 `rowspan` / `colspan`，`header_scope: row | column | rowgroup | colgroup | both | none`；
- `code-block`：`language` 为字符串或 `null`；
- `emphasis`：`emphasis_kind: em | strong | source-term`；
- `footnote-ref` 与 `footnote-body`：作为 Container，Enter 额外携带 `address_occurrence_id` 与 `equivalence_id`；
- `link`：作为 Container，Enter 额外携带 `occurrence_id` 与 `equivalence_target`。

Container 必须按单一 Stack 严格 LIFO：Exit 的 `kind` 必须等于栈顶 Kind，禁止交叉范围，流结束时栈必须为空。单事件在深度优先遍历遇到该语义节点的位置发出，并属于当时全部未关闭父 Container。任何缺失 Exit、额外 Exit 或跨越都必须阻塞。

`occurrence_id`、`address_occurrence_id` 与 `equivalence_id` 都是非 Null UUID URN String。`equivalence_id` 是 Address Mapping 审核时分配的 UUIDv7 等价组身份，在当前解析闭包内唯一；它不由 raw ID 或标题派生。一个 Footnote Ref 和它指向的 Body 使用同一 `equivalence_id`，多个 Ref 可以共享该 ID，但每个 Node 解析闭包中必须恰有一个 Active Body；每个 Ref / Body 仍有不同 `address_occurrence_id`。普通 Anchor 的声明也拥有独立等价组，跨 Node 合并必须有显式 Address Mapping。

`equivalence_target` 是批准后的非空 LoreBuddy URI 或保留的 External URI String；`alt` / `title` 是 String 或 JSON `null`，缺失与空字符串不同。Mapping 为 `missing | unsafe | ambiguous` 时不得用 `null` 生成比较事件或 Pass；只能保留原始 Record、产生阻塞 Issue，待解决或批准 Exception 后重新投影。

普通 `text` 与 `line-break` 保持第 3 节形状；`block-break` 只属于可见文本协议，结构流由 Container 边界表达，不重复发出。Anchor 与 Image 是单事件；Footnote Ref、Footnote Body 与 Link 必须成对使用 Enter / Exit，以固定其覆盖范围。可见文本事件流在同一 DOM / Markdown Image 语义节点位置按第 3.1 节恰好发出一个 `image-alt`；结构事件流只在 `image.alt` 保存该值，不重复发出 `image-alt`。

例如 Heading：

```jsonl
{"kind":"heading","level":2,"t":"enter"}
{"t":"text","v":"专注"}
{"kind":"heading","t":"exit"}
{"equivalence_target":"lorebuddy://node/...","kind":"link","occurrence_id":"urn:uuid:...","t":"enter"}
{"kind":"link","t":"exit"}
```

未列出的纯展示 Wrapper 不进入比较投影，但其移除规则必须属于已审核页面族。实现不能自行把未知 HTML Element 判为纯展示。

### 4.2 Source 与 Library 的链接、Anchor 与 Footnote 差异

原始 URL 与最终 LoreBuddy URI 本来就不同，因此禁止直接比较两边的 Target 字符串。底层 Attribute 先建立不可变语义的 `core.source-reference-occurrence@0.1.0`：它固定 Reference ID、`reference_kind: anchor | link | image | resource`、Artifact / Entry、Element、Canonical Attribute、`source_event_ordinal`、Raw Value、Lexical Byte Evidence 与 Lifecycle。审核后的 Link / Address 身份不能回写该 Raw Record。

普通 Link / Image / Resource 解析再建立规范 Link Mapping Record：

```text
Source Reference Occurrence `{id,revision,digest}`
→ raw_url
→ resolved source target
→ approved equivalence_target
→ final Library occurrence
```

`core.link-mapping@0.1.0` 至少固定 Mapping ID、Source Reference Occurrence 的 `{id,revision,digest}`、Resolution Status / Target、规范化步骤、唯一 `equivalence_target`、最终 Node ID / Markdown Locator / Target、Review 和 Lifecycle。Entry、Attribute、`source_event_ordinal` 与 Raw Target 只从所绑 Source Reference 解析，Mapping 禁止复制这些字段形成第二事实源。Active Mapping 对一个 Source Reference 只能有一条；所绑 Revision / Digest 不一致时失效并阻塞。`source_event_ordinal` 的语义是第 6 节定义的 Reference Attribute Scan Ordinal。

Source 与 Library 的结构比较投影都以同一个 Source Reference ID 作为 `occurrence_id`，并以同一个 `equivalence_target` 发出 `link` / `image` 事件。Resource 不生成 Library Structure Event，但其 Resolution / Asset Usage 仍必须闭合。原始 URL、解析步骤和最终 URL 分别保存在 Mapping 中，不进入“必须相等”的投影字段。一个来源 Reference 缺失、重复映射或映射到不同语义目标时必须阻塞。

普通 Link / Image Reference 的比较映射严格一对一。Resource 不生成 Library Structure Event，但每个进入转换范围的 Resource Reference 仍必须有唯一 Active Link Mapping，以闭合 Resolution 和可能的 Asset Usage。若一个 Source Fragment 后续被拆成多个 Node，单个来源链接仍必须经审核选择恰好一个最终语义目标；不能把一个 Reference 复制为多条最终链接。无法唯一选择时保留 `ambiguous` 并阻塞。需要表达一对多身份迁移时使用 Redirect Record，不能借 Link Mapping 改写事件基数。

Anchor 与 Footnote ID 也可能在 Markdown 中合法重编码，不能直接比较原字符串。`core.address-occurrence@0.1.0` 是审核语义 Wrapper，不是第二份 Raw Occurrence：它固定稳定 `address_occurrence_id`、`address_kind: anchor | footnote-ref | footnote-body`、唯一 Base Source Reference 的 `{id,revision,digest}`、Review 与 Lifecycle。Entry、`source_event_ordinal`、Raw ID / Target 只从 Base 解析，禁止复制。`footnote-ref` 的 Base 必须是 `<a href>` Reference；`anchor` / `footnote-body` 的 Base 必须是 `id` 或 `name` Reference。分类变化创建新 Revision / Record 并保留旧生命周期，不改变底层 Reference 或 Fragment Digest。

`core.address-mapping@0.1.0` 至少固定 Mapping ID、Semantic Address Occurrence 的 `{id,revision,digest}`、最终 Node ID / Markdown ID / Locator、`equivalence_id`、Review 与 Lifecycle；Raw 坐标只从 Wrapper 的 Base Reference 解析，Mapping 不复制另一套计数。Source 与 Library 两侧结构投影统一发出 `address_occurrence_id + equivalence_id`。每个 Active Address Occurrence 恰有一条 Active Mapping；所绑 Revision / Digest 不一致时失效并阻塞。Ref → Body 完整性按上一节的等价组规则验证。

消费关系必须互斥且完备：已进入转换范围的 `<a href>` Raw Reference 恰好由一条 Active 普通 Link Mapping，或一条 `address_kind: footnote-ref` 的 Active Address Occurrence 消费；不得两者同时存在。已进入转换范围的每个 Image / Resource Raw Reference 恰好由一条 Active Link Mapping 消费；每个 `id` / `name` Raw Reference 恰好由一条 Active `anchor` 或 `footnote-body` Address Occurrence 消费。Footnote 消费后，底层 `source-link` / `source-anchor` Raw Event 只投影为 Footnote Event，不再额外生成普通 Link / Anchor Event。零消费或双重消费以 `REFERENCE_CONSUMPTION_CONFLICT` 阻塞；Footnote Ref 无唯一 Active Body、或两个 Source ID 映射到同一未经合并批准的目标也必须阻塞。

允许的结构差异必须引用 `metadata/exceptions/` 中的稳定 Exception ID，并在应用例外前后分别保存事件流摘要。禁止把“Markdown 表达不同”设为通配例外。

### 4.3 测试向量

摘要输入（每一显示行后都有一个 LF，包括最后一行）：

```text
lorebuddy-structure-events-v1
{"kind":"paragraph","t":"enter"}
{"t":"text","v":"规则"}
{"kind":"paragraph","t":"exit"}
```

期望 SHA-256：

```text
eecf53afc2cecfa749e8b147f2a39531cb599e2f00882f9129d4b8abc54a49f4
```

## 5. 来源片段事件

协议 ID：`core.source-fragment-events@0.1.0`  
Domain Prefix：UTF-8 `lorebuddy-source-fragment-events-v1\n`

`fragment_digest` 对批准范围产生的 Source Structure Event Stream 计算，包括解码后的原字符、Anchor、List、Table、Link 原始 Occurrence、Image Candidate、Pre、Code、Sup 与 Sub。它发生在 Library 改写前，不使用最终 LoreBuddy URI，也不应用可修订的 Link / Address Mapping 或 Visibility Decision。该原始证据流无条件保留所有 DOM 子树及其中的文字和引用；不得因为当前审核认为内容不显示就从 Fragment Evidence 删除。

Visibility 是外部审核事实，不进入 Source Fragment Event。Source 与 Library 的可见文本 / 结构比较从原始证据流与 `metadata/visibility-decisions/` 共同导出：Decision 为 `hidden` 的整个子树排除，`visible` 保留，`unknown` 阻塞；比较投影不发 `visibility` Wrapper。Fidelity Record 必须固定所用 Decision ID / Revision / Digest。改变 Visibility Decision 会得到新的比较结果，但不改变 Fragment Digest。

Source Fragment 只沿用第 4 节的 Block、List、Table、Preformatted 与 Inline Container，以及普通 `text` / `line-break`；明确排除 Addressable、Link 和 Image 事件。后面三类需要审核后的 UUID / Equivalence，不属于不可变 Raw Evidence，必须分别用本节的 `source-anchor`、`source-link`、`source-image` 表达。Source Fragment 中的 `text.v` 覆盖恢复 DOM Text 的精确解码字符序列，包括 ASCII 空白与换行，不执行第 3.2 节的可见文本折叠或 `block-break` 规则。HTML Tokenizer 对 CR / Character Reference 的处理由 Parser Receipt 固定；Entry Digest 与可选 Raw Selection Digest 仍负责证明原始 lexical bytes。来源引用使用以下事件，所有字段均必填，未知值用 `null`：

```jsonl
{"attribute":"href","element":"a","kind":"source-link","raw_target":"../原路径.htm#片段","t":"enter"}
{"kind":"source-link","t":"exit"}
{"alt":"...","attribute":"src","candidate_descriptor":null,"candidate_ordinal":0,"element":"img","raw_target":"image.png","render_slot_ordinal":0,"t":"source-image","title":null}
{"attribute":"src","element":"script","raw_target":"app.js","resource_role":"script","t":"source-resource"}
{"attribute":"id","element":"div","raw_id":"来源锚点","t":"source-anchor"}
```

Source Fragment 内容事件禁止包含随机 UUID、解析后的 Source ID、`resolved_kind` 或最终 `equivalence_target`；否则重新登记 Occurrence 或改变解析策略会在来源字符未变时错误改变 Fragment Digest。`source-link` 是 Container；`source-anchor`、`source-image` 与 `source-resource` 是单事件。所有 Enter / Single Event 的 `attribute` 使用 HTML Tokenizer 得到的 ASCII Lowercase Canonical Name；`HREF` 等原始 lexical spelling / bytes 只保存在 Occurrence 的 byte-range evidence。DOM 事件的 `element` 是规范小写 HTML Element，独立 CSS Entry 的 URL Token 使用 `element: null`。Source Link Exit 仍只含 `kind`、`t`。`source-resource.resource_role` 来自本节固定派发表。Footnote 不是独立 Raw Event：Semantic Address Occurrence 先包装底层 `<a href>` 的 `source-link` 或 `id` / `name` 的 `source-anchor` Reference，Address Mapping 再产生比较投影中的 Footnote Ref / Body 并固定 Body Locator；这样人工分类不会改写 Fragment Digest。

v0.1 按 Element Context 派发引用，不能只看 Attribute 名：

| Element Context | Attribute / Token | Raw Event | `resource_role` / 说明 |
|---|---|---|---|
| 任意 Element | `id`、`name` | `source-anchor` | 两个 Attribute 分别发出 |
| `a` | `href` | `source-link` Enter / Exit | 唯一默认语义链接 Container |
| `img` | `src`、`srcset` | `source-image` | 同一 Render Slot |
| `picture > source` | `srcset` | `source-image` | 归入所属 `picture` Slot |
| `video` | `poster` | `source-image` | 独立 Poster Slot |
| `link` | `href` | `source-resource` | `link-resource` |
| `script` | `src` | `source-resource` | `script` |
| `iframe`、`frame` | `src` | `source-resource` | `embedded-document` |
| `embed` | `src` | `source-resource` | `embedded-object` |
| `object` | `data` | `source-resource` | `embedded-object` |
| `audio`、`video`，或其下 `source` | `src` | `source-resource` | `media` |
| `track` | `src` | `source-resource` | `track` |
| `base` | `href` | `source-resource` | `base-uri` |
| Inline `style`、`style` Element、独立 CSS Entry | CSS URL Token | `source-resource` | `css-url` |

`area[href]`、`input[type=image][src]`、`srcset` 出现在非 Image Context、以及表中未登记的 URL-bearing Element / Attribute 在 v0.1 必须以 `UNSUPPORTED_REFERENCE_ELEMENT` 或 `UNSUPPORTED_REFERENCE_ATTRIBUTE` 阻塞；Raw Entry 字节仍保留，但不能把它误发成 Link / Image，也不能静默忽略。新增 Context 必须升级协议并增加 Fixture。

`render_slot_ordinal` 在一个 Fragment 内按 DOM 阅读顺序、从 0 开始标识每个 `<img>`、完整 `<picture>` 或 `<video poster>` 渲染槽；`candidate_ordinal` 在槽内从 0 开始，并按该槽中 Source Reference Event 的发出顺序连续编号。对 `<img src srcset>`，`src` 固定为 Candidate 0，`srcset` Candidate 从 1 开始保持来源顺序；对 `<picture>`，按子元素 DOM 顺序扫描，并在同一元素内遵循第 6 节的 `src` 后 `srcset` 顺序，末尾 `<img>` Fallback 仍属于同一 Slot；单独的 `src` 或 `poster` 只有 Candidate 0。每个 URL Candidate 发出独立 `source-image`，共享 Slot，并逐字保存 Descriptor。Alt / Title 对同一 Slot 的所有 Candidate 必须相同，并且可见文本流只在 Slot 位置发一次 `image-alt`。v0.1 的 Fidelity Projection 不支持 Responsive Image 多 Candidate：Raw Evidence 必须完整保存，但 Candidate 数量大于 1 时以 `UNSUPPORTED_RESPONSIVE_IMAGE` 阻塞，不能任选一个目标或伪造一对一 Mapping。CSS URL 一律使用 `source-resource`；若页面族认定 CSS Image 承担正文语义，v0.1 同样阻塞并等待新协议。

`raw_target`、`raw_id`、`alt` 与 `title` 指锁定 HTML / CSS Tokenizer 输出的 Character Reference 解码后字符串、URL Resolution 前的值；不 Trim、不做 Unicode Normalization、不做 Percent Decode、不折叠空白。缺失 Attribute 为 JSON `null`，显式空值为 `""`。Source Reference Occurrence Record 另存精确 lexical byte range / digest；事件字段不能冒充原始 bytes。

`fragment_digest` 不应用 Link / Address Mapping，否则后续节点拆分或 Anchor 重编码会改变 Source Fragment 摘要。Library Fidelity 比较使用第 4.2 节的结构投影，二者职责不同。

Fragment 身份仍是 UUID；摘要只证明所选内容，没有携带 Entry、Locator 或审核身份。Source Fragment Record 还必须独立固定：

- `entry_id` 与 `entry_digest`；
- Provenance Locator；
- Boundary Decision ID；
- Parser / Decoder Receipt；
- Source Event Stream 的路径、事件数、精确文件字节数与普通 `file_digest`；该 Byte Count / Digest 均排除虚拟 Domain Prefix，带 Prefix 的语义摘要由 `fragment_digest` 单独保存。

若存在可证明的原始 Byte Range，还可以计算 `raw_selection_digest`：Domain Prefix 为 `lorebuddy-source-fragment-raw-v1\n`；每段先写 JCS `{end,length,start}` 与 LF，再写恰好 `length` 个原始 byte。Range 按来源顺序排列，不在段间增加字符。它不能替代语义事件摘要，因为 DOM Fragment 可能由多个不连续 Range 组成。

### 5.1 Fidelity Coverage Map 坐标

协议 ID：`core.fidelity-coverage-map@0.1.0`。

Coverage Map 显式连接 Node Provenance、正文 UTF-8 Byte Range 与 Full 模式下的 Source Fragment Event Range。一个 Binding 恰好绑定一个 `provenance_id`；一个 Unit 是最小对应单元，使用稳定 UUIDv7。Unit 中多个 `body_utf8_ranges` 与多个 `source_fragment_event_ranges` 分别按来源顺序拼接为“序列对序列”的一个比较输入，不表示两组 Range 的笛卡尔积。不同对应关系必须拆成不同 Unit。

`source_fragment_event_ranges` 使用规范 Fragment JSONL 的零基、半开 Record Index `{start_record,end_record}`；它与 Entry 级 Reference Attribute Scan 的 `source_event_ordinal` 完全不同。每个 Range 必须非空、按 `(start_record,end_record)` 排序、互不重叠且不超过 Fragment Record 固定的事件数。选中事件拼接前，每段都必须保持所有 Container 的 Enter / Exit 平衡；Range 若切开 Container 或单个 `text` Event，v0.1 阻塞并要求建立更精确 Fragment / Unit，不能复制或截断 Event。

`body_utf8_ranges` 同样是非空、排序、不重叠的半开区间，边界必须位于有效 UTF-8 Code Point 和锁定 Markdown Parser 的完整语义节点边界。每个 Unit 从这些范围重建 Library 事件，再对所选 Source Event 应用该 Unit 固定的 Link / Address Mapping、Visibility Decision 和 Exception，独立比较 Visible Text 与 Structure。只有全部 Unit 都通过，Fidelity Record 才能通过。

闭包验证固定为：同一 Provenance 最多一个 Binding；该 Binding 全部 Unit 的正文 Range 规范并集必须等于 Node Provenance 的 `body_utf8_ranges`；同一 Provenance 的 Unit 不得重叠；每个正文贡献 Provenance 恰好属于一个 Active Assertion；`transcription` Node 的正文贡献 Range 并集必须覆盖全部非空正文 byte。不同 Provenance 独立覆盖同一 Range 时，Overlap Review 必须列出 Assertion、Provenance、Unit 与精确区间。v0.1 不定义多来源联合变换；Correction / Errata 必须由独立协议和审核表达。

Full Fidelity Record 的 Coverage Map 包含 Fragment 与 Source Event Range；Node Assertion 和 Public Fidelity Attestation 只保留 `{algorithm, bindings:[{provenance_id, units:[{id, body_utf8_ranges}]}]}`。三者的公开投影必须逐字段相等。Audit Binding 负责把公开 Provenance / Unit 映射回私有 Fragment、Fidelity Record 与投影算法，不能靠数组位置配对。

### 5.2 测试向量

摘要输入（每一显示行后都有一个 LF，包括最后一行）：

```text
lorebuddy-source-fragment-events-v1
{"t":"text","v":"专注"}
```

期望 SHA-256：

```text
0cdbfde1fc3390a3c9c16ebc639aebeedc3abccf14f7134efebdaea2ddc6eec1
```

## 6. Candidate 与 Occurrence Key

Key 只用于把重跑结果匹配到已有 UUID Record；Key 变化不自动删除旧 Record，也不自动分配新的语义身份。

统一算法为：协议 Domain Prefix、一个 JCS Object、LF，再取 SHA-256。字段必须完整，未知值使用 `null`。

| Key | Domain Prefix | JCS 字段 |
|---|---|---|
| Boundary Candidate | `lorebuddy-boundary-candidate-v1\n` | `artifact_id, entry_id, locator, fragment_digest, proposal_algorithm` |
| Navigation Occurrence | `lorebuddy-navigation-occurrence-v1\n` | `artifact_id, navigation_entry_id, parent_key, ordinal, raw_name, raw_local, rule_version` |
| Source Reference Occurrence | `lorebuddy-source-reference-occurrence-v1\n` | `artifact_id, entry_id, reference_kind, element, attribute, source_event_ordinal, raw_value, rule_version` |
| Semantic Address Occurrence | `lorebuddy-address-occurrence-v1\n` | `base_reference_occurrence_id, address_kind, rule_version` |
| Asset Usage | `lorebuddy-asset-usage-v1\n` | `node_id, asset_digest, source_reference_occurrence_id, markdown_locator, rule_version` |
| Detected Issue | `lorebuddy-issue-key-v1\n` | `code, artifact_id, entry_id, locator, rule_version` |

Navigation `ordinal` 是父对象下按来源顺序、从 0 开始的 Object 序号，包含没有 Local 的分组对象。

Source Reference `source_event_ordinal` 共用整个 Entry 的一个序号流，从 0 开始；语义是“Reference Attribute Scan Ordinal”，不是 Link、Image、Resource、Anchor 各自独立计数。Semantic Address Occurrence 只复用其 Base Reference 的值，绝不增加序号；Candidate Key 的 `base_reference_occurrence_id` 等于规范 Record 中 `base_reference.id`。恢复 DOM 按深度优先前序遍历，每个 Element 在访问 Child 前按 `id`、`name`、`href`、`src`、`data`、`poster`、`srcset` Candidate、Inline CSS URL 的顺序扫描；只有第 5 节派发表对该 Element Context 登记的实际 Attribute / Candidate / URL Token 才发出对应 Event，但检测到未登记的 URL-bearing Attribute 必须占用一个 Ordinal 后阻塞，防止修复协议后其后的 Key 全部漂移。`<style>` 中的 URL 在该 Element 的位置按 CSS Token 顺序计数；外部 Stylesheet 是独立 Source Entry，在该 CSS Entry 的 Token 顺序中计数，再由 Analysis Receipt 固定其与 HTML 页面族的作用关系。

Fragment Event 的发出顺序固定为：先发 Element 对应的允许结构 Container Enter，再按 `id`、`name` 发 `source-anchor`，然后仅对 `<a href>` 发 `source-link` Enter，再按派发表与扫描顺序发 `source-image` / `source-resource`，随后遍历 Child，最后发 `source-link` Exit 与结构 Container Exit。`<style>` 内容中的 `source-resource` 按 Token 位置夹在其 Text / Token Stream 中。Footnote Ref 复用其 `<a href>` 的 Ordinal，Footnote Body 复用其 `id` 或 `name` 的 Ordinal；它们不增加新 Ordinal，也不与普通 Source Link / Anchor 重复生成 Raw Event。Parser、Recover 配置、Element Context Dispatcher、`srcset` Parser、CSS Tokenizer 与规则版本必须在 Receipt 中锁定。

`core.source-reference-occurrence@0.1.0` 的 `reference_kind` 只允许 `anchor | link | image | resource`，并固定 `element`；`attribute` 使用 Canonical Name `id | name | href | src | data | poster | srcset | style:url | stylesheet:url`。Resource Record 还必须固定派发表中的 `resource_role`。同一原始 Element 同时含 `id` 与 `name` 时生成两个底层 Anchor Reference，不得合并后重新编号；Footnote Body 的 Semantic Address Occurrence 必须明确选择其中一个，另一个在转换范围内仍需由普通 Anchor Address Occurrence 消费。

Asset Usage 的 `source_reference_occurrence_id` 必须解析到 `reference_kind: image` 的 Active Source Reference Occurrence；没有来源 Reference 的 Library 原生 Asset Usage 显式写为 JSON `null`，并由独立 Creation Provenance 证明。`markdown_locator` 固定为对象 `{body_utf8_start, body_utf8_end, markdown_ast_path, parser, parser_version}`：Byte Range 是最终 Markdown 正文区域内、对应完整 Image / Link Syntax 的半开区间；AST Path 使用 Parser 定义的 Child Index 数组。所有 Locator 字段必填，无法定位时阻塞，不能换用行号。

同一个 Key 若匹配多个已存在 UUID，或同一 UUID 被两个不同 Key 同时声明，必须以 `NON_DETERMINISTIC_OUTPUT` 阻塞，不能任选一个。

### 6.1 Boundary Candidate 测试向量

摘要输入（每一显示行后都有一个 LF，包括最后一行）：

```text
lorebuddy-boundary-candidate-v1
{"artifact_id":"urn:uuid:00000000-0000-7000-8000-000000000001","entry_id":"urn:uuid:00000000-0000-7000-8000-000000000002","fragment_digest":"sha256:0000000000000000000000000000000000000000000000000000000000000000","locator":null,"proposal_algorithm":"test.boundary@1.0.0"}
```

期望 SHA-256：

```text
292f5c463dbec1dbf2fca9aa29623283eb642cb8232056b1383e5beda1d73682
```

## 7. 验证要求

实现至少通过：

1. 本文全部测试向量；
2. 不同 Map 插入顺序得到相同 JCS bytes；
3. 不同 Locale、Timezone、临时目录和文件枚举顺序得到相同事件与摘要；
4. 中文、Surrogate Pair、U+00A0、U+3000、CRLF、Pre、Code、Sup、Sub、Definition List、Table Caption / Row Group、Rowspan、Colspan 和 Footnote 固定样例；
5. Link Rewrite 保持 Occurrence 一对一的正反例；
6. 未知 Visibility、动态 Script 内容和未批准结构差异均不能通过。

测试向量文件在规范确认后必须固化为机器可执行 JSONL Fixture，至少覆盖三个事件摘要、Boundary / Navigation / Source Reference / Semantic Address / Asset Usage / Issue Key、Raw Selection，以及普通 Link 与 Footnote 的互斥消费、Definition List、复杂 Table、Hidden Subtree 和 `srcset`。在这些 Fixture 齐备前，本草案不得标记为 Frozen，任何实现也不得声称 `core.*@0.1.0` 协议一致。本文数值是 `0.1.0` 的规范预览；修改任何 Domain Prefix、事件字段或空白规则都必须发布新的协议版本。
