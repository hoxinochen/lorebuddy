# Markdown 与元数据规范草案

状态：Draft  
规范版本：`0.1.0`

## 1. 设计目标

知识节点（Knowledge Node）必须同时满足：

- 人可以直接阅读和维护；
- 未知的未来 AI 可以不依赖 LoreBuddy Runtime 理解正文与上下文；
- 机器可以验证身份、类型、版本、关系和 Provenance；
- 官方或来源正文不会被编辑元数据污染；
- 文件移动、标题变化或索引重建不会破坏节点身份。

规范格式采用 UTF-8 Markdown + YAML Front Matter。Markdown 是规范正文载体，数据库和搜索索引只能是派生表示。

## 2. 一个文件表达一个节点

每个 `.md` 文件只表达一个语义单元、一个主要语言和一个版本上下文。

以下内容必须拆分：

- 同一规则的 2014 与 2024 表达；
- 勘误前与勘误后文本；
- 英文原文与中文翻译；
- 官方规则与 House Rule；
- 同名但正文表达、适用范围或权威上下文不同的生物、法术、物品或地点；仅来源位置不同的相同表达在人工确认后可以使用一个 Node 和多条 Provenance；
- 一页中的多个可独立引用主题。

节点不以固定 Token 数切分。过大节点可以触发审核警告，但不能为适配模型上下文窗口而自动破坏语义边界。

章节（Chapter）属于 Source Navigation，不是默认 Node 边界。禁止生成 `Chapter08.md` 这类仅表达来源分段的 Library 文件；应生成 `concentration--<uuid>.md`、`opportunity-attack--<uuid>.md` 等语义主题文件。若一个章节本身确实是不可再分的叙事或规则单元，必须由 Boundary Ledger 明确批准，而不是按文件名自动保留。

### 2.1 连续来源要求

`content.mode: transcription` 的 v0.1 节点正文应该对应一个连续 Source Fragment。

如果一个主题散布在多个不连续位置，优先拆成多个节点并使用 `core.part_of` 或 `core.references` 连接。这样可以避免在一个文件中维护脆弱的逐段来源映射。

只有当业务语义确实不可拆分时，才允许多个 Fragment，并必须增加逐段 Provenance 记录和人工审核。转换器不得自动拼接后假装它是连续原文。

## 3. 文件编码与基本格式

- 编码必须为 UTF-8，无 BOM。
- 换行必须为 LF。
- 文件末尾必须有一个换行。
- Front Matter 必须位于文件开头，以 `---` 包围。
- 正文与 Front Matter 之间保留一个空行。
- 普通段落不进行固定列宽硬换行，避免产生无语义 Diff。
- 不自动进行 Unicode NFC/NFKC、全半角、标点或空格“美化”。
- YAML 字符串中可能被解析为日期、布尔值或数字的值必须显式加引号。

Front Matter 使用 `core.yaml-json-subset@0.1.0`：语法基于 YAML 1.2，并且解析结果必须落入 JSON Data Model。Mapping Key 只能是字符串；标量只允许 JSON String、Boolean、Number 与 Null。解析器必须拒绝重复 Key、Anchor、Alias、Merge Key `<<`、自定义 Tag、Directive、复杂 Key、多文档流、NaN / Infinity、隐式 Timestamp 和实现特有类型。`---` 只作为本文规定的两个边界行，禁止 `...` 结束标记。Schema 验证、摘要和 Disclosure Projection 都作用于该 Profile 产生的 JSON 值；任何 Parser 得到不同值都必须阻塞，不能“最后一个重复 Key 获胜”。

Source 的原始编码保持不变。Library 转为 UTF-8 是派生表示变化，不代表允许修改显示文字。

## 4. 推荐 Front Matter

