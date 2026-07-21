# 权利、访问与发布规范草案

状态：Draft  
规范版本：`0.1.0`

## 1. 目标

本规范回答四个不同问题：

1. 某主体是否可以在当前环境读取内容；
2. LoreBuddy 是否有权保存、转换或再分发内容；
3. 公开 Package 可以披露哪些 Provenance、Dependency 和 Review 字段；
4. Release Archive 中究竟允许出现哪些文件。

访问控制（Access Control）、权利（Rights）、来源权威（Authority）和规范性（Normativity）互不替代。`visibility: public` 不是版权许可；“官方”也不自动表示允许复制或再分发。

## 2. Access Policy

`public | restricted | private` 是发布类别，不是一个足以授权读取的线性安全等级。两个不同 Campaign 的私有域通常互不可读。

Access Domain 与 Access Policy 分别存放于 `metadata/policies/access-domains/`、`metadata/policies/access/`；Rights Claim / Decision 存放于 `metadata/rights/`；Disclosure Approval 存放于 `metadata/disclosures/approvals/`。它们都是 Content Manifest 覆盖的人工事实。

Package Manifest 必须引用 Access Policy：

```yaml
access:
  visibility: "restricted"
  access_domain_id: "urn:uuid:..."
  policy_id: "urn:uuid:..."
```

- `public`：`access_domain_id` 必须解析到标记为匿名可读的公共 Access Domain Record；
- `restricted`：面向一个组织、项目或授权群体；
- `private`：面向更窄主体，但不暗示任意 Private Package 彼此可见；
- `access_domain_id` 解析到唯一 `core.access-domain@0.1.0` Record；`policy_id` 解析到 `core.access-policy@0.1.0` Record，且 `policy.domain_id` 必须逐字等于 Manifest 的 `access_domain_id`；
- Policy 保存允许的 Principal、Role 或外部策略引用，不把 Secret 写进 Package。

Domain 与 Policy Record 必须位于当前 Package 或可读且已锁定的 Content Dependency，并进入相应 Content Manifest；无法唯一解析、Digest 不符或 Domain 不一致都必须阻塞。

外部策略引用必须使用不可变三元组 `{id, version, digest}`，在授权域的 Build Lock 中物化为本地快照；构建时禁止联网解析“当前版本”。每次依赖授权判断必须在受限 Audit / Build Package 保存 `core.access-decision-receipt@0.1.0`：固定 Build Lock Digest、Dependency Reference、Principal ID、Dependency Access Domain ID、Policy ID / Version / Digest、Evaluator ID / Version / Digest、判定与有效期。Principal、私有 Domain、Policy Digest 和受限 Dependency 身份默认禁止投影进 Public Package；公开侧只通过批准的 Public Build Attestation 声明 `access_review: attested`。

```yaml
schema: "core.access-decision-receipt@0.1.0"
id: "urn:uuid:..."
build_lock_digest: "sha256:..."
evaluation_as_of: "2026-07-20T00:00:00Z"
dependency_ref: {}
principal_id: "urn:uuid:..."
dependency_access_domain_id: "urn:uuid:..."
action: "read"
policy:
  id: "urn:uuid:..."
  version: "1.2.0"
  digest: "sha256:..."
evaluator:
  id: "..."
  version: "..."
  digest: "sha256:..."
decision: "allowed"
validity: {}
```

依赖是否合法由 `can_read(build_principal, dependency_access_domain)` 判定，不能只比较三个 Visibility 字符串。Campaign A 的构建主体没有 Campaign B 权限时，即使两者都是 `private`，依赖仍必须失败。

Package 是最小访问边界。同一 Package 内若某个 Review、Asset 或 Locator 需要更严格的 Access Domain，必须移动到独立 Audit / Content Package，并在当前 Package 中保留批准的投影；不采用难以防止 Index / Log 泄漏的逐文件隐式 ACL。

### 2.1 固定评估时点

Release Candidate 必须由调用方显式提供一个 RFC 3339 UTC `evaluation_as_of`，并写入 Release Manifest、Rights Decision 与 Release Rights Binding。Access Decision Receipt、Rights Claim / Decision、Disclosure Approval、Attestation 和 Binding 的 Lifecycle / Validity 全部只在该同一时点评估。构建器不得读取系统“当前时间”填充或重放门禁；改变评估时点是一次显式的新发布输入，必须重新生成 Decision、Approval / Attestation 和 Binding。消费者可以另外判断现实当前时间是否已经超过有效期，但不得把该动态判断伪装成原 Release 的可重现结论。

### 2.2 权利治理域与审计上下文

权利治理域（Rights Authority Domain）回答“谁有权签发 Claim、Decision 与最终 Binding”，访问域（Access Domain）回答“谁能读取这些 Record”。两者正交；Public Package 与受限 Audit Package 必然可以拥有不同 Access Domain，但必须在同一明确的 Rights Authority Domain 中完成发布审核。

目标 Package 的 `rights.authority_domain_id` 与 Release Manifest 的 `rights.authority_domain_id` 必须相等，并在受限 Audit Context 中唯一解析到 Active `core.rights-authority-domain@0.1.0`。Release 动作使用的 Rights Decision 与 Release Rights Binding 必须共同存在于目标 Release 之外的同一个 `core.audit` Package。该 Audit Package 在 `metadata/rights/authority-delegations/` 保存或通过 Lock 引用 Active `core.rights-authority-delegation@0.1.0`；Delegation 至少固定 Authority Domain `{id,digest}`、Delegate Party / Package、`issue-claim | withdraw-claim | issue-decision | issue-binding` Capability、Subject / Action Scope、Reviewer / Evidence、Validity 与 Lifecycle。签发 Release Decision / Binding 的 Delegation 必须同时覆盖当前 Audit Package、目标 Package 和动作。Audit Package 的 `package.lock.json` 是本次受限 Audit Context Lock，必须锁定目标 Package 身份与 Package Lock、全部外部 Claim Source 及其 Claim Authority、Build / Audit Input、Schema、Registry 和评估工具；Decision 与 Binding 都固定该 Lock Digest，并另存 Audit Package 自身的 `owner_claims_root_digest`。所有者不能在 Lock 中自引用自身 Content Manifest；若不是 Claim Lineage Genesis，其直接前驱 Audit Package Version 必须作为 `claim-source` 锁定。Audit Context Lock 与 Decision 禁止携带目标 Release Manifest、Content / Library / Index Root 或最终 Payload Inventory Digest；这些最终字节事实只能首次出现在 Release Rights Binding，避免经 Lock 间接恢复摘要递归。

授权验证器必须先按 Access Policy 证明其可读取 Audit Package，再验证 Delegation 覆盖当前目标、动作和 `evaluation_as_of`。在该锁定上下文内，`release_binding_id` 必须唯一解析到一条 Active Binding；零条或多条都阻塞。Public Reader 无权读取 Audit Context 时只能验证 Public Attestation，不能声称独立重放私有 Rights Decision。Rights Authority Domain 本身不是法律授权事实的自动证明，仍以 Reviewer、Evidence 和可信分发的 Audit Context 摘要为信任根。

