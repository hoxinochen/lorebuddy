# M2-B 最小 Rule Assertion 契约

状态：**设计已启动**  
Schema：`m2.rule-assertion@0.1.0`  
适用 Profile：`m2-rule-cluster-pilot@0.2.0`

## 1. 目标与停止条件

本契约只证明一个可审核、可追溯的规则断言能够被表达和确定性拒识。它不表达完整规则
语义，不执行规则，不生成全量 Rule Object，也不向 DND Terminal 写入。

M2-B 的停止条件是：Schema、跨字段 Validator 和 fixture 能区分有效候选、缺失来源、
越界来源范围、非法扩展字段，以及审核状态不一致；相同输入得到相同错误集合。

## 2. 为什么采用这一结构

Rule Assertion 采用通用的 `trigger`、`conditions`、`activities`、`effects`、
`prerequisites`、`choices` 六个 Clause 集合。Clause 只保留 `kind` 和原文 `text`，
避免把 D&D 的伤害、职业、法术或怪物字段提升为平台核心；同一结构可容纳其他 TRPG
系统，后续系统特有字段应进入 Profile 扩展。

替代方案是直接建立 D&D 专属的万能对象，或让自然语言字段自由扩展。前者会锁死平台
边界并增加迁移成本，后者无法稳定验证和比较。因此本轮选择封闭字段、保留原文表达，
把语义解释留给后续候选生产与人工审核。

## 3. 最小字段

| 字段 | 要求 |
|---|---|
| `schema` | 固定为 `m2.rule-assertion@0.1.0`。 |
| `id` | 稳定 UUID URN；旧 ID 不复用。 |
| `ruleset` | `system`、`version`、`profile_id`，只声明适用范围。 |
| `assertion` | 六类 Clause：Trigger、Condition、Activity/Operation、Effect、Prerequisite、Choice。至少一类非空；每个 Clause 仅有 `kind` 与 `text`。 |
| `source_bindings` | 至少一个 Entry 绑定，含 `entry_id`、受限相对 `source_path` 和正向 `body_range`。 |
| `review_status` | `candidate`、`in_review`、`approved` 或 `rejected`。 |
| `review_record` | 仅终态必需；包含 review ID、人工决策、审核人和理由，且决策必须与状态一致。 |

Schema 使用 `additionalProperties: false`。因此 `damage`、`class`、`spell` 等未经 Profile
批准的字段会被拒绝，而不会悄悄进入平台核心。

## 4. 审核状态边界

```text
candidate → in_review → approved
                     ↘ rejected
```

Validator 只检查状态与 review record 的结构一致性，不替代人工决定：

- `candidate` / `in_review` 不得携带终态 review record；
- `approved` 必须有 `decision: approved` 的人工记录；
- `rejected` 必须有 `decision: rejected` 的人工记录；
- Schema 通过不等于规则事实通过。

## 5. 版本、迁移与边界

`m2.rule-assertion@0.1.0` 是新增实验 Schema，不改写 M1 Schema，也不把它加入当前 M1
Registry Profile。后续若需要结构变化，应发布新 Schema 版本并保留旧版本 Validator；不
得原地改变 `source_bindings` 的范围含义。M2-C 才能在用户确认的小样本上产生候选，且
必须继续保留 `candidate` 与 `approved` 的边界。

## 6. 交给 Antigravity 的下一项任务

在本 Schema 上实现候选生产器的最小 fixture 适配层：只生成 3–5 个脱敏、可复核的候选
断言，覆盖一个状态/生命周期例子、一个 Activity/Effect 例子和一个 Prerequisite/Choice
例子；每个候选绑定精确 Entry 范围并保持 `review_status: candidate`。同时提供单元测试和
失败清单。不得读取全量规则、自动标记 `approved`、生成 Rule Card 或修改 DND Terminal。
