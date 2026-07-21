# LoreBuddy 知识包规范草案

状态：Draft  
规范版本：`0.1.0`  
适用里程碑：Milestone 0

## 1. 规范目标

知识包（Knowledge Package）是 LoreBuddy 的长期保存、交换、审核和发布单位。

一个合规 Package 必须：

- 能独立说明自己包含什么、来自哪里、适用于什么上下文；
- 能保留实际摄取来源并证明其字节完整性；
- 能把知识拆成稳定、独立、可追溯的节点；
- 能在不依赖数据库或特定 AI 的情况下被读取；
- 能在 100 本以上资料、100,000 个以上节点时继续工作；
- 能确定性生成 Manifest、Alias、Relationship 和 Navigation 等索引；
- 能表达多系统、多规则版本、多语言、多世界和私有 Campaign；
- 能迁移 Schema 而不静默改变官方正文或复用旧 ID。

本规范不定义搜索算法、知识图谱引擎、RAG、Embedding、Agent 或 Runtime。

## 2. 规范用语

本文中的“必须”“禁止”是合规要求；“应该”表示除非有记录充分的例外，否则必须遵循；“可以”表示可选能力。

### 2.1 核心术语

| 术语 | 定义 |
|---|---|
| 知识包（Knowledge Package） | 独立发布、授权、依赖、构建和访问控制的内容边界 |
| 作品（Work） | 抽象作品，例如一本规则书，不绑定语言、印次或文件 |
| 出版版本（Edition） | 特定语言、修订、印次和发布时间的作品表达 |
| 来源工件（Source Artifact） | 实际摄取的不可变字节对象，例如 CHM、PDF、ZIP 或网页快照 |
| 来源条目（Source Entry） | Artifact 内的独立资源，例如 HTML、图片、CSS 或导航文件 |
| 来源片段（Source Fragment） | Entry 内可被复合定位器识别的精确内容范围 |
| 知识节点（Knowledge Node） | 一个语言、版本和权威上下文下的独立语义表达 |
| 来源证据（Provenance） | 从 Node 回溯到 Fragment、Entry、Artifact、Edition 和 Work 的证据链 |
| Profile | 在核心 Node Envelope 上增加特定语义约束的 Schema |
| 派生索引（Derived Index） | 可从事实源完整重建、不得手工编辑的数据结构 |

## 3. 不可变边界

### 3.1 Package 边界

Package 是以下边界的最小共同单位：

- 独立发布和语义版本化；
- 一致的授权与再分发策略；
- 一致的访问控制等级；
- 明确且可锁定的依赖；
- 独立构建、验证和废弃。

规则系统不是 Package 边界。一个 Package 可以只包含一本书、一个社区汇编、一个世界设定或一个私有 Campaign；同一规则系统通常由多个 Package 组合。

#### 未采用：`packages/dnd5e/`

该结构把系统、版本、授权和发布周期绑定在一起。当前 CHM 已同时包含 2014、2024、2025、第三方和模组内容，证明这种边界无法长期保持一致。

### 3.2 Source、Library、Metadata、Index 边界

| 区域 | 是否人工维护 | 是否可重建 | 是否允许修改原始文字 |
|---|---|---|---|
| `sources/artifacts/*/original/`、`entries/` | 登记后不可变 | 否 | 禁止 |
| `sources/artifacts/*/receipts/` | 由锁定流程生成并追加 | 可重新计算，但历史回执保留 | 不保存改写正文 |
| `sources/catalog/` | 人工维护、显式修订 | 否 | 只保存 Work / Edition 身份事实与 Claim |
| `library/` | 是 | 否 | 忠实转写正文禁止改写 |
| `metadata/` | 是 | 否 | 不保存伪装成原文的编辑说明 |
| `schemas/`、`registries/` | 是，发布后不可原地改写同一 Document ID | 否 | 不保存 Source 正文 |
| `index/` | 禁止手工维护 | 是 | 不适用 |
| `reports/` | 仅由流程生成 | 流程可重跑；历史运行事实不可反推 | 不适用 |

`metadata/` 与 `library/` 都是事实源，但职责不同：Library 保存知识表达，Metadata 保存边界、关系、重定向、迁移和审核事实。

## 4. 仓库级结构