### 2.3 目标候选锁

Audit Context Lock 对目标 Package 必须使用 `core.rights-target-candidate-lock@0.1.0`，不能复用要求最终 Manifest Digest 的普通 Dependency 项。其 JCS 对象只允许包含：`package_id`、`package_version`、`action`、`package_manifest_digest`、`package_lock_digest`、锁定的 Release File Role / Subject Expansion / Claim Selection Registry `{id,digest}`，以及预分配的 `release_binding_id`、Public 模式的 `public_rights_attestation_id`。Domain Prefix 为 `lorebuddy-rights-target-candidate-lock-v1\n`，JCS Object 后追加 LF 再取 SHA-256，得到 `target_candidate_lock_digest`。

该对象禁止包含 Content / Library / Index Root、Output / Release Manifest Digest、Decision Digest、Binding Digest 或 Payload Inventory Digest。Decision 固定 `target_candidate_lock_digest`；Binding Validator 再要求其中 Package / Registry / 预分配 ID 与目标 Candidate 逐字段相等。这样 Direct 模式只有 `Release Manifest → Decision → Target Candidate Lock`，Lock 不再反向引用 Release Manifest；最终字节仍只由外部 Binding 固定。

## 3. Rights Claim

Rights Claim 可以作用于 Package、Work、Edition、Artifact、Entry、Fragment、Node、Asset、Receipt、Attestation 或其他规范 Metadata Record。Work、Edition、Artifact 的 `rights_claim_ids[]` 与 Package Manifest 的 `rights.claim_ids[]` 只是对 `metadata/rights/claims/` 的引用，不是第二份权利事实源：

```yaml
schema: "core.rights-claim@0.1.0"
id: "urn:uuid:..."
subject:
  kind: "artifact"
  id: "urn:uuid:..."
authority:
  domain:
    id: "urn:uuid:..."
    digest: "sha256:..."
  delegation:
    id: "urn:uuid:..."
    digest: "sha256:..."
  issuer_party_id: "urn:uuid:..."
permissions:
  preserve: "allowed"
  extract: "allowed"
  format_transform: "unknown"
  create_derivative: "unknown"
  redistribute_source: "denied"
  redistribute_transcription: "unknown"
  redistribute_asset: "unknown"
  publish_metadata: "allowed"
  publish_receipt: "unknown"
basis: "..."
evidence_ids: []
review:
  status: "approved"
  review_id: "urn:uuid:..."
validity: {}
lifecycle:
  status: "active"
  revision: 1
```

每项权限只允许：

- `allowed`：有审核证据支持；
- `denied`：明确不允许；
- `unknown`：尚未证明；
- `not-applicable`：该对象与动作无关。

默认规则是拒绝：`unknown` 不能被当作 `allowed`。自由文本 Notes 可以解释证据，但不能改变机器判定。

`evidence_ids[]` 只能解析到同一可读 Access Domain 中 Active 的 `core.evidence@0.1.0`，或公开 Package 中 Active 的 `core.public-evidence-receipt@0.1.0`；Rights Claim 不得直接混用任意 URL、Fragment、合同、Review 或私有 Evidence ID。Public Receipt 只提供 `attested` 证据等级，完整 Evidence 的敏感 Locator 与内容仍受自身 Access / Disclosure 约束。

Claim 的 `authority.domain` 与 `delegation` 都使用 `{id,digest}`，并必须在受限 Audit Context 中唯一解析。Delegation 必须在 `evaluation_as_of` 为 Active，包含 `issue-claim` Capability，Delegate 必须等于 Claim 的 Issuer，Subject / Permission / Scope 必须覆盖该 Claim；Review 必须为 `approved` 且 Review / Reviewer / Evidence 可解析。Claim Authority 可以不同于 Release Decision 的 Authority Domain，但必须列入 Audit Context Lock 的 Accepted Claim Authority Set。

Schema 可以保存 `review.status: pending` 的 Draft Claim，但它不能授予权限。除被有效授权 Tombstone 抑制外，所有 Lifecycle 为 Active、Subject / Scope 可能适用的 Claim 都进入 Selected Set：只有 Authority 与 Review 均通过的 Claim 使用声明权限；缺失 Authority、未授权、Pending / Rejected Review 或不可读 Evidence 一律把相关权限视为 `unknown`，增加 `unresolved_claim_count` 与 `unauthorized_claim_count`，并阻止 `allowed`。这样目标 Package 自行加入一条 Pending `allowed` Claim 不能抬高发布结论。

### 3.1 权限合并

对某个发布动作，先为 Release Payload 中每个文件建立 `{path, role, subject_ids, required_permissions}` Coverage Record。`subject_ids` 至少包含目标 Package ID，并按版本化 `core.rights-subject-expansion@0.1.0` 反复应用下列边直到不再出现新 Subject；它是确定性传递闭包，不接受作者白名单：

- `source-artifact` 文件加入 Artifact，以及锁定 Inventory 中代表容器物理内容的每一个 Entry，不受 Entry Lifecycle 影响；每个 Entry 继续沿下述 Entry 边展开；
- `source-metadata` 的 `artifact.yaml` 加入 Artifact；`inventory.jsonl` / `path-map.jsonl` 加入 Artifact 与其中代表的每一个物理 Entry，并继续沿 Entry 边展开；
- `source-entry` / `source-asset` 加入 Entry 与 Artifact；Entry 沿全部审核 Source Mapping 加入 Edition → Work，并加入所有直接以该 Entry 为 Source、或 Transformation Input 可传递回该 Entry 的 Asset Subject；Asset 再反向闭合其 Source Entry / Transformation Input；
- `source-fragment-evidence` 的 Fragment Record 与 Event Stream 都加入 Fragment，并展开 Fragment → Entry → Artifact → Edition → Work；Event Stream 不因缺少独立 Record ID 而降级为普通 Metadata；
- `knowledge-node` 加入 Node，并沿每条正文 Provenance 展开 Fragment → Entry → Artifact → Edition → Work；`library-asset` 加入 Asset，并沿 Asset Record / Transformation 展开到全部 Source Entry，再继续应用 Entry 边；
- Receipt / Attestation / Approval 加入自身及其公开 Subject；Metadata 文件加入其中定义的规范 Record；派生 Index 加入 Package 与该分片实际投影的全部规范 Subject；
- Manifest / Lock 至少加入 Package 与其实际引用的 Dependency、Schema / Registry、Receipt / Attestation / Approval Subject；Public Release Manifest 还必须加入其内联 Public Rights Attestation 自身。

Inventory / Path Map 不完整、Artifact 中物理 Entry 未被 Inventory 表示、Source Mapping 未决、Asset Transformation 无法回溯、Index Projection 无法枚举、Subject 不可读或展开有歧义时，该文件未覆盖并阻塞。这样 Artifact 级 `allowed` 不能掩盖非 Active Entry、内部图片 Entry、Edition / Work 或 Asset 上的 `denied`。

