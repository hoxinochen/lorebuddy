# LoreBuddy Roadmap

状态：Draft / 无固定日期承诺  
用途：描述渐进式开发顺序和退出条件，不替代架构规范。

## 1. Roadmap 原则

- M0 描述完整架构上限，不等于全部立即实现。
- 当前 Milestone 的强制范围以对应 Implementation Profile 为准。
- Future Milestone 和 Future RFC 不得自动成为当前实现门禁。
- Roadmap 不承诺日期；顺序可按样本结果调整，但必须更新 Profile。
- Source 不可变、稳定身份、分层、追溯和确定性构建是跨阶段约束。
- 任一阶段通过都不自动授权下一阶段、公开发布或全量转换。

## 2. 项目当前状态

Milestone 0 已建立架构基线，Milestone 0.5 已完成 Scope Alignment，M1-A 与 M1-B 已通过架构门禁。M1-C1 已通过人工验收，M1-C2A 已生成全量 Markdown 构建，M1-C2B 已通过 Release Gate。M1-C3 已完成人工与自动验收。M1-C4 已生成低文件数 GPT Project Export。

---

## Current Product State

### Current Release

当前产品基线包括 M1-C3 Obsidian Baseline Vault 与 M1-C4 GPT Project Export。前者包含 6,819 份可搜索 Note、104 个本地资产、8,187 个完整 HHC 导航节点、1,489 个分层导航索引、首页、稳定 Ownership Manifest 与报告；后者把全部正文原字节收纳为 20 个可上传文件，通过全局任务路由和包级内容导航减少无关检索，并保留后续文件名额。

### User-visible Capabilities

- Full Markdown Archive：6,819 个真实 HTML Entry 已生成可阅读 Markdown；
- Asset Extraction：104 个可用本地资产已提取并校验；
- Deterministic Build：两次独立全量构建完整目录零差异；
- Validator：可检查 UTF-8、路径、Front Matter、Manifest、Asset 与输出闭合；
- Reports：提供编码、Fidelity、Link、Asset、Navigation 和失败分类；
- Manifest：每个物理 Entry 有稳定 ID、Source Path、Navigation Paths 和输出位置；
- Obsidian Baseline Vault：可直接打开、按与 Source Path 最相符的 HHC 主路径浏览和全文搜索；
- Navigation：Home、69 个顶层入口及保留纯目录节点与兄弟顺序的完整 HHC 树；
- Link Projection：已解析内部链接和本地图片在发布视图中闭合。
- GPT Project Export：可把完整正文作为低文件数资料上传给 GPT 使用，并按任务、来源和导航主题缩小检索范围。

### Current Limitations

产品暂未实现：

- 尚未向用户现有 Vault 执行增量覆盖发布；
- 尚无 Fragment、Knowledge Node 或 AI Native Knowledge Library。
- GPT 内容包不包含图片二进制，合并后的原相对链接不保证可点击。

Source Reality：

- 4,403 个缺失目标、135 个缺失 Anchor、134 个缺失本地 Asset；
- 38 个 External Image Reference；
- 74 个正文极短但完整保留的 Source 页面；
- 1 个 Intentional Blank 页面。

当前 Milestone：

- M2 以 Rule Cluster Pilot 启动可选择的规则知识层；
- Antigravity 已外部实现 Book Catalog 与 Ruleset Profile，等待 LoreBuddy 接纳验收；
- 本轮只证明 D&D 2024 小样本的候选、审核、Rule Card 与终端候选包闭环。

### 已完成的真实使用验证与下一步

用户已经在 ChatGPT Project 使用 M1-C4 Export，并形成两套基于实际体验的优化稿：
一套为 GPT 的 20 文件以内特化输入，另一套为 NotebookLM 使用的语料库。两者又用于
DND Terminal 的建卡、测试怪物数据、技能合规和角色卡合规工作。结论见
[`M1 使用反馈与 v0.2 需求依据`](docs/milestone-1/m1-usage-feedback-and-v02-requirements.md)。

M1 已冻结为 `v0.1.0`。当前已启动 M2 Rule Cluster Pilot；其边界、外部交付状态与
验收门禁见 [`M2 文档索引`](docs/milestone-2/README.md)。

---

## User Deliverables

| 阶段 | User Deliverable |
|---|---|
| M0 | 可审阅的 Knowledge Package Architecture Baseline |
| M0.5 | 与本地优先、单用户、Obsidian 目标对齐的 M1 实施合同 |
| M1-A | 可执行 CLI、Schema Registry、Validator 与测试基础 |
| M1-B | 完整 Source Inventory、原始 Entry 保存和可复核摘要 |
| M1-C1 | 10 个经人工验收的真实 Markdown 样本 |
| M1-C2A | Full Markdown Archive、Assets、Reports、Validator、Manifest |
| M1-C2B | Release Checklist、Known Limitations、Release Decision、Publisher Input Contract |
| M1-C3 | Obsidian Baseline Vault：可浏览、可搜索、图片、内部链接、自动索引 |
| M1-C4 | GPT Project Export：20 个上传文件、完整正文、稳定来源元数据和后续文件余量 |
| M2 | 可选择的规则知识层试点：Book Catalog 接纳、Rule Object 候选/审核、Rule Card 与终端候选包 |
| M3 | 可日常使用、可增量发布、可回滚的正式 Obsidian Vault |
| M4 | 面向实际查询的导航、全文搜索与来源定位 |
| M5 | 第二 Ruleset 的可用知识包，证明产品不绑定 D&D |
| M6 | 与生成内容隔离的个人笔记、Campaign、House Rule 和批注工作流 |
| Future RFC | 经授权、可审计的共享或公开 Release |

