# 索引规范草案

状态：Draft  
规范版本：`0.1.0`

## 1. 基本原则

索引（Index）是派生产物，不是事实源。

所有 `index/` 内容必须：

- 能从 Package Manifest、Source、Library、Metadata、Schema 和 Lock 完整重建；
- 禁止手工编辑；
- 删除后不丢失任何来源、正文、关系或审核事实；
- 在相同输入与工具链下产生字节一致输出；
- 以开放、可流式读取的 JSON / JSONL 保存；
- 不依赖 SQLite、图数据库、向量数据库或某个搜索引擎才能解释。

数据库可以从 Index 或事实源继续派生，但不能成为 Package 唯一可读表示。

## 2. 目录结构

```text
release-manifest.json

index/
    manifest.json
    output-manifest.json
    build.json

    files/
        <00-ff>.jsonl

    nodes/
        <00-ff>.jsonl

    aliases/
        <language>/
            <00-ff>.jsonl

    relationships/
        forward/
            <00-ff>.jsonl
        reverse/
            <00-ff>.jsonl

    provenance/
        by-node/
            <00-ff>.jsonl
        by-entry/
            <00-ff>.jsonl
        coverage/
            <00-ff>.jsonl

    navigation/
        source/
            <00-ff>.jsonl
        semantic/
            <00-ff>.jsonl

    assets/
        records/
            <00-ff>.jsonl
        usages/
            <00-ff>.jsonl
```

空分片可以不生成。分片名称由后文为各索引定义的稳定键之 SHA-256 首字节决定，不依赖文件枚举顺序或本地环境。

## 3. `manifest.json` 与 Content Manifest 分片

内容清单（Content Manifest）覆盖 Package 的事实源。为避免 100,000 个 Node 令一个 JSON 文件无限增长，`manifest.json` 只列分片摘要，具体文件记录写入 `files/<00-ff>.jsonl`。

```json
{
  "schema": "core.index-manifest@0.1.0",
  "package_id": "urn:uuid:...",
  "package_version": "0.1.0",
  "scope": "package-facts",
  "shards": [
    {
      "path": "files/00.jsonl",
      "records": 412,
      "digest": "sha256:...",
      "first_key": "library/...",
      "last_key": "sources/..."
    }
  ],
  "library_file_count": 123,
  "library_root_digest": "sha256:...",
  "content_root_digest": "sha256:..."
}
```

每条分片记录为：

```json
{
  "path": "library/nodes/rule/01/example--....md",
  "size": 1234,
  "digest": "sha256:...",
  "role": "knowledge-node"
}
```

`role` 必须来自由 `package.lock.json` 锁定的 `core.release-file-roles@0.1.0` 注册表。v0.1 至少定义 `package-control`、`package-instructions`、`source-artifact`、`source-metadata`、`source-entry`、`source-asset`、`source-receipt`、`source-fragment-evidence`、`knowledge-node`、`library-asset`、`receipt-attestation`、`metadata-record`、`schema-document`、`registry-document`、`derived-index`、`content-manifest`、`output-manifest`、`release-manifest`。Content / Output Manifest 和 Release Payload Inventory 对同一路径必须使用同一个角色；未注册角色或角色不一致都必须阻塞。角色是 Rights Coverage 的机器输入，不能由文件扩展名临时猜测；Source Asset、Source Fragment Evidence 与 Receipt / Attestation 必须使用专门角色，不能藏在宽泛 `source-entry` 或 `metadata-record` 下规避额外权限。

注册表同时固定 `core.release-file-role-dispatch@0.1.0`，每个规则包含 Match 类型、规范 Path Pattern、可选 Schema Class / MIME Predicate、角色和优先级。分类作用于 Content / Output Manifest 已解析的规范记录，不信任作者填写的 `role`；生成器先计算唯一 Expected Role，再要求文件记录逐字相等。v0.1 派发顺序与闭包为：