Claim 选择采用闭包扫描，不信任调用方传入列表。种子集合必须包含目标 Package、Release Decision 所在 Audit Package、该 Audit Package Lock 中声明的每个 `claim-source` 与 `build | audit-input`、目标 Package 的所有 Content Dependency，以及 Provenance、Asset、Receipt 或 Attestation 引出的全部可读 Claim Source Package；继续沿锁定的 Claim Source 边展开到闭包。Decision 的 `audit_context.package_id / package_version / lock_digest / owner_claims_root_digest` 固定所有者与受限上下文，遗漏所有者自身或任一锁定 Claim Source 都阻塞。每个来源的 Rights Claim 文件子集计算独立 `claims_root_digest`；所有来源的 `{package_id, package_version, claims_root_digest}` 按 Package ID / Version UTF-8 bytes 排序，使用 Prefix `lorebuddy-rights-claim-universe-v1\n`、逐条 JCS Object 与 LF 计算 `claim_universe_digest`。Universe 包含 Active、Inactive 与 Tombstone，避免删除或停用 Claim 后旧 Decision 仍被误认为当前。

每个 `claims_root_digest` 使用 Prefix `lorebuddy-rights-claims-root-v1\n`，对该 Package 的 `metadata/rights/claims/**`，以及以 Rights Claim 为目标的 Tombstone 文件记录 `{path,size,digest,record_kind}` 按 Path UTF-8 bytes 排序、逐条写 JCS Object 与 LF 后计算。单个 Package 内相同 Claim ID 的重复文件、未墓碑删除或摘要冲突都阻塞。整个 Universe 还必须满足：多条发现路径得到的完全相同 `{package_id,package_version,claims_root_digest}` 先折叠为一个 Source；同一 `{package_id,package_version}` 若对应不同 Root 则阻塞；每个规范 Claim ID 在所有 Claim Source 中全局唯一；同 ID 同摘要的重复副本也阻塞，同 ID 不同摘要同时作为身份冲突阻塞。Tombstone 自身 Record ID 同样全局唯一，其 `target_claim_id` 必须唯一指向被替代身份。所有唯一性检查在排序和 Selected Set 计算前执行，禁止依赖并列顺序消歧。

Claim Source 使用追加式 `core.rights-claim-lineage@0.1.0`。每个 `claim-source` Lock 项除当前 Root 外，还固定直接前驱 `{package_version,claims_root_digest}`；首版前驱为 `null`，并要求 Approved Genesis Review。Validator 必须沿前驱链走到 Genesis：当前 Claim / Tombstone `{path,size,digest,record_kind}` 集合必须包含前驱集合的逐字不变超集，任何旧 Record 删除、改写或换 Path 都阻塞。Rights Claim 发布后不可原地改权限、Authority、Review 或 Lifecycle；撤回时保留原 Claim 并追加带新 UUID 的 Tombstone，替换时 Tombstone 明列 Replacement Claim ID。Tombstone 本身必须具有 Authority / Issuer / Approved Review，Delegation 包含 `withdraw-claim` 并覆盖目标 Claim；未授权 Tombstone 不抑制原 Claim，且计为 unresolved。

`claim_lineage_digest` 使用 Prefix `lorebuddy-rights-claim-lineage-v1\n`，对每个 Claim Source 的 `{package_id,package_version,claims_root_digest,predecessor_package_version,predecessor_claims_root_digest,genesis_review_id_or_null}` 按 Package ID / Version 排序、逐条写 JCS Object 与 LF 后计算。循环、缺失前驱、多个直接前驱、不可读历史或集合差分未由追加 Record 表达都阻塞。只有 Valid、Active 且授权的 Tombstone 才在选择前抑制目标 Claim；旧 `denied` 因此不能通过发布一个省略它的新 Package Version 静默消失。

在该 Universe 中先按 Claim Lineage 验证 Tombstone，再选择固定评估时点为 Active、未被有效 Tombstone 抑制、且 `subject.id` 出现在任一 Coverage Record `subject_ids` 中、Scope 可适用的全部 Rights Claim；Scope 无法证明不适用时以 `unknown` 参与。`claim_inputs[]` 必须与该集合按 Claim ID UTF-8 bytes 排序后逐项完全相等，不能漏掉一条 `denied`。选中集合的 `selected_claim_set_digest` 使用 Prefix `lorebuddy-rights-selected-claims-v1\n`，对 `{id,digest}` 排序记录流计算。Package Manifest、Work、Edition、Artifact 等对象上的 `rights_claim_ids[]` 只是便于发现和交叉验证的反向完整性断言，不是选择器；它们必须等于同一 Package 中以该对象为 Subject 的 Claim Ledger 集合，少列、多列或 Subject 不符都阻塞。现实世界中未被登记到任何受控 Claim Source 的事实仍无法自动发现，这是 Reviewer 与治理流程的边界，不能用算法声称已经证明。

Accepted Claim Authority Set 使用 Prefix `lorebuddy-rights-claim-authorities-v1\n`，对 Audit Context Lock 中获准的 `{authority_domain_id,authority_domain_digest,delegation_id,delegation_digest,delegate_id,capabilities}` JCS Record 按前五个字段的 UTF-8 bytes 排序后计算 `claim_authority_set_digest`；Capability 数组先按 UTF-8 bytes 排序。每条可能适用的 Claim 与 Tombstone 都生成 `{record_id,record_kind,record_digest,authority_status,review_id,review_digest}`，按 `(record_id,record_kind)` 排序并用 Prefix `lorebuddy-rights-claim-authority-evaluations-v1\n` 计算 `claim_authority_evaluation_digest`。`authority_status` 只允许 `approved | unresolved`；未授权 Tombstone 不抑制目标 Claim，未授权 Claim 的相关权限按 `unknown` 合并。Decision 必须保存两个 Digest、`unauthorized_claim_count` 和 `unresolved_claim_count`，重放时逐条重算。

任一外部 Claim Source 不可读、Content Manifest 不完整、锁定 `claims_root_digest` 不符、Claim / Tombstone 无法解析、Subject Closure 有歧义或 `unresolved_claim_count > 0` 时，Decision 不得产生 `allowed`；若没有更强的显式 `denied`，结果为 `unknown`。Decision Owner 自身不要求尚未完成的 Content Manifest，而是直接扫描其 Claim / Tombstone 子集并要求结果等于 `audit_context.owner_claims_root_digest`；其他校验相同。`claim_universe_count` 统计 Universe 中 Claim 与 Claim Tombstone Record 数；`selected_claim_count` 必须等于 `claim_inputs[]` 长度。

选定 Claim 按权限项合并：

```text
任一 denied       → denied
否则任一 unknown  → unknown
否则全部 allowed 或 not-applicable，且至少一个 allowed → allowed
否则              → unknown
```

更具体 Subject 可以补充事实，但不能覆盖上层明确 `denied`。真正需要例外时必须有独立、带范围和失效条件的 Rights Review，不允许靠字段覆盖实现。

