# M1 Implementation Profile

状态：Confirmed  
Profile ID：`m1-profile@0.1.0`

## 1. 目的

本文把 M0 的完整架构上限裁剪为 M1 的可执行合同。状态含义：

- `REQUIRED`：M1 Exit Gate 前必须实现并验证；
- `OPTIONAL`：允许实现，但不得拖延 REQUIRED 闭环；
- `DEFERRED`：保留兼容点，当前不实现且不得成为门禁；
- `OUT_OF_SCOPE`：不属于 M1；若要引入，必须先修改本 Profile。

“未实现”不等于从 M0 删除；Future RFC 启用时必须复用稳定 ID、Package 边界和现有摘要，不得要求重新理解 CHM。

## 2. 产品与运行约束

| 约束 | 状态 | M1 合同 |
|---|---|---|
| 单用户、本地优先 | REQUIRED | 单机完成 Acquire、Build、Validate、Publish |
| 单发布设备 | REQUIRED | 同一时刻只有一个 Build / Publish Authority |
| Workspace / Vault 分离 | REQUIRED | 工程事实源只在 Workspace；Vault 只接收发布视图 |
| 现有外部同步 | REQUIRED | LoreBuddy 不控制、不探测同步实现 |
| 本地发布锁 | REQUIRED | 防止同一设备并发发布；不实现分布式锁 |
| 5～10 个复杂样本 | REQUIRED | 样本覆盖真实结构风险，不追求数量 |
| 全量 CHM 转换 | OUT_OF_SCOPE | M1 Exit Gate 不允许自动触发 |
| Runtime / RAG / Embedding | OUT_OF_SCOPE | 不设计运行时接口或向量存储 |

### 2.1 与 M0 的冲突评估

M0 架构与当前产品目标没有模型级冲突：受限本地摄取、最小 Node、基础 Provenance 和派生 Index 都是 M0 已允许的路径；Rights / Public Release 是架构上限，不是所有受限本地构建的必经步骤。

存在一项阶段标签冲突：根级 `AGENTS.md` 仍声明“当前阶段为 Milestone 0”。本轮按停止条件不修改该文件；M1 Profile 获得确认后、任何实现开始前，必须把根级阶段门禁更新为 M1，并明确本 Profile 的优先级。未更新前只允许继续编写和审核文档。

根级 `AGENTS.md` 中关于 Full / Attested Fidelity、Rights Claim 和 Release Binding 的约束按能力激活解释：只有实现或声明对应级别时才必须完整遵守。M1 不声明这些级别，因此使用 `m1-sample-validated`，但不得以此放宽 Source 不可变、稳定身份、Traceability 和确定性构建。

## 3. M0 文档调用矩阵

### 3.1 `chm-analysis.md`

| M0 能力 | 状态 | M1 使用方式 |
|---|---|---|
| 容器身份与 SHA-256 基线 | REQUIRED | Acquire 前后核对同一原件 |
| 文件规模、类型与顶层分布 | REQUIRED | Inventory 完整性与样本选择基线 |
| HHC / HHK 导航事实 | REQUIRED | Source Navigation Index 与样本上下文 |
| 编码统计 | REQUIRED | Entry 级 Decoder 选择和失败门禁 |
| HTML、链接、资产、重复风险 | REQUIRED | 样本组合与问题清单 |
| 来源性质判断 | REQUIRED | 保持 `unknown` / `claimed`，禁止自动标记官方 |

M1 不重跑整份分析以扩写 M0；实现只需用同一 Artifact 摘要验证基线未漂移。

### 3.2 `chm-conversion-strategy.md`