```text
AGENTS.md
README.md

spec/
    knowledge-package.md
    markdown.md
    metadata.md
    provenance.md
    relationships.md
    indexes.md
    integrity.md
    rights-and-release.md
    validation.md
    versioning.md

schemas/
    core/
    profiles/

registries/
    systems.yaml
    rulesets.yaml
    node-kinds.yaml
    relationship-types.yaml
    namespaces.yaml
    release-file-roles.yaml
    disclosure-profiles/

packages/
    <namespace>/
        <package-slug>/

docs/
    decisions/
    milestone-0/
```

当前 `docs/milestone-0/` 是设计草案区。确认后，规范性内容应固化到 `spec/`，机器可验证 Schema 应固化到 `schemas/`。

平台级 `spec/`、`schemas/core/` 和 `registries/` 禁止出现 D&D 专属字段或枚举。

## 5. Package 目录结构

```text
packages/<namespace>/<package-slug>/
    package.yaml
    package.lock.json
    release-manifest.json
    AGENTS.md

    sources/
        catalog/
            works/
            editions/
        artifacts/
            <artifact-key>/
                artifact.yaml
                original/
                entries/
                receipts/
                    extraction.json
                    analysis.json
                inventory.jsonl
                path-map.jsonl

    library/
        nodes/
            <kind>/
                <shard>/
                    <slug>--<uuid>.md
        assets/
            sha256/
                <prefix>/
                    <digest>.<ext>

    registries/
        disclosure-profiles/

    metadata/
        parties/
            records/
            public-projections/
        evidence/
            records/
            public-receipts/
        fragments/
        boundaries/
        fidelity/
        structured-extractions/
        source-mappings/
        relationships/
        navigation/
            source-occurrences/
            semantic/
        references/
            occurrences/
        links/
            mappings/
        addresses/
            occurrences/
            mappings/
        assets/
            records/
            usages/
        visibility-decisions/
        provenance-receipts/
        attestations/
        audit-bindings/
        policies/
            access-domains/
            access/
        rights/
            authority-domains/
            authority-delegations/
            claims/
            decisions/
            release-bindings/        # 仅受限 Audit Package；不得进入被绑定 Release
        disclosures/
            approvals/
        issues/
        exceptions/
        reviews/
        tag-candidates/
        redirects/
        tombstones/
        vocabularies/
        migrations/

    schemas/
        <package-namespace>/

    index/
        manifest.json
        output-manifest.json
        build.json
        files/
        nodes/
        aliases/
        relationships/
        provenance/
        navigation/
        assets/
            records/
            usages/

    reports/
        inventory/
        conversion/
        validation/
        migration/
```

`sources/catalog/` 不保存会从 `pending` 原地变为 `approved` 的映射。Work / Edition Record 的修正通过显式 Revision 和 Package Version 发布；原始 Artifact 字节不受影响。Entry / Fragment 到出版来源的可变审核断言统一进入 `metadata/source-mappings/`。

`sources/artifacts/.../receipts/` 保存达到 Source Complete 所必需的机器回执，包括锁定的提取/分析工具、配置、规则和结果摘要；它们属于长期来源证据并进入 Content Manifest。`metadata/issues/` 保存已经进入人工治理流程的问题事实；`metadata/exceptions/` 保存批准的例外及其范围；`metadata/reviews/` 保存审核结论。检测日志、性能数据和临时差异进入 `reports/`。报告可以重建或丢弃，机器回执与人工裁决不得只存在于报告中。

`metadata/parties/records/` 与 `metadata/evidence/records/` 分别保存当前 Access Domain 的完整 Party / Evidence；本来可公开的完整 Record 也使用这些目录。受限对象不得以同一 ID 复制删字段版本到 Public Package；公开侧必须在 `metadata/parties/public-projections/` 或 `metadata/evidence/public-receipts/` 创建随机新 ID、经 Disclosure Approval 的规范 Public Record，并由受限 Audit Binding 映射回私有 `{id,digest}`。`evidence_ids[]` 只能引用完整 Evidence 或 Public Evidence Receipt，不能直接塞入任意 Fragment、URL、Review 或私有 ID。