公开转写 Package 至少要求 `create_derivative`、`redistribute_transcription`、`publish_metadata` 为 `allowed`；包含原始 HTML/图片时还分别要求 `redistribute_source` / `redistribute_asset`。仅有 `preserve: allowed` 不能推出任何公开权利。

合并结果必须固化为 `core.rights-decision@0.1.0`，至少记录目标发布动作、显式 `evaluation_as_of`、目标 Package Lock Digest、Rights Authority / Audit Context、Claim 选择/Subject 展开算法、Claim Universe / Selected Set 摘要与计数、参与 Claim 的 `{id, digest}`、逐权限结果、Reviewer、有效期、语义 Coverage Digest、覆盖统计和最终 `allowed | denied | unknown`。生成器不得现场读取自由文本自行决定。Decision 只绑定不含文件摘要的语义 Coverage；它不得保存当前 Release Manifest Digest、Content Root 或最终 Payload Inventory Digest，否则会重新混合语义判定与最终字节绑定。

```yaml
schema: "core.rights-decision@0.1.0"
id: "urn:uuid:..."
release_subject:
  package_id: "urn:uuid:..."
  package_version: "0.1.0"
  action: "public-release"
evaluation_as_of: "2026-07-20T00:00:00Z"
authority:
  rights_authority_domain_id: "urn:uuid:..."
  rights_authority_domain_digest: "sha256:..."
  delegation:
    id: "urn:uuid:..."
    digest: "sha256:..."
audit_context:
  package_id: "urn:uuid:..."
  package_version: "0.1.0"
  lock_digest: "sha256:..."
  owner_claims_root_digest: "sha256:..."
target_package_lock_digest: "sha256:..."
target_candidate_lock_digest: "sha256:..."
claim_selection:
  algorithm: "core.rights-claim-selection@0.1.0"
  subject_expansion: "core.rights-subject-expansion@0.1.0"
  claim_universe_digest: "sha256:..."
  claim_universe_count: 100
  claim_lineage_digest: "sha256:..."
  selected_claim_set_digest: "sha256:..."
  selected_claim_count: 42
  claim_authority_set_digest: "sha256:..."
  claim_authority_evaluation_digest: "sha256:..."
  unauthorized_claim_count: 0
  unresolved_claim_count: 0
claim_inputs:
  - id: "urn:uuid:..."
    digest: "sha256:..."
coverage:
  algorithm: "core.rights-coverage@0.1.0"
  subject_inventory_digest: "sha256:..."
  total_files: 1234
  uncovered_files: 0
  result: "complete"
permission_results: {}
result: "allowed"
reviewer_id: "urn:uuid:..."
validity: {}
lifecycle:
  status: "active"
  revision: 1
```

Rights Coverage 对每个最终 Payload File 执行，默认拒绝：

| 注册文件角色 | 至少需要的权限 |
|---|---|
| `source-artifact` | `redistribute_source`；其 Inventory 含任一 `source-asset` Entry 时再要求 `redistribute_asset` |
| `source-metadata` | `publish_metadata` |
| `source-entry` | `redistribute_source` |
| `source-asset` | `redistribute_source`、`redistribute_asset` |
| `source-fragment-evidence` | `redistribute_source`、`publish_metadata` |
| `knowledge-node` | `create_derivative`、`redistribute_transcription`、`publish_metadata` |
| `library-asset` | `redistribute_asset`；存在格式/尺寸/内容变换时再要求 `create_derivative` |
| `source-receipt`、`receipt-attestation` | `publish_receipt`、`publish_metadata` |
| `package-control`、`package-instructions`、`metadata-record`、`schema-document`、`registry-document`、`derived-index`、`content-manifest`、`output-manifest` | `publish_metadata` |
| `release-manifest` | `publish_metadata`；`rights.mode: public-attestation` 时条件性再要求 `publish_receipt` |

Package 级 Claim 可以为控制、Metadata 和派生 Index 提供 `publish_metadata` 覆盖；Node、Source、Asset 或 Receipt 的更具体 Claim 仍共同参与合并，不能覆盖上层 `denied`。每个文件必须有至少一个适用 `allowed` Claim，任何未覆盖、`unknown` 或 `denied` 都阻塞。文件 `role` 必须来自 Lock 固定的 `core.release-file-roles@0.1.0`；未知或在 Content / Output / Payload Inventory 间不一致的角色阻塞。Decision 的 Coverage 固定 `{path, role, subject_ids, required_permissions}` 记录按 Path 排序后的摘要、总文件数与未覆盖数。

内联 Public Rights Attestation 不拥有第二个文件角色，但它不是权限例外：当 `release-manifest` 的 `rights.mode` 为 `public-attestation` 时，该文件的 `subject_ids` 必须包含 Attestation ID，`required_permissions` 必须包含 `publish_receipt`。Direct 模式不得无条件继承该权限。遗漏条件权限会改变 Coverage Digest 并阻塞。

`subject_inventory_digest` 使用 Prefix `lorebuddy-rights-coverage-v1\n`，随后按 `path` UTF-8 bytes 排序，逐条写入上述字段的 JCS Object 与 LF。`subject_ids` 与 `required_permissions` 在每条记录内按 UTF-8 bytes 排序。任何同 Path 重复记录必须先阻塞，不能参与摘要。

最终字节绑定使用目标 Release 之外、属于同一 Rights Authority Domain 但可处于不同 Access Domain 的 Audit Package 中的 `core.release-rights-binding@0.1.0`。它与所引 Release Rights Decision 共同存放于该 Audit Package，Binding 位于 `metadata/rights/release-bindings/`，不得进入被绑定 Release 的 Content、Index 或 Archive。最小结构为：

```yaml
schema: "core.release-rights-binding@0.1.0"
id: "urn:uuid:..."
release_subject:
  package_id: "urn:uuid:..."
  package_version: "0.1.0"
  action: "public-release"
evaluation_as_of: "2026-07-20T00:00:00Z"
authority:
  rights_authority_domain_id: "urn:uuid:..."
  rights_authority_domain_digest: "sha256:..."
  delegation:
    id: "urn:uuid:..."
    digest: "sha256:..."
audit_context:
  package_id: "urn:uuid:..."
  package_version: "0.1.0"
  lock_digest: "sha256:..."
  owner_claims_root_digest: "sha256:..."
rights_decision:
  id: "urn:uuid:..."
  digest: "sha256:..."
subject_inventory_digest: "sha256:..."
selected_claim_set_digest: "sha256:..."
release:
  release_manifest_digest: "sha256:..."
  content_manifest_digest: "sha256:..."
  content_root_digest: "sha256:..."
  library_root_digest: "sha256:..."
  output_manifest_digest: "sha256:..."
  index_root_digest: "sha256:..."
  payload_policy:
    id: "core.release-payload@0.1.0"
    digest: "sha256:..."
  payload_file_count: 1234
  payload_inventory_digest: "sha256:..."
public_rights_attestation:
  id: "urn:uuid:..."
  digest: "sha256:..."
disclosure_approval:
  id: "urn:uuid:..."
  digest: "sha256:..."
reviewer_id: "urn:uuid:..."
validity: {}
lifecycle:
  status: "active"
  revision: 1
```