```yaml
---
schema: "core.knowledge-node@0.1.0"

id: "urn:uuid:019f0000-0000-7000-8000-000000000101"
package_id: "urn:uuid:019f0000-0000-7000-8000-000000000001"
kind: "core.rule"

title: "专注"
language: "zh-Hans"
aliases:
  - value: "Concentration"
    language: "en"
    role: "source-title"

applicability:
  systems:
    status: "known"
    values:
      - system: "dnd"
        rulesets:
          - "dnd.5e-2014"
  settings:
    status: "not-applicable"
    values: []
  campaigns:
    status: "not-applicable"
    values: []

content:
  mode: "transcription"
  fidelity_target: "verbatim-visible-text"
  body_byte_digest: "sha256:..."
  visible_text_digest:
    algorithm: "core.visible-text-events@0.1.0"
    value: "sha256:..."
  structure_digest:
    algorithm: "core.structure-events@0.1.0"
    value: "sha256:..."
  fidelity_evidence:
    aggregate_mode: "full"
    overlap_review_ids: []
    assertions:
      - id: "urn:uuid:..."
        coverage_map:
          algorithm: "core.fidelity-coverage-map@0.1.0"
          bindings:
            - provenance_id: "urn:uuid:019f0000-0000-7000-8000-000000000201"
              units:
                - id: "urn:uuid:..."
                  body_utf8_ranges:
                    - start: 0
                      end: 1234
        mode: "full"
        fidelity_record_id: "urn:uuid:..."

responsibility:
  - party_id: "urn:uuid:..."
    role: "community-transcriber"
    content_scope: "body"
    basis: "source-explicit"

authority_claims:
  - status: "claimed"
    role: "community-translation"
    party_id: "urn:uuid:..."
    scope: "body"
    evidence_ids:
      - "urn:uuid:019f0000-0000-7000-8000-000000000401"

normativity_claims:
  - status: "normative"
    scope:
      systems:
        status: "known"
        values:
          - system: "dnd"
            rulesets:
              - "dnd.5e-2014"
      settings:
        status: "not-applicable"
        values: []
      campaigns:
        status: "not-applicable"
        values: []
    basis: "source-claimed"
    evidence_ids:
      - "urn:uuid:019f0000-0000-7000-8000-000000000401"

provenance:
  - id: "urn:uuid:019f0000-0000-7000-8000-000000000201"
    mode: "embedded-fragment"
    fragment_id: "urn:uuid:..."
    source_mapping_ids:
      - "urn:uuid:..."
    traceability: "full"
    artifact_id: "urn:uuid:..."
    artifact_digest: "sha256:836eea8912cf..."
    entry_id: "urn:uuid:..."
    original_entry_path: "/玩家手册/施法/专注.htm"
    entry_digest: "sha256:..."
    locator:
      schema: "core.provenance-locator@0.1.0"
      anchor: null
      navigation_occurrence_ids:
        - "urn:uuid:..."
      navigation_paths:
        - - "旧版内容（2014）"
          - "玩家手册2014（旧版）"
          - "施法"
          - "专注"
      heading_path:
        - "专注"
      entry_raw_byte_ranges:
        - start: 18240
          end: 19582
      decoded_text:
        encoding: "gbk"
        coordinate: "unicode-scalar-value"
        ranges:
          - start: 9000
            end: 9660
      dom:
        parser: "..."
        parser_version: "..."
        selector_language: "xpath-1.0"
        selector: "..."
      text_quote:
        prefix: "..."
        exact: "..."
        suffix: "..."
    fragment_digest:
      algorithm: "core.source-fragment-events@0.1.0"
      value: "sha256:..."
    coverage: "full"
    role: "transcription"
    body_utf8_ranges:
      - start: 0
        end: 1234

structured_extractions: []

tags:
  - id: "dnd5e.rules.spellcasting"
    assertion:
      basis: "editorial-reviewed"
      evidence_ids: []

relationships:
  - id: "urn:uuid:..."
    predicate: "core.references"
    target: "urn:uuid:..."
    assertion:
      basis: "source-explicit"
      evidence_ids:
        - "urn:uuid:019f0000-0000-7000-8000-000000000401"

lifecycle:
  status: "active"
  node_revision: 1

extensions: {}
---
```

示例值不是对当前 CHM 来源身份的事实声明。

## 5. 对初始字段建议的调整

初始建议为：

```yaml
id:
system:
type:
title:
aliases:
sources:
tags:
relationships:
version:
```

推荐调整如下：