`metadata/rights/authority-domains/` 保存权利治理域（Rights Authority Domain）身份；`authority-delegations/` 声明哪个 Party / Package 在什么 Subject / Action Scope 内拥有 `issue-claim | withdraw-claim | issue-decision | issue-binding` Capability。Claim Source 与 Audit Package 都必须由受限 Audit Context 锁定相应 Delegation；它们不授予读取权限，不能替代 Access Policy。`metadata/rights/release-bindings/` 只允许出现在受限 `core.audit` Package。Release Rights Binding 固定另一个目标 Release 的最终 Manifest 与 Payload 摘要；若它进入被绑定 Package 的 Content、Index 或 Archive，会形成不可计算的自引用，Validator 必须直接拒绝。

`release-manifest.json` 是生成的发布完整性封条，分别固定事实源的 `content_root_digest`、Library 子集的 `library_root_digest` 与派生索引的 `index_root_digest`，但不把自身纳入摘要。它同时声明显式 `evaluation_as_of`、Release Payload 白名单、Access Policy、Rights Authority Domain、Disclosure Profile 和按当前 Reader 视角计算的 Assurance；Public Release 只内联不泄漏私有 Claim / Reviewer 的 Public Rights Attestation，不引用受限 Rights Decision。两种发布模式都只携带预分配的 `release_binding_id`，不携带外部 Binding Digest。它不提供发布者身份认证。具体算法见索引规范与[权利、访问和发布规范](rights-release-spec.md)。

### 5.1 为什么使用 `<namespace>/<package-slug>`

- `namespace` 表示维护责任域，避免不同来源使用相同 slug。
- `package-slug` 便于人工浏览，但不承担永久身份。
- Manifest 中的 UUID 才是 Package 身份，目录移动不改变依赖关系。

替代方案是反向域名形式的单目录，例如 `com.example.package`。它更扁平，但对本地团队和私有 Package 不够直观，而且域名所有权变化会产生误导。

### 5.2 为什么对 Node 分片

100,000 个文件放在同一目录会影响 Git、文件监视器、编辑器和部分文件系统。节点按 `kind` 和 `SHA-256(node-id)` 首字节分片，可以保持目录规模稳定。

禁止直接使用 UUIDv7 的高位前缀分片。UUIDv7 高位包含时间，批量创建的 Node 会集中在相同前缀，形成目录热点。

分片只影响存储位置，不参与节点语义。任何引用都必须使用 Node ID，不得使用相对路径作为永久引用。

## 6. Package Manifest

`package.yaml` 是 Package 的人工维护入口。建议最小结构：

```yaml
schema: "core.package-manifest@0.1.0"

id: "urn:uuid:019f0000-0000-7000-8000-000000000001"
namespace: "community"
slug: "dnd5e-cn-compendium-20260630"
title: "DND 5E 不全书 20260630 摄取包"

spec_version: "0.1.0"
package_version: "0.1.0"
package_kind: "core.acquisition"

languages:
  - "zh-Hans"

applicability:
  systems:
    status: "known"
    values:
      - system: "dnd"
        rulesets:
          - "dnd.5e-2014"
          - "dnd.5e-2024"
  settings:
    status: "unknown"
    values: []
  campaigns:
    status: "not-applicable"
    values: []

access:
  visibility: "restricted"
  access_domain_id: "urn:uuid:..."
  policy_id: "urn:uuid:..."

rights:
  mode: "direct"
  authority_domain_id: "urn:uuid:..."
  claim_ids: []
  decision_id: null
  notes: "逐 Work / Edition 审核前不得对外发布。"

dependencies: []

extensions:
  required: []
  optional: []
```

### 6.1 字段约束

- `id`：创建后永久不变，使用 UUIDv7 的 `urn:uuid:` 表达。
- `namespace` 与 `slug`：可读定位，不是身份。
- `spec_version`：Package 遵循的 LoreBuddy 规范版本。
- `package_version`：Package 自身发布版本，使用 SemVer。
- `package_kind`：来自注册表，例如 `core.acquisition`、`core.rules`、`core.setting`、`core.campaign`、`core.audit`、`core.build`。Audit / Build Package 仍是普通受限 Package，必须有自己的 Manifest、Access Domain、Content Manifest 和版本，不能成为目录外的隐藏证据仓。
- `languages`：BCP 47 列表。
- `applicability`：显式声明系统、规则版本、世界和 Campaign；不得从目录名推断。
- `access`：引用 Access Policy；`visibility` 至少支持 `public`、`restricted`、`private`，但不同私有域不能按字符串比较权限。
- `rights`：`authority_domain_id` 标识权利治理域，不得与 Access Domain 混用。Release 动作的 Decision 与 Binding 共同存在于目标 Release 之外、具有有效 Authority Delegation 的受限 Audit Package；Direct 模式可在 Release Manifest 引用其 Decision，公开派生包只能使用 `mode: public-attestation` 与预分配的 `public_rights_attestation_id`，不得复制私有 Decision ID。没有 Active Decision 时机器结果固定为 `unknown`。最终 Release 携带预分配 `release_binding_id`，但不得携带 Binding Digest。自由文本不替代审核。
- `dependencies`：只允许引用明确版本或 Lock 中的内容摘要。

