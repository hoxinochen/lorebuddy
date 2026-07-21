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

Milestone 0 已建立架构基线，Milestone 0.5 已完成 Scope Alignment。当前 `Milestone 1-A: Executable Foundation` 已完成待确认：可执行 Schema、Registry、Fixture、Validator、ID / Slug、配置、CLI 与测试已建立；尚未创建正式 Package、读取 CHM 或写入 Obsidian Vault。

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

---

## 5. Milestone 1：Minimal Ingestion Vertical Slice

当前状态：M1-A Executable Foundation 完成待确认；M1-B 尚未开始。

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

---

## 6. Milestone 2：Controlled Batch Ingestion

### Goal

把样本闭环扩展为可暂停、可审核、可恢复的受控批次摄取。

### In Scope

页面族批次队列；Issue / Review；增量构建和恢复；覆盖、质量、性能报告；必要的 Redirect / Tombstone；按真实问题扩展 Fidelity。

### Out of Scope

无人监督全量转换；公开发行；正式目录迁移；AI Runtime 或向量数据库。

### Acceptance Criteria

批次可重跑且失败不污染批准结果；人工决策可复用；未支持页面稳定阻塞并可恢复；性能满足约定批次规模。

### Exit Gate

用户批准批次策略和审核容量，再单独决定是否扩大覆盖。

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

## 12. Roadmap 变更规则

- 新需求先归类到当前 Profile、Future Milestone 或 Future RFC。
- 改变当前 Exit Gate 必须更新对应文档并说明迁移影响。
- 延后能力不得用未版本化临时字段提前占位。
- 样本可以调整顺序，但不能放宽 Source 不可变与追溯。
- 每个 Milestone 完成后重新评估下一阶段，不自动连续执行。