1. `package.yaml`、`package.lock.json` → `package-control`；Package 根 `AGENTS.md` → `package-instructions`；
2. `sources/artifacts/*/original/**` → `source-artifact`；同一 Artifact 根的 `artifact.yaml`、`inventory.jsonl`、`path-map.jsonl` → `source-metadata`；`receipts/**` → `source-receipt`；
3. `sources/artifacts/*/entries/**` 必须反查同 Artifact `inventory.jsonl` 的唯一 Source Entry。`media_type.detected` 为 `text/*` 或注册的文本型 `application/xhtml+xml | application/xml | application/json | application/javascript` 时 → `source-entry`；其他值、缺失或未知值一律按更严格的 `source-asset`，不能由扩展名降级；
4. `metadata/fragments/<shard>/<uuid>.yaml` 与同目录 `<uuid>.events.jsonl` 必须成对，YAML Record 单向固定 Event Stream 的 Path / Length / Digest，并共同 → `source-fragment-evidence`；Event Stream 不反向保存 Record Digest，避免摘要环；`metadata/fragments/**` 的其他形状阻塞；
5. `library/nodes/**` → `knowledge-node`；`library/assets/**` → `library-asset`；
6. Schema Class 注册为 Receipt / Attestation 的规范 Record 优先 → `receipt-attestation`，无论它位于哪个允许的 Metadata 子目录；
7. `sources/catalog/**` 与其余 `metadata/**` → `metadata-record`；Package 自有 `schemas/**`、`registries/**` 分别 → `schema-document`、`registry-document`；
8. `index/manifest.json` → `content-manifest`；除 `index/output-manifest.json` 外的其余 `index/**` → `derived-index`；后两种根级文件分别 → `output-manifest`、`release-manifest`。

`core.release-file-role-dispatch@0.1.0` 的 Receipt / Attestation Schema Class 成员封闭为：`core.access-decision-receipt@0.1.0`、`core.public-evidence-receipt@0.1.0`、`core.public-provenance-receipt@0.1.0`、`core.public-build-attestation@0.1.0`、`core.public-fidelity-attestation@0.1.0`，它们作为独立文件时使用 `receipt-attestation`。`core.extraction-receipt@0.1.0` 与 `core.analysis-receipt@0.1.0` 必须位于对应 Artifact 的 `receipts/**` 并按更高优先级使用 `source-receipt`；出现在其他路径直接阻塞。`core.public-party-projection@0.1.0` 是 `metadata-record`。Public Rights Attestation 只允许内联于 Release Manifest，不形成独立文件角色，但 Public 模式必须为该 `release-manifest` 条件性增加 `publish_receipt` Required Permission。新增任何成员必须发布新版本 Registry 并改变 `registry_set_digest`，实现不能按 Schema 名后缀自行归类。

Path 必须恰好命中一个最终分支；同优先级多命中、无法反查 Entry、Schema Class 冲突或零命中都阻塞。Registry 的规则、文本 MIME 集和 Receipt / Attestation Schema Class 列表都进入 `registry_set_digest`。这样把图片标为 `source-entry`、把 Public Receipt 标为 `metadata-record` 都会在 Rights Decision 前失败。

内容集合必须包含 `package.yaml`、`package.lock.json`、Package 级 `AGENTS.md`、`sources/`、`library/`、`metadata/`、Package 自有 `schemas/` 与 `registries/`。当前 Access Domain 内的人工裁决属于 `metadata/`，因此也在 Content Manifest 中；公开 Package 只能包含经 Disclosure Approval 的 Review / Receipt 投影，完整私有证据进入受限 Audit Package。Content Manifest 不包含 `index/`、`release-manifest.json`、仓库级文档或可重建的 `reports/`。

要求：

- 文件记录按 Package 相对路径的 UTF-8 字节序排序；
- 分片键是相对路径 SHA-256 的首字节；
- `content_root_digest` 对全局路径顺序的记录流计算：UTF-8 字节前缀 `lorebuddy-content-root-v1\n`，随后逐条写入 JCS 记录和一个 LF；分片边界不参与根摘要；
- `library_root_digest` 从同一全局文件记录中只筛选路径以 `library/` 开头的记录，保持原排序，用前缀 `lorebuddy-library-root-v1\n`、逐条 JCS 记录和 LF 计算；`library_file_count` 是该子集数量。空 Library 的输入只有 Prefix。该根排除 `metadata/attestations/`，因此 Public Build Attestation 可以安全绑定它；
- `manifest.json` 的 `shards` 按分片路径 UTF-8 字节序排序，并校验每个分片的字节摘要；
- v0.1 Content Manifest 只接受规范普通文件；Symbolic / Hard Link 与其他特殊类型全部禁止，不能跟随后把目标伪装成文件；未来支持必须发布新的 Payload Protocol；
- 文件权限和宿主绝对路径不得参与跨平台内容摘要。