`payload_inventory_digest` 使用 Prefix `lorebuddy-release-payload-inventory-v1\n`，对最终 `{path,size,digest,role}` 记录按 Path UTF-8 bytes 排序、逐条写 JCS Object 与 LF 后计算；该集合包含 `release-manifest.json`。Binding 位于外部 Audit Package，因此可以同时固定 Release Manifest 自身摘要和完整 Payload，而不产生自引用。其 ID 必须在组装 Candidate 前随机预分配。Public 模式要求 `public_rights_attestation` 与 `disclosure_approval`，Direct 模式两者必须为 JSON / YAML `null`。Restricted / Direct Release 与 Public Release 都必须有 Active Binding；目标 Release Manifest 只携带该预分配 ID，不携带 Binding Digest，后者由 Audit Package 的 Content Manifest 验证。

### 3.2 Release Rights Binding 验证协议

协议 ID：`core.release-rights-binding-validation@0.1.0`。Validator 不得只验证字段存在，必须在锁定 Audit Context 中执行以下逐字段等式；任一不等、不可解析或多重解析都阻塞：

1. 唯一 Active Binding 的 `id` 必须等于目标 Manifest 的 `rights.release_binding_id`；Binding 所在 Package 必须等于 Decision 与 Binding 的 `audit_context.package_id / package_version`，其 `package.lock.json` 摘要必须等于两者的 `audit_context.lock_digest`，自身 Claim / Tombstone 子集摘要必须等于两者的 `owner_claims_root_digest`；
2. Binding 与 Decision 的 `authority` 逐字段相等；Delegation 的 `{id,digest}` 必须解析到覆盖目标 Package、动作与 `evaluation_as_of` 的 Active Record；目标 Package Manifest、Release Manifest、Decision 与 Binding 的 `rights_authority_domain_id` 必须全部相等；
3. Binding、Decision 与 Release Manifest 的目标 Package ID / Version、发布动作和 `evaluation_as_of` 必须相等；Decision 的 `target_candidate_lock_digest` 必须按第 2.3 节重算，且 Package / Registry / 预分配 ID 与当前 Candidate 相等；Binding 的 `rights_decision.{id,digest}` 必须解析到同一 Audit Package 中唯一 Active Decision；
4. Binding 的 `subject_inventory_digest`、`selected_claim_set_digest` 必须分别等于 Decision 的 Coverage / Claim Selection 字段；Decision 的 Claim Lineage、Authority Set 与 Authority Evaluation Digest 必须由锁定 Audit Context 重算相等；Decision 必须为 `result: allowed`、Coverage Complete、零未覆盖文件、零未授权 Claim、零未解析 Claim，并在评估时点有效；
5. Validator 必须从最终 Archive 的实际文件集合重新派发 File Role，并以锁定的 Subject Expansion、Claim Universe 和 Required Permission 表重算 `{path,role,subject_ids,required_permissions}`；所得 Coverage Digest、文件数和逐权限结论必须与 Decision 完全相等；
6. 对目标 `release-manifest.json` 实际字节重算摘要，并要求 Binding 的 Release Manifest、Content Manifest、Content / Library / Index Root、Output Manifest、Payload Policy 和文件数逐字段等于 Manifest 及其所引 Manifest；
7. 按最终 Archive 实际 `{path,size,digest,role}` 重算 Payload Inventory；集合必须精确等于 Release Payload 白名单并包含 Release Manifest 自身。重算 Digest 只与外部 Binding 的 `payload_inventory_digest` 比较；该 Digest 禁止进入目标 Manifest，否则形成自引用。重算文件数同时等于 Binding 与 Manifest；
8. Public 模式对内联 Public Rights Attestation 计算规范子对象摘要，要求其 `{id,digest}` 等于 Binding，且 Attestation 的 `action` 等于 Rights Wrapper；Binding 的 Disclosure Approval 必须唯一解析，且其 ID 等于 Attestation 的 `disclosure_approval_id`，Profile / Projection / Subject Digest 与当前内联值完全相等。Direct 模式要求 Binding 的两个公开字段均为 `null`，Manifest 的 Decision `{id,digest}` 与 Binding 所引 Decision 完全相等；
9. `core.audit-binding@0.1.0` 所引 Release Rights Binding `{id,digest}` 必须是上述同一 Record，不能复制或覆盖任何最终 Release 字段。

该协议的输出是 Pass / Fail，不产生可覆盖原字段的“修正后 Binding”。通过 Schema 但未通过这些等式的 Record 不得参与 Release Ready 判定。

Public Release 的完整 Rights Decision、Reviewer、Claim 身份与 Release Rights Binding 保存于受限 Audit Package。公开 `release-manifest.json` 只内联随机 ID 的 `core.public-rights-attestation@0.1.0`；该对象按父 Manifest 语义绑定 Package ID / Version、`evaluation_as_of`、Content / Library / Index Root、Payload Policy 和文件数，但不得包含私有 Decision、Claim、Reviewer 或 Evidence ID。Restricted Release 只有在 Release Reader 可读取已授权 Audit Context 时，才可以使用 `rights.mode: direct` 引用其中 Active Decision 的 ID 与 Digest；Access Domain 无需与目标 Package 相同。

```json
{
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
```

该 Attestation 的完整 Disclosure Approval、Rights Decision 与 Release Rights Binding 都由受限 Audit Binding 固定；公开 Manifest 的 Rights Wrapper 只携带预分配的 `release_binding_id`、获准的 Profile、Approval 引用与随机 Attestation ID。Approval 的 Subject Revision 必须等于 `lifecycle.revision`，并在 `evaluation_as_of` 有效。不得把引用 Content Root 的 Approval 放回当前 Content Manifest，否则形成摘要循环。Public Package 的 `package.yaml` 只预先引用 `rights.mode: public-attestation + public_rights_attestation_id`，不引用 Attestation Digest。

## 4. Provenance 的两种披露模式

完整 Locator 可能包含受限路径、Text Quote、字节范围、内部 Package ID 或内容摘要。Node Provenance 因此使用显式联合类型。

### 4.1 `embedded-fragment`

适用于消费者有权读取完整 Source Evidence 的 Package：

```yaml
mode: "embedded-fragment"
fragment_id: "urn:uuid:..."
source_mapping_ids:
  - "urn:uuid:..."
locator: {}
```

要求：

- Fragment 和 Source Mapping 在当前 Package 或可读 Content Dependency 中可解析；
- Entry、Artifact 与 Locator 摘要全部验证；
- Traceability 等级为 `full`。

### 4.2 `external-public-receipt`

适用于公开派生 Package 无权披露完整 Source Evidence 的情况：

```yaml
mode: "external-public-receipt"
receipt_id: "urn:uuid:..."
receipt_digest: "sha256:..."
traceability: "attested"
```

