# Schema 提案

状态：Draft  
目标实现标准：JSON Schema Draft 2020-12

## 1. 设计原则

LoreBuddy 使用“核心 Envelope + 命名空间化 Profile”的 Schema 架构。

核心 Schema 只定义跨 TRPG 稳定成立的结构。具体系统的法术、职业、怪物数据或检定机制由 Package Schema 定义。

设计目标：

- 平台核心不绑定 D&D；
- 新系统可以增加 Profile，而不修改核心 Node Schema；
- 不同系统的同名概念不会被误认为同一数据模型；
- Schema 可以独立版本化和显式迁移；
- YAML Front Matter 与 JSON 记录使用同一验证语义；
- 100,000 个以上 Node 可以流式验证。

## 2. 未采用“万能 TRPG Schema”

Spell、Monster、Class、Condition 在不同系统中并不共享稳定语义：

- PF2e Spell 有 Action、Trait、Tradition、Heightening 等模型；
- D&D 5e Spell 使用 Level、School、Components、Concentration 等模型；
- Call of Cthulhu 不以同一种 Spell/Monster/Class 体系组织规则；
- Shadowrun 的角色、装备与法术受版本和子系统影响；
- 叙事型或原创系统可能完全没有这些概念。

如果平台建立一个包含所有字段的通用 Spell 或 Monster Schema，结果要么充满无意义可选字段，要么把 D&D 语义错误投射到其他系统。

替代设计是保持小型核心，把确实跨多个系统稳定复用的能力在获得证据后逐步提升到 Core。

## 3. Schema 分层

```text
schemas/
    core/
        package-manifest.schema.json
        package-lock.schema.json
        knowledge-node.schema.json
        party.schema.json
        public-party-projection.schema.json
        evidence.schema.json
        public-evidence-receipt.schema.json
        source-work.schema.json
        source-edition.schema.json
        source-artifact.schema.json
        source-entry.schema.json
        source-fragment.schema.json
        source-mapping.schema.json
        provenance-locator.schema.json
        boundary-decision.schema.json
        visibility-decision.schema.json
        fidelity-coverage-map.schema.json
        fidelity-record.schema.json
        structured-extraction-record.schema.json
        navigation-occurrence.schema.json
        semantic-navigation.schema.json
        source-reference-occurrence.schema.json
        link-mapping.schema.json
        address-occurrence.schema.json
        address-mapping.schema.json
        relationship.schema.json
        disclosure-profile.schema.json
        access-domain.schema.json
        access-policy.schema.json
        access-decision-receipt.schema.json
        rights-authority-domain.schema.json
        rights-authority-delegation.schema.json
        rights-claim.schema.json
        rights-decision.schema.json
        rights-target-candidate-lock.schema.json
        release-rights-binding.schema.json
        disclosure-approval.schema.json
        public-provenance-receipt.schema.json
        public-build-attestation.schema.json
        public-fidelity-attestation.schema.json
        public-rights-attestation.schema.json
        audit-binding.schema.json
        release-payload.schema.json
        release-archive-metadata.schema.json
        extraction-receipt.schema.json
        analysis-receipt.schema.json
        source-path-map-record.schema.json
        issue.schema.json
        exception.schema.json
        review.schema.json
        redirect.schema.json
        tombstone.schema.json
        index-manifest.schema.json
        index-build.schema.json
        index-output-manifest.schema.json
        release-manifest.schema.json
        asset-record.schema.json
        asset-usage.schema.json

    profiles/
        rule.schema.json
        reference-entry.schema.json
        narrative-entity.schema.json
        event.schema.json

packages/<namespace>/<package>/schemas/
    <package-namespace>/
        ...
```

### 3.1 Core Schema

Core Schema 定义基础协议和可追溯结构，必须保持系统中立。

### 3.2 Core Profile

Core Profile 对 Node Envelope 增加跨系统较稳定的语义约束，但不假设具体规则字段。

### 3.3 Package Profile

Package Profile 定义系统、世界或数据源特有结构，例如：

```text
dnd5e.spell@0.1.0
dnd5e.creature-stat-block@0.1.0
pf2e.spell@0.1.0
coc7e.investigator-occupation@0.1.0
```

Package Profile 的标识必须包含命名空间，并在 Package Manifest 中声明。

### 3.4 标识与解析协议

LoreBuddy 区分四种标识：

| 类别 | 形式 | 职责 |
|---|---|---|
| 实体身份 | `urn:uuid:<uuidv7>` | Package、Node、Work、Edition、Party、Entry、Fragment、Relationship 等稳定身份 |
| Schema / Registry Document ID | `<namespace>.<name>@<semver>` | 解析到已锁定的本地 Schema 或一份版本化注册表文档，例如 `core.knowledge-node@0.1.0`、`core.relationship-types@0.1.0` |
| Vocabulary Term ID | 命名空间化稳定词项，不带文档版本 | Node Kind、Relationship Predicate、System、Ruleset 等词项，例如 `core.rule`、`core.corrects`、`dnd.5e-2014` |
| 可导航 URI | `lorebuddy://node/<uuid>` 等 | Markdown 中的稳定导航表达，可确定性还原实体 URN |

`package.lock.json` 必须把每个 Schema / Registry Document ID 映射到本地相对路径与 SHA-256，并锁定每个 Vocabulary Term 来自哪份 Registry Document。构建器禁止通过网络解析，也禁止两个依赖对同一完整 Document ID 提供不同摘要。

