# Milestone 1：最小摄取纵向闭环

状态：**M1-C4 已完成；真实使用验证已补录，待工程基线封存**
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
| [M1-B Controlled Acquisition](m1b-controlled-acquisition.md) | 受控 CHM 摄取、完整 Entry Inventory 与 Source Preservation |
| [M1-C1 Real Markdown Samples](m1c1-real-markdown-samples.md) | 10 个真实页面的 Markdown、资产、链接与确定性验证 |
| [M1-C2A Full Markdown Build](m1c2a-full-markdown-build.md) | 全部 HTML Entry 的 Markdown、资产、报告与稳定发布输入 |
| [M1-C2B Release Gate](m1c2b-release-gate.md) | 异常工程分类、Release Checklist 与 Publisher Input Contract |
| [M1 Known Limitations](m1-known-limitations.md) | Converter、Source Reality 与 Accepted Limitation 基线 |
| [M1-C3 Obsidian Baseline Publisher](m1c3-obsidian-baseline-publisher.md) | 独立 Vault 投影、Ownership、Validator、确定性与产品验收 |
| [M1-C3 人工验收记录](m1c3-acceptance.md) | Obsidian 人工验收、最终基线与本机杂项文件边界 |
| [M1-C4 GPT Project Export](m1c4-gpt-project-export.md) | 低文件数 GPT 项目资料、文件预算、原字节闭合与确定性 |
| [M1 使用反馈与 v0.2 需求依据](m1-usage-feedback-and-v02-requirements.md) | GPT / NotebookLM 实际体验、DND Terminal 验证与下一阶段需求 |
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

M1-A 与 M1-B 已通过架构门禁。M1-C1 已通过人工验收，M1-C2A 已完成全量构建。M1-C2B 已完成三个 Converter Bug 家族的最小修复并通过 Release Gate。M1-C3 已完成自动验收与 Obsidian 人工验收：6,819 份正文、104 个 Asset、8,187 个 HHC 导航节点和 1,489 个分层导航索引。M1-C4 已把该基线确定性导出为 20 个 GPT Project 上传文件，保留全部 6,819 份 Note 原字节，并增加全局任务路由、包级内容导航和默认新版优先策略，不进入 Fragment 或 Knowledge Layer。

M1-B 已确认以下实施边界：

1. M1-A 基础设施继续作为依赖；
2. Artifact 与 Entry 使用显式来源事实派生的确定性 UUIDv5；
3. CHM 原件保持忽略、未提交和不可修改；
4. 真实产物只写入 Git 忽略的 `build/`；
5. 不生成 Fragment、Boundary、Knowledge Node、Library、Relationship 或 Publisher；
6. 不访问 Obsidian Vault，不进入 M1-C。

完成 M1-B 后必须停止并等待架构确认；M1-B 通过不自动授权样本语义解析、公开发布或 Vault 写入。