Receipt 使用 `core.public-provenance-receipt@0.1.0`，存放于 `metadata/provenance-receipts/`：

```yaml
schema: "core.public-provenance-receipt@0.1.0"
id: "urn:uuid:..."
claim:
  status: "reviewed"
  public_source_labels: []
audit_holder_party_id: "urn:uuid:..."
issued_for:
  node_id: "urn:uuid:..."
  node_revision: 1
  provenance_id: "urn:uuid:..."
  body_utf8_ranges:
    - start: 0
      end: 1234
  body_byte_digest: "sha256:..."
  visible_text_digest:
    algorithm: "core.visible-text-events@0.1.0"
    value: "sha256:..."
  structure_digest:
    algorithm: "core.structure-events@0.1.0"
    value: "sha256:..."
disclosure_profile:
  id: "core.provenance-public-minimal@0.1.0"
  digest: "sha256:..."
disclosure_approval_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

Provenance Receipt 不包含 Fidelity 结论；保真声明必须使用独立 Public Fidelity Attestation，并由 Node 的 `fidelity_evidence.assertions[]` 对正文范围引用。`issued_for.body_utf8_ranges` 必须逐字段等于该 `provenance_id` 在全部 Active Fidelity Coverage Map Unit 中 Range 的规范并集，不能另填一个宽泛范围。

公开 Receipt 的 UUID 必须随机分配，不能由私有 Package、Fragment、Artifact 或摘要确定性派生。默认禁止包含：

- 私有/受限 Package ID、版本、路径或解析 URI；
- Artifact、Entry、Fragment 或私有 Manifest Digest；
- Text Quote、Byte Range、DOM Selector、内部导航路径；
- 未经批准的 Work / Edition、人员或合同信息。

允许字段由版本化 Disclosure Profile 逐字段白名单控制。Profile 是 Schema / Registry Document，存放于平台或 Package 的 `registries/disclosure-profiles/`，使用带 SemVer 的 Document ID，并由 `package.lock.json` 固定本地 Path 与 Digest。最小字段包括适用 Subject Schema、Projection Algorithm、允许/必需 JSON Pointer Pattern 与值约束；未允许的字段默认拒绝。Release Manifest 必须列出实际使用的 `{id, digest}`，禁止通过网络解析同名最新版。

每个 Receipt / Attestation 还必须引用 `core.disclosure-approval@0.1.0`。Approval 至少固定：Subject Schema / ID / Revision、Subject Digest、Disclosure Profile ID / Digest、实际公开叶子字段的 JSON Pointer 集合、Projection Algorithm、`approved_projection_digest`、目标 Visibility / Access Domain、公开 Reviewer 投影、有效期与状态。完整 Reviewer、证据和拒绝理由留在受限 Audit Package。

Approval 的 `subject_digest` 使用 Prefix `lorebuddy-disclosure-subject-v1\n` + 最终公开 Subject 完整解析值的 JCS bytes + LF 计算。`core.disclosure-projection@0.1.0` 的摘要输入为 UTF-8 Prefix `lorebuddy-disclosure-projection-v1\n`、一个 JCS Object 和 LF。Object 固定为 `{subject:{schema,id,revision},bindings:[...]}`；`bindings` 为最终公开 Subject 中所有叶子值的 `{pointer,value}`，按 Pointer UTF-8 bytes 排序，数组使用精确索引 Pointer。叶子 Pointer 集合必须与 Approval 的 `approved_pointers` 完全相等，并全部通过 Profile 白名单和值约束。`disclosure_approval_id` 是预分配 UUID，可以参与投影；Subject 禁止包含 `approved_projection_digest` 本身。任一公开值、数组顺序或 Revision 变化都必须重新审批。

公开 Receipt 是审核声明，不是完整 Source 的替代品。公开消费者可以验证 Receipt 属于当前 Release，但不能据此独立重放私有 Source；因此生成的 Release Manifest 必须把 Traceability Aggregate 标记为 `attested`，禁止声称 `full`。已授权 Rights Authority Audit Context 中的独立 Audit Package 使用 `core.audit-binding@0.1.0` 保存 `receipt_id → private Fragment / Mapping / Review` 的完整映射；该 Binding 进入 Audit Package Content Manifest，公开 Package 不得携带。

## 5. Receipt / Attestation 不得混用

| 类型 | 位置 | 默认可公开 | 职责 |
|---|---|---:|---|
| Extraction / Analysis Receipt | Source Artifact `receipts/` | 否 | 证明解包、解析、工具和统计 |
| Public Provenance Receipt | 公开 Package `metadata/provenance-receipts/` | 经批准 | 公开最小来源审核声明 |
| Public Evidence Receipt | 公开 Package `metadata/evidence/public-receipts/` | 经批准 | 以随机新 ID 提供 Attested Evidence，不披露私有 Evidence 身份或 Locator |
| Public Party Projection | 公开 Package `metadata/parties/public-projections/` | 经批准 | 为责任字段提供随机公开 Party ID，不复制私有 Party ID |
| Public Build Attestation | 公开 Package `metadata/attestations/` | 经批准 | 说明输出由受限构建完成，但不暴露输入身份 |
| Public Fidelity Attestation | 公开 Package `metadata/attestations/` | 经批准 | 声明 Source / Library 保真检查已通过，不披露私有 Source Event Digest |
| Public Rights Attestation | Public `release-manifest.json` 内联 | 经批准 | 绑定最终发布根与完整 Rights Coverage，不披露私有 Decision / Claim / Reviewer |
| Release Rights Binding | Restricted Audit Package `metadata/rights/release-bindings/` | 否 | 把 Rights Decision 绑定到最终 Release Manifest 与完整 Payload 字节 |
| Audit Binding | Restricted Audit Package `metadata/audit-bindings/` | 否 | 把随机 Public ID 映射回完整私有证据、Decision、Lock 和目标 Release |
| Full Review / Evidence | Restricted Audit Package | 否 | 保存人员、证据、私有 Locator、完整依赖和法律/授权判断 |

摘要是内容指纹，不是天然脱敏数据。任何 Digest 字段也必须经过 Disclosure Profile 审核。

Public Fidelity Attestation 的最小结构为：

```yaml
schema: "core.public-fidelity-attestation@0.1.0"
id: "urn:uuid:..."
subject:
  node_id: "urn:uuid:..."
  node_revision: 1
  assertion_id: "urn:uuid:..."
  coverage_map:
    algorithm: "core.fidelity-coverage-map@0.1.0"
    bindings:
      - provenance_id: "urn:uuid:..."
        units:
          - id: "urn:uuid:..."
            body_utf8_ranges:
              - start: 0
                end: 1234
  body_byte_digest: "sha256:..."
  visible_text_digest:
    algorithm: "core.visible-text-events@0.1.0"
    value: "sha256:..."
  structure_digest:
    algorithm: "core.structure-events@0.1.0"
    value: "sha256:..."