---

## 3. Milestone 0：Architecture Baseline

### Goal

建立 Knowledge Package 的长期架构上限和 CHM 输入事实基线。

### In Scope

CHM 只读分析；Package 与四层边界；Source、Provenance、Node、Relationship；Markdown、Metadata、Schema、Index；Integrity、Rights、Access、Release；D-001 至 D-016 和风险登记。

### Out of Scope

正式摄取与转换；可执行转换器和发布器；Obsidian 产品体验；Runtime、RAG、Embedding 与 Campaign。

### Acceptance Criteria

文档交叉一致；CHM 统计与摘要可复核；决策和风险有记录；架构能容纳多个 Ruleset 及私有/公开场景。

### Exit Gate

M0 Draft 被接受为 Architecture Baseline；未激活能力不成为 M1 门禁。

### User Deliverable

一套可供后续实现、审核和迁移使用的 Knowledge Package Architecture Baseline。

---

## 4. Milestone 0.5：Scope Alignment

### Goal

把长期架构与当前单用户、本地优先、Obsidian 消费需求对齐。

### In Scope

M1 Implementation Profile；Decision Status；Obsidian Publish Profile；Acceptance Criteria；Deferred Backlog；Roadmap。

### Out of Scope

创建 Package；解包或转换 CHM；编写转换器、发布器或 Fixture；写入 Vault。

### Acceptance Criteria

Required / Deferred 无歧义；Workspace / Vault 和本地配置边界明确；未来 Rights / Public Release 不阻塞 M1；文档通过一致性检查。

### Exit Gate

用户确认 M1 Profile、决策状态、Obsidian Profile 和验收标准。

### User Deliverable

一份明确当前产品边界、Vault 目标和 Deferred 能力的 M1 实施合同。

---

## 5. Milestone 1：Minimal Ingestion Vertical Slice

当前状态：M1-A、M1-B 与 M1-C1 已确认；M1-C2A 已完成；M1-C2B Release Gate 已通过；M1-C3 人工与自动验收完成；M1-C4 GPT Project Export 已完成。

### Goal

用 5～10 个复杂样本证明 CHM 到 Obsidian 阅读视图的最小纵向闭环。

### In Scope

受限 Acquisition Package；完整 Entry Inventory 与原始 Entry；样本解析；Boundary 人审；Knowledge Node 与 Provenance；五类最小 Index；Staging、Dry Run、Publish Manifest、测试发布；基础 Fidelity 和确定性重跑。

### Out of Scope

全量转换；公开发布和完整 Rights Governance；正式 Vault 目录；Runtime、搜索、RAG、Embedding；插件、双向同步和多设备并发发布。

### Acceptance Criteria

高风险样本通过自动/人工验收；四层可重建；Obsidian Link、Properties、附件跨设备可用；所有权、失败恢复和本地锁通过；重跑结果确定。

### Exit Gate

用户批准样本格式和日常体验；Acceptance Record 无未批准 Critical / High 问题。

### User Deliverable

Full Markdown Archive、可追溯 Manifest、Assets、Reports，以及 Release Gate 通过后的 Obsidian Baseline Vault。

---

## 6. Milestone 2：Rule Cluster Pilot

### Goal

以受控的 D&D 2024 小样本证明“书籍选择 → 规则候选 → 审核对象 → LLM Rule Card /
终端候选包”的闭环。受控批次是这一闭环的实现纪律，而不是本阶段唯一产品目标。

### In Scope

M2-A 外部 Book Catalog 交付的接纳验收；Ruleset Profile；最小 Rule Object 契约；
来源绑定；规则候选；确定性验证；人工审核；D&D 2024 状态/生命周期与武器精通的
小样本；Rule Card；只读终端候选包；质量报告。

### Out of Scope

无人监督全量转换；将模型候选自动采纳；直接修改 DND Terminal；公开发行；正式目录
迁移；AI Runtime、向量数据库；COC、社交与心智规则簇。

### Acceptance Criteria

外部 M2-A 交付可与 M1-C3 Manifest 闭合且其身份状态不被夸大；每个批准对象可定位
到 Entry 与正文范围；候选不能绕过审核；相同已批准输入可确定性生成 Rule Card；终端
候选包不包含未批准对象；人工案例验证所选状态与武器精通链路。

### Exit Gate

