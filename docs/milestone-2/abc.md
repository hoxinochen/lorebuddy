# M2 ABC：Rule Cluster Pilot 启动授权

状态：**Confirmed**
确认日期：2026-09-09
开发版本：`v0.2.0.dev0`

## 1. 目标

以 D&D 2024 小样本验证：书籍与 Ruleset 选择能够约束输入范围；规则能被表达为带来源
定位和审核状态的对象；批准对象可以确定性编译为低推理模型可读的 Rule Card，以及
只读的 DND Terminal 候选包。

## 2. 协作边界

| 角色 | 责任 |
|---|---|
| Codex | Schema 与验收设计、任务规划、输入锁定、确定性 Validator、独立复核与 Gate 结论 |
| Antigravity | Book Catalog、候选抽取、规则簇实现、单元/冒烟测试、交付 Manifest 与问题清单 |
| 用户 | 确认 Ruleset Profile、审核策略、冲突处理和是否采纳下游候选 |
| DND Terminal | 仅作为批准候选包的未来消费者；本阶段不写入或替换其现有规则 |

Antigravity 的通过测试只能证明其交付符合声明的测试范围，不能替代 Codex 的独立验收，
也不能把候选提升为规则权威。

## 3. 范围与停止条件

允许 M2-A 外部交付接纳、最小 Rule Object 契约、候选/批准状态、D&D 2024 的 Conditions /
0 HP 试点、少量 Weapon Mastery 试点、Rule Card 和终端候选包。

在用户明确扩大范围前，停止于试点验收；不做全库转换、COC、社交/心智簇、Runtime、
向量检索、公开发布、真实终端写入或用户 Vault 覆盖。

## 4. 不可变输入

M1-C4 `v0.1.0` 是冻结基线。外部交付必须声明其使用的 M1-C3 Manifest 身份、文件摘要、
生成器版本和输入 Profile。任何缺失或不匹配都使交付保持 `pending_acceptance`。