## 4. Output Manifest 与 Release Manifest

`index/output-manifest.json` 列出除自身之外的全部 `index/` 文件、长度、SHA-256 与注册 `role`，并计算 `index_root_digest`。`index/manifest.json` 使用 `content-manifest`，其他派生分片通常使用 `derived-index`；未知角色阻塞。记录按 Package 相对路径的 UTF-8 字节序排序；摘要输入使用 `lorebuddy-index-root-v1\n`、逐条 JCS 记录和 LF。自排除避免递归摘要。最终 Payload Inventory 另外为 `index/output-manifest.json` 指定 `output-manifest`，为根级 Manifest 指定 `release-manifest`。

Package 根级 `release-manifest.json` 是最终生成的发布完整性封条，至少包含：

```json
{
  "schema": "core.release-manifest@0.1.0",
  "package_id": "urn:uuid:...",
  "package_version": "0.1.0",
  "evaluation_as_of": "2026-07-20T00:00:00Z",
  "content_manifest_digest": "sha256:...",
  "content_root_digest": "sha256:...",
  "library_root_digest": "sha256:...",
  "output_manifest_digest": "sha256:...",
  "index_root_digest": "sha256:...",
  "payload_policy": {
    "id": "core.release-payload@0.1.0",
    "digest": "sha256:..."
  },
  "payload_file_count": 1234,
  "access": {
    "domain_id": "urn:uuid:...",
    "policy_id": "urn:uuid:...",
    "policy_digest": "sha256:..."
  },
  "rights": {
    "mode": "public-attestation",
    "action": "public-release",
    "authority_domain_id": "urn:uuid:...",
    "release_binding_id": "urn:uuid:...",
    "attestation": {
      "schema": "core.public-rights-attestation@0.1.0",
      "id": "urn:uuid:...",
      "action": "public-release",
      "result": "allowed",
      "coverage": "complete",
      "rights_algorithm": "core.rights-merge@0.1.0",
      "disclosure_profile": {
        "id": "core.rights-public-minimal@0.1.0",
        "digest": "sha256:..."
      },
      "disclosure_approval_id": "urn:uuid:...",
      "validity": {},
      "lifecycle": {"status": "active", "revision": 1}
    }
  },
  "disclosure_profiles": [
    {
      "id": "core.rights-public-minimal@0.1.0",
      "digest": "sha256:..."
    }
  ],
  "assurance": {
    "evaluated_for": "release-reader",
    "traceability": {
      "aggregate": "attested",
      "nodes": {"total": 100, "full": 90, "attested": 10, "unverified": 0, "not_applicable": 0}
    },
    "fidelity": {
      "aggregate": "attested",
      "nodes": {"total": 100, "full": 90, "attested": 10, "unverified": 0, "not_applicable": 0}
    },
    "reproducibility": {
      "aggregate": "attested",
      "library": "attested",
      "index": "full"
    }
  }
}
```

`release-manifest.json` 不把自身纳入摘要。它使消费者能够分别验证事实源、Library 子集与可重建索引，而不把它们混成一个循环 Manifest。Public Rights Attestation 内联于该自排除文件，并按 Schema 语义自动绑定父 Manifest 的 Package ID / Version、`evaluation_as_of`、Content / Library / Index Root、Payload Policy 与文件数；不得携带私有 Rights Decision、Claim、Reviewer 或 Evidence ID。Restricted Release 可以使用 `rights.mode: direct`，其形状为 `{mode, action, authority_domain_id, release_binding_id, decision:{id,digest}}`；Public 模式形状为 `{mode, action, authority_domain_id, release_binding_id, attestation:{...}}`，Wrapper 与 Attestation 的 `action` 必须相等。`authority_domain_id` 必须等于 Package Manifest 的 Rights Authority Domain，但不要求 Audit Package 使用相同 Access Domain。`release_binding_id` 必须在 Candidate 组装前随机预分配，只用于在锁定且授权的 Audit Context 中发现目标 Release 之外的唯一 Record；Manifest 禁止引用 Binding Digest，否则会重新形成自引用。Public Release 禁止出现 Decision ID / Digest。

