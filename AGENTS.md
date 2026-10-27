# LoreBuddy 工程协作规范

本文件适用于整个仓库。更深目录中的 `AGENTS.md` 可以增加 Package 特有要求，但不得放宽本文件的不可变约束。

## 1. 项目定位

LoreBuddy 是 TRPG（Tabletop RPG）知识平台，不是 D&D 工具、聊天机器人、RAG Demo 或格式转换器。

D&D 5e 只是首个输入场景。所有平台级设计都必须能够容纳 Pathfinder 2e、Call of Cthulhu、Shadowrun、Savage Worlds、Homebrew 和原创系统。

设计或修改前必须回答：

1. 为什么这样设计？
2. 替代方案是什么？
3. 为什么不采用替代方案？
4. 对版本、迁移、追溯和未来系统有什么影响？

## 2. 产品交付原则

在不破坏 Architecture Authority、Deterministic Build、Source Fidelity 和 Module Boundary 的前提下，LoreBuddy 默认优先缩短用户获得可用产品的反馈周期。

若多个方案均满足工程质量要求，默认优先：

- 更早交付用户可见能力；
- 更短反馈循环；
- 更小、可验证、可独立发布的 Milestone；
- 避免为了未来架构提前引入当前版本不会使用的复杂度。

该原则属于产品策略，不能作为降低 Fidelity、Validator、Architecture 或测试质量的理由。

## 3. 沟通与文档

- 默认使用简体中文。
- 专业术语首次出现时采用“中文（English）”形式；Schema、Runtime、Package、Manifest、Front Matter、Graph、Relationship、Protocol 等约定术语可直接保留英文。
- 文档采用工程说明风格，不写营销文案，不用未验证的断言代替证据。
- 架构变更必须更新相应规范；改变已确认边界时必须增加架构决策记录（Architecture Decision Record，ADR）。
- 不确定的来源、授权、版本或映射必须显式标记为 `unknown`、`claimed` 或 `inferred`，不得猜测。
- 当 Prompt 已明确声明“先读取并遵守 AGENTS.md、ROADMAP.md、Milestone 文档”时，后续 Prompt 不应重复复述这些文档内容。Prompt 应尽可能保持精简，只描述本轮目标、新增约束、本轮范围和 Deliverable。

## 4. 当前阶段门禁

当前阶段为 `Milestone 2: Rule Cluster Pilot（规则簇试点与接纳）`。当前实施合同是
`docs/milestone-2/implementation-profile.md`，启动授权与边界见
`docs/milestone-2/abc.md`。M1-C4 是已冻结的 `v0.1.0` 基线；M2 只消费其显式
Manifest 和受控的外部交付，不重写 M1 Source 或 Publisher。

M2-A 的 Book Catalog、Entry-to-Book Mapping、Ruleset Profile 与 Review Queue 已由
Antigravity 在外部工作区实现，当前状态为 `externally_implemented_pending_acceptance`。
它在通过 LoreBuddy 的输入锁定、集合闭合、字段语义和 Profile 验收前，只能作为候选
交付，不得被称为已批准的出版身份、规则事实或 DND Terminal 准入数据。

本阶段只允许：

- 验收并登记 M2-A 外部交付；
- 定义 Rule Assertion、Trigger / Condition、Activity、Effect、Prerequisite、Choice 和
  Source Binding 的最小契约；
- 生成带来源范围和审核状态的规则候选；
- 对经确认的 D&D 2024 小样本执行规则簇试点、确定性验证和人工审核；
- 从已批准对象确定性编译 Rule Card，以及只读的 DND Terminal 候选包。

在 M2 Exit Gate 获得确认前：

- 不进行全量 Rule Object 转换、自动采纳或批量覆盖；
- 不把 Antigravity 输出、模型输出或冒烟测试当作规则权威或正式接纳；
- 不直接修改 DND Terminal、角色卡、怪物模板或正在运行的 Campaign；
- 不把 D&D 专属字段提升为平台核心，也不在本阶段实现 COC / 社交 / 心智规则簇；
- 不实现 Runtime、RAG、Embedding、向量数据库、公开 Release、多人同步或用户 Vault 覆盖；
- 不修改 M1 Source、已通过的 Publisher 或 GPT Export；
- 不因路径、书名或 Catalog 分类自动把来源身份、权利或规则优先级升级为 `verified`。

## 5. 不可变原则

### 4.1 原始来源不可变

原始来源（Source）包括摄取的容器文件及其解包后字节。进入 `sources/` 后禁止：

- 改编码、格式化或清理 HTML；
- 修正错字、标点、链接或样式；
- 删除脚本、注释、隐藏文本或重复资源；
- 以去重文件覆盖原始文件；
- 用新版本覆盖旧版本；
- 丢弃原始路径、大小写、摘要或提取记录。