### 6.2 Package Lock

`package.lock.json` 锁定：

- 依赖 Package 的类型、ID、精确版本和 Manifest 摘要；受限 Audit Context 还为 `claim-source` 项锁定当前 / 前驱 Claims Root 与 Lineage，为 `rights-target` 使用不含最终 Release 摘要的 Target Candidate Lock；
- Schema 与注册表摘要；
- 构建工具链版本；
- 可选扩展的启用状态。

构建过程不得解析网络上的“最新版”。Lock 变化必须是显式评审变更。

以上是同一 Access Domain 内的完整 Lock 语义。公开 Package 的发布 Lock 不得复制未获披露批准的受限依赖身份或内容指纹；这类输入由受限 Audit / Build Package 保存完整 Lock，公开侧只锁定随机 Public Attestation。两种 Lock 都是规范输入，但属于不同 Package 和 Access Domain，禁止把私有 Lock 作为“未列入 Manifest 的隐藏文件”塞入公开工作树。

### 6.3 Package SemVer 语义

已发布的 `<package_id, package_version>` 内容不可改写；任何变化都必须发布新版本。

- **Patch**：不改变 Node 正文、适用范围、规范性、关系语义、依赖或可见性的非语义修正，例如显示元数据或更精确但不改变结论的 Provenance 补充。
- **Minor**：向后兼容的新增，例如新增 Node、Alias、Source Evidence 或 Relationship；可以弃用旧 Node，但不得移除旧 ID 或改变其已有语义。
- **Major**：移除或重新解释已有 Node、改变适用范围或 Normativity、改变 Redirect 目标、引入不兼容 Schema、改变 Content Dependency 或收紧/放宽 Access / Rights 公开边界。

来源勘误优先新增修正表达并建立 `corrects` / `supersedes`，通常可以作为兼容新增发布 Minor；禁止直接改写旧 Node 后伪装成 Patch。

`reports/` 不属于 Release Payload，也不参与 Package SemVer。若历史运行报告需要对外归档，应进入独立、受限且自行版本化的 Audit Package，不能悄悄附在内容 Package 中。

## 7. 身份规则

### 7.1 稳定语义实体

除版本化 Schema / Registry Document、Vocabulary Term 和内容摘要外，所有持久化规范 Record 都使用 UUIDv7，并以标准 UUID URN 表达。包括但不限于 Package、Party、Work、Edition、Artifact、Entry、Fragment、Node、Boundary / Visibility Decision、Source Mapping、Navigation / Source Reference / Semantic Address / Asset Occurrence 与 Mapping、Relationship、Policy、Claim、Receipt、Attestation、Redirect 和 Tombstone：

```text
urn:uuid:019f0000-0000-7000-8000-000000000001
```

采用 UUIDv7 的原因：

- 全局冲突概率可忽略；
- 不依赖标题、路径、语言或内容；
- 按创建时间大致有序，利于存储与审计；
- 已有标准表示，不依赖 LoreBuddy 域名永久存在。

#### 未采用：slug ID

标题会改名、重译和冲突，路径重构会破坏引用。

#### 未采用：正文摘要 ID

勘误、转写修复或合法正文更新会改变摘要，从而错误地改变实体身份。摘要用于完整性，不用于语义身份。

### 7.2 不可变字节身份

Artifact 和 Entry 必须记录 SHA-256：

```yaml
digest: "sha256:836eea8912cf..."
```

同一摘要表示相同字节，但不自动表示相同来源语义。两个不同路径或不同 Edition 可以合法引用相同字节。