| 原字段 | 调整 | 原因 |
|---|---|---|
| `id` | 保留，限定为稳定 UUID URN | 标题、路径和摘要都会变化 |
| `system` | 改为 `applicability.systems[]` | 节点可能跨系统或与系统无关，也可能支持多个规则上下文 |
| `type` | 改为命名空间化 `kind` | 避免各系统对 Spell、Condition 等同名类型产生冲突 |
| `title` | 保留 | 人工显示名，不承担身份 |
| `aliases` | 改为结构化数组 | Alias 需要语言与角色 |
| `sources` | 改为 `provenance` | 不仅要列文件，还要表达 Work、Edition、Artifact、Entry 和 Locator |
| `tags` | 保留但命名空间化 | 自由文本标签无法稳定迁移 |
| `relationships` | 改为结构化有向边 | 需要目标 ID、谓词和断言依据 |
| `version` | 拆分 | Schema、Package、Node、Edition 和 Ruleset 版本含义不同 |

## 6. 字段规范

### 6.1 `schema`

声明当前文件遵循的 Node Schema 版本。已发布的 Schema 标识不得指向内容变化的文件。

### 6.2 `id`

- 必填；
- 使用 UUIDv7 的 `urn:uuid:` 形式；
- 创建后永久不变；
- 禁止从标题、路径或正文摘要生成；
- 删除后不得复用。

### 6.3 `package_id`

指向拥有该 Node 的 Package。跨 Package 引用仍使用 Node ID，不复制节点。

### 6.4 `kind`

使用注册表中的命名空间标识，例如：

- `core.rule`
- `core.reference-entry`
- `core.narrative-entity`
- `dnd5e.spell`
- `pf2e.spell`

`dnd5e.spell` 与 `pf2e.spell` 不是同一个 Schema。

### 6.5 `title`

- 必填；
- 是当前语言中的主要显示名；
- 可以来自来源标题，也可以是经审核的编辑性标题；
- 若为编辑性标题，其存在不得改变正文；
- 标题变化不改变 ID。

### 6.6 `language`

使用 BCP 47。简体中文使用 `zh-Hans`，不要用含义模糊的 `cn` 或 `zh-CN` 替代文字系统信息，除非确实需要地区语义。

### 6.7 `aliases`

每项包含：

- `value`：原样显示值；
- `language`：BCP 47；
- `role`：如 `source-title`、`common-name`、`abbreviation`、`former-name`。

Alias 不是唯一键。同一个 Alias 可以解析到多个节点，调用方必须结合系统、规则版本、Package 和上下文消歧。

### 6.8 `applicability`

显式描述适用范围。每个维度必须使用 `status: known | unknown | not-applicable`。空 `values` 只表示该状态下没有值，不能同时承担“未知”和“确定不适用”两种含义。不得根据文件目录自动填充确定值。

Package、Node、Normativity Claim 与 Relationship 必须复用同一个 `core.applicability` `$defs`：`systems.values[]` 统一使用 `{system, rulesets[]}`，不得在 Node 中改用单数 `ruleset`。范围较窄时仍使用单元素数组。

一个 House Rule 可以适用于某个 Campaign；一个世界设定实体可以不属于任何规则系统；一个通用知识节点也可以没有系统适用项。

### 6.9 `content`

`mode` 建议支持：

| 值 | 含义 |
|---|---|
| `transcription` | 从来源可见正文忠实转换，禁止改写 |
| `editorial` | LoreBuddy 编写的概念、说明或分类内容 |
| `record` | 未来人工录入的 Campaign、Session 等事实记录 |

`fidelity_target` 只描述 Markdown 正文，建议支持：

| 值 | 含义 |
|---|---|
| `verbatim-bytes` | 仅适用于可直接保留字节的格式 |
| `verbatim-visible-text` | 结构转换，但显示文字和顺序保真 |
| `editorial` | 非来源转写 |

`body_byte_digest` 对 Markdown 正文区域的精确 UTF-8 字节计算 SHA-256，用于检测未登记修改。算法如下：

1. 文件必须以 `---\n` 开始；
2. 找到独占一行的第二个 `---\n`；
3. 其后必须恰有一个空行；
4. 摘要区域从该空行之后的第一个正文 byte 开始；
5. 正文必须以恰好一个 LF 结束，该 LF 参与摘要；
6. 不做 Unicode、空白、HTML 或行宽规范化。