Release Archive 的允许文件集合严格等于 Content Manifest 文件、Output Manifest 文件、`index/output-manifest.json` 和 `release-manifest.json` 的并集。发布器必须从空目录按清单复制；消费者必须拒绝任意额外文件。因此 `reports/`、私有 Lock、完整 Review、缓存或临时日志不能在摘要仍通过时被夹带发布。`evaluation_as_of` 是发布流程显式提供并锁定的 RFC 3339 UTC 评估时点，不得在重放时读取系统“当前时间”；Access、Rights、Disclosure 与 Binding 必须使用同一值。精确规则见[权利、访问与发布规范](rights-release-spec.md)。

该 Manifest 只提供内部完整性，不能单独认证发布者。未来的签名或透明日志应签署该文件摘要及 Access / Rights / Disclosure Policy；Milestone 0 期间消费者必须从可信渠道取得预期摘要。

## 5. `build.json`

构建描述记录：

```json
{
  "schema": "core.index-build@0.1.0",
  "generator": {
    "name": "lorebuddy-indexer",
    "version": "0.1.0",
    "digest": "sha256:..."
  },
  "spec_version": "0.1.0",
  "package_lock_digest": "sha256:...",
  "schema_set_digest": "sha256:...",
  "registry_set_digest": "sha256:...",
  "inputs_root_digest": "sha256:...",
  "serialization": "jcs-rfc8785+jsonl-lf"
}
```

`inputs_root_digest` 必须等于 Content Manifest 的 `content_root_digest`。规范 `build.json` 不记录当前时间、主机名、用户名或本机路径。真实执行时间和性能数据进入 `reports/.../run.json`，不参与 Package 确定性摘要。

`schema_set_digest` 与 `registry_set_digest` 分别使用 Domain Prefix `lorebuddy-schema-set-v1\n`、`lorebuddy-registry-set-v1\n`。从 `package.lock.json` 取完整记录 `{id,path,digest}`，按 `(id, path)` 的 UTF-8 bytes 排序，对每条写 JCS Object 与 LF 后计算 SHA-256。空集合的输入只有 Prefix。Document ID、相对路径或摘要任一变化都会改变集合摘要；运行时发现 Lock 外 Document 必须失败。

## 6. Node Index

每条记录提供最小可发现信息：

```json
{
  "id": "urn:uuid:...",
  "path": "library/nodes/...md",
  "kind": "core.rule",
  "title": "专注",
  "language": "zh-Hans",
  "package_id": "urn:uuid:...",
  "applicability": {
    "systems": {"status": "unknown", "values": []},
    "settings": {"status": "unknown", "values": []},
    "campaigns": {"status": "unknown", "values": []}
  },
  "lifecycle_status": "active",
  "body_byte_digest": "sha256:...",
  "visible_text_digest": "sha256:...",
  "structure_digest": "sha256:...",
  "fidelity_aggregate_mode": "full",
  "fidelity_assertion_ids": ["urn:uuid:..."]
}
```

Node Index 不复制完整正文。调用方读取 `path` 中的 Markdown 原文。

## 7. Alias Index

Alias 必须是一对多索引。

```json
{
  "display": "Concentration",
  "language": "en",
  "role": "source-title",
  "search_key": "concentration",
  "normalization": "core.alias-search@1.0.0",
  "targets": [
    {
      "node_id": "urn:uuid:...",
      "package_id": "urn:uuid:...",
      "kind": "core.rule",
      "applicability": {
        "systems": {"status": "unknown", "values": []},
        "settings": {"status": "unknown", "values": []},
        "campaigns": {"status": "unknown", "values": []}
      }
    }
  ]
}
```

要求：

- `display` 原样保留；
- `search_key` 仅用于候选召回，不承担身份或自动合并；
- 规范化算法必须命名、版本化并记录；
- 不同语言分别分区；
- 一个 Alias 命中多个版本、系统或 Package 是正常结果；
- 消歧由调用上下文完成，Index 不静默选择一个“最佳”节点。

搜索规范化可以使用大小写折叠、Unicode 规范化或语言特有策略，但这些变化只存在于 `search_key`，不得回写 Front Matter 或正文。