用户接受 M2-A 接纳结论与试点规则簇；候选/批准边界、来源定位和低推理消费收益均可
复核。通过不自动授权全量转换、COC 扩展或 DND Terminal 写入。

### User Deliverable

可选择的 D&D 2024 规则试点包：经审核的少量规则对象、Rule Card、终端候选包，以及
覆盖、问题与质量报告。

---

## 7. Milestone 3：Obsidian Production Publishing

### Goal

把已验证内容安全发布到正式 Obsidian 子目录，形成日常流程。

### In Scope

正式发布目录；发布端迁移；稳定 Properties、附件和导航；增量发布、备份、回滚、可观测性；测试目录受控迁移；必要时加强原子切换。

### Out of Scope

LoreBuddy 自有同步；多设备并发发布；用户编辑自动回流；公开互联网发行。

### Acceptance Criteria

正式目录在目标设备稳定可用；不破坏用户内容；迁移和回滚完成演练；Dry Run 与错误报告可理解。

### Exit Gate

用户接受正式目录为日常只读知识库，并确认恢复流程可操作。

### User Deliverable

可作为日常 TRPG 参考资料使用的正式 Obsidian Vault，支持增量更新、备份和回滚。

---

## 8. Milestone 4：Knowledge Navigation and Search

### Goal

在不改变事实源的前提下增强导航、检索和关系发现。

### In Scope

语义导航；Alias、Relationship、Provenance 查询；本地全文搜索；可重建 Graph / Search Index；搜索质量评估。

### Out of Scope

RAG、Embedding 和 Agent Runtime；把搜索数据库变成事实源；自动生成规则解释。

### Acceptance Criteria

常见查询定位正确 Node 和来源；索引可删除重建；私有边界不泄漏；搜索失败有固定样例。

### Exit Gate

用户确认导航和搜索改善真实使用且没有引入事实漂移。

### User Deliverable

可从标题、Alias、关系和来源快速定位知识的本地导航与搜索体验。

---

## 9. Milestone 5：Second Ruleset Package

### Goal

用第二个 TRPG 系统验证平台 Core 没有绑定 D&D。

### In Scope

选择第二 Ruleset 输入；新 Package 与命名空间 Profile；Core 复用评估；跨系统 Alias、Relationship、导航测试；Schema 提升或保持特化的决策。

### Out of Scope

万能 TRPG Schema；自动统一语义不同的概念；多系统 Runtime Resolver。

### Acceptance Criteria

第二系统无需修改核心身份模型；特有字段保持隔离；只有多系统证明的语义才考虑进入 Core；迁移不改写已有正文。

### Exit Gate

Core / Profile 边界通过第二系统反证，相关 ADR 被确认。

### User Deliverable

一个真实可用的第二 Ruleset Package，以及跨系统并存而不互相污染的知识体验。

---

## 10. Milestone 6：Personal Knowledge and Campaign Layer

### Goal

支持个人笔记、Campaign、House Rule 和长期批注，同时保护来源转写。

### In Scope

私有 Campaign Package；Session、NPC、Location、Timeline、House Rule；Annotation / Overlay；Stable Node ID 关联；个人内容备份、访问与迁移。

### Out of Scope

把用户编辑合并进忠实转写正文；默认公开 Campaign；未设计的多用户实时协作。

### Acceptance Criteria

用户与生成内容分离；重新发布不丢个人内容；House Rule 覆盖显式可追溯；私有索引不跨边界泄漏。

### Exit Gate

用户确认个人知识工作流稳定，访问和恢复边界明确。

### User Deliverable

不会被重新发布覆盖的个人笔记、Campaign、NPC、Timeline、House Rule 和批注空间。

---

## 11. Future RFC：Sharing and Public Release

### Goal

仅在出现真实共享或公开发行需求时启用完整 Rights、Disclosure 与 Release 架构。

### In Scope

Rights Authority Domain；Claim / Lineage / Decision；Release Rights Binding；Public Receipt / Attestation；Access / Disclosure；Public Release Manifest、Payload 白名单和可信分发。

### Out of Scope

用本地 Publish Manifest 冒充公开合规；Rights 未知时默认允许；通过保留私有指纹规避披露审核。

### Acceptance Criteria

权利主体、Reviewer 和动作明确；默认拒绝合并与 Binding 可重放；公开 Payload 不泄漏受限证据；法律授权与技术完整性分别记录。

### Exit Gate

独立 RFC、法律/授权确认、威胁模型和 Implementation Profile 全部批准后，才允许公开 Release。

### User Deliverable

在授权明确后可安全共享、审计和验证的 LoreBuddy Release。

## 12. Roadmap 变更规则

- 新需求先归类到当前 Profile、Future Milestone 或 Future RFC。
- 改变当前 Exit Gate 必须更新对应文档并说明迁移影响。
- 延后能力不得用未版本化临时字段提前占位。
- 样本可以调整顺序，但不能放宽 Source 不可变与追溯。
- 每个 Milestone 完成后重新评估下一阶段，不自动连续执行。