`visible_text_digest` 使用 `core.visible-text-events@0.1.0`，只用于 HTML → Markdown 可见文字保真验证；`structure_digest` 使用 `core.structure-events@0.1.0` 验证审核投影后的结构。`fidelity_evidence.assertions[]` 必须通过版本化 Coverage Map 为每个正文贡献 Provenance 和正文 UTF-8 半开 Byte Range 指定 `full` Fidelity Record 或 `attested` Public Fidelity Attestation。规范事件、空白规则、Domain Prefix、Link Projection 与测试向量见[完整性与事件协议](integrity-protocols.md)。这些摘要都不是 Node ID。

正文贡献角色包括 `transcription | translation | correction`；每条这类 Provenance 的 `body_utf8_ranges` 必须与引用它的 Fidelity Coverage Map Binding 中全部 Unit Range 的规范并集完全相等。`evidence` 与 `structured-extraction` 角色不贡献正文，正文范围必须为空；后者通过独立 `structured_extractions[]` 覆盖 Front Matter / Extension 字段。对 `content.mode == transcription`，所有非空正文 byte 必须由至少一个 Fidelity Assertion 覆盖；范围不得越界。`editorial` / `record` 正文不做 Source Fidelity 比较，`fidelity_evidence` 必须为空或省略，但仍必须维护 `body_byte_digest` 和责任主体。

`aggregate_mode` 是计算字段：每个正文贡献 Provenance 必须恰好出现在一个 Active Assertion 的一个 Binding 中；只有全部 Binding / Unit 都由 `mode: full` Assertion 覆盖并通过时才为 `full`；任一贡献只能由 Attestation 覆盖时为 `attested`；缺失、失败或互相矛盾时 Node 无效。Evidence-only Provenance 不降低正文 Fidelity，但它自己的 Traceability 状态仍单独保留。

`coverage_map.algorithm` 在 v0.1 固定为 `core.fidelity-coverage-map@0.1.0`。每个 Binding 只含一个 `provenance_id`，同一 Assertion 中不得重复；其 `units[]` 是最小对应单元（Correspondence Unit）。一个 Unit 的一个或多个 `body_utf8_ranges` 共同表示按正文顺序拼接的一个序列，不表示 Range 之间或 Source Range 之间的笛卡尔积；不同对应关系必须拆成不同 Unit。Binding 按 `provenance_id` UTF-8 bytes 排序，Unit 按 ID 排序，Unit 内 Range 按 `(start,end)` 排序且不得重叠。每个 Unit ID 使用稳定 UUIDv7。

对每个 Provenance，其 Binding 所有 Unit Range 的规范并集必须逐字等于该 Provenance 的 `body_utf8_ranges`，且同一 Provenance 的 Unit 之间不得重叠。不同 Provenance 可以独立证明同一正文范围；每一个重叠区间都必须由 `overlap_review_ids[]` 引用的 Active Review 精确列出 Node ID、Assertion ID、Provenance ID、Unit ID、半开区间、理由与 Reviewer。未登记重叠阻塞，`overlap_review_ids` 去重排序。v0.1 不定义“多个来源联合改写出一段正文”的 Source Algebra；Base + Errata 等组合必须使用独立 Correction / Exception 协议，不能借多个 Provenance 暗示未定义变换。

`assertions[]` 使用判别联合。`mode: full` 必须且只能携带 `fidelity_record_id`；`mode: attested` 必须且只能携带 `fidelity_attestation_id` 与 `fidelity_attestation_digest`，例如：

```yaml
- id: "urn:uuid:..."
  coverage_map:
    algorithm: "core.fidelity-coverage-map@0.1.0"
    bindings:
      - provenance_id: "urn:uuid:..."
        units:
          - id: "urn:uuid:..."
            body_utf8_ranges:
              - start: 0
                end: 1234
  mode: "attested"
  fidelity_attestation_id: "urn:uuid:..."
  fidelity_attestation_digest: "sha256:..."
```