| 阶段 | 状态 | M1 限制 |
|---|---|---|
| Acquire | REQUIRED | 保存原始容器、身份、大小、摘要和本地获取事实 |
| Inventory | REQUIRED | 枚举全部 Entry；路径、长度、安全性与摘要可验证 |
| Preserve Source | REQUIRED | 保留 CHM 与全部原始 Entry，不改字节 |
| Decode / Parse Evidence | REQUIRED | 只对样本完整解析；全部 Entry 至少保留检测事实 |
| Work / Edition 分类 | REQUIRED | 只建立样本所需 Source Mapping；未知保持未知 |
| Source Reference Graph | REQUIRED | 只闭合样本内 Link、Anchor、Image 与附件引用 |
| Boundary Candidate / Human Review | REQUIRED | 机器提议、用户批准后才分配正式 Node ID |
| Render Library | REQUIRED | 只生成已批准样本 Node |
| Fidelity Validation | REQUIRED | 使用本文第 3.7 节的最小子集 |
| Build Indexes | REQUIRED | 只生成第 3.6 节最小索引 |
| Release / Public Gate | DEFERRED | Obsidian Publish 不等于公开 Release |
| 全量启动条件 | OUT_OF_SCOPE | M1 结束时只形成后续建议 |

### 3.3 `knowledge-package-spec.md`

| 能力 | 状态 | M1 合同 |
|---|---|---|
| Package 边界 | REQUIRED | 建立一个受限 Acquisition Package；本轮不创建 |
| Source / Library / Metadata / Index 分层 | REQUIRED | 四层不得互相写回 |
| Package Manifest | REQUIRED | 实现 M1 最小字段与受限状态 |
| Package Lock | REQUIRED | 锁定工具、Schema、Registry 和配置摘要；不含私人绝对路径 |
| UUIDv7 稳定身份 | REQUIRED | 通过样本验证分配、重跑复用和标题改名行为 |
| Artifact / Entry / Fragment | REQUIRED | 支撑基础 Provenance 和重建 |
| Work / Edition / Source Mapping | REQUIRED | 只对样本记录经人工确认或 unknown 的事实 |
| 基础 Knowledge Node | REQUIRED | 一个文件一个表达版本和语义单元 |
| Relationship | REQUIRED | 只维护正向断言，反向边由 Index 生成 |
| 确定性构建 | REQUIRED | 同输入和决策生成字节一致的规范输出 |
| Access / Content Dependency 高级模型 | DEFERRED | M1 只有一个受限 Package，无跨权限依赖 |
| Release Ready | DEFERRED | 不生成公开 Release Manifest |

### 3.4 `markdown-metadata-spec.md`

| 能力 | 状态 | M1 合同 |
|---|---|---|
| UTF-8、LF、YAML 可移植子集 | REQUIRED | Properties 与规范 Node 同时通过解析 |
| 基础 Front Matter | REQUIRED | 使用第 4 节定义的 M1 字段投影 |
| 忠实转写正文 | REQUIRED | 不总结、意译、补写或静默纠错 |
| Heading、表格、受限 HTML | REQUIRED | 样本中按原结构选择 Markdown 或允许的 HTML |
| embedded-fragment Provenance | REQUIRED | M1 不使用公开 Receipt 联合分支 |
| Link 与 Asset | REQUIRED | 样本范围内闭合且可在 Obsidian 解析 |
| Relationship | REQUIRED | 正向事实与稳定 Assertion ID |
| Structured Extraction | OPTIONAL | 仅当样本需要证明 Profile 字段时实现 |
| Public Receipt / Attestation | DEFERRED | 不进入 Properties 或发布视图 |
| 完整责任与规范性审核 | REQUIRED | 最小记录 `unknown` / 已核实事实，不建立治理流程 |

### 3.5 `schema-proposal.md`

以下 Schema 的可执行最小版本为 `REQUIRED`：

- Package Manifest；
- Source Artifact；
- Source Entry；
- Source Fragment 与 Locator；
- Knowledge Node Envelope；
- Source Mapping；
- Boundary Candidate / Decision；
- Relationship。

Issue / Review 的最小记录为 `OPTIONAL`，但人工 Boundary Decision 必须有可重放的批准记录。Party、Evidence、Rights、Public Attestation、Release Manifest、Redirect 和 Tombstone 的完整 Schema 为 `DEFERRED`；若样本发生真实拆分、撤回或 ID 替代，则先升级 Profile，不临时发明字段。