review_subject_digest: "sha256:..."
claim: "restricted-source-fidelity-reviewed"
result: "passed"
coverage: "full"
disclosure_profile:
  id: "core.fidelity-public-minimal@0.1.0"
  digest: "sha256:..."
disclosure_approval_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

`review_subject_digest` 使用 Prefix `lorebuddy-fidelity-attestation-subject-v1\n` + `JCS(subject)` + LF 计算。Node 的 Attested Fidelity Assertion 必须逐字段等于 `subject` 中的 Node、Assertion 与公开 Coverage Map，并验证 Attestation 文件摘要；旧 Attestation 不能用于不同 Revision、Unit 或正文。公开 Map 只能含 Provenance、Unit ID 和 Body Range，禁止携带 Source Fragment Event、私有 Fragment / Mapping ID 或私有摘要。

受限 `core.audit-binding@0.1.0` 至少固定 Public Record 的 `{kind,id,digest}`、Public Package ID / Version、`release_rights_binding: {id,digest}`，以及每个私有 Party / Evidence / Review / Decision / Lock 的 `{kind,id-or-null,digest}`。Public Party Projection / Evidence Receipt 分支必须把随机 Public ID 映射到对应私有 Party / Evidence 与 Disclosure Approval，公开 Record 本身不得携带该反向引用。对 Public Fidelity Attestation，它还必须固定 Private Fidelity Record `{id,digest}`、`core.fidelity-public-projection@0.1.0`、投影结果摘要，以及 Public Provenance / Unit 到 Private Fragment 的逐 Binding 映射；投影结果必须等于 Attestation 的 `review_subject_digest`。最终 Release Manifest、Root 与 Payload 事实只由所引 Release Rights Binding 定义，Audit Binding 不复制第二套可能漂移的值。它还保存签发 Review、状态与有效期。Public Record Digest 对独立 Receipt / Attestation / Projection 使用其规范文件摘要；对内联 Public Rights Attestation 使用 Prefix `lorebuddy-public-rights-attestation-v1\n` + 该子 Object 的 JCS bytes + LF。Binding 的私有引用不得反向投影进 Public Index。

## 6. Lock 与受限 Build Dependency

### 6.1 发布 Lock

Release Payload 中的 `package.lock.json` 只允许包含：

- 可公开 Content Dependency 的 Package ID、版本和摘要；
- 公开 Schema / Registry Document；
- 当前 Release 可公开的 Receipt / Attestation ID 与摘要；
- 公开消费者可读取的工具标识。

它禁止包含未获披露批准的私有/受限 Package ID、版本、Manifest Digest、路径、域名或解析 URI。

### 6.2 完整构建 Lock

需要受限输入的完整 Build Lock 必须保存在构建 Principal 可读取的独立 Audit / Build Package 中，并进入该受限 Package 的 Content Manifest；它不要求与目标 Public Package 使用同一 Access Domain。公开 Package 只携带随机 Public Build Attestation：

```yaml
schema: "core.public-build-attestation@0.1.0"
id: "urn:uuid:..."
issued_for:
  package_id: "urn:uuid:..."
  package_version: "0.1.0"
  library_root_digest: "sha256:..."
  library_file_count: 123
review_subject_digest: "sha256:..."
claim: "restricted-build-inputs-reviewed"
reproducibility: "attested"
access_review: "attested"
disclosure_profile:
  id: "core.build-public-minimal@0.1.0"
  digest: "sha256:..."
disclosure_approval_id: "urn:uuid:..."
lifecycle:
  status: "active"
  revision: 1
```

Public Attestation 不复制受限输入摘要。`review_subject_digest` 使用 Prefix `lorebuddy-build-attestation-subject-v1\n` + `JCS(issued_for)` + LF 计算。`library_root_digest` 只由 Content Manifest 中 `library/` 文件记录计算，排除 `metadata/attestations/`，因此不会递归。若公开消费者无法从零复建，Release Manifest 的 Reproducibility Aggregate 必须声明 `library: attested`，不能声称 `full`。

Attestation 位于 Content Manifest 内，因此禁止在自身字段中引用当前 `content_root_digest` 或 `index_root_digest`，避免递归摘要。Release Manifest 通过 Content Root 把该 Attestation 绑定到最终发布组合。受限 Audit / Build Package 的 Audit Binding 同时固定 Attestation ID、完整 Build Lock、Access Decision Receipt 与最终 Public Release Manifest Digest。

替代方案是把完整私有 Lock 放进公开包后“只隐藏路径”。摘要、版本和 Package ID 仍可能成为稳定指纹，因此不采用。

### 6.3 Release Assurance 聚合

Assurance 是生成的 Release Manifest 事实，不由作者在 `package.yaml` 自由填写，并且必须声明评估视角 `evaluated_for: release-reader`。

- Node Traceability 为 `full`：所有正文贡献 Provenance 对 Release Reader 都能解析完整 Fragment → Entry → Artifact 与审核 Source Mapping；为 `attested`：没有缺失项，但至少一项只能解析到有效 Public Provenance Receipt；纯 Editorial / Record Node 为 `not-applicable`；缺失、范围未覆盖或 Receipt 无效为 `unverified`。
- Node Fidelity 先验证每个 Coverage Map Binding / Unit 的范围闭包与 Full / Attested 投影一致性，再使用计算得到的 `content.fidelity_evidence.aggregate_mode`；Package Aggregate 取全部适用 Node 的最弱值，并保存 `full / attested / unverified / not_applicable` 数量，不能只留一个掩盖混合状态的字符串。
- Reproducibility 分成 `library` 与 `index`：公开且锁定的输入可重放到同一 `library_root_digest` 时 Library 为 `full`；受限输入只能由有效 Public Build Attestation 证明时为 `attested`；Index 能由当前 Content、公开工具、Schema 与 Registry Lock 重建到同一 `index_root_digest` 时为 `full`。任一分量 `unverified` 则 Aggregate 为 `unverified`，否则任一为 `attested` 则 Aggregate 为 `attested`。

## 7. Review 与 Party 的公开投影

完整 Issue、Exception、Review、Party 和 Evidence 默认留在其所属 Access Domain。本来公开的 Party / Evidence 可以直接发布；受限对象的公开表达必须使用随机新 ID 的 `core.public-party-projection@0.1.0` 或 `core.public-evidence-receipt@0.1.0`，并由受限 Audit Binding 映射。公开 Package 只能包含经过 Disclosure Approval 的最小投影，例如：

- 审核类别；
- 结论；
- 公开责任组织或公开 pseudonymous Party；
- 公开 Receipt ID；
- 适用 Node；
- 不含合同、个人身份、私有 Fragment 或内部拒绝理由。

Party Schema 必须逐字段标注 `public | domain-restricted | secret-reference`。公开构建对 Metadata 运行字段级投影和泄漏检查；禁止以同一私有 ID 保存不同字节的“公开版”。删除敏感字段后如果无法支持结论，Package 必须保持 Restricted，不能制造无证据的公开结论。

## 8. Release Payload 白名单