Public Fidelity Attestation 必须绑定同一 Node ID、`node_revision`、Assertion ID、公开 Coverage Map、`body_byte_digest`、`visible_text_digest` 与 `structure_digest`；只要任一值变化，旧 Attestation 就不能重放。Attestation 不得包含 Fragment、Source Event Range、Mapping 或受限摘要；最小结构和公开投影规则见[权利、访问与发布规范](rights-release-spec.md)。

### 6.10 `responsibility`、`authority_claims` 与 `normativity_claims`

每种正文模式都必须说明责任主体。`transcription` 记录转写或翻译责任；`editorial` 和 `record` 记录实际作者。Party 可以是已登记的人、组织、团体或显式 `unknown`，不能用 Package 身份代替作者身份。

权威身份与规范性分别使用带范围、证据和审核状态的数组断言。`authority_claims` 可以表达 publisher、licensee、official-translation、community-translation、third-party、private-author 等角色。

`normativity_claims.status` 建议值：

- `normative`
- `optional`
- `informative`
- `playtest`
- `unknown`

每条 Normativity Claim 有自己的 `scope`，因此可以表达“在 Campaign A 中 normative，在其他上下文中不适用”。`basis` 说明判断来自 `source-explicit`、`source-claimed`、`editorial-reviewed` 或 `unknown`。不得仅因出版者为官方就假设所有内容均为最终规范规则。

### 6.11 `provenance`

Provenance 是显式联合类型：

- `mode: embedded-fragment`：`fragment_id` 必须解析到当前 Package 或可读 Content Dependency 中唯一的 Source Fragment Record；Node 中的 Locator 与 Digest 快照必须逐字段匹配规范记录；
- `mode: external-public-receipt`：只引用本 Package 中经 Disclosure Approval 的 Public Provenance Receipt，不得包含受限 Fragment、Artifact、Entry、Locator 或私有摘要；必须声明 `traceability: attested`。

公开 Receipt 示例：

```yaml
provenance:
  - id: "urn:uuid:..."
    mode: "external-public-receipt"
    receipt_id: "urn:uuid:..."
    receipt_digest: "sha256:..."
    traceability: "attested"
    coverage: "full"
    role: "transcription"
    body_utf8_ranges:
      - start: 0
        end: 1234
```

`embedded-fragment` 的 Source Fragment Record 是 Entry、Locator 与 Fragment Digest 的事实源。发布后的 Fragment 所指范围不可原地改变。它还必须通过 `source_mapping_ids` 引用规范 Source Mapping Record，不得直接复制一个未经审核的 Work / Edition 结论。

每条 `embedded-fragment` 记录，或 Public Receipt 在授权域中的后端 Audit Record，必须同时回答：

- 当前 Provenance Record 与 Fragment 的稳定 ID；
- 实际读取了哪个 Artifact 和 Entry，并核对它们的摘要；
- Entry 字节是否仍与转换时一致；
- 使用了哪个 Fragment，以及 Locator Schema、Parser 和坐标系；
- 该 Fragment 声称映射到哪个 Edition 和 Work；
- 映射是 verified、claimed、inferred 还是 unknown；
- Node 正文覆盖 Fragment 的全部还是部分；
- 来源在 Node 中承担 transcription、translation、correction 或 evidence 中哪种角色。

上述完整问题是 `embedded-fragment` 或授权 Audit Package 必须回答的 Full Traceability 要求。公开 Receipt 只能证明“授权审计方已验证某项声明”，不能让公开消费者独立读取私有 Source；只写书名、章节名、文件路径、HTML 行号或 URL 也不足以冒充 Full Traceability。

`embedded-fragment` 中同一 Entry 可以在 HHC 多次挂载，因此必须使用一个或多个稳定 `navigation_occurrence_ids`。显示路径只是辅助快照，不能作为 occurrence 身份。

在 `embedded-fragment` 快照中，`original_entry_path` 必须逐字保存 CHM Directory 中的原始逻辑名称，包括是否存在开头 `/`、大小写、空格与原始 Unicode 形式；它不是面向显示的路径。安全落盘路径和 UI 显示名必须使用独立字段，禁止覆盖原始名称。`external-public-receipt` 禁止携带该字段，除非 Disclosure Profile 逐字段批准。