Vocabulary Term ID 的语义在创建后稳定；注册表升级可以补充显示名、状态或约束，但不兼容的语义必须创建新 Term ID，不能靠给每个使用位置追加 `@semver` 改变含义。这样 Node 中的 `core.rule` 与关系中的 `core.corrects` 保持简洁稳定，同时其定义仍由版本化、带摘要的注册表文档控制。

可导航 URI 不是新的实体身份：`lorebuddy://node/<uuid>` 必须机械映射为 `urn:uuid:<uuid>`。没有 LoreBuddy Runtime 的消费者仍可从 URI 中读取 UUID，并通过 Package Index 查找相对文件。

## 4. 核心 Schema

### 4.1 Package Manifest

职责：声明 Package 身份、版本、适用范围、访问、权利、依赖和扩展。

必须验证：

- UUID ID；
- namespace 与 slug 语法；
- `spec_version`、`package_version`；
- BCP 47 语言；
- 系统与 ruleset 注册项；
- Access Policy、Access Domain、Rights Authority Domain、Rights Claim / Decision 与 Disclosure Profile；Manifest 的 `access_domain_id` 必须等于所引 Policy 的 `domain_id`，`rights.authority_domain_id` 不得与它混用，Rights 字段只能保存规范 Claim / Decision / Public Attestation 引用；
- 锁定依赖；
- 必需扩展是否可用。

不包含：Node 列表、Alias 列表或反向关系。这些属于 Index。

#### 4.1.1 Package Lock 与 Source Receipt

`core.package-lock@0.1.0` 是规范构建输入，必须验证 Package ID / Version、封闭的 Dependency 类型 `content | build | provenance | audit-input | claim-source | rights-target`、精确 Package Version / Manifest Digest、Schema / Registry `{id,path,digest}`、工具 `{id,version,digest}` 与启用扩展。`claim-source` 使用当前 / 前驱 Claims Root 与 Lineage；`rights-target` 必须使用 `core.rights-target-candidate-lock@0.1.0` 联合分支，禁止普通 Dependency 的最终 Manifest Digest 字段。Public Lock 和受限完整 Build / Audit Lock 使用同一 Envelope，但由 Rights / Disclosure Validator 限制可披露字段；Lock 禁止网络解析和浮动版本。

Source Complete 还依赖四类机器契约：

- `core.extraction-receipt@0.1.0`：Artifact Digest、Extractor ID / Version / Binary Digest、完整配置、输出 Inventory / Path Map Digest、结果与交叉实现比对；
- `core.analysis-receipt@0.1.0`：Parser / Recovery / Decoder / CSS Tokenizer / Rule Set 的 ID、Version、Digest、输入 Inventory Digest、统计与阻塞 Issue 摘要；
- `core.source-entry@0.1.0` Inventory：每个容器目录项的原始路径证据、Section / Logical Offset、长度、媒体类型、Entry ID 与 Digest；
- `core.source-path-map-record@0.1.0`：原始 Path Bytes / Decoding、规范安全 Storage Path、冲突与可逆状态。

Receipt 存放于对应 Artifact 的 `receipts/` 并进入 Content Manifest。`inventory.jsonl` 是 `core.source-entry@0.1.0` 的规范记录流与 Entry ID 唯一事实源；`path-map.jsonl` 是从 Inventory 确定性生成的 `core.source-path-map-record@0.1.0` 投影，不得出现 Inventory 中不存在的 Entry 或不同字段值。两者都使用确定性 JSONL，并由 Extraction Receipt 锁定摘要。运行时间和性能数据仍进入 `reports/`，不能混入规范 Receipt 摘要。

### 4.2 Knowledge Node Envelope

职责：验证所有 Node 共有字段：

- `schema`；
- `id`；
- `package_id`；
- `kind`；
- `title`、`language`、`aliases`；
- `applicability`；
- `content`；
- `responsibility`；
- `authority_claims`；
- `normativity_claims`；
- `provenance`；
- `structured_extractions`；
- `tags`；
- 简单 `relationships`；
- `lifecycle`；
- `extensions`。

核心 Envelope 不包含法术环位、AC、职业等级、技能名称或 D&D Ability Score。

Package、Node、Normativity Claim 与 Relationship 复用同一 `core.applicability` 定义。每个维度显式使用 `known | unknown | not-applicable`；`systems.values[]` 的固定形状为 `{system, rulesets[]}`，不允许同一语义在不同文件中切换单数/复数字段。

### 4.3 Party

职责：为作者、出版者、翻译者、转写者、审核者和私有记录创建者提供统一引用。

Party 可以表示 person、organization、collective 或明确的 unknown。它只表达责任主体身份，不等同于世界内 NPC，也不进入叙事实体模型。完整规范 Record 存放于 `metadata/parties/records/`，每个 ID 在一个 Access Domain 中只有一个事实源。每个字段必须标注 `public | domain-restricted | secret-reference`。本来就可公开的 Party 可以直接存在于 Public Package；受限 Party 不得用同一 ID 制作删字段副本，而必须在公开 Package 的 `metadata/parties/public-projections/` 创建随机新 ID 的 `core.public-party-projection@0.1.0`，只含 Disclosure Profile 批准的公开 Label / Role、Approval 引用和 Lifecycle。公开责任字段引用这个 Public ID；受限 Audit Binding 再把它映射到私有 Party `{id,digest}`。

### 4.3.1 Evidence Record

`core.evidence@0.1.0` 为 `evidence_ids[]` 提供统一、可解析的完整规范目标，存放于 `metadata/evidence/records/`。最小字段包括 Evidence ID、注册的 `kind`、`subject`、一个或多个带类型的 Locator / Record Reference、可验证时的 `{algorithm,digest}`、Access Domain、Rights Claim 引用、Review 与 Lifecycle。Secret、Credential、合同原文或个人信息不得直接内嵌；只能引用同一可读 Access Domain 中的受控对象。