发现原始资料错误时，记录问题与勘误关系，不修改旧来源。

上述不可变要求专指 Artifact 容器、Entry 与其原始路径证据。`sources/catalog/` 中的 Work / Edition Claim 可以在新 Package 版本中显式提高记录 Revision；旧发布不可改写。会变化的 Entry / Fragment → Edition 审核结论必须放在 `metadata/source-mappings/`，不放入 Catalog 假装不可变来源。

### 4.2 Source 与 Library 分离

- `sources/` 保存证据。
- `library/` 保存面向读取与检索的知识表达。
- `metadata/` 保存人工维护的分类、边界、关系与迁移事实。
- `index/` 只保存可重建的派生产物。

任何派生内容都不得写回 Source。任何索引都不得成为事实源。

### 4.3 官方正文不得改写

标记为忠实转写（Verbatim Transcription）的正文不得总结、简化、意译、重排或静默纠错。允许的格式转换必须通过可见文本保真验证。

官方英文原文、官方译本、社区译本、第三方内容和 House Rule 必须分别建模。当前 CHM 中的中文文本不能仅凭目录名称自动标记为官方文本。

### 4.4 节点独立

- 一个知识节点只表达一个语言、规则版本、权威上下文下的一个语义单元。
- 2014 与 2024 规则、勘误前后文本、不同语言、官方规则与 House Rule 不得合并到同一正文。
- 修改一个节点不得要求同步修改其他节点；反向关系由索引生成。
- 节点拆分、合并或删除后必须保留重定向（Redirect）或墓碑（Tombstone），旧 ID 永不复用。

### 4.5 全链路追溯

正式节点必须能够沿以下链路追溯：

```text
Knowledge Node
→ Source Fragment
→ Source Entry
→ Source Artifact
Source Fragment / Entry
→ reviewed source mapping
→ Edition
→ Work
```

实际摄取证据与出版来源声明是两种事实，二者通过可审核的多对多映射连接。若书籍、版本、章节或页码未经核验，必须保留未知状态，不能从路径名称直接升级为已验证事实。

在授权 Access Domain 中，上述完整链必须可解析。公开 Package 无权披露受限 Source 时，只能使用 `external-public-receipt` 并标记 `traceability: attested`；完整 Fragment、Mapping、Review 和 Lock 必须存在于受限 Audit Package，公开 Receipt 不得冒充 Full Traceability。

## 6. 目标目录职责

平台级目录不得包含 D&D 专属命名。

```text
spec/                 # 规范正文
schemas/core/         # 平台核心 Schema
schemas/profiles/     # 平台通用 Profile
registries/           # 稳定标识与词汇注册表
packages/             # 独立知识包
docs/                 # 分析、决策、风险和里程碑文档
```

每个 Package 使用：

```text
packages/<namespace>/<package-slug>/
    package.yaml
    package.lock.json
    release-manifest.json
    sources/
    library/
    metadata/
    schemas/
    registries/
    index/
    reports/
    AGENTS.md
```

Package 是发布、授权、依赖和访问控制边界。不得把整个规则系统默认做成一个永久 Package。

## 7. 新增知识的位置