### 7.3 ID 生命周期

- ID 创建后不得更换或复用。
- 标题变化不改变 ID。
- 节点拆分或合并时创建新 ID。
- 旧 ID 通过 Redirect 指向替代节点，或通过 Tombstone 解释为何不再有效。
- `supersedes` 不等同于 Redirect：前者表示版本关系，后者表示身份迁移。

## 8. Source 模型

### 8.1 Work

Work 表示抽象作品，保存：

- 标题与别名；
- 作者、出版者或组织；
- 作品类型；
- 外部标准标识；
- 已知权威关系；
- 权利信息的来源。

Work 不保存具体页码、语言文本或文件摘要。

### 8.2 Edition

Edition 表示特定出版表达，保存：

- 所属 Work；
- 语言与文字系统；
- 版本、印次、发布日期；
- ISBN、产品编号等外部标识；
- Errata 和修订关系；
- 出版者、授权与翻译状态；
- 可验证程度。

同一 Work 的 2014、2024、不同语言或不同印次必须是不同 Edition。

### 8.3 Artifact

Artifact 表示实际摄取文件。必须保存：

- 原始文件字节；
- 原文件名；
- 格式、大小和 SHA-256；
- 获取来源及获取时间；
- 提取工具与版本；
- 权利和访问状态；
- 容器级元数据；
- 完整 Inventory。

新输入必须创建新 Artifact，不得覆盖旧文件。

### 8.4 Entry

Entry 表示 Artifact 内的资源。必须保存：

- 原始内部路径和路径字节证据；
- 安全存储路径；
- 原始大小写和 Unicode 形式；
- 长度与 SHA-256；
- 声明 MIME、检测 MIME；
- 声明编码、检测编码；
- 容器 Section、Offset、Length 等可获得信息；
- 提取状态和异常。

每个 Artifact 的 `sources/artifacts/<artifact-key>/inventory.jsonl` 是其 Entry ID 与 Entry 字段的唯一规范事实源：一行恰好一个 `core.source-entry@0.1.0` Record，按 `storage_path` UTF-8 bytes 排序。`entries/` 只保存这些 Record 指向的不可变提取字节，不另存身份；`path-map.jsonl` 是从同一组 Source Entry Record 确定性投影的 `core.source-path-map-record@0.1.0` 流，不是第二份路径事实源。Extraction Receipt 必须锁定 Inventory 与 Path Map 的文件摘要，并验证投影可以双向回到同一 Entry ID。

原始内部路径 byte 必须以 RFC 4648 Base64 保存，并记录 Directory Record 摘要；Unicode 路径只是带 Charset 与解码状态的视图。原始内部路径与宿主文件系统路径必须通过 `path-map.jsonl` 双向映射。含路径穿越、保留名、大小写冲突、无法解码或 Unicode 冲突的 Entry 必须隔离，不能直接落盘。

### 8.5 Fragment

Fragment 不是清洗后的副本，而是 Entry 内的可定位范围。每个 Fragment 必须有唯一的规范 Source Fragment Record，存放于 `metadata/fragments/<shard>/<uuid>.yaml`；`<shard>` 取 `SHA-256(fragment-id)` 首字节。

Source Fragment Record 至少保存 Fragment ID、Entry ID 与摘要、复合 Locator、带 Domain Prefix 的 Fragment 语义摘要、规范 Source Event Stream 的相对路径/记录数/精确文件字节数/普通文件摘要、选择算法/人工决策和生命周期。Record 使用 `<uuid>.yaml`，事件流使用同分片下 `<uuid>.events.jsonl`。虚拟 Prefix 不计入文件字节数与普通文件摘要；两种摘要不得共用一个模糊字段。Record 不复制清洗后的来源正文，但 Event Stream 包含精确解码原文，因此 Record 与 Stream 都使用 `source-fragment-evidence` Release File Role，发布时要求 `redistribute_source`，不得按普通 Metadata 处理。`embedded-fragment` Node Provenance 可以携带便于离线阅读的 Locator 快照，但必须与该规范记录一致，不能成为第二个 Fragment 事实源；`external-public-receipt` 禁止复制受限 Locator。

Locator 应组合：

- 原始内部路径；
- Entry 摘要；
- Anchor；
- HHC 导航路径；
- Heading 路径；
- DOM Path；
- 原始字节范围；
- 前文、精确文本、后文组成的 Text Quote；
- Fragment 摘要。

