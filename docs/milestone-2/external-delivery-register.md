# M2 外部交付登记

状态：**pending_acceptance**

## D-2026-09-04-antigravity-book-catalog

| 字段 | 当前登记 |
|---|---|
| 提供方 | Antigravity |
| 交付物 | Book Catalog、Entry-to-Book Mapping、Ruleset Profiles、Review Queue、统计报表 |
| 交付标识 | `antigravity-book-catalog@2026-09-04` |
| 声明覆盖 | 6,819 M1-C3 Entry；6,808 映射；11 条隔离队列；92 本候选书籍/独立来源 |
| 当前用途 | M2-A 接纳候选；不得直接作为批准规则、出版身份、Rights 结论或 DND Terminal 输入 |
| 输入身份 | 待提交 M1-C3 Publisher Manifest 摘要与交付文件摘要后锁定 |
| 接纳状态 | `externally_implemented_pending_acceptance` |

交付的逻辑路径为 `lorebuddy-规则书/01-规则集画像与书籍归属/`；该位置属于用户提供的
外部工作区，不是 LoreBuddy 仓库内的事实源。本项目不通过本登记复制或收纳其规则正文。

## 接纳工作

1. 由 Codex 对照锁定的 M1-C3 Manifest 复算集合闭合和路径一致性；
2. Antigravity 提供生成器版本、运行参数、输入 Manifest 摘要及每个交付文件摘要；
3. 将 `authority` 等路径分类字段降为 `claimed` 的来源身份信息，除非另有审核证据；
4. 为每条映射补充或可确定性重建 `mapping_basis`；
5. 通过后在本文件追加接纳结论；失败项仅进入 Review Queue，不回写 M1 Source。

## Codex 独立接纳结论（2026-09-09）

**结论：`pending_acceptance`（未通过 M2-A Gate）。** 此结论只针对
`antigravity-book-catalog@2026-09-04` 于 2026-09-09 11:45 +08:00 生成的候选交付；
不修改 M1-C3、规则正文或任何 DND Terminal 数据。

| 检查项 | 独立结果 | 证据 / 结论 |
|---|---|---|
| 上游输入锁定 | PASS | 本地 `build/m1c3-obsidian-baseline/.lorebuddy/publisher-manifest.jsonl` 为 6,819 条，SHA-256 `d9172ac3befdd0be00547d9d72f9f212e2ead8c16412c96b9a155a32adf56458`，与交付声明一致。 |
| 集合闭合与路径 | PASS | `entry-to-book-mapping.m2a.jsonl` 6,808 条与 `review-queue.jsonl` 11 条互斥，联合集合与 M1-C3 Manifest 一致；逐条 `source_path`、`output_path` 一致。 |
| 交付可复现元数据 | PASS（技术元数据） | Delivery ID、生成器版本、复现命令、输入摘要及 6 个登记文件的 SHA-256 / 大小均存在，且实测摘要一致。 |
| 映射字段语义 | PASS | 映射均含合同必需字段；`mapping_status: deterministic`，`source_identity_status: claimed`，并使用声明的三类 `mapping_basis`。 |
| 未审计身份 / 权威升级 | **BLOCK** | `book-catalog.yaml` 的 92 条记录仍含 `authority: official-current`、`official-legacy`、`official-expansion` 等字段。它们没有独立审核证据或 `claimed` 身份包络，且与 Antigravity 报告“已移除 authority 字段”的声明矛盾；不得据此升级出版身份、Rights、规则权威或终端采纳。 |
| Profile 的语义边界 | **BLOCK** | `ruleset-profiles.yaml` 除书籍集合和 fallback 外还使用 `excluded_categories`、`version_precedence`，并在战役 Profile 中使用 `campaign_overlay`。这些字段超出 M2-A 的输入选择职责；即使报告声明 fallback 不裁决冲突，当前结构仍无法证明没有隐含的冲突裁决或 House Rule 覆盖。 |

本次独立检查由 `lorebuddy.validation.validate_m2a_delivery` 固化；它的失败不会写入
外部交付目录或 M1 输出。M2-B、M2-C、M2-D 仍未启动。

### 返还 Antigravity 的阻断修复任务

1. 发布新的 Delivery ID（不得覆写本候选），将 Catalog 的 `authority` 改为明确的
   `claimed_*` 分类并以 `source_identity_status: claimed` 包络，或移除该字段；不得新增
   Rights、`verified`、`approved` 或 DND Terminal 采纳断言。
2. 将 M2-A `ruleset-profiles.yaml` 收敛为 `id`、显示名称/说明、`active_books`、
   `fallback_books`；把 `excluded_categories`、`version_precedence`、`campaign_overlay` 留在
   未接纳的候选设计或后续经用户确认的 Profile 扩展，不能作为 M2-A 输入选择语义。
3. 重算所有受影响文件及 Delivery Manifest 摘要，附上 Antigravity 单元/冒烟结果；随后由
   Codex 用固定 M1-C3 Manifest 重新运行独立 Validator。接纳前不得生成 Rule Assertion、
   Rule Card 或任何终端候选包。