`core.alias-search@1.0.0` 的默认算法固定为：使用 Unicode 15.1.0 数据执行 NFKC；按同版本 `CaseFolding.txt` 执行完整 Default Case Folding（`T` 映射不启用）；把 Unicode 15.1.0 `White_Space` 属性的连续字符替换为一个 U+0020 并去除首尾 U+0020；保留标点、音调符号和其余字符。输入是 `display` 的 Unicode Scalar Value 序列，输出是 `search_key`。例如 `Concentration` 得到 `concentration`，`Ａ Ｂ`（中间 U+00A0）得到 `a b`。拼音、简繁转换、去音调或语言特有 Tokenization 必须使用另一个版本化算法 ID 与 Fixture，不能悄悄加入本算法。

## 8. Relationship Index

正向关系来自 Node Front Matter 与独立 Relationship Record。反向关系完全生成。

### 8.1 Forward

```json
{
  "assertion_id": "urn:uuid:...",
  "source": "urn:uuid:...",
  "predicate": "core.references",
  "target": "urn:uuid:...",
  "origin": {
    "kind": "inline",
    "path": "library/nodes/...md",
    "json_pointer": "/relationships/0",
    "relationship_record_id": null
  },
  "scope": {
    "systems": {"status": "unknown", "values": []},
    "settings": {"status": "unknown", "values": []},
    "campaigns": {"status": "unknown", "values": []}
  },
  "lifecycle_status": "active",
  "assertion": {
    "basis": "source-explicit",
    "evidence_ids": ["urn:uuid:..."]
  }
}
```

### 8.2 Reverse

```json
{
  "assertion_id": "urn:uuid:...",
  "target": "urn:uuid:...",
  "predicate": "core.referenced_by",
  "source": "urn:uuid:...",
  "forward_predicate": "core.references",
  "origin": {
    "kind": "inline",
    "path": "library/nodes/...md",
    "json_pointer": "/relationships/0",
    "relationship_record_id": null
  },
  "scope": {
    "systems": {"status": "unknown", "values": []},
    "settings": {"status": "unknown", "values": []},
    "campaigns": {"status": "unknown", "values": []}
  },
  "lifecycle_status": "active",
  "assertion": {
    "basis": "source-explicit",
    "evidence_ids": ["urn:uuid:..."]
  }
}
```

要求：

- 作者只维护正向边；
- 每条作者断言必须有稳定 `assertion_id`；同一 `(source, predicate, target)` 上的多条证据断言不得折叠；
- `origin.path` 使用 Package 相对路径，`json_pointer` 指向规范解析后的 YAML/JSON 数据位置；独立记录同时填写 `relationship_record_id`；
- Reverse 记录必须原样保留 Forward 的 `assertion_id`、范围、生命周期、证据和 Origin，保证能回到唯一事实断言；
- `evidence_ids[]` 只能复制 Release Reader 可解析的 Active `core.evidence@0.1.0` 或 `core.public-evidence-receipt@0.1.0` ID；受限 Evidence 必须先用随机新 ID 生成经 Disclosure Approval 的 Public Evidence Receipt，或让整条 Relationship 留在受限 Package，禁止把私有 ID 当作指纹泄漏；
- Index 根据 Relationship Type 注册表生成反向谓词；
- 禁止把未声明为传递的关系自动做传递闭包；
- `conflicts_with` 等对称关系可以生成镜像索引，但事实源仍只有一条断言；
- 无法解析的目标是阻塞错误或明确的外部引用，不能静默丢弃。

## 9. Provenance Index

Provenance Index 显式区分两种模式：

```text
embedded-fragment:
    Node → Fragment → Entry → Artifact
    Fragment / Entry → reviewed source mapping → Edition → Work
    Entry / Fragment → Nodes

external-public-receipt:
    Node → Public Provenance Receipt
```

公开 Receipt Index 不得包含私有 Package / Fragment / Entry ID、摘要、路径或 Locator。它只索引当前 Release 已批准披露的 Receipt 字段，并标记 `traceability: attested`。

### 9.1 By Node

对 `embedded-fragment` 列出每个 Node 的来源链、Locator 和 Mapping 验证状态；对 `external-public-receipt` 只列 Receipt ID、摘要、Disclosure Profile 和 Attested 状态。

### 9.2 By Entry

