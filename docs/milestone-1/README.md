# Milestone 1：最小摄取纵向闭环

状态：**M1 Design Confirmed / M1-A 完成待确认**  
实施配置版本：`m1-profile@0.1.0`  
前置基线：[Milestone 0](../milestone-0/README.md)

## 1. 目标

Milestone 1（M1）验证 LoreBuddy 的最小纵向闭环能在真实本地环境落地：保存一个 CHM Artifact 及全部 Entry，从中选择 5～10 个复杂样本，经人工边界确认生成 Knowledge Node、最小派生 Index 和 Obsidian Publish View，并证明结果可追溯、可验证、可重建。

M1 是单用户、本地优先（Local-first）的实施切片，不是公开发行、全量摄取或 AI Runtime 里程碑。

## 2. 规范关系

M0 描述 LoreBuddy 的长期架构上限；M1 Implementation Profile 决定当前必须实现的子集。M0 中未被 M1 标记为 `REQUIRED` 的能力，不自动成为 M1 门禁。

优先级如下：

1. Source 不可变、Source / Library / Metadata / Index 分离、稳定身份、基础 Traceability 和确定性构建等 M0 不可变原则继续生效；
2. [Implementation Profile](implementation-profile.md) 决定 M1 激活哪些 M0 协议；
3. [Decision Status](decision-status.md) 决定 D-001 至 D-016 在 M1 的采用状态；
4. [Obsidian Publish Profile](obsidian-publish-profile.md) 只约束 M1 的本地消费视图，不定义公开 Release；
5. Future Milestone 与 Future RFC 不得反向扩大 M1 门禁。

若 M1 文档与 M0 的不可变原则冲突，必须停止并新增 ADR；若只是未激活 M0 的未来能力，以本 Profile 的 `DEFERRED` / `OUT_OF_SCOPE` 为准。

## 3. 最小纵向闭环

```text
原始 CHM
→ 受限 Acquisition Package
→ Entry Inventory
→ 原始 Entry 保存与摘要
→ 5～10 个复杂样本解析
→ Boundary Candidate
→ 人工确认
→ Markdown Knowledge Node
→ 基础 Provenance
→ 最小派生 Index
→ Obsidian Publish View
→ Workspace Staging 验证
→ Dry Run
→ 安全发布到测试子目录
→ 基础 Fidelity 验证
→ 确定性重跑验证
```

本轮只定义该闭环，不执行任何一环。

## 4. 文档索引

| 文档 | 职责 |
|---|---|
| [Implementation Profile](implementation-profile.md) | M1 调用的 M0 子集、状态和实施边界 |
| [Decision Status](decision-status.md) | D-001 至 D-016 的 M1 状态 |
| [Acceptance Criteria](acceptance-criteria.md) | 样本、构建、发布和人工验收门禁 |
| [Obsidian Publish Profile](obsidian-publish-profile.md) | Workspace → Staging → Vault 的本地发布合同 |
| [Backlog](backlog.md) | 暂缓能力、未来启用条件和兼容点 |
| [M1-A Executable Foundation](m1a-executable-foundation.md) | Schema、Registry、Fixture、Validator、CLI 与测试基础 |
| [项目 Roadmap](../../ROADMAP.md) | 渐进式开发顺序与各阶段 Exit Gate |

## 5. 本轮不产生的内容

- 不创建 `packages/`；
- 不创建正式 `sources/`、`library/`、`metadata/` 或 `index/`；
- 不解包或转换 CHM；
- 不编写转换器、索引器或发布器；
- 不创建本地配置文件；
- 不访问或写入 Obsidian Vault；
- 不修改 `.obsidian/`；
- 不生成样本 Node。

## 6. M1 实施硬边界

- 当前只有一个 Build / Publish Authority；
- Vault 同步由用户现有机制负责；
- 生成内容默认只读、可重建；
- Vault 不是事实源、缓存或中间工作目录；
- 发布器只能管理 Publish Manifest 声明拥有的文件；
- M1 不声称 `Release Ready(public)`、完整 Rights 合规或完整 M0 Fidelity；
- 当前 CHM 的来源身份与再分发权仍为 `unknown`，M1 产物保持受限、仅用于本地验证。

## 7. 当前执行状态

M1 设计已确认。`Milestone 1-A: Executable Foundation` 已建立可执行 Schema、Registry、Fixture、Validator、稳定 ID / Slug、配置读取、CLI 和自动测试，等待本轮实现确认。

进入 M1-B 前仍需用户确认：

1. 8 个 M1 最小 Schema 的字段边界；
2. UUIDv5 只用于显式输入的确定性基础身份，最终 Node 身份仍等待样本验证；
3. 中文标题在 M1-A 不依赖拼音库，默认回退为 `node--<short-id>.md`；
4. M1-B 只允许建立受限 Acquisition Package 与真实 Inventory，不自动开始样本转换；
5. 本地绝对路径继续只由未跟踪配置注入。

确认 M1-A 不等于授权公开发布、CHM 摄取或 Vault 写入。