没有单一定位方式能同时满足精确和跨版本稳定，因此必须保留复合定位器。

已发布的 Fragment Record 不原地改变所指范围。仅增加等价定位方式可以发布记录修订；边界、Entry 或所选文本发生变化时必须创建新 Fragment ID，并通过审核迁移引用。这样多个 Node 可以安全共享一个 Fragment，而不会产生无法校验的同名 Locator。

## 9. Artifact 与 Edition 映射

当前 CHM 一个 Artifact 聚合多个 Work 与 Edition。映射必须是 `metadata/source-mappings/` 中有稳定 ID 的可审计断言，并允许以 Entry 或 Fragment 为主体：

```yaml
schema: "core.source-mapping@0.1.0"
id: "urn:uuid:..."
subject:
  kind: "fragment"
  id: "urn:uuid:..."
target:
  kind: "edition"
  id: "urn:uuid:..."
scope:
  navigation_occurrence_ids:
    - "urn:uuid:..."
claim_status: "claimed"
evidence_ids:
  - "urn:uuid:..."
review:
  status: "pending"
  review_id: null
lifecycle:
  status: "active"
  revision: 1
```

`claim_status` 至少支持：

- `verified`：由可审计证据和人工审核确认；
- `claimed`：来源自身声明，但未独立核验；
- `inferred`：LoreBuddy 根据结构提出的候选；
- `unknown`：无法判断。

`unknown` 时 `target.kind` 必须是 `unresolved` 且 `target.id` 为 `null`；不能伪造占位 Edition。目标为 Edition 时，Work 由 Edition Record 唯一解析；目标为 Work 表示已知作品但具体 Edition 未知。Node Provenance 必须通过 `source_mapping_ids` 引用记录，不得只复制 Work / Edition 显示字段。

禁止仅凭路径把 `inferred` 自动升级为 `verified`。

## 10. Library 模型

### 10.1 一个 Node 一个表达

一个知识节点只保存：

- 一个主要语言；
- 一个明确规则/设定/事件上下文；
- 一个可独立维护的语义单元；
- 一种正文表达版本；
- 一组能够分别完整说明的 Provenance 链。

跨语言、跨规则版本、勘误前后、官方与 House Rule 必须拆为不同节点，并用 Relationship 连接。不同 Edition 若经审核确认承载完全相同的正文表达、适用范围和权威上下文，可以作为同一 Node 的多条 Provenance；Edition ID 不单独决定 Node 身份。

### 10.2 概念节点与表达节点

可以建立无官方正文的概念节点（Concept Node），用于连接跨版本或跨语言表达。概念节点的编辑性说明必须明确标记为 LoreBuddy 断言，不得冒充官方正文。

不应自动创建概念等价关系。字符串相同或翻译相似只能生成候选。

### 10.3 文件路径

推荐格式：

```text
library/nodes/<kind>/<sha256-node-id-prefix>/<slug>--<uuid>.md
```

示例：

```text
library/nodes/rule/01/concentration--019f0000-0000-7000-8000-000000000001.md
```

`slug` 只提高人工可读性。文件可以移动或改名，ID 和 Relationship 不受影响。

## 11. Relationship 模型

关系是有向、带类型、带断言来源的边。

平台核心建议包含：

- `core.part_of`
- `core.references`
- `core.depends_on`
- `core.applies_to`
- `core.conflicts_with`
- `core.translation_of`
- `core.variant_of`
- `core.revises`
- `core.corrects`
- `core.supersedes`
- `core.overrides`

每种关系必须在注册表声明：

- 语义；
- 允许的源、目标类型；
- 反向谓词；
- 是否对称；
- 是否传递；
- 允许的限定字段。

作者只维护正向关系。反向关系由 Index 生成，避免一条边要求修改两个 Node。

简单关系可以写在 Node Front Matter。需要独立 Provenance、生效范围、时间或审核状态的关系必须提升为 `metadata/relationships/` 下的独立记录。

## 12. 权威、规范性与适用范围

不使用单一 `authority: high | low` 排序。至少拆分：

