# LoreBuddy M1 Backlog

状态：Accepted Backlog  
原则：Backlog 项不是 M1 门禁，除非通过新的 Implementation Profile 或 ADR 显式激活。

## 1. 使用规则

每项 Backlog 必须说明未来启用条件和 M1 兼容点。不得因为“未来可能需要”提前实现完整协议，也不得用临时字段占用 M0 已保留的语义空间。

优先级只表示未来讨论顺序，不是交付承诺；Roadmap 不承诺固定日期。

## 2. Deferred 架构能力

| 项目 | 预计阶段 | 启用条件 | M1 兼容点 |
|---|---|---|---|
| 完整 Source Fragment Event | M2 候选 | 样本证明基础事件不足，且 Fixture 可稳定 | 保留 Fragment ID、Locator、Entry Digest |
| Full Fidelity Coverage Map | M2 / M3 | 出现多 Provenance、多 Range 或需声明 Full | M1 不使用 `full` / `attested` 状态 |
| 全量 Reference Context | M2 | 批量页面出现 M1 未支持 Attribute / Element | 未知组合稳定阻塞，不静默忽略 |
| Redirect / Tombstone | M2 | 已发布 Node 发生拆分、合并或撤回 | UUID 永不复用，Slug 不承担身份 |
| 完整 Content / Output Manifest | M2 | 受限 Package 批量构建需要分片完整性 | M1 Build Inventory 使用兼容 Path/Digest Record |
| Public Release Manifest | Future RFC | 明确存在对外发行需求 | M1 Publish Manifest 使用不同 Schema / 名称 |
| Rights Authority Domain | Future RFC | 多主体签发或公开发行 | M1 不把单用户写成隐式全局权威 |
| Claim Lineage | Future RFC | 权利 Claim 进入长期治理 | Artifact / Entry / Node ID 可被未来 Claim 引用 |
| Release Rights Binding | Future RFC | 需要对最终公开字节做权利绑定 | Obsidian 本地发布不占用 Binding 字段 |
| Public Attestation | Future RFC | 受限证据需要面向公开消费者投影 | M1 不发布私有 Locator / Digest |
| Access Domain / Principal | M6 / RFC | 出现多个私有用户或隔离 Package | M1 Acquisition Package 保持受限标记 |

## 3. 摄取与规模化

| 项目 | 预计阶段 | 启用条件 | M1 兼容点 |
|---|---|---|---|
| Controlled Batch Ingestion | M2 | M1 样本门禁稳定，错误分类可统计 | 所有人工边界与 Mapping 可重放 |
| 全量 CHM 转换 | M2 后另行批准 | 批次吞吐、失败恢复和审核容量已证明 | M1 不写自动全量开关 |
| 增量重新摄取 | M2 | 出现新 Artifact 版本或 Parser 升级 | Acquire Record 与 Artifact Digest 不覆盖旧版 |
| Parser 多实现交叉验证 | M2 | 复杂 HTML 差异影响 Fidelity | M1 锁定 Parser 与版本 |
| 大规模分片和 Git 性能策略 | M2 | 文件量接近实际性能阈值 | M1 使用稳定 ID 和可迁移路径 |
| 自动重复候选 | M2 | 批量内容需要人工去重队列 | M1 不自动合并同标题/同摘要 Node |

## 4. Obsidian 产品化

| 项目 | 预计阶段 | 启用条件 | M1 兼容点 |
|---|---|---|---|
| 正式目录 `LoreBuddy` | M3 | M1 使用体验和跨设备验收通过 | 测试目录由配置选择，不写进 Node |
| 更强原子目录切换 | M3 | 同步观察到中间状态或 Manifest-last 不足 | M1 Journal / Manifest 保留升级入口 |
| 用户 Annotation Overlay | M6 | 用户需要在生成 Note 旁维护长期批注 | Stable Node ID 可作为 Overlay Key |
| 双向编辑同步 | Future RFC | 明确编辑冲突、来源权威和合并语义 | M1 将生成 View 标记为可重建只读 |
| Obsidian 插件 | Future RFC | 标准 Markdown 无法满足核心 UX | M1 不把插件字段写进规范 Package |
| Wikilink Renderer | M3 候选 | 样本证明路径 Link 的阅读体验不足 | Link Target 仍由稳定 Node ID 解析 |
| 自定义 Properties View | M3 候选 | 用户确认需要更多可见元数据 | 完整 Metadata 留在 Workspace 可投影 |
| 发布端迁移工具 | M3 | 更换唯一发布设备 | 配置不硬编码路径，Manifest 不含设备身份 |

## 5. 导航、搜索与 AI

| 项目 | 预计阶段 | 启用条件 | M1 兼容点 |
|---|---|---|---|
| 语义导航 | M4 | 最小 Source Navigation 与关系索引稳定 | M1 Index 不成为事实源 |
| 全文搜索 | M4 | Node 数量和用户查询需求明确 | Markdown 保持独立可读 |
| 知识图谱视图 | M4 | Relationship 谓词和范围稳定 | 正向 Assertion ID 已保留 |
| RAG / Embedding | Future RFC | 明确检索质量、成本和隐私边界 | M1 不为向量检索改写正文 |
| Agent / Runtime | Future RFC | 有可验证的规则解析与上下文需求 | Package / Node / Provenance 是稳定输入 |
| 本地模型适配 | Future RFC | 模型接口和离线约束明确 | 发布格式不绑定供应商 |

## 6. 多系统与个人知识

| 项目 | 预计阶段 | 启用条件 | M1 兼容点 |
|---|---|---|---|
| 第二 Ruleset Package | M5 | Core Schema 已被 D&D 样本证明且需反证通用性 | D&D 字段只在命名空间扩展 |
| Pathfinder / CoC Profile | M5 候选 | 取得可用输入和样本 | Package 目录不绑定规则系统 |
| Campaign Layer | M6 | 需要 Session、NPC、Timeline 或 House Rule | 私有 Campaign 使用独立 Package |
| 用户个人笔记关联 | M6 | Stable Node Link UX 已验证 | 用户 Note 保持在生成目录外 |
| House Rule Override | M6 | 需要规则上下文与显式覆盖 | M1 不把编辑意见混入转写正文 |

## 7. 同步与协作

| 项目 | 预计阶段 | 启用条件 | M1 兼容点 |
|---|---|---|---|
| LoreBuddy 自有同步 | OUT_OF_SCOPE / RFC | 现有同步无法满足且需求可证明 | M1 不读取或控制同步状态 |
| 多设备并发发布 | Future RFC | 必须从两台设备构建发布 | M1 单发布设备和本地锁明确 |
| 多用户协作审核 | Future RFC | 出现真实多 Reviewer 工作流 | M1 Boundary Approval 保留稳定记录 |
| 分布式发布锁 | Future RFC | 多发布 Authority 被批准 | M1 Lock 只声明本机作用域 |

## 8. 启用流程

Backlog 项进入实施前必须：

1. 指明真实用户需求和失败案例；
2. 选择目标 Milestone 或新 RFC；
3. 更新对应 Implementation Profile；
4. 说明对现有 ID、Schema、Manifest 和迁移的影响；
5. 增加验收标准；
6. 确认不会追溯性改变 Source 或已批准 Node 正文。