- 原始容器、原始 HTML、图片、CSS、导航和索引资源进入 `sources/artifacts/`。
- 每个 Artifact 的 `inventory.jsonl` 是 `core.source-entry@0.1.0` 的唯一规范记录流；`entries/` 只保存其指向的不可变字节，`path-map.jsonl` 只能由 Inventory 确定性生成。
- 达到 Source Complete 所需的 Extraction / Analysis Receipt 进入对应 Artifact 的 `sources/artifacts/.../receipts/`，不得只留在运行报告。
- 出版物与版本身份记录进入 `sources/catalog/`；Entry / Fragment 到 Work / Edition 的审核映射进入 `metadata/source-mappings/`。
- 正式知识节点进入 `library/nodes/`。
- Library 使用的派生资产进入 `library/assets/`；规范 Asset Record 与每次使用分别进入 `metadata/assets/records/`、`metadata/assets/usages/`，并保留到 Source Entry 的映射。
- 规范 Source Fragment Record 进入 `metadata/fragments/`；已发布 Fragment 的范围不得原地改变。
- Fragment Record 与同名 `.events.jsonl` 包含来源原文证据，Release File Role 必须是 `source-fragment-evidence` 并要求 `redistribute_source`；禁止作为普通 `metadata-record` 发布。
- Entry / Fragment 到 Work / Edition 的审核断言进入 `metadata/source-mappings/`，Node 只能引用稳定 Mapping ID。
- 人工确认的节点边界进入 `metadata/boundaries/`。
- Source / Library 事件摘要、所用 Link / Address Mapping 的 `{id,revision,digest}`、Visibility Decision 与批准差异的保真结论进入 `metadata/fidelity/`；原始 Reference Occurrence 进入 `metadata/references/occurrences/`，Mapping 本体分别进入 `metadata/links/mappings/`、`metadata/addresses/mappings/`，页面族或具体子树的可见性裁决进入 `metadata/visibility-decisions/`，完整临时 Diff 仍进入 `reports/`。
- Front Matter / Extension 的结构化抽取断言进入 `metadata/structured-extractions/`，逐 JSON Pointer 固定 Provenance、映射规则与抽取器；不得把它伪装成正文保真模式。
- Link、Image、Resource、Anchor 的原始 Attribute Occurrence 统一进入 `metadata/references/occurrences/`；语义 Link / Image / Resource Mapping 进入 `metadata/links/mappings/`，Anchor / Footnote 的 Semantic Address Occurrence 与 Mapping 分别进入 `metadata/addresses/occurrences/`、`metadata/addresses/mappings/`，不得只存在于 Index。转换范围内每个 Raw Reference 必须按规范被恰好一个语义消费者消费，零消费或双重消费都阻塞。
- 人工维护的语义导航树与兄弟顺序进入 `metadata/navigation/semantic/`；Source Navigation Occurrence 进入 `metadata/navigation/source-occurrences/`。
- 复杂关系断言进入 `metadata/relationships/`。
- 完整责任主体与 Evidence 分别进入 `metadata/parties/records/`、`metadata/evidence/records/`。受限对象的公开表达必须在 `public-projections/`、`public-receipts/` 使用随机新 ID，并由 Audit Binding 映射；禁止以同一私有 ID 制作删字段副本。`evidence_ids[]` 只能解析到完整 Evidence 或 Public Evidence Receipt，不能直接混用任意 URL 或其他 Record ID。
- 已进入治理流程的问题、批准例外与审核结论分别进入 `metadata/issues/`、`metadata/exceptions/` 与 `metadata/reviews/`。
- Access Domain / Policy、Rights Authority Domain / Delegation、Rights Claim / Decision 与 Disclosure Approval 分别进入 `metadata/policies/access-domains/`、`metadata/policies/access/`、`metadata/rights/` 与 `metadata/disclosures/approvals/`。Rights Authority Domain 管签发责任，Access Domain 管读取权限，禁止混用。
- 版本化 Disclosure Profile 进入平台或 Package 的 `registries/disclosure-profiles/`，并由 `package.lock.json` 固定 Document ID、Path 与 Digest；Approval 只引用它，不复制另一份白名单。
- 公开 Receipt / Attestation 到受限 Fragment、Review、Decision 或 Build Lock 的完整映射进入受限 Audit Package 的 `metadata/audit-bindings/`，不得放入公开 Package。
- Release 动作的 Rights Decision 与最终 Release Rights Binding 共同进入目标 Release 之外、具有 Active Authority Delegation 的 Audit Package；该 Package 可以使用不同 Access Domain。Binding 位于 `metadata/rights/release-bindings/`，不得放回被绑定 Release 形成摘要循环。
- 重定向和墓碑进入 `metadata/redirects/` 与 `metadata/tombstones/`。
- 可重建的检测结果、转换执行日志与验证报告进入 `reports/`；人工裁决不得只存在于报告中。
- Alias、反向关系、导航和内容清单等生成结果进入 `index/`。

禁止直接手工编辑 `index/`。若索引错误，应修改事实源或生成器后重建。

## 8. 元数据维护

- Front Matter 必须通过对应 Schema。
- `id` 使用稳定 UUID URN；标题、slug、路径和正文摘要都不是身份。
- `language` 使用 BCP 47，例如 `zh-Hans`、`en`。
- `aliases` 必须携带语言；Alias 冲突是合法的一对多关系。
- `version` 不得作为含义不明的通用字段。必须区分规范版本、Schema 版本、Package 版本、节点修订、来源版本和规则版本。
- 关系必须使用注册的、有方向的谓词，并记录断言依据。
- 标签使用命名空间化标识；不得把自由文本标签当作稳定分类。
- 正文摘要只用于完整性校验，不用于节点身份。

## 9. 新增 Package

新增 Package 前必须明确：

1. 发布与版本化边界；
2. 授权及再分发策略；
3. 访问控制等级；
4. 依赖及允许的依赖方向；
5. 语言与适用的规则系统、规则版本、世界或 Campaign；
6. Source 来源及可验证程度；
7. 所需的扩展 Schema。