Package Working Tree 不是 Release Archive。发布器必须从空 Staging Directory 按白名单复制文件，禁止直接归档整个 Package 目录。

合法 Release Payload 的文件集合严格等于：

```text
Content Manifest 的全部文件记录
∪ Output Manifest 的全部文件记录
∪ index/output-manifest.json
∪ release-manifest.json
```

Archive Entry 集合还必须包含上述文件的每个非根祖先目录各一次，除此之外不得有其他目录；`payload_file_count` 只统计文件。目录 Entry 不能携带内容。

`index/manifest.json` 已由 Output Manifest 覆盖。消费者必须枚举 Archive：

- 缺少任一白名单文件：失败；
- 出现任一额外文件：失败；
- 路径重复、大小写/Unicode 冲突或越界路径：失败；
- Symlink、Hard Link、Device、FIFO、Socket、Sparse Entry、Resource Fork、Alternate Data Stream 及任意其他非规范目录/普通文件类型：失败；
- 任一长度或摘要不符：失败。

路径检查必须作用于 Archive Header、PAX / ZIP Extra Field 解析后的最终有效路径：只允许 `/` 分隔的 Package 相对 UTF-8 路径；拒绝绝对路径、Drive Prefix、NUL、反斜杠、`.` / `..` Segment、空 Segment，以及规范碰撞键相同的两个 Path。`core.archive-path-collision@0.1.0` 固定使用 Unicode 15.1.0：先对每个完整 Path 执行 NFC，再按同版本 `CaseFolding.txt` 做完整 Default Case Folding（不启用 `T` Mapping）；不执行 NFKC，也不改写实际归档 Path。碰撞键逐 Unicode Scalar Value 比较。不得跟随或解析任何 Link Target。

Archive Header 采用默认拒绝的 `core.release-archive-metadata@0.1.0`：只保留 Path、`directory | regular-file` 类型、规范 Size、校验和与压缩所必需字段；文件 Mode 固定 `0644`，目录固定 `0755`，UID / GID 为 `0`，User / Group Name 为空，所有时间为规范零值（ZIP 使用 `1980-01-01T00:00:00`），禁止 Host Absolute Path、ACL、xattr、Finder / NTFS Metadata 和自定义 PAX / ZIP Extra Field。Tar 只允许为表达最终 UTF-8 Path / Size 所必需且值与规范 Entry 相等的 PAX Key；ZIP 只允许 UTF-8 标志及规范要求的 CRC / Size 字段。Archive Adapter 遇到未登记 Header 必须拒绝，不能透传。Entry 按最终 Path UTF-8 bytes 排序生成。

`reports/`、完整 Build Lock、完整 Review、控制台日志、临时路径和缓存不属于 Release Payload。若需保存，进入独立受限 Audit Package。

Release Manifest 的精确结构见[索引规范](index-spec.md)，至少固定：

```json
{
  "evaluation_as_of": "2026-07-20T00:00:00Z",
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
    "attestation": {}
  },
  "disclosure_profiles": [],
  "assurance": {}
}
```

`payload_file_count` 包含 Release Manifest 自身但不包含目录 Entry，用于快速发现集合偏差；规范文件集合仍由上述并集定义。`disclosure_profiles[]` 每项必须是精确 `{id, digest}`，不能只列可漂移的 ID。

## 9. `Release Ready(public)` 判定

流程先预分配 Public Attestation / Release Rights Binding ID，生成无最终 Root 的 Target Candidate Lock 与完整 Path / Role / Subject / Permission 计划；受限 Audit Package 据此生成 Rights Decision。只有 Decision 为 `allowed`，发布器才组装不可修改的 Release Candidate（Direct 模式此时写入 Decision Digest，Public 模式写入批准的 Attestation 值），计算最终摘要并在 Audit Package 生成 Release Rights Binding；最后重放 Binding Validation，期间不得修改 Candidate。只有以下条件全部为真，才允许把 Candidate 标记为 Public Release 并分发：

1. Package `access.visibility == public`，Access Policy 允许匿名读取；
2. Release Payload 的每个文件都按 Rights Coverage 映射到 Subject 与所需权限，Package 级 `publish_metadata` 及所有更具体 Claim 的合并结果均为 `allowed`；
3. 不存在 `unknown` 或 `denied` 的公开所需权限；
4. Content Dependency 全部公开可读；受限构建输入只通过批准的 Public Attestation 表达；
5. 每条 Provenance 是可公开的 `embedded-fragment`，或是带 Disclosure Approval 的 `external-public-receipt`；
6. Release Manifest 按 `release-reader` 视角正确生成 Traceability、Fidelity 与 Reproducibility Aggregate 及计数，不夸大公开可验证能力；Attested Fidelity 不含 Source Event Digest；
7. Public Lock 不含受限身份或指纹；
8. Review / Party / Evidence 已按随机 Public ID、Disclosure Approval 与 Audit Binding 完成公开投影，未复制私有 ID；
9. Release Payload 文件集合精确匹配白名单，只含规范目录/普通文件，Archive Path 与 Header Metadata 通过默认拒绝检查，且不存在 `reports/` 或额外文件；
10. Content Root、Index Root、Release Manifest 和访问泄漏测试通过；
11. 受限 Audit Package 中的 Rights Authority Delegation、Rights Decision、Release Rights Binding 与 Audit Binding，以及公开 Public Rights Attestation、Disclosure Approval 和 Access Policy，均在 Manifest 的 `evaluation_as_of` 为 Active 且有效，并完整通过 `core.release-rights-binding-validation@0.1.0`；
12. 发布者从可信渠道分发预期 Release Manifest 摘要，或未来使用签名。

该判定是默认拒绝的布尔门禁。Schema 允许 `visibility: public` 并不代表门禁自动通过。

## 10. 完整性与认证的边界

当前 Release Manifest 是完整性组合：它能发现预期 Manifest 下的文件变化，但不能单独证明发布者身份，也不能阻止攻击者整体替换 Package 和 Manifest。

Milestone 0 不实现签名。消费者必须从可信渠道获得预期 Release Manifest Digest。未来签名应同时绑定：

- Release Manifest Digest；
- Package ID / Version；
- Access Policy；
- Public Rights Attestation（完整 Rights Decision 仍留在授权 Rights Authority Audit Context）；
- Disclosure Profile 集合。

因此本文使用“发布完整性封条”，不把它描述为身份认证或法律授权证明。

## 11. 当前 CHM 的结论

当前 CHM 的 Rights、翻译身份和再分发范围均未完成审核：

- Access Policy 必须是 Restricted；
- `redistribute_source`、`redistribute_transcription`、`redistribute_asset` 默认 `unknown` 或已知 `denied`；
- 不满足 `Release Ready(public)`；
- 可以在授权环境保存 Artifact 并进行 Milestone 0 只读分析；
- 未来能否建立公开派生 Package，取决于逐 Work / Edition Rights Review 和 Disclosure Approval。

“保存完整证据”和“允许公开全文”是两个独立结论，不能互相推出。