```yaml
schema: "core.evidence@0.1.0"
id: "urn:uuid:..."
kind: "core.source-record-reference"
subject:
  kind: "rights-claim"
  id: "urn:uuid:..."
references:
  - kind: "source-fragment"
    id: "urn:uuid:..."
    locator: null
verification:
  algorithm: "sha256"
  digest: "sha256:..."
access_domain_id: "urn:uuid:..."
rights_claim_ids: []
review:
  status: "approved"
  review_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

所有 `evidence_ids[]` 必须解析到 Active `core.evidence@0.1.0`，或 `metadata/evidence/public-receipts/` 中的 `core.public-evidence-receipt@0.1.0`，不能直接混用任意 Fragment、URL、Review 或其他 Attestation ID。Evidence Record 可以再引用这些对象并明确引用类型。本来可公开的 Evidence 可以直接发布；受限 Evidence 必须创建随机新 ID 的 Public Evidence Receipt，只保存公开 Subject、审核声明、Disclosure Profile / Approval 和 `traceability: attested`，不得包含私有 Evidence ID / Digest / Locator。Audit Binding 固定 Public Receipt `{id,digest}` 到私有 Evidence / Review 的映射。这样每个 ID 仍只有一个规范 Record，公开引用也不会泄漏私有 ID。

```yaml
schema: "core.public-party-projection@0.1.0"
id: "urn:uuid:..."
kind: "pseudonymous-party"
display_label: "公开审核方"
public_roles: []
disclosure_profile:
  id: "core.party-public-minimal@0.1.0"
  digest: "sha256:..."
disclosure_approval_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

```yaml
schema: "core.public-evidence-receipt@0.1.0"
id: "urn:uuid:..."
issued_for:
  subject_kind: "relationship"
  subject_id: "urn:uuid:..."
claim: "restricted-evidence-reviewed"
traceability: "attested"
disclosure_profile:
  id: "core.evidence-public-minimal@0.1.0"
  digest: "sha256:..."
disclosure_approval_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

两个 Public Record 的 UUID 都随机分配，不能由私有 Party / Evidence ID 或 Digest 派生；其 Disclosure Approval 与 Audit Binding 按第 4.12 节及权利发布规范验证。

### 4.4 Source Work

职责：描述抽象作品及稳定外部标识。

建议字段：

```yaml
schema: "core.source-work@0.1.0"
id: "urn:uuid:..."
titles: []
creators: []
publishers: []
work_kind: "rulebook"
external_ids: []
authority_claims: []
rights_claim_ids: []
lifecycle:
  status: "active"
  revision: 1
```

`authority_claims` 是 Work 自身的断言；`rights_claim_ids` 只保存到 `metadata/rights/claims/` 规范记录的引用，不能内嵌另一份权利事实。

### 4.5 Source Edition

职责：描述特定语言、修订和出版表达。

建议字段：

```yaml
schema: "core.source-edition@0.1.0"
id: "urn:uuid:..."
work_id: "urn:uuid:..."
language: "zh-Hans"
edition_label: "..."
revision: "..."
published_on: null
publisher: null
translation:
  status: "unknown"
  source_edition_id: null
external_ids: []
relationships: []
rights_claim_ids: []
verification: "claimed"
lifecycle:
  status: "active"
  revision: 1
```

### 4.6 Source Artifact

职责：描述实际摄取字节。

建议字段：

```yaml
schema: "core.source-artifact@0.1.0"
id: "urn:uuid:..."
original_filename: "DND五版不全书26.06.30.chm"
media_type: "application/vnd.ms-htmlhelp"
format: "chm"
size: 36787743
digest: "sha256:836eea..."
acquisition: {}
container_metadata: {}
extraction:
  tool: "7-Zip"
  tool_version: "26.02"
  status: "provisional"
rights_claim_ids: []
```

### 4.7 Source Entry

职责：描述 Artifact 内一个资源及其无损存储映射。

建议字段：

```yaml
schema: "core.source-entry@0.1.0"
id: "urn:uuid:..."
artifact_id: "urn:uuid:..."
original_path: "/玩家手册/施法/专注.htm"
original_path_bytes:
  encoding: "base64"
  value: "L+eOqeWutuaJi+WGjC/mlr3ms5Uv5LiT5rOoLmh0bQ=="
original_path_decoding:
  charset: "utf-8"
  status: "exact"
directory_record_digest: "sha256:..."
storage_path: "entries/..."
size: 12345
digest: "sha256:..."
media_type:
  declared: "text/html"
  detected: "text/html"
charset:
  declared: "gb2312"
  decoded_as: "gbk"
container_location:
  section: 1
  section_logical_offset: 0
  uncompressed_length: 12345