混合授权或来源不明的聚合工件应先进入最严格访问级别的摄取 Package。完成来源审核后，再发布更细粒度的派生 Package。

公开 Package 不得把不可公开读取的 Package 作为 Content Dependency。受限 Build Dependency 的完整 Lock 进入受限 Audit / Build Package；公开侧只允许随机、逐字段批准的 Public Attestation，不得复制私有 Package ID、版本、摘要、路径或 URI。Provenance 必须显式选择 `embedded-fragment` 或 `external-public-receipt`，不得用摘要引用绕过权限。

`public | restricted | private` 不是足够的线性授权模型；依赖还必须通过 Access Domain / Principal 判定。公开 Release 采用默认拒绝 Rights 合并，并从空目录按 Payload 白名单生成；`reports/`、私有 Lock、完整 Review 或任意额外文件不得进入 Release Archive。

## 10. 支持新的 TRPG 系统

- 先建立系统与规则版本注册项，再建立 Package。
- 平台核心只提供通用 Envelope、来源、关系、规则、参考条目、叙事实体和事件等能力。
- Spell、Monster、Class、Condition 等系统特有概念必须使用命名空间化 Package Schema。
- 至少在多个系统中证明语义一致后，字段或关系才能提升到平台核心。
- 不建立包含大量无意义可选字段的“万能 TRPG Schema”。

## 11. 避免重复知识

- 相同标题、文件名、Alias 或相似正文只能产生重复候选，不能触发自动合并。
- 逐字相同但来源、版本或适用范围不同的文本仍可作为不同节点保存。
- 同一表达的多处引用优先建立一个节点和多条来源/导航关系；是否为同一表达必须经过审核。
- 版本变体使用 `variant_of`、`revises`、`corrects`、`supersedes` 或 `translation_of` 等关系连接。
- 汇总概念可以建立无官方正文的概念节点，但不得把编辑性总结混入官方转写正文。

## 12. 转换与验证要求

- 转换必须可重跑、幂等并锁定工具版本。
- 构建过程中不得依赖网络上的“最新内容”。外部资源必须作为单独摄取行为处理。
- HTML 中的脚本不得在转换时执行。
- 编码按 Source Entry 检测并记录；不得对整个容器假设单一编码。
- Markdown 无法忠实表达表格、脚注或复杂布局时，保留受限原始 HTML，并产生审核项。
- Full / Attested 保真必须使用 Fidelity Coverage Map；不得用 `provenance_ids[]`、`fragment_ids[]`、`body_utf8_ranges[]` 三个平行数组暗示对应关系。每个 Unit 必须显式绑定正文 Range，Full 模式还要绑定 Source Fragment Event Record Range 并逐 Unit 验证。
- Rights Claim 必须从受控 Claim Universe 扫描并做 Selected Set 全等校验，`rights_claim_ids[]` 只能做一致性检查；不得让调用方通过少传一条 Claim 排除 `denied`。
- Rights Claim / Tombstone 必须是追加式 Lineage，携带可解析的 Authority Domain、Delegation、Issuer 与 Review；Pending、未授权或历史链不完整只能得到 `unknown`，不得授予 `allowed`。
- Rights Subject Closure 必须传递覆盖 Artifact Inventory 中每个物理 Entry，不受 Lifecycle 影响，并继续展开 Edition / Work 与 Asset；Claim ID 与 Claim Source Package Root 在完整 Universe 中必须唯一。
- Release 门禁使用 Manifest 明示的 `evaluation_as_of`，不得读取系统当前时间；目标 Manifest 只携带 Rights Authority Domain 与预分配 `release_binding_id`，禁止携带外部 Binding Digest，并必须通过 `core.release-rights-binding-validation@0.1.0` 的全部跨 Record 等式。
- 同一输入、相同工具链、相同人工决策账本必须生成字节一致的规范输出。
- 所有异常必须进入机器可读问题清单，禁止静默跳过。

## 13. 提交前检查

涉及规范或知识数据的变更至少检查：

- 是否改动了原始 Source；
- 是否混淆了实际工件与声称出版来源；
- 是否引入 D&D 平台级字段；
- 是否让标题、路径或摘要承担身份；
- 是否把索引当作事实源；
- 是否破坏多版本、多语言或私有 Package 隔离；
- 是否保留完整 Traceability；
- 是否需要 ADR、Schema 迁移或重定向；
- 是否能确定性重建并得到零意外差异。

## D&D生产工作区路由

涉及D&D全库普查、机制候选分组或生产工具时，先读`docs/projects/DNDRulePipeline.md`，再进入该工作区读取其AGENTS及接手入口。跨仓登记仅提供导航，不改变本仓M2门禁或自动接纳子项目成果。
