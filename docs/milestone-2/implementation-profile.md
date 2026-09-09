# M2 Implementation Profile

状态：**Confirmed**
Profile ID：`m2-rule-cluster-pilot@0.2.0`

## 1. 规则表达边界

M2 的平台最小核心不是七个业务簇，而是以下可组合的 Rule Assertion：

```text
Rule Assertion
├─ Trigger / Condition
├─ Activity / Operation
├─ Effect
├─ Prerequisite
├─ Choice
└─ Source Binding + review status
```

`Weapon Mastery`、D&D 2024 状态、法术和怪物特性是 D&D Profile 扩展；COC 的理智、
线索和社交不属于本 Profile。一个候选对象不等于正式规则对象：只有 Schema、来源范围、
Ruleset 适用性和人工审核均通过后才可标记为 `approved`。

## 2. 阶段

| 阶段 | 状态 | 交付与 Gate |
|---|---|---|
| M2-A Book Catalog 接纳 | 外部已实现，待验收 | 锁定外部交付；验证 6,819 Entry 集合闭合、映射依据、Profile 选择与 11 条隔离队列 |
| M2-B 最小契约 | 未开始 | Rule Assertion / Source Binding Schema、候选与批准状态机、Validator fixture |
| M2-C 规则簇试点 | 未开始 | Conditions / 0 HP 与少量 Weapon Mastery 的候选、审核记录和批准对象 |
| M2-D 消费验证 | 未开始 | Rule Card、终端候选包、对照案例、低推理消费质量报告 |

## 3. M2-A 接纳条件

1. 外部交付以独立 Delivery ID、生成器版本、输入 Manifest 摘要和文件摘要登记；
2. 映射 Entry 集合与 M1-C3 Publisher Manifest 完全相等，或明确进入互斥 Review Queue；
3. 每条映射至少有 `entry_id`、`source_path`、`output_path`、`book_id` 与 `mapping_basis`；
4. Book 身份、权威、Rights 和规则采纳状态不得由路径分类自动升级为 `verified` / `approved`；
5. Profile 只决定输入集合及显式 fallback，不暗示跨书冲突已被语义裁决；
6. 接纳检查可重跑，失败不会修改 M1 或下游对象。

## 4. M2-C / M2-D 验收条件

- 每个批准对象都能定位到一个或多个 Entry 和精确正文范围；
- 候选、审核中、批准、拒绝状态不可混淆；
- 相同批准输入生成的 Rule Card 与终端候选包字节一致；
- 人工案例覆盖状态影响、动作/命中触发、资格门禁和至少一个例外/覆盖情形；
- 对照原始长 Markdown，报告输入量、适用 Ruleset、结论、遗漏和无法判定项；
- 未批准对象不会进入终端候选包。

## 5. 明确不做

不主张 LLM 提取天然“零幻觉”或规则执行天然“零漏算”。确定性只适用于冻结的批准对象和
确定性编译器；自然语言抽取始终是可审核候选过程。