M1 Schema 必须保持 M0 Schema ID / 版本兼容。允许缩小必需字段集合的唯一方式是定义明确的 M1 Profile Schema，不得悄悄改变 Core Schema 含义。

### 3.6 `index-spec.md`

以下派生索引为 `REQUIRED`：

- 最小 Node Index；
- Alias Index；
- Relationship Index，含可重建反向边；
- Provenance Index，至少支持 Node → Fragment 与 Entry → Node；
- Source Navigation Index，保留样本对应 HHC Occurrence。

索引必须可删除重建、排序确定、不得成为事实源。完整 Content / Output / Release Manifest、Rights File Role Dispatch、公开 Payload 白名单和规模化分片策略为 `DEFERRED`。M1 可以使用内部 Build Inventory 证明构建确定性，但不得称其为 M0 Public Release Manifest。

### 3.7 `integrity-protocols.md`

| 协议能力 | 状态 | M1 验证 |
|---|---|---|
| Artifact SHA-256 | REQUIRED | 与 M0 分析基线一致 |
| Entry 长度与 SHA-256 | REQUIRED | Inventory、保存字节与重读结果一致 |
| Visible Text Events | REQUIRED | 每个样本 Source / Node 摘要相等 |
| Structure Events 最小子集 | REQUIRED | Heading、List、Table、Link、Image、Pre/Code 中样本实际出现项 |
| Link / Address 完整协议 | REQUIRED | 只实现样本用到的事件和互斥消费；未知组合阻塞 |
| Source Fragment Event 全协议 | OPTIONAL | 若不实现，不得声称 M0 Full Fidelity |
| Fidelity Coverage Map 全协议 | DEFERRED | M1 使用一对一样本 Coverage Record，不宣称 `full` / `attested` |
| 全部 Candidate / Occurrence Fixture | DEFERRED | M1 只固化实际使用的 Key 和测试向量 |

M1 的保真结论名称固定为 `m1-sample-validated`，不能映射为 M0 的 `Library Valid(full)`、`full` 或 `attested`。

### 3.8 `rights-release-spec.md`

整份规范在 M1 为 `DEFERRED`。M1 仍必须：

- 将 Acquisition Package 标记为受限本地内容；
- 不对外发布；
- 不把未知 Rights 解释为允许再分发；
- 在数据模型中保留未来 Rights / Access 扩展位置。

M1 不创建 Rights Authority Domain、Claim、Lineage、Decision、Binding、Public Attestation、Target Candidate Lock 或 Public Release Manifest。

## 4. M1 Obsidian View 投影

Obsidian View 是从规范 Library / Metadata 派生的消费格式，不是第二事实源。允许为了阅读性：

- 使用可读稳定 Slug；
- 把已批准的 Node 字段投影为最小 Properties；
- 把规范关系投影成 Vault 相对 Link / Wikilink；
- 把 Library Asset 复制到发布附件目录；
- 生成仅供导航的索引 Note。

禁止在 Obsidian 产物中新增或覆盖规范事实。用户修改生成文件不会自动回流 Workspace；重新发布可以覆盖 Manifest 所有的生成文件。

## 5. 本地配置与可移植性

配置解析优先级为：显式 CLI 参数 → `LOREBUDDY_OBSIDIAN_VAULT` → 未跟踪的 `config.local.toml` → 缺失即失败。任何层级都不得提供代码内置的私人路径默认值。

`config.local.toml` 与 `build/` 已加入 `.gitignore`。本轮不创建配置文件；未来可以提供只含占位符的 `config.local.toml.example`。

## 6. M1 Exit Gate

只有 [Acceptance Criteria](acceptance-criteria.md) 全部满足，且用户明确批准样本格式、链接、Properties、附件和使用体验后，M1 才能结束。M1 通过不自动授权 M2 全量批处理或 M3 正式 Vault 发布。