extraction_status: "complete"
issues: []
```

`original_path_bytes` 是路径身份的规范证据，使用 RFC 4648 Base64；`directory_record_digest` 固定原始目录记录。`original_path` 只是按 `original_path_decoding` 得到的 Unicode 视图；无法严格解码时状态为 `failed`，不得用替换字符伪造可逆路径。`storage_path` 必须与二者分开，确保路径重写可逆且安全。面向显示的路径必须另存。

每个 Source Entry Record 作为一行存放于所属 Artifact 的 `inventory.jsonl`；该流是 Entry ID 和上述字段的唯一规范定义。`entries/` 中的文件只由 `storage_path` 指向，`path-map.jsonl` 只投影 `{entry_id, original_path_bytes, original_path_decoding, storage_path, collision_status}`，不得独立修改路径事实。

CHM 压缩 Section 中的 Offset 是 LZX 解压逻辑流坐标，不是原 CHM 文件的物理 byte offset，必须使用 `section_logical_offset` 命名，禁止误称 `file_offset`。

### 4.8 Source Fragment 与 Provenance Locator

Source Fragment Record 是 Fragment ID 的唯一规范定义，存放于 `metadata/fragments/<shard>/<uuid>.yaml`。Locator 只是该记录中的可复用坐标结构，不单独承担实体身份。

建议结构：

```yaml
schema: "core.source-fragment@0.1.0"
id: "urn:uuid:..."
entry_id: "urn:uuid:..."
entry_digest: "sha256:..."
locator:
  schema: "core.provenance-locator@0.1.0"
  anchor: null
  navigation_occurrence_ids: []
  navigation_paths: []
  heading_path: []
  entry_raw_byte_ranges:
    - start: 0
      end: 0
  decoded_text:
    encoding: "gbk"
    coordinate: "unicode-scalar-value"
    ranges:
      - start: 0
        end: 0
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
source_event_stream:
  path: "metadata/fragments/00/<uuid>.events.jsonl"
  records: 1
  bytes: 42
  file_digest: "sha256:..."
decision_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

约束：

- Source Fragment 的 `id`、`entry_id`、`entry_digest`、`locator`、版本化 `fragment_digest` 与 Boundary Decision 必填；
- `source_event_stream.bytes` 与 `file_digest` 只覆盖磁盘上精确 JSONL bytes，不含虚拟 Domain Prefix；`fragment_digest.value` 才是对 Prefix + 同一 JSONL bytes 计算的协议语义摘要。两者禁止共用泛名 `digest`；
- Locator 至少包含一种精确定位信息；
- 所有 Range 使用半开区间 `[start, end)`；
- `entry_raw_byte_ranges` 以解包后、尚未解码的 Entry 原始 byte 为坐标；
- `decoded_text.ranges` 以 Decoder 输出的 Unicode Scalar Value 序号为坐标，并记录所用编码；
- Text Quote 保留原字符，不进行 Unicode 规范化；
- DOM Selector 必须记录 Parser、Parser 版本和 Selector Language，因为恢复型 Parser 可能产生不同树；
- `navigation_occurrence_ids` 可以有多个，以表达 HHC 重复挂载；显示路径只作辅助快照。

已发布 Fragment Record 的 Entry 或选择范围不可原地改变；范围变化创建新 ID。Node Provenance 中若嵌入 Locator 快照，验证器必须确认其与 Source Fragment Record 一致。

`fragment_digest`、可见文本与结构摘要的规范字节算法及测试向量见[完整性与事件协议](integrity-protocols.md)；Schema 只验证协议 ID 和 Digest 形状，不能自行发明另一套归一化。

### 4.9 Source Mapping、Boundary 与 Occurrence

Source Mapping Record 连接实际证据与声称出版来源：

```yaml
schema: "core.source-mapping@0.1.0"
id: "urn:uuid:..."
subject:
  kind: "fragment"
  id: "urn:uuid:..."
target:
  kind: "unresolved"
  id: null
claim_status: "unknown"
evidence_ids: []
review:
  status: "pending"
  review_id: null
lifecycle:
  status: "active"
  revision: 1
```

`target.kind: unresolved` 时 `id` 必须为 `null`；其他 Target 必须存在。Node Provenance 引用稳定 Mapping ID，不能直接复制一个未经审核的 Edition 结论。

Boundary Decision、Source Navigation Occurrence 与 Source Reference Occurrence 都是规范 Metadata Record，不只存在于派生 Index：

- `metadata/parties/records/` 与 `public-projections/`：完整责任主体，以及使用随机新 ID 的公开投影；
- `metadata/evidence/records/` 与 `public-receipts/`：完整 Evidence，以及不泄漏私有身份的公开 Attested Receipt；
- `metadata/boundaries/`：候选、决定、Reviewer、Fragment ID 与 Node ID；
- `metadata/navigation/source-occurrences/`：HHC/HHK 中每个挂载位置的稳定 ID、父 ID、Ordinal、原始 Name / Local、Parser Evidence；
- `metadata/references/occurrences/`：Entry 内每个 Anchor / Link / Image / Resource Attribute 的稳定 Raw Occurrence、原始值与 Locator；
- `metadata/links/mappings/`：Source Reference Occurrence 到最终 Node / Source Entry / External / Missing 目标的审核映射；
- `metadata/addresses/occurrences/`、`metadata/addresses/mappings/`：包装一个 Raw Reference Occurrence 的 Semantic Anchor / Footnote 身份、最终 ID 与稳定 Equivalence ID；
- `metadata/assets/records/`：Library Asset 的内容摘要、MIME、尺寸、Source Entry、变换与 Rights 引用；`usages/` 保存其在 Node 中每次出现的稳定 ID、上下文和 Source Reference Occurrence；
- `metadata/visibility-decisions/`：页面族或具体子树的 `visible | hidden | unknown` 裁决、范围、规则版本、Reviewer 与 Evidence；
- `metadata/navigation/semantic/`：人工维护的语义导航身份、父子关系和稳定 `sibling_ordinal`；Index 只投影；
- `metadata/fidelity/`：Node、Fragment、正文范围、事件协议、Source / Library 可见文本摘要、结构投影摘要，以及所用 Link / Address Mapping、Visibility Decision、Exception 的 `{id,revision,digest}` 引用与最终 Pass / Fail；Mapping 本体仍只位于 `metadata/links/mappings/` 或 `metadata/addresses/mappings/`；
- `metadata/structured-extractions/`：Front Matter / Extension 字段的 JSON Pointer、Value Digest、Provenance、映射规则、抽取器与审核结论；
- 受限 Audit Package 的 `metadata/audit-bindings/`：Public Receipt / Attestation ID 到私有 Fragment、Mapping、Review、Decision、Build Lock 与目标 Release 的完整映射。