1. **来源身份**：publisher、licensee、third-party、community、private、unknown；
2. **翻译身份**：original、official-translation、licensed-translation、community-translation、unknown；
3. **规范性**：normative、optional、informative、playtest；
4. **适用范围**：system、ruleset、setting、campaign；
5. **覆盖关系**：corrects、supersedes、overrides；
6. **访问和权利**：Access Domain、Visibility、分项 Rights Permission、Disclosure Approval；

原因：House Rule 对出版商不是官方规则，但可以在某个 Campaign 内是规范性规则；官方 Playtest 由官方发布，但不一定是最终规范规则。

“当前有效规则”属于未来 Runtime 的上下文解析：

```yaml
rules_context:
  ruleset: "dnd.5e-2024"
  as_of: "2026-07-20"
  language: "zh-Hans"
  enabled_optional_modules: []
  package_lock: "sha256:..."
  campaign_overlay: null
```

Milestone 0 只保存解析所需事实，不实现 Resolver。

## 13. 多语言

- 每个 Node 只有一个主要 `language`。
- Alias 必须分别标记语言。
- 翻译是独立 Node，通过 `core.translation_of` 连接。
- 原文和译文的 Provenance 分别保存。
- 不假设一对一翻译；一个译文可以引用多个来源片段。
- 搜索用大小写、全半角、拼音或 Unicode 规范化键只能存在于 Index，不能回写 Source 或 Library 正文。

## 14. 版本维度

禁止使用一个笼统的 `version` 字段。必须区分：

| 字段 | 含义 |
|---|---|
| `spec_version` | LoreBuddy 规范版本 |
| `schema` | 当前文件使用的 Schema 及版本 |
| `package_version` | Package 发布版本 |
| `node_revision` | 稳定 Node 的编辑修订号 |
| `edition` | 出版版本 |
| `ruleset` | 规则系统版本 |
| `effective_from` / `effective_until` | 规则或勘误的适用时间 |
| `generator_version` | 派生工具版本 |

升级规范或 Schema 不得自动改变官方正文。正文变化必须是来源驱动的内容修订，并单独审核。

## 15. 依赖与访问控制

- 依赖类型封闭为 `content`、`build`、`provenance`、`audit-input`、`claim-source` 和只允许出现在受限 Audit Context 的 `rights-target`；完整依赖必须写入构建或审计 Principal 可读的 Manifest 与 Lock。Public Lock 禁止披露未经批准的 `build | provenance | audit-input | claim-source | rights-target` 受限身份。
- `content` 依赖是读取或解释 Node 所必需的 Package，必须形成有向无环图；构建主体必须对每个依赖通过 `can_read`，不能假设两个 `private` Package 彼此可见。
- `build` 依赖只在授权构建环境中使用。公开消费者无法读取受限输入时，公开 Package 只携带不暴露私有身份/摘要并绑定 `library_root_digest` 的 Public Build Attestation；生成的 Release Manifest 必须把 Library Reproducibility 聚合为 `attested`。完整 Build Lock 与 Access Decision Receipt 进入受限 Audit / Build Package。
- `provenance` 引用是证据引用，不导入对方内容。Node 明确选择 `embedded-fragment` 或 `external-public-receipt`；后者只能声明 `traceability: attested`。
- `audit-input` 只为受限审核提供 Authority、Evidence、Review、Decision 或 Lock；`claim-source` 只把目标 Package 的 Rights Claim / Tombstone 子集纳入 Claim Universe。二者不成为 Library 内容依赖，也不能据此向 Public Reader 暴露私有身份。
- `rights-target` 使用 `core.rights-target-candidate-lock@0.1.0`，只锁定目标 Package Manifest / Lock、协议 Registry 与预分配 ID；禁止携带最终 Release Manifest、Root、Decision / Binding Digest 或 Payload Inventory，避免 Direct 模式摘要环。
- 公开 Release 中的 `package.lock.json` 只包含公开 Content Dependency、Schema / Registry 与批准公开的 Receipt / Attestation。禁止泄漏受限 Package ID、版本、Manifest Digest、路径或解析 URI。
- Package 内 Index 默认只索引本 Package。依赖闭包的聚合索引属于 Package 外的部署产物。
- Access、Rights、Receipt 投影、Dependency Lock 和 Release Payload 的规范算法见[权利、访问与发布规范](rights-release-spec.md)。

## 16. 确定性构建

规范输出必须满足：