只在调用方可读的 Access Domain 内，列出某个 Source Entry 被哪些 Node 覆盖，以及对应 Fragment 范围。公开 Receipt 不生成私有 Entry 方向的反向记录。

### 9.3 Coverage

`coverage/<00-ff>.jsonl` 报告：

- 已节点化 Fragment；
- 未节点化可见正文；
- 多节点重叠覆盖；
- 仅导航或模板内容；
- 被人工排除的范围及原因；
- 无法解码、无法解析或待审核范围。

Coverage Index 不能把“未转换”自动视为错误。不同 Package 可以有不同摄取目标，但任何排除都必须有显式状态，不能静默消失。

## 10. Navigation Index

来源导航（Source Navigation）和语义导航（Semantic Navigation）必须分开。

### 10.1 Source Navigation

保留 HHC 等原始导航的：

- 顺序；
- 层级；
- 显示名称；
- 原始 Local；
- 重复出现位置；
- 无 Local 的分类节点；
- 坏链接状态；
- 到 Entry 或 Node 的解析结果。

同一目标在 HHC 多处出现时，每个出现位置都有独立 occurrence ID，不能去重后丢失来源结构。

Occurrence ID 的事实源是 `metadata/navigation/source-occurrences/`；Index 只重排和投影，不能在构建时临时发号。Candidate Key、Ordinal 与 UUID 匹配协议见[完整性与事件协议](integrity-protocols.md)。

### 10.2 Semantic Navigation

面向知识浏览。它的树身份、显示 Label、父子关系、目标 Node 和 `sibling_ordinal` 是编辑决策，规范事实源存放在 `metadata/navigation/semantic/` 的 `core.semantic-navigation@0.1.0` Record 中。审核后的分类、`part_of` 关系和 Package 词汇表只能提出候选，不能在构建时无规则地决定顺序。

同一父项下 `sibling_ordinal` 必须是唯一非负整数；生成器按 `(semantic_navigation_id, parent_item_id-or-root, sibling_ordinal, item_id)` 投影。重复 Ordinal、循环、悬空目标或同一 Item 多父必须阻塞。若需要同一 Node 在多处出现，应创建多个稳定 Navigation Item ID，而不是复用一个 Item 身份。

Semantic Navigation 不复制 Source Navigation，也不声称是出版物原目录。二者可以同时把同一 Node 放在不同位置。

## 11. Asset Index

Asset Record 与 Asset Usage 必须分开。

Asset Record 以内容摘要为身份，记录：

- 内容寻址路径；
- SHA-256；
- MIME 与尺寸；
- 一个或多个 Source Entry；
- 转码或尺寸变换记录；
- `rights_claim_ids` 与 Access Domain 引用；Index 可以附带当前 Rights Decision 的派生结果，但必须标记 Decision ID / Digest，不能回写 Asset Record。

Asset Usage 以稳定 occurrence ID 表达某个 Node 中的一次使用，记录：

- Asset 摘要与 Node ID；
- 来源或 Markdown 中的相对路径与精确位置；
- 此次出现位置的原始 `alt`、`title` 与图注；
- 对应 Source Entry / Fragment 和 Source Reference Occurrence ID；
- 审核状态与批准的差异。

同一图片在不同上下文可以有不同 `alt` 或图注；把这些字段放在 Asset Record 会错误合并语境，因此不采用。Asset Record 与 Usage 分别写入 Index 的 `assets/records/` 和 `assets/usages/`；其规范事实源分别是 `metadata/assets/records/` 与 `metadata/assets/usages/`，Index 不得临时补造身份或变换事实。

Asset Usage 的事实源是 `metadata/assets/usages/`；Index 中的 Usage 是可重建投影。来源图片还必须引用 `metadata/references/occurrences/` 的稳定 Source Reference Occurrence ID。

Source 资产不去重覆盖。Library 可以按摘要去重，但必须保留每个原始路径的 Provenance。

## 12. 序列化、分片与排序

- JSON 使用 JSON Canonicalization Scheme（JCS，RFC 8785）语义。
- JSONL 每行一个完整 JSON Object，以 LF 结尾。
- 字符串排序均比较原始 UTF-8 字节，不受 Locale 影响；元组按字段从左到右比较。
- Map Key 按规范序列化规则排序。
- 语义无序集合排序；来源导航、Fragment 顺序等有序数据保持原顺序。
- 数字不得用于保存超过安全整数范围的外部 ID；此类值使用字符串。
- 禁止 NaN、Infinity 和实现相关浮点序列化。