Reference 与 Address 使用两层模型。`core.source-reference-occurrence@0.1.0` 只固定 Raw Attribute 事实，不携带后续语义；Link Mapping 与 `core.address-occurrence@0.1.0` 都只绑定该 Raw Record 的 `{id,revision,digest}`，禁止复制 Entry、Ordinal 或 Raw Value。Address Occurrence 通过 `base_reference: {id,revision,digest}` 包装为 `anchor | footnote-ref | footnote-body`，再由 `core.address-mapping@0.1.0` 以 Address Occurrence 的 `{id,revision,digest}` 固定最终 Markdown 身份。已进入转换范围的每个 `<a href>` Source Reference 必须恰好由一条 Active 普通 Link Mapping 或一条 Active `footnote-ref` Address Occurrence 消费；每个 Image / Resource Source Reference 必须恰好由一条 Active Link Mapping 消费；每个 `id` / `name` Source Reference 必须恰好由一条 Active `anchor` 或 `footnote-body` Address Occurrence 消费。零消费和双重消费都以 `REFERENCE_CONSUMPTION_CONFLICT` 阻塞；不得因 Footnote 分类重复发出普通 Link / Anchor。

Fidelity Record 的最小形状为：

```yaml
schema: "core.fidelity-record@0.1.0"
id: "urn:uuid:..."
node_id: "urn:uuid:..."
node_revision: 1
assertion_id: "urn:uuid:..."
body_byte_digest: "sha256:..."
coverage_map:
  algorithm: "core.fidelity-coverage-map@0.1.0"
  bindings:
    - provenance_id: "urn:uuid:..."
      fragment:
        id: "urn:uuid:..."
        revision: 1
        source_event_stream:
          records: 100
          file_digest: "sha256:..."
          semantic_digest: "sha256:..."
      units:
        - id: "urn:uuid:..."
          body_utf8_ranges:
            - start: 0
              end: 1234
          source_fragment_event_ranges:
            - start_record: 8
              end_record: 37
          comparisons:
            visible_text:
              algorithm: "core.visible-text-events@0.1.0"
              source_before_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              library_before_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              source_after_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              library_after_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              result: "equal"
            structure:
              algorithm: "core.structure-events@0.1.0"
              source_before_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              library_before_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              source_after_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              library_after_exceptions:
                path: null
                records: 1
                bytes: 42
                file_digest: "sha256:..."
                semantic_digest: "sha256:..."
              result: "equal"
          link_mapping_refs: []
          address_mapping_refs: []
          visibility_decision_refs: []
          exception_refs: []
          result: "passed"
result: "passed"
review:
  status: "approved"
  review_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

每个 Binding 只对应一个 Node Provenance；Full 模式的 `fragment` 必须逐字段匹配该 Embedded Provenance 与规范 Fragment Record。`source_fragment_event_ranges` 使用 Fragment JSONL 中从 0 开始的半开 Record Index，与 Entry 级 `source_event_ordinal` 不是同一坐标。Range 必须非空、有序、不重叠、不越界，并保持 Container Enter / Exit 平衡；若边界落在一个 Text Event 或 Markdown AST 语义节点内部，v0.1 必须建立更精确 Fragment / Unit 或阻塞，不能近似扩大。

Unit 的多个 Source Range 与多个 Body Range 分别按来源顺序拼接成“序列对序列”的一个对应组，每个 Unit 独立生成比较事件。四个 Event Descriptor 必须各自完整序列化，禁止 Anchor / Alias。Descriptor 的 `bytes` 与 `file_digest` 排除虚拟 Domain Prefix；`semantic_digest` 包含各自算法 Prefix。`path` 为规范事件流相对路径或 `null`；即使完整流只在 Report 中，记录数与两种摘要仍必填并可通过重建验证。Mapping / Decision / Exception Ref 都使用 `{id,revision,digest}` 并按 ID 排序；Range 按起点、终点排序。只有所有 Unit 的 After-Exception 两侧语义摘要相等、引用 Active 且覆盖闭包一致时，顶层 `result` 才能是 `passed`。

首次持久化时为 Record 分配 UUIDv7；确定性 Candidate / Occurrence Key 只用于重跑匹配，不充当实体 ID。Key 的规范算法由完整性协议定义。

Knowledge Node 的 `provenance[]` 必须使用 JSON Schema `oneOf` 区分 `embedded-fragment` 与 `external-public-receipt`。前者要求 Fragment / Mapping / Locator，后者要求 Public Receipt、Disclosure Approval 和 `traceability: attested`，并通过 `unevaluatedProperties: false` 禁止受限 Locator 字段混入公开分支。公开 Receipt 与 Build Attestation 的字段规则见[权利、访问与发布规范](rights-release-spec.md)。

`content.fidelity_evidence.assertions[]` 的每一项使用 `oneOf`：`full` 必须且只能引用 `fidelity_record_id`；`attested` 必须且只能引用 `fidelity_attestation_id + fidelity_attestation_digest`。两者都固定公开 `coverage_map`；其每个 Binding 只绑定一个 Provenance，每个稳定 Unit 明确列出正文 Range。Full Record 在相同 Map 上增加 Fragment、Source Event Record Range 和逐 Unit 比较；Public Attestation 只能保留公开投影。顶层保存计算得到的 `aggregate_mode` 与排序后的 `overlap_review_ids[]`，跨 Provenance / Unit 覆盖、重叠审批和聚合由语义 Validator 检查。`content.fidelity_target` 是独立枚举，只表示 Markdown 正文目标，不得与 Evidence 对象或 Structured Extraction 复用字段名。Attested 分支不得携带 Fragment、Source Event Range、Mapping 或受限摘要。

### 4.10 Relationship

职责：表达带类型、方向、范围和证据的断言。

```yaml
schema: "core.relationship@0.1.0"
id: "urn:uuid:..."
predicate: "core.corrects"
source: "urn:uuid:..."
target: "urn:uuid:..."
scope:
  systems:
    status: "unknown"
    values: []
  settings:
    status: "unknown"
    values: []
  campaigns:
    status: "unknown"
    values: []