具体联合 Schema、披露字段与合规等级见[权利、访问与发布规范](rights-release-spec.md)。

### 6.12 `structured_extractions`

结构化抽取（Structured Extraction）作用于 Front Matter 或 `extensions` 中的字段，不属于 Markdown 正文保真。每条断言至少包含：稳定 ID、一个或多个目标 JSON Pointer、Provenance ID、规范 `core.structured-extraction-record@0.1.0` ID，以及 Lifecycle。

Extraction Record 存放于 `metadata/structured-extractions/`，固定 Node ID / Revision、目标 Pointer 与当前值的 JCS Digest、Fragment / Provenance、字段映射规则 ID / Version / Digest、抽取器 ID / Version / Digest、审核状态和冲突结果。目标 Pointer 集合去重后按 UTF-8 bytes 排序；同一 Pointer 只能有一个 Active Record，冲突必须阻塞。正文仍使用 `content.fidelity_target: verbatim-visible-text` 或其他正文目标，不能因为存在结构字段而改成另一个全局模式。

### 6.13 `tags`

- 使用结构化断言，并引用注册表或 Package 词汇表中的命名空间标识；
- 标签是编辑性分类，不是官方正文；
- 标签本身可以有多语言显示名，但 Node 中只保存稳定标识；
- 未审核的自动标签只能写入 `metadata/tag-candidates/`，不能进入 Node `tags`。进入 Node 后必须记录审核依据。

### 6.14 `relationships`

简单关系包含：

- `predicate`；
- `target`；
- `assertion.basis`；
- 稳定 Relationship / Assertion ID；
- `scope`、生命周期和稳定 `evidence_ids`。

禁止按 `provenance` 数组位置引用证据；数组插入或重排不能改变 Relationship 含义。

禁止在目标节点手工复制反向边。复杂、有时间范围或多方证据的关系写入独立 Relationship Record。

### 6.15 `lifecycle`

`status` 至少支持：

- `draft`
- `active`
- `deprecated`
- `withdrawn`

`node_revision` 是该稳定 Node 的语义修订号，不表示来源 Edition、规则版本、Package 版本或纯格式迁移。

### 6.16 `extensions`

系统或 Package 特有字段必须置于命名空间化扩展中，并由对应 Schema 验证：

```yaml
extensions:
  dnd5e:
    profile: "dnd5e.spell@0.1.0"
    data: {}
```

未知的必需扩展必须导致验证失败；未知的可选扩展可以保留但不得解释。

## 7. 正文规范

### 7.1 忠实转写正文

`content.mode: transcription` 时，正文只允许包含来源 Fragment 的内容表达。禁止加入：

- 摘要；
- 规则解释；
- AI 说明；
- 任何 Source Fragment 中不存在的新注释，包括新增“译者注”；
- 自动补全的上下文句；
- 静默纠错；
- 为方便检索重复插入的关键词。

来源本来存在的标题、译者注、脚注、边栏和错误必须保留，并通过结构表达。

### 7.2 Heading

- 使用 ATX Heading（`#`）；
- 不为满足“一文件一个 H1”而新增来源中不存在的标题；
- 不自动重排 Heading 层级；
- 来源 Heading 不规范时保留其语义层级，并记录转换规则；
- `title` Front Matter 足以提供节点显示名。

### 7.3 表格

- 无合并单元格的简单表格可以使用 GFM Table；
- 含 `rowspan`、`colspan`、嵌套内容或语义性布局的表格使用受限原始 HTML；
- 禁止为了生成 GFM Table 丢弃空单元格、合并关系、脚注或排序；
- 表格单元格的读取顺序必须参与文本保真验证。

### 7.4 受限 HTML

Markdown 无法忠实表达时，可以使用语义 HTML，例如：

- `table`、`thead`、`tbody`、`tr`、`th`、`td`；
- `sup`、`sub`、`ruby`；
- `details`、`summary`；
- `figure`、`figcaption`；
- 必要的 `span` 或 `div`，但必须带有规范定义的语义 class。

Library 禁止：