- 构建时不访问网络；
- 所有工具、Schema、注册表和依赖有精确版本与摘要；
- 文件遍历顺序显式按 UTF-8 字节序排序；
- JSON 使用固定规范化序列化；
- 不写入机器绝对路径；
- 不得读取系统当前时间写入规范输出；Release 的 `evaluation_as_of` 只能作为显式、锁定且可重放的输入；
- 有序数组保持来源顺序，无序集合按规定排序；
- Source 正文字节不参与 Unicode、标点或空白“美化”；
- 相同输入、相同 Lock 和相同审核账本连续构建两次，规范输出字节必须完全相同。

运行时间、主机信息和真实执行时间可以进入非规范运行日志，但不得影响 Package 内容摘要。

## 17. Schema 迁移

- 已发布 Schema 的内容不得原地修改。
- 不兼容变化提升 Major 版本。
- 迁移必须显式执行，禁止读取时静默写回。
- 迁移前后都必须验证。
- 默认要求 Node ID 和官方正文摘要保持不变。
- 拆分、合并通过新 ID、Redirect 和 Tombstone 表达。
- 迁移产生独立报告，并记录不可逆项。
- 大规模格式迁移与正文修订不得混在同一提交。

## 18. 当前 CHM 的推荐 Package 策略

第一步不建立一个永久的 `dnd5e` 总包，而是建立受限摄取 Package：

```text
packages/community/dnd5e-cn-compendium-20260630/
```

它保存：

- 当前 CHM Artifact；
- 解包 Entry 与 Inventory；
- Extraction / Analysis Receipt；
- Work / Edition 候选映射；
- Source Fragment 与节点边界账本；
- 来源、授权、Issue / Exception / Review 元数据及可重建转换报告。

Package 整体使用最严格的未决权利与访问策略。完成审核后，可以建立更细的规则、设定或私有派生 Package，通过 Provenance Receipt 引用摄取 Package 中的 Source。

公开派生 Package 不得把受限 Source 当作公开 Content Dependency。它只能携带经授权公开的证据描述，并将完整证据登记为 Build Dependency 或外部 Provenance Reference；若这不足以满足发布所需的可验证级别，则派生 Package 必须保持同等或更严格的访问级别。

替代方案是立即按目录拆成几十个 Package。暂不采用，因为目录粒度不一致，来源身份和授权尚未核验；过早拆分会把猜测固化为架构事实。

## 19. 合规级别

建议定义三个递进级别：

### 19.1 Source Complete

- Artifact 摘要、原始字节、Entry Inventory 和 Path Map 完整；
- 所有非零 Entry 均可提取或有阻塞报告；
- 两个独立提取实现已全量比对，Extraction / Analysis Receipt 已锁定工具、配置和结果；仅抽样交叉验证时最多为 `source-provisional`；
- Source 未被修改。

### 19.2 Library Valid

- Node 通过 Schema；
- 正文保真门禁通过；
- Node 在当前可读 Access Domain 或其授权 Audit Package 闭包中具有 Full Provenance；公开投影若只携带 Receipt，必须明确标记 `traceability: attested`，不得声称公开消费者可独立复查 Source；
- Relationship 无悬空引用；
- 所有歧义已审核或明确隔离。

### 19.3 Release Ready

- 依赖已锁定；
- Index 可确定性重建；
- Content、Output 与 Release Manifest 摘要全部验证通过；
- Rights 合并算法对发布动作返回 `allowed`，Access Policy、Disclosure Approval 和受限依赖投影全部通过；
- Claim Source 的追加式 Lineage、Claim / Tombstone Authority Delegation 与 Approved Review 全部可重放，未授权或 Pending Claim 没有授予权限；
- Rights Authority Delegation、Audit Context、Decision 与 Binding 唯一解析，并通过 `core.release-rights-binding-validation@0.1.0` 的全部跨 Record 等式；
- 公开构建不泄漏未授权 Access Domain 的 Package 身份、摘要或内容；
- Release Archive 精确等于 Payload 白名单，不包含 Report、私有 Lock 或完整受限 Review；
- 迁移与回滚路径明确。

`Release Ready(public)` 的完整默认拒绝布尔条件见[权利、访问与发布规范](rights-release-spec.md)。

当前项目只完成设计草案，尚未达到上述任何数据合规级别。