effective_from: null
effective_until: null
assertion:
  basis: "source-explicit"
  evidence_ids: []
lifecycle:
  status: "active"
  revision: 1
```

只有需要独立生命周期、范围或 Provenance 的关系才创建独立记录。普通 `references` 可以内嵌在 Node。

独立 Relationship 的 `id` 就是该断言的稳定 Assertion ID；内嵌关系也必须有同样语义的稳定 `id`。生成索引时统一输出为 `assertion_id`，不得按数组位置或三元组临时生成身份。

### 4.11 Issue、Exception 与 Review

职责：保存人工治理事实，而不是构建日志。

- Issue 使用稳定 UUID `issue_id` 聚合一个或多个确定性 `issue_key`，并记录状态、证据和 Resolution；
- Exception 必须限定适用 Artifact、Entry、Fragment、规则版本和失效条件；
- Review 保存审核对象、结论、责任 Party、依据与审核时间。

三者属于 `metadata/` 并进入 Content Manifest。自动检测明细与运行性能留在 `reports/`，不得用 Report 代替人工裁决。

### 4.12 Access、Rights 与 Public Attestation

- `core.access-domain@0.1.0`：定义可读取内容的安全域身份；Package Manifest 的 `access_domain_id` 必须与所引 Access Policy 的 `domain_id` 相等；
- `core.access-policy@0.1.0`：定义特定 Access Domain 的允许 Principal；Visibility 不承担跨私有域授权；外部 Policy 引用必须固定不可变 Version 与 Digest；
- `core.access-decision-receipt@0.1.0`：在受限 Audit / Build Package 中固定 Principal、Dependency Domain、Policy Version / Digest、构建 Lock 与判定结果；
- `core.rights-authority-domain@0.1.0`：定义可签发 Rights Claim / Decision / Binding 的治理域身份；它与 Access Domain 正交，不能授予读取权限；
- `core.rights-authority-delegation@0.1.0`：固定被委托 Party / Package、`issue-claim | withdraw-claim | issue-decision | issue-binding` Capability、Subject / Action Scope 与有效期；Claim Source 和 Audit Package 都必须使用它证明签发权限；
- `core.disclosure-profile@0.1.0`：版本化 Registry Document，按 Subject Schema 定义默认拒绝的 JSON Pointer 白名单、必需字段与值约束；
- `core.rights-claim@0.1.0`：对保存、提取、格式转换、派生、Source/Transcription/Asset 再分发、Metadata/Receipt 发布分别声明 `allowed | denied | unknown | not-applicable`，并固定 Authority Domain / Delegation / Issuer / Review；未批准或未授权 Claim 只能产生 `unknown`；
- `core.rights-claim-lineage@0.1.0`：要求 Claim / Tombstone Ledger 跨 Package Version 追加，锁定直接前驱 Root；已发布 Record 不得删除、改写或换 Path；
- `core.rights-decision@0.1.0`：从追加式 Claim Source Lineage 扫描全部适用 Claim，固定 Universe / Lineage / Selected Set、Claim Authority Evaluation、语义 Payload Coverage 与逐权限结果；不得包含当前 Release Root、Manifest 或最终 Payload Digest；
- `core.rights-target-candidate-lock@0.1.0`：在受限 Audit Lock 中固定目标 Package Manifest / Lock、Rights Registry 与预分配 ID，明确排除最终 Release / Root / Payload 摘要；
- `core.release-rights-binding@0.1.0`：与所引 Release Decision 共同存在于目标 Release 之外、同一 Rights Authority Domain 的 Audit Package；固定最终 Payload Inventory Digest、Release Manifest Digest 与审核有效期，Audit Package 可以使用不同 Access Domain；
- `core.public-party-projection@0.1.0`：使用随机新 ID 提供最小公开 Party Label / Role，禁止携带私有 Party ID / Digest；
- `core.public-evidence-receipt@0.1.0`：使用随机新 ID 声明受限 Evidence 已审核，Traceability 只能是 `attested`，禁止携带私有 Evidence ID / Digest / Locator；
- `core.public-provenance-receipt@0.1.0`：只允许 Disclosure Profile 白名单字段，不含私有 Package / Fragment / Entry 身份或摘要；
- `core.public-build-attestation@0.1.0`：声明受限构建已审核，并绑定非递归 `library_root_digest`，但不复制受限输入指纹，也不自引用当前 Content / Index Root；
- `core.public-fidelity-attestation@0.1.0`：绑定 Node ID / Revision、Assertion ID、公开 Fidelity Coverage Map 及 Body / Visible / Structure Digest，并声明保真门禁结果；不得复制 Fragment、Source Event Range、Mapping 或受限摘要；
- `core.public-rights-attestation@0.1.0`：内联于 Public Release Manifest，绑定该 Manifest 的 Content / Index Root 与完整 Payload，禁止披露私有 Decision、Claim、Reviewer 或 Evidence ID；
- `core.audit-binding@0.1.0`：只存在于受限 Audit Package，把 Public Receipt / Attestation 映射到完整私有 Evidence、Decision、Lock 与 Release Rights Binding；Public Fidelity 分支还固定 Private Fidelity Record 与公开投影算法；
- `core.release-payload@0.1.0`：定义 Release Archive 文件集合与额外文件失败规则；
- `core.release-archive-metadata@0.1.0`：限制 Entry 类型、路径与 Header；拒绝 Link / Special File、宿主时间、UID / GID、ACL / xattr 和未登记 PAX / ZIP Extra Field。

Rights 与 Access 的跨对象合并超出 JSON Schema 能力，由语义 Validator 按默认拒绝算法执行。Validator 必须扫描包含 Decision Owner / Audit Lock 的 Claim Universe，验证追加式 Claim Lineage、全 Universe Claim ID 与 Package Root 唯一、Claim / Tombstone Authority、Approved Review 和 `claim_inputs[]` 集合全等；Subject Expansion 必须传递覆盖 Artifact 中每个物理 Entry、Fragment Evidence、Edition / Work 与 Asset。发布时还必须检查 `release_binding_id` 已预分配、目标 Manifest 不含 Binding Digest，并逐项执行 `core.release-rights-binding-validation@0.1.0` 的跨 Record 等式；全部 Validity 使用同一显式 `evaluation_as_of`。完整协议见[权利、访问与发布规范](rights-release-spec.md)。

### 4.13 Redirect

职责：保留身份迁移。

支持：

- 一对一替代；
- 一对多拆分；
- 多对一合并；
- 带原因和迁移版本。

Redirect 不表示规则版本取代。规则版本关系使用 `supersedes`、`corrects` 等 Relationship。

### 4.14 Tombstone

职责：记录一个 ID 已撤回且不应重用。

必须包含：原 ID、撤回原因、状态、替代项（如有）、审核记录和生效版本。Tombstone 不得删除原 Git 历史中的内容证据。

### 4.15 Index、Output 与 Release Manifest

职责：分别描述事实文件分片、派生输出摘要与最终发布完整性封条。

Index Manifest 列出 Content File 分片、`content_root_digest` 以及从 `library/` 文件记录计算的非递归 `library_root_digest`；Output Manifest 列出除自身外的 Index 文件和 `index_root_digest`；Release Manifest 固定三个根摘要及其 Manifest 摘要并自排除。Release Manifest 还必须验证 Access Policy `{id,digest}`、Disclosure Profile `{id,digest}`、Rights 的 `direct | public-attestation` 联合类型，以及按 `release-reader` 计算的 Traceability / Fidelity / Reproducibility Aggregate。规范 Manifest 不包含运行时当前时间，以保证确定性。执行时间进入非规范 Run Report。

## 5. Core Profile

### 5.1 `core.rule`

表示规范性或可选规则表达。只约束：

- 必须声明带 Scope 与 Evidence 的 Normativity Claim；
- 必须声明适用范围或明确 unknown；
- transcription 正文必须在当前可读域或授权 Audit Package 中有 Full Provenance；公开投影可以使用明确标记的 Attested Receipt；
- 可以使用已注册的核心版本关系，也可以使用 Package 命名空间中的 prerequisite、exception 等系统关系。

它不定义 D20、Difficulty Class、Action Economy 等机制。

### 5.2 `core.reference-entry`

表示可独立查阅的结构化条目，例如某系统的法术、装备、状态或生物数据块。

Core 只要求：

- 显示标题；
- 来源和适用范围；
- 一个命名空间化 Package Profile；
- 结构化字段属于派生断言，不能取代正文来源。

### 5.3 `core.narrative-entity`

表示世界设定中的实体，例如地点、组织、人物、物件或神祇。

Core 不预设 NPC 属性、阵营、种族或地理坐标。具体世界或系统可以通过 Profile 增加字段。

### 5.4 `core.event`

表示可放入 Timeline 的事件。只提供：

- 参与实体；
- 时间表达原文；
- 可选的历法标识；
- 精确、范围、模糊或未知时间；
- Provenance。

完整跨历法 Runtime 不属于 Milestone 0。

## 6. 用户提出类型的归属建议

| 类型 | 推荐归属 | 原因 |
|---|---|---|
| Rule | `core.rule` | 跨系统可稳定表达规则文本 |
| Spell | Package Profile | 各系统字段和语义不同 |
| Monster | 不进入 Core；优先使用系统 `creature` / `stat-block` Profile | “Monster” 是系统与叙事判断，不是通用数据类型 |
| Class | Package Profile | 等级、特性和进阶机制不通用 |
| Condition | Package Profile | 状态定义、叠加与移除规则不通用 |
| Equipment | `core.reference-entry` + Package Profile | 通用 Envelope 可复用，规则字段不可复用 |
| Item | `core.reference-entry` 或 `core.narrative-entity` + Package Profile | 规则物品与叙事物件是不同语义 |
| Location | `core.narrative-entity` | 基础实体概念通用，地理扩展命名空间化 |
| NPC | `core.narrative-entity` + Package Profile | 叙事实体通用，人物数值与 Campaign 状态不通用 |
| Timeline Event | `core.event` | 可建立最小跨系统事件 Envelope |
| Relationship | Core 独立记录或 Node 内简化边 | 图语义属于平台协议 |
| Campaign | 未来 Package Profile | 当前里程碑不冻结 Campaign 状态模型 |
| Session | 未来 Package Profile | 当前里程碑不冻结日志、事实与回忆边界 |

## 7. D&D 首包的候选 Profile

以下仅作为 Package Schema 候选，不进入平台 Core：

```text
dnd5e.rule
dnd5e.spell
dnd5e.creature-stat-block
dnd5e.class
dnd5e.subclass
dnd5e.species
dnd5e.background
dnd5e.feat
dnd5e.condition
dnd5e.equipment
dnd5e.magic-item
dnd5e.adventure-encounter
```

上列是稳定 Profile Term ID；具体 Schema Document ID 必须带版本，例如 `dnd5e.spell@0.1.0`。

在来源结构审核前不应冻结字段。先从 5～10 个复杂样本验证：

- 字段是否逐字存在于来源；
- 2014 与 2024 是否需要不同 Schema Major 或同 Schema 的不同 Ruleset 约束；
- 结构化字段是否会误导为官方原文；
- 表格、例外、变体和引用能否无损表达。

## 8. 结构化字段的权威边界

从 HTML 提取 `level`、`school`、`armor_class` 等字段属于结构化提取（Structured Extraction），即使值逐字来自来源，也包含字段映射这一编辑断言。

要求：

- 原始正文仍是规范证据；
- `content.fidelity_target` 只描述正文；结构字段通过 Node 的 `structured_extractions[]` 引用独立 Record；
- `core.structured-extraction-record@0.1.0` 固定 Node Revision、目标 JSON Pointer / Value Digest、Fragment Provenance、抽取器与映射规则的 ID / Version / Digest；
- 字段组带 Fragment Provenance，同一 Pointer 只能有一个 Active Record；
- 抽取结果与正文冲突时，以来源证据为准并阻塞发布；
- 不允许为了让 Schema 通过而推测缺失字段。

未采用“结构化字段就是官方真相”的方案，因为字段命名、单位标准化和枚举映射本身都是 LoreBuddy 的解释。

## 9. Relationship Type 注册表

每个谓词至少定义：

```yaml
id: "core.translation_of"
label:
  zh-Hans: "翻译自"
  en: "translation of"