- `script`；
- 事件处理属性；
- `iframe`、`object`、ActiveX；
- `form`；
- 任意可执行 URL；
- 只为视觉还原而复制的大量 Office Style。

被移除的可执行或纯展示结构仍完整保存在 Source 中。

### 7.5 链接

- 已解析的 Node 链接使用稳定 LoreBuddy URI：`lorebuddy://node/<uuid>`。
- Full Traceability Package 中尚未节点化的来源目标使用：`lorebuddy://source-entry/<entry-uuid>?fragment=<fragment-uuid>`；没有精确 Fragment 时省略 Query。
- 公开 Package 无权披露 Source Entry 时使用 `lorebuddy://provenance-receipt/<receipt-uuid>`，禁止把私有 Entry ID 填入 Source URI。
- 外部 HTTP(S) URL 原样保留。
- 原资料中的坏链接不得静默改成猜测目标；应保留来源证据并产生问题记录。
- Markdown 链接不是 Relationship 的替代品。语义关系仍应写入 Front Matter 或独立 Relationship Record。

上述 URI 是稳定交换标识，不要求 Runtime 才能解释。`embedded-fragment` Package 的 Provenance / Navigation Index 必须提供 URI 到 Package 相对路径、Entry 和 Fragment Locator 的映射；`external-public-receipt` 只映射到公开 Receipt。未知消费者即使不识别自定义 Protocol，仍可从同一 Markdown 的 Provenance 分支判断公开可验证等级。

### 7.6 图片与资产

- Library 资产使用内容寻址路径；
- `alt`、`title` 和来源图注必须保留；
- Asset Index 记录 Library 资产到一个或多个 Source Entry 的映射；
- 外部图片不得在构建中静默下载；
- OCR 属于未来派生数据，不能覆盖图片或冒充图片内原文。

## 8. YAML 可移植子集

为避免解析器差异，Front Matter：

- 使用 YAML 1.2 语义；
- 禁止重复键；
- 禁止自定义 Tag；
- 禁止 Anchor、Alias 和 Merge Key；
- 日期、版本、摘要、ID 和看似数字的标识必须加引号；
- 不依赖 YAML 1.1 的 `yes/no/on/off` 隐式布尔值；
- Map Key 必须是字符串；
- 未知顶层字段验证失败，扩展只能进入 `extensions`。

JSON Schema Draft 2020-12 是机器验证的规范来源。YAML 只是作者格式。

## 9. 编辑与修订

- 修改正文或会改变 Node 语义的 Front Matter 后必须提高 `node_revision`。
- 只改变 Schema 表达、字段布局或序列化形式且语义等价的迁移，不提高 `node_revision`；由 `schema` 版本与 Migration Record 记录。
- 只移动或重命名文件、且字节内容不变时，可以不提高 `node_revision`。
- 修复转换器造成的 Markdown 错误必须保留 Node ID、提高语义修订、更新 `body_byte_digest`、`visible_text_digest` 与 `structure_digest`，并记录转换修复报告。
- 来源自身发生勘误时，不直接覆盖旧 Node；建立新表达并连接 `core.corrects` 或 `core.supersedes`。
- Schema 迁移不得顺便修改官方正文。

## 10. 最小验证

每个 Node 至少通过：

1. UTF-8、LF 与 Front Matter 格式检查；
2. YAML 子集检查；
3. JSON Schema 验证；
4. ID 全局唯一检查；
5. Package、Work、Edition、Artifact、Entry、Fragment、Party 和 Relationship 引用检查；
6. Embedded Provenance 的 Entry、Fragment、Source Mapping 与摘要检查，或 External Receipt 的 Disclosure Approval 检查；
7. `body_byte_digest`、`visible_text_digest` 与 `structure_digest` 检查；
8. Fidelity Coverage Map 的 Binding / Unit 闭包、范围覆盖、排序、重叠 Review 与 Full / Attested 投影检查；
9. Structured Extraction 的 JSON Pointer、Value Digest、Provenance、映射规则与冲突检查；
10. 忠实转写可见文本和结构往返检查；
11. 不允许的 HTML 与可执行内容检查；
12. Index 重建一致性检查。