各索引的主排序键必须固定为：

| Index | 分片键 | 分片内排序键 |
|---|---|---|
| Content File | `path` | `path` |
| Node | `id` | `id` |
| Alias | `language + U+0000 + search_key` | `(language, search_key, display, role)`；`targets` 再按 `(node_id, package_id, kind, applicability 的 JCS bytes)` |
| Relationship Forward | `source` | `(source, predicate, target, assertion_id)` |
| Relationship Reverse | `target` | `(target, predicate, source, assertion_id)` |
| Provenance By Node | `node_id` | `(node_id, provenance_id)` |
| Provenance By Entry | `entry_id` | `(entry_id, fragment_start_key, node_id, provenance_id)` |
| Coverage | `entry_id` | `(entry_id, fragment_start_key, coverage_status, node_id-or-empty)` |
| Source Navigation | `source_navigation_id` | `(source_navigation_id, occurrence_ordinal, occurrence_id)` |
| Semantic Navigation | `semantic_navigation_id` | `(semantic_navigation_id, parent_item_id-or-empty, sibling_ordinal, item_id)` |
| Asset Record | `asset_digest` | `asset_digest` |
| Asset Usage | `asset_digest + U+0000 + occurrence_id` | `(asset_digest, node_id, occurrence_id)` |

`fragment_start_key` 是 Locator Schema 定义的 ASCII 排序键：若有 `entry_raw_byte_ranges`，取最小 `start` 并写为 `0:` + 20 位零填充十进制；否则若有 `decoded_text.ranges`，取最小 `start` 并写为 `1:` + 20 位零填充十进制；否则写 `2:` + Fragment UUID URN。Range 起点必须是非负、最多 20 位的十进制整数。该 Key 只在已经按 `entry_id` 分组后比较；相同 Key 再由后续排序字段消歧。`node_id-or-empty` 中空字符串只作为排序哨兵，不写回业务字段。分片文件由“分片键的 SHA-256 首字节”决定。

## 13. 规模策略

使用 JSONL 和稳定分片的原因：

- 可流式生成和验证，不需要一次加载 100,000 个 Node；
- Git Diff 仍然可读；
- 单个记录变化只影响一个分片；
- 可并行构建，但最终排序确定；
- 未来容易导入 SQLite、全文搜索、Graph 或向量系统。

未采用“每种索引一个巨大 JSON”，因为小变更会造成大 Diff 和高内存占用。

未采用“数据库文件作为规范索引”，因为数据库格式、页布局和版本不利于长期可读、可审计和确定性 Diff。

## 14. Package 与隐私边界

- Index 默认只覆盖当前 Package。依赖闭包的联合索引属于 Package 外部署产物。
- 构建公开 Package 时，不得读取或输出私有 Package 的 Node、Alias、标题、关系、路径或报告。
- 私有 Package 指向公开 Node 的关系只存在于私有索引中；公开 Node 的反向索引不得暴露该关系。
- 聚合搜索索引属于部署产物，不写回任何单个 Package。

## 15. 验证要求

索引构建至少验证：

1. 所有 Index 文件均能从事实源重建；
2. 连续构建两次得到相同摘要；
3. Content、Output 与 Release Manifest 中每个文件长度、摘要和根摘要正确；
4. Node Index 没有重复或缺失 ID；
5. Alias 保持一对多，不发生覆盖；
6. Relationship 没有悬空目标，反向边与注册表一致，且每条断言的稳定 ID、Origin、范围、生命周期和证据未丢失；
7. Source Navigation 保留顺序、重复位置和坏链接状态；
8. Provenance 双向索引一致；
9. Asset Record 与 Usage 双向完整，Occurrence 未被内容去重吞并；
10. 访问边界测试证明没有私有信息泄漏；
11. 在不同临时目录、文件枚举顺序、Locale 和 Timezone 下构建，规范输出仍字节一致；
12. 任意 Index 文件变化都会改变 `index_root_digest`，任意事实源变化都会改变 `content_root_digest`；
13. Release Archive 文件集合精确匹配 Payload 白名单，额外的 Report、Lock、Symlink 或任意未知文件都会失败。