source_kinds: ["*"]
target_kinds: ["*"]
inverse: "core.has_translation"
symmetric: false
transitive: false
provenance_required: true
description: "源节点是目标节点在另一语言中的表达。"
```

核心候选关系：

| 谓词 | 语义注意事项 |
|---|---|
| `core.part_of` | 组合关系，不自动传递规则效力 |
| `core.references` | 弱引用，不表示依赖 |
| `core.depends_on` | 理解或适用所需依赖 |
| `core.applies_to` | 规则或事实适用于目标 |
| `core.conflicts_with` | 对称关系，必须有上下文 |
| `core.translation_of` | 不表示逐字等价 |
| `core.variant_of` | 弱版本/表达关联，不表示取代 |
| `core.revises` | 新表达修订旧表达 |
| `core.corrects` | 明确修正错误 |
| `core.supersedes` | 在指定上下文中取代，不删除旧节点 |
| `core.overrides` | 常用于局部规则或 Campaign 覆盖，必须限定范围 |

`related_to` 可以作为弱兜底，但不能成为主要关系类型，否则 Graph 将失去可计算语义。

## 10. JSON Schema 约束策略

- 使用 Draft 2020-12。
- 所有 Core Object 使用 `additionalProperties: false`。
- 扩展只允许进入 `extensions`，并按 Package 声明动态验证。
- 使用 `$defs` 复用 UUID、Digest、BCP 47、SemVer、Lifecycle 等定义。
- 不用 JSON Schema `format` 作为唯一验证依据；关键格式增加明确 Pattern 和语义 Validator。
- 对关系目标存在性、依赖环、摘要一致性等跨文件规则使用独立 Validator，不能强塞进 JSON Schema。
- Schema 验证错误必须给出 JSON Pointer、文件路径和稳定错误代码。

## 11. Schema 组合

推荐验证顺序：

```text
YAML 子集解析
→ Core Knowledge Node Envelope
→ kind 对应 Core Profile
→ extensions 中声明的 Package Profile
→ 跨文件语义验证
→ Provenance 与正文保真验证
```

不采用依赖 YAML 隐式 Tag 选择 Schema 的方案，因为不同解析器行为不一致，也不利于未知未来工具读取。

## 12. Schema 版本与迁移

- Schema 标识必须包含版本。
- Patch 只允许澄清或收紧不改变有效实例集合的错误；任何实例兼容性变化至少提升 Minor。
- 不兼容字段变化提升 Major。
- 已发布 Schema 文件不可原地改写。
- 迁移器必须显式声明 source schema、target schema 和工具摘要。
- 迁移前后保存报告，并验证 Node ID 与正文摘要默认不变。
- 系统 Profile 的升级不要求平台 Core 同步升级。

## 13. Milestone 0 后的验证样例

在冻结 `0.1` Schema 前，至少建立：

1. 同一规则的 2014 与 2024 两个 Node；
2. 一个中文社区译文与英文来源 Node；
3. 一个 Errata 修正关系；
4. 一个 Campaign House Rule 覆盖官方规则的关系；
5. 一个同名但不同来源的 Alias 冲突；
6. 一个复杂表格节点；
7. 一个跨 Package Source Provenance；
8. 一个 Redirect 拆分案例；
9. 一个私有 Package，验证索引不泄漏；
10. 一个非 D&D 系统 Profile，证明 Core 未被 D&D 字段绑死。
