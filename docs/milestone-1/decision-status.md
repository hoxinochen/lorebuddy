# M1 架构决策状态

状态：Confirmed  
基线：[M0 D-001 至 D-016](../milestone-0/decisions-and-risks.md)

## 1. 状态定义

- `ACCEPTED_FOR_M1`：作为 M1 实施约束生效；不代表该能力全部完成；
- `ACCEPTED_WITH_LIMITS`：接受方向，只实现明确列出的最小子集；
- `DEFERRED`：保留设计，推迟到未来 Milestone / RFC；
- `REQUIRES_SAMPLE_VALIDATION`：方向成立，但必须由样本验证后才能冻结实施细节。

## 2. 决策表

| 决策 | M1 状态 | M1 解释 |
|---|---|---|
| D-001 Package 是发布与权限边界 | `ACCEPTED_FOR_M1` | 一个受限 Acquisition Package 承载当前 CHM；Obsidian View 不是 Package |
| D-002 保留 Artifact 与全部 Entry | `ACCEPTED_FOR_M1` | M1 必须保存容器和完整 Entry Inventory，不只保存样本 |
| D-003 Work / Edition / Artifact / Entry / Fragment 分层 | `ACCEPTED_FOR_M1` | 样本 Provenance 使用该链；未知出版映射保持 unknown |
| D-004 Node ID 与内容和路径解耦 | `REQUIRES_SAMPLE_VALIDATION` | 验证 UUIDv7 分配、重跑复用、标题变化和 Slug 稳定策略 |
| D-005 一个 Node 一个表达版本 | `ACCEPTED_FOR_M1` | 样本不得混合版本、语言、权威上下文或编辑说明 |
| D-006 Core Envelope + 命名空间 Profile | `ACCEPTED_FOR_M1` | M1 先证明 Core；D&D 特有字段只能进入命名空间扩展 |
| D-007 权威、规范性与范围分离 | `ACCEPTED_FOR_M1` | 只记录样本已知事实；未审核字段为 unknown，不实现 Resolver |
| D-008 Boundary Ledger 是边界权威 | `ACCEPTED_FOR_M1` | 机器仅提议，用户批准后才能生成正式 Node |
| D-009 只维护正向关系 | `ACCEPTED_FOR_M1` | 反向关系完全由最小 Index 生成 |
| D-010 Index 派生且确定性构建 | `ACCEPTED_FOR_M1` | M1 实现五类最小索引；完整 Release Manifest 暂缓 |
| D-011 私有 Campaign 使用独立 Package | `ACCEPTED_FOR_M1` | 接受隔离原则；M1 不实现 Campaign 或 Access Domain |
| D-012 当前 CHM 先进入受限摄取 Package | `ACCEPTED_FOR_M1` | 不因本地 Obsidian 使用把内容提升为 public |
| D-013 公开声明与受限审计证据分离 | `DEFERRED` | 未来 Sharing / Public Release RFC；M1 无公开消费者 |
| D-014 版本化事件协议与稳定映射 | `ACCEPTED_WITH_LIMITS` | 只实现 Artifact / Entry 摘要、Visible Text 和样本所需基础 Structure |
| D-015 Rights Decision 与 Release Binding 分离 | `DEFERRED` | 未来 Rights Governance RFC；M1 Publish Manifest 不承担权利判断 |
| D-016 Rights Authority Domain 与 Access Domain 分离 | `DEFERRED` | 未来多主体或公开发行时启用 |

## 3. 需要样本回答的问题

D-004 在 M1 不预先冻结以下细节：

1. UUIDv7 在 Boundary Approval 时还是更早分配；
2. 可读 Slug 是否包含短 ID 后缀；
3. 标题修改时文件名保持不变还是生成受控 Rename；
4. 同名 Node 的消歧优先使用规则版本、来源范围还是短 ID；
5. Obsidian Wikilink 以文件路径还是 Alias 作为稳定目标。

样本验证必须以“旧 Link 不漂移、重跑无意外 Rename、不同大小写/Unicode 文件系统无冲突”为选择标准。

## 4. D-014 的 M1 限制

M1 必须实现：

- CHM Artifact 摘要；
- 全部 Entry 的长度与摘要；
- 每个样本的 Visible Text Event 比较；
- 样本实际出现的 Heading、List、Table、Link、Image、Pre / Code 基础结构比较；
- 失败时输出稳定问题记录，不静默降级。

M1 不实现完整 Source Fragment Event、全部 Reference Context、Full Fidelity Coverage Map、公开 Fidelity Attestation 或跨实现完整 Fixture。M1 结果只能标记为 `m1-sample-validated`。

## 5. Deferred 的兼容要求

D-013、D-015、D-016 延后期间：

- 不复用未来 Rights / Access 字段表达本地发布状态；
- 不把 Obsidian Publish Manifest 命名为 Release Manifest；
- 不把当前用户身份写成隐式全局 Rights Authority；
- 稳定 Node / Artifact / Entry / Fragment ID 和摘要必须能被未来 Audit Record 引用；
- 当前受限 Package 不得声明公开可再分发。

## 6. 确认效果

确认本表只批准 M1 的实施范围。它不修改 M0 决策正文，不授权公开发布，不批准全量转换，也不承诺 Future Milestone 的实现顺序之外的具体方案。
