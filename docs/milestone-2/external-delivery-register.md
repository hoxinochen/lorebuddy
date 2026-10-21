# M2 外部交付登记

状态：**accepted_for_m2_input**

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

## Codex 独立接纳结论（2026-09-09，前序交付）

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

## Codex 独立接纳结论（2026-09-09，新交付）

**结论：`accepted_for_m2_input`。** 接纳对象为新的
`antigravity-book-catalog@2026-09-09`，前序交付保持在
`m2a-delivery-manifest.2026-09-04.json`、`book-catalog.2026-09-04.yaml` 和
`ruleset-profiles.2026-09-04.yaml` 中归档，未被覆写。

Codex 使用固定的 M1-C3 Publisher Manifest 和仓内
`lorebuddy.validation.validate_m2a_delivery` 重新执行，结果为 `valid: true`，错误数为
0。6,819 Entry 的闭合、6,808/11 互斥分流、逐条路径、Mapping 字段、Delivery 文件摘要、
Catalog 来源身份状态和 Profile 字段白名单均通过。

| 固定对象 | 摘要 |
|---|---|
| Delivery ID | `antigravity-book-catalog@2026-09-09` |
| M1-C3 Manifest | `d9172ac3befdd0be00547d9d72f9f212e2ead8c16412c96b9a155a32adf56458` |
| Mapping | `030a2d30d2d39601a6dc97d1bd293f3742387ca26293f7053e0501755a77bbec` |
| Review Queue | `f72609e9728704418768ef8140dd31bed07ea89c464ea64e67703f6a48f05e55` |
| Book Catalog | `97a55427b642e770f443834316f7be81f95b0f3763d205a7ed7ecc9a2bfbac62` |
| Ruleset Profiles | `d8d97f8635bd86a99299bf2891602223469bec04e940f81836ab4c1952a169c8` |
| Validation Report | `0a976f39be9024a4b33d593d396c758eb5f64e8d989b88f81e66268e9f46b050` |
| Smoke Report | `1f33f32c51f01eb143e0d10e5ed5e6e8e62cdbe52f8911a01d75481b46d8959a` |
| Delivery Manifest | `b53c52a0a205a1098698da69829286eb792ff41fe7ba5b9b9400e9fcb9beebda` |

接纳范围与例外：

- 仅接纳为 M2 后续候选输入边界；不等于出版身份、Rights、规则权威或 DND Terminal 采纳；
- Catalog 的 `source_identity_status: claimed` 仍是未独立核验的来源身份声明；
- Profile 只提供 `active_books` 与 `fallback_books` 选择，fallback 不裁决跨书冲突、覆盖或
  House Rule；
- Review Queue 的 11 条记录继续隔离，不进入规则候选集合；
- 本接纳不授权全量 Rule Object、自动采纳、Rule Card、终端候选包或 Runtime。

Antigravity 的生成器与冒烟测试报告可作为交付证据，但不替代上述 Codex 独立 Validator。

## Codex 独立验收与样本复核（2026-10-16）

User本轮要求验收M2-B修订交付，并独立复核首批四组外部展示样本。本节仅记录当前精确交付的检查与返修结论；M2-A既有`accepted_for_m2_input`不变。

| 检查对象 | 交付身份 | 本次结论 |
|---|---|---|
| M2-B修订交付 | `antigravity-m2b-fixtures@2026-09-09-r2`；Manifest SHA-256 `7c2bcb4ecd2dc653213c0ac9afb9094ec1d96fa21d085f7a21f90f929b000b11` | **未通过完整接纳，保持`externally_implemented_pending_acceptance`**；样本数据及重跑检查通过，但交付生成器有两项未关闭问题 |
| 首批规则簇展示样本 | `antigravity-m2-cluster-samples@2026-10-16-r1`；Manifest SHA-256 `d655d2e741fd5b229db76722b4f763ff85b16a5348bf505a1d69c4beb31bba2d` | **`changes_required`（Codex复核结论）**；可用于讨论样本形态，不能据此批准规则、宣称版本守卫已实现或进入正式消费 |

### 输入身份、方法与通过项

验收时LoreBuddy HEAD为`ba104b64dae881147cc87880b688cadfffa0da18`，唯一既有未提交变更是`docs/milestone-1/backlog.md`，SHA-256为`3c05bdd753a1b2f1ac343ebdf32741505ed7b23de5205315e294483e62dc4468`。Schema、Validator、M1-C3 Manifest、M2-A Mapping和NotebookLM输入摘要与交付声明一致；dirty文档被单独核对，没有用HEAD替代实际字节。

先审阅两份生成器，再将生成器原字节分别复制到两个新目录，各用独立进程运行。所有写入均位于仓库忽略的`build/m2-independent-review-2026-10-16/`及临时目录，未直接运行会覆写外部交付目录的原位重现命令。独立检查不只读取生产方的PASS报告，也不把生产方自己的双目录检查当作唯一复现证据。

| 项目 | 独立检查结果 |
|---|---|
| M2-B交付文件 | Manifest列出的21个文件摘要／大小全部匹配；另有Manifest本身。历史归档按旧Manifest的21个文件核对通过，根目录旧Manifest副本与归档Manifest一致；历史文件不混入当前规范输出集合 |
| M2-B正向与原文 | 5个候选通过仓内Validator；27条子句逐字位于绑定UTF-8切片，且本次每条均唯一命中；6个来源绑定均实际覆盖子句；候选没有伪造Review |
| M2-B负向 | 6个负向对象都被拒绝；独立检查本次实际错误码与预期单码全等。此数据结果通过，不等于生产方生成器已经实施严格全等检查 |
| M2-B复现 | 两个新进程输出共22个文件（含Manifest）逐字节相同，并与当前交付的规范输出相同 |
| 展示样本文件与状态 | 29个Manifest列出文件摘要／大小及集合闭合通过；8个断言通过Schema且均为`candidate`，10份投影为`draft`，预览为`sample_preview`；这些不是批准状态 |
| 展示来源桥接 | 8条桥接逐条核对Entry身份、原始路径、M2-A书籍归属、完整Note／Raw Entry摘要，以及三侧片段摘要、范围与行号。M1-C3与NotebookLM片段仅统一换行后相等；出版／翻译／权利状态保持原有边界 |
| 展示复现 | 两个新进程输出共30个文件（含Manifest）逐字节相同，并与交付相同；这证明输出可复现，不证明其中规则解释正确 |
| 仓内回归 | `.venv/bin/python3 -B -m pytest -q tests/test_rule_assertion.py tests/test_m2a_delivery.py -p no:cacheprovider`通过（5项） |

### M2-B未通过项

1. **M2B-R2-001 / P1：输入锁定只有声明，缺少运行前实测相等检查。** `generate_and_verify_m2b.py:24`起将HEAD、dirty状态／摘要及Schema／Validator摘要写成常量；启动流程没有在写产物前复算并拒绝不匹配输入。独立故障注入只把已导入模块内的`SCHEMA_SHA256`改成64个`0`，实际Schema文件不变，生成器仍报告SUCCESS，并在新Manifest写入错误声明。当前正式交付的摘要确实匹配，但该生成流程不能保证输入变化后仍只消费锁定合同。返修要求：写输出前核对真实输入与固定声明；不匹配立即失败。增加Schema／Validator／基线或受锁定dirty输入不匹配的反例；不把任何dirty状态一律当错误。
2. **M2B-R2-002 / P2：负向错误码只检查包含关系。** `generate_and_verify_m2b.py:916`使用`exp in res["errors"]`；独立注入在INV-1的实际错误列表追加`UNEXPECTED_REVIEW_FAULT`，生成器仍完成并报告SUCCESS。返修要求：按声明的重复／顺序处理方式比较完整预期与实际错误码集合，额外或缺失错误均失败；为额外错误补反例。

旧的F2原文和报告范围问题在r2数据中已经修复，不重复作为本次失败项。上述两项关闭前，不将r2登记为已通过M2-B Gate。返修交付使用新Delivery ID并保留本次字节和失败证据。

### 四组样本未通过项

1. **M2S-R1-001 / P1：S4没有真正按输入执行判断。** `generate_and_verify_samples.py:772`的`run_s4_guards()`直接构造两个拒绝结果；Profile活跃书籍也是硬编码，未从锁定Profile读取并执行集合判断。独立检查只在导入模块内把输入Entry的`book_id`换成活跃集合内的`phb-2024`，仍返回`PROFILE_SOURCE_EDITION_MISMATCH`。因此S4阅读样张中的“实测捕获”只能说明固定结果被输出，不能证明版本守卫有效。返修要求：实现仅服务这些样本的小型纯判断函数，接收查询／Entry及真实锁定Profile；同时运行歧义、错误版本、合法2024输入、单一候选等正反例，不扩展产品Runtime。
2. **M2S-R1-002 / P1：S3结构化链加入了错误武器归属和未经支持的命中计算。** `samples/s3-topple-chain.projection.json:21`把`Halberd`列入Topple示例；冻结武器表Entry `urn:uuid:40bb60f7-0636-5aee-8ce3-ff7aaf2f7190`的Halberd行实际是“横扫”，阅读样张和`comparison.md`也没有一致支持机器草案。第28行又把命中简化成`Attack roll >= target AC`，超出此处绑定的Topple条款。返修要求：为武器映射增加精确支持片段并修正列表；将“攻击已确认命中”作为DM／消费者输入，避免本轮重建攻击判定；对照问题中“持战戟”应先说明其默认词条不满足Topple条件，特殊能力有证据时另行表达。
3. **M2S-R1-003 / P2：倒地投影增加了来源没有的攻击类型限制。** `samples/s3-prone-condition.projection.json:17`只表达5尺内近战优势、5尺外远程劣势；绑定原文以攻击者距离划分，没有按近战／远程收窄。返修要求：忠实表达距离条件；以10尺触及近战、5尺内远程分别验证倒地这一来源贡献的修正，并把其他优劣势来源的合并留给独立规则／裁定。
4. **M2S-R1-004 / P2：专注豁免DC在多个表达中不一致。** `samples/S2-paralyzed-incapacitated-concentration.md:26`及第70行遗漏DC上限30，原文、断言及Terminal预览保留了上限。80点伤害时，样张公式给出40，来源与预览给出30。返修要求：公式由同一候选事实生成，至少覆盖这一上界案例，统一图、表、机器投影及预览。
5. **M2S-R1-005 / P2：阅读样张和JSON分别硬编码，新增语义缺少足够细的来源绑定。** `generate_and_verify_samples.py:822`的`render_reading_samples(projections, ...)`没有读取`projections`参数（AST检查读取次数为0）；上述真实差异说明两种表达已发生漂移。现有8条桥接也没有覆盖新增武器表映射、18项技能枚举等支持来源，部分精通取得／更换方式超出绑定的通用资格段落。返修要求：由同一份候选事实生成编辑性摘要、投影及预览；原文保持独立逐字保存；每个新增结构化结论／关系绑定支持片段，证据不足时明确未决，不按常识补齐。只增加当前样本必需的支持片段。
6. **M2S-R1-006 / P2：报告夸大验证结果及来源身份。** `comparison.md:20`等处使用“彻底杜绝混版”“完全隔离”，S4称其为系统实测拦截；`issues.jsonl`又把本地输入称为“官方源数据”。这些超出当前可运行判断、来源身份和未执行模型评测的证据。返修要求：明确人工分析、实际执行用例和未运行模型的边界；使用“受限摄取来源”等符合`claimed`／`unknown`身份的表达，保留失败与未决，不将目录归属或结构化视图升级为规则权威。

S1神导术双版本对照的主要机制及来源切片通过本次核对；S2“麻痹→失能→专注终止”的核心关系与原文相符。这些局部结果不替代其他字段、关系或整包接纳，也不构成正式规则批准。

### 证据、复现及停止点

独立检查脚本与结果位于`build/m2-independent-review-2026-10-16/`：

- `review.py`、`summary.json`：清单、输入、原文、Schema、桥接和独立进程重跑；本次`summary.json` SHA-256为`66b2574c185d56528ecde7a6bbda121094fc9043f5762bc4ab7444b360fdaf48`。
- `reports/findings.jsonl`、`reports/semantic-counterexamples.json`：8项机器可读问题及DC／倒地语义反例；本节保留持久问题结论，临时报告不作为规则事实源。
- `m2b-run-1.log`、`m2b-run-2.log`、`samples-run-1.log`、`samples-run-2.log`：四次独立进程输出；各自新目录保留重建产物。
- `m2b-extra-error-fault.log`、`m2b-lock-mismatch-fault.log`及对应隔离目录：仅修改导入模块的内存值后复现，未改外部生成器或仓内Validator。
- `protected-before.json`：检查开始时固定224个仓内／外部交付／受控输入文件；检查后它们的字节均相同。本节登记是检查完成后的独立文档写入，既有Backlog变更保留。

本轮只追加此登记；外部交付、Schema／Validator、Source、M1输出、NotebookLM／GPT语料及DND Terminal均未修改。未进行正式规则批准、后续实现、Commit或Push；下一步为Antigravity按本次问题修订，再针对新交付复核。

## Codex r3／样本r2独立复核（2026-10-19）

**结论：两项新交付仍需返修。** 原8项问题中，6项在当前修订中关闭，2项部分修复但未关闭；另发现2项可复现问题。以下仅适用于本节锁定的新交付，保留2026-10-16的失败记录，不追溯改写旧结果。M2-A既有接纳不变，不产生正式规则批准或Terminal准入。

| 对象 | 独立实测Manifest SHA-256 | 结论 |
|---|---|---|
| `antigravity-m2b-fixtures@2026-09-09-r3` | `fdfec97d85d332906ac4180e94dab526f0f299a8a1bbf11f19076096440f5625` | 保持`externally_implemented_pending_acceptance`；M2-A输入摘要检查仍有放过失配的分支 |
| `antigravity-m2-cluster-samples@2026-10-16-r2` | `6df11e553f4c0ad616769d315aed753aca1c24ef440366dee7de9be7bd051c25` | `changes_required`；业务判断有实质改进，但确定性、跨视图一致性和引用保真仍未满足 |

### 当前输入与通过证据

检查时HEAD仍为`ba104b64dae881147cc87880b688cadfffa0da18`。实际dirty文件为既有`docs/milestone-1/backlog.md`与本登记，摘要分别为`3c05bdd753a1b2f1ac343ebdf32741505ed7b23de5205315e294483e62dc4468`和`906cade94bcca3dc8bba0c3016ad29ebeb257963df42e6a02739cde8ab0a99ff`，均与新交付声明一致。本节是在这些检查完成后追加，不属于被验输入快照。

- 两份Manifest列出的21／31个文件摘要、大小、集合及当前输入身份核对通过。原M2-B r2归档Manifest仍为`7c2bcb4ecd2dc653213c0ac9afb9094ec1d96fa21d085f7a21f90f929b000b11`；将旧检查快照中的M2-B现役文件映射到r2归档后，连同样本r1与受控来源共91项历史字节检查通过。
- M2-B的5个正向、27条唯一原文子句、6个精确错误码反例通过。分别用两个新进程重建，22个文件（含Manifest）完全相同并匹配交付；独立注入多／少错误码均在写产物前失败。Schema、Validator、HEAD、dirty身份声明失配也均被拒绝。
- 样本的9个候选断言、11个草案投影、9条来源桥接通过结构／状态与路径、全文及片段摘要、范围、行号检查；M1-C3与NotebookLM片段只统一换行后相等。另对9组Raw HTML／Note做去格式与空白的可见文本诊断，结果一致；此诊断不冒充正式Full Fidelity Coverage Map。
- 从实际绑定武器表独立提取出5种失衡武器，Halberd为横扫；已确认命中作为外部事实。S4的歧义、错误版本、合法2024和Profile消歧用例通过；另测无Profile单一候选和内存映射改为活跃书籍的正向用例，判断随输入变化。倒地10尺触及近战／5尺内远程的单源贡献及80伤害DC30案例通过。
- 仓内相关回归再次通过：`.venv/bin/python3 -B -m pytest -q tests/test_rule_assertion.py tests/test_m2a_delivery.py -p no:cacheprovider`，共5项。未运行模型评测，不宣称已测得幻觉率下降。

### 原8项问题的当前处理

| 原编号 | 当前状态 | 独立判断 |
|---|---|---|
| M2B-R2-001 | **部分修复，Open** | 四类声明失配已拦截，但实际M2-A Manifest摘要失配仍可被放过，详见下文 |
| M2B-R2-002 | **Closed** | 当前完整错误码列表严格相等，多／少错误码独立注入均拒绝且不写产物 |
| M2S-R1-001 | **Closed** | 固定拒绝结果已改为实际输入驱动判断，指定正反例及独立正向变更通过；新增字节确定性问题另列 |
| M2S-R1-002 | **Closed** | 新增武器表精确桥接，5种失衡武器与Halberd反例正确，命中判定改为外部事实 |
| M2S-R1-003 | **Closed** | 按距离表达倒地贡献，近战／远程边界案例通过 |
| M2S-R1-004 | **Closed** | 当前阅读／投影／预览均保留DC上限30，80伤害案例正确 |
| M2S-R1-005 | **部分修复，Open** | 阅读已读取投影，移除了部分无来源枚举，但预览仍独立硬编码，一致性检查没有读取预览 |
| M2S-R1-006 | **Closed** | 原过强保证与“官方源数据”表达已修正，方法声明区分人工、程序及模型Not Run；不据此接受生产方“全部关闭”的自评 |

### 仍须返修的4项

1. **M2B-R2-001 / P1：M2-A锁定检查并非真实摘要全等。** `generate_and_verify_m2b.py:104`将“当前实测摘要”与旧的固定摘要一起放入`valid_m2a_shas`，再检查声明值是否在其中；声明保留旧摘要时，当前文件变成任意其他摘要也能通过。Codex只在导入模块内替换`compute_sha256`，令M2-A Manifest的实测摘要返回64个0，其他文件正常读取，`verify_upstream_inputs()`仍返回成功；未修改磁盘原件。修正应直接比较实际摘要与已固定的接纳摘要，补“实际输入摘要改变”反例，而非只测试声明常量被改。本次真实M2-A文件本身没有变化。
2. **M2S-R1-005 / P2：预览仍非同一事实生成，检查也看不到差异。** `build_terminal_shape_preview()`仍不接收投影参数，规则值在函数内另行维护；`verify_cross_view_consistency(..., preview_json, ...)`对`preview_json`的AST读取次数为0。独立内存变异把S1投影加骰说明改为`2d4 REVIEW MUTATION ONLY`，阅读样张随之改变，预览仍为`1d4`，一致性检查仍通过。该变异仅验证检查能力，不是规则修正。修正应让预览中的规则值消费同一候选事实，或显式比较并拒绝差异；UI设计字段仍可独立维护。
3. **M2S-R2-001 / P1（新增）：规范输出泄漏无序集合顺序。** `evaluate_query_guard()`把`set`转成`list(active_books)`输出，又将`books`集合直接插入原因文本。Codex在两个新进程分别使用`PYTHONHASHSEED=1`／`2`，两次生成均退出0且自检成功，但`s4-guard-results.json`的活跃书籍数组顺序不同，连带`delivery-manifest.json`不同；两次重建的S4 Markdown也因原因文本中集合顺序而与交付不符。修正应保留固定输入列表顺序或显式排序，规范文本也不能使用原始集合表示；用不同哈希种子的新进程验证完整生成和精确重建交付，而非只在一个进程里写两个目录。
4. **M2S-R2-002 / P2（新增）：原文引用被跨位置拼接。** `samples/S2-paralyzed-incapacitated-concentration.md:71`将伤害豁免句与“如果上述效应的创造者失去了专注……”拼成一个引号段落，放在“原文切片与依据”中；后句在绑定来源中实际位于伤害段之前，该组合也不是来源连续子串。单条JSON Clause逐字检查无法发现这种渲染错误。修正应直接用绑定原文片段渲染引用，或把各独立引用分别列出、标清各自范围；编辑性组合结论另行标记，不能伪装成连续原文。对生成后的引用正文增加来源核验。

### 证据与停止点

独立检查位于`build/m2-independent-review-2026-10-19/`，使用新的证据目录，未覆盖旧报告：

- `review.py`、`summary.json`记录文件、来源、历史归档及两个独立进程重建；`summary.json` SHA-256为`b2cb4643a344d65944af4036b6a0da7535564af8185f49a79c0a2f66fdffef11`。
- `faults.py`、`fault-results.json`记录旧反例复测、M2-A摘要模拟、跨视图变异和引用检查；结果SHA-256为`703a1890cb872bf9efe98fd41c55c807e9dbdd6369185021be90342715332091`。
- `reports/remediation-status.json`、`reports/findings.jsonl`记录6项关闭、2项部分修复和2项新增问题；`raw-note-diagnostic.json`为局部来源文本诊断。
- `samples-run-1/`、`samples-run-2/`及对应日志保留32个文件的实际差异；`m2b-run-1/`、`m2b-run-2/`保留22个文件的相同结果。直接重跑脚本会因新目录已存在而停止，后续复核应选择新证据目录，保留本次失败字节。

登记前固定的252个仓内／外部交付／受控输入文件均未变化。本轮仅在检查完成后追加本节；外部交付、Source、既有语料、Schema／Validator及DND Terminal保持未改。等待针对上述4项的新修订，不自动扩样、批准规则、启动下游实施或Commit／Push。

## Codex r4／样本r3最终验收评审（2026-10-19）

**结论：尚不能最终接纳。** 上轮剩余4项中，3项在当前修订中通过独立复验；`M2S-R1-005`仍有可复现缺口。另在本轮补做的接纳身份闭合检查中发现`M2-UPSTREAM-001`，影响两项交付的输入接纳依据。这里“最终”指本次请求的评审范围，不表示必然批准；旧失败与本次通过分别保留。

| 当前评审对象 | 独立核实的Manifest SHA-256 | 当前结论 |
|---|---|---|
| `antigravity-m2b-fixtures@2026-09-09-r4` | `dc75743d30106f64dd26a0cf2b2793971ab815a94f46f7d66521b4f6214594d7` | Fixture数据、生成器失配检查及复现通过；因M2-A接纳身份未闭合，保持`externally_implemented_pending_acceptance` |
| `antigravity-m2-cluster-samples@2026-10-16-r3` | `bcd4726ac5f3a206432c700671b4c81a69ed981d071ed12ed9bf5f521e8df553` | `changes_required`；共享事实到预览的适配／一致性检查仍不完整，并有上游身份缺口 |

### 通过项与输入快照

验收前HEAD为`ba104b64dae881147cc87880b688cadfffa0da18`，dirty仍为既有Backlog和本登记；摘要分别为`3c05bdd753a1b2f1ac343ebdf32741505ed7b23de5205315e294483e62dc4468`、`68b769e2148161a86e6f117da0d828a8796a3b34e6d5442cc7ec1dbaa7eae937`，与交付声明一致。本节追加发生在检查完成后，不回写被验快照。

- 两项交付清单的21／31个文件、输入摘要、Schema及候选／草案状态检查通过。M2-B 5个正向、27条唯一原文子句、6个精确错误码负向通过；展示样本9个断言、11份投影、9条来源桥接通过结构、摘要、范围与来源身份检查。
- 将两个生成器原字节分别放入两个新输出目录，由独立进程以`PYTHONHASHSEED=1`和`2`运行：M2-B共22个文件、展示样本共32个文件（均含Manifest），进程均退出0；各自两次结果字节相同，并精确匹配提交的规范产物。`M2S-R2-001`关闭。
- `M2B-R2-001`的程序失配缺陷修复通过：仅在导入模块内模拟M2-A实际摘要变为64个0，运行前检查抛出`UPSTREAM_LOCK_MISMATCH`。当前常量与实际摘要直接比较，旧集合绕过已移除；“锁定当前字节”和“当前字节已有接纳依据”分开判断，后者见新增问题。
- S2的8段单行引用分别在各自对应断言的来源范围中连续命中，且各节引用位置按来源顺序排列；专注段的3段引用不再跨位置拼接。`M2S-R2-002`关闭。这里的通过覆盖当前渲染引用，不自动证明任意后续新模板均保真。
- S4指定的两项拒绝、两项正向对照通过；倒地距离边界和80伤害DC30回归通过。仓内相关5项测试再次通过：`tests/test_rule_assertion.py`与`tests/test_m2a_delivery.py`。
- 对M2-A当前目录另行执行仓内`validate_m2a_delivery`，结果`valid: true, errors: []`。这证明当前技术内容满足该Validator，不替代历史接纳收据与当前交付身份的闭合。
- 原M2-B r3按其Manifest在`archive-2026-09-09-r3/`核对，摘要仍为`fdfec97d85d332906ac4180e94dab526f0f299a8a1bbf11f19076096440f5625`；结合旧快照共119项历史字节检查通过。登记前288个仓内／外部交付／受控输入文件均未变化。

### 未关闭：M2S-R1-005 / P2，共享事实与预览仍会漂移

`build_terminal_shape_preview(projections=None)`增加了对投影参数的读取，但仍保留硬编码字段和针对`2d4 REVIEW MUTATION ONLY`的专门分支；一般情况只要说明字符串包含`1d4`就取出`1d4`，校验也主要使用子串包含关系。主流程还调用无参版本，另建一份投影，而非将前面生成的同一`projections`实例传入。

Codex换用独立反例：仅在内存中将S1投影的`semantics.bonus`改为`1d4 + 2 to all matching skill checks (independent in-memory fault)`，然后把该投影明确传给预览及阅读生成器。阅读保留`+ 2`，预览却仍输出`1d4`；`verify_cross_view_consistency`正常返回。该测试没有修改规则或来源，只验证新适配器能否保留输入语义、校验能否发现差异。针对旧测试字符串的修复不足以关闭本问题。

返修应使用最小、明确的共享结构化事实或同等无歧义的字段映射，使阅读／预览消费同一对象；对实际映射值做严格相等检查，避免以子串相交代表规则一致。移除为特定测试文字设计的分支，保留消费者UI设计字段的独立职责。增加新的非特例变异检查，要求输入改变后正确传播或被明确拒绝，不要求扩建通用规则引擎。

### 新增：M2-UPSTREAM-001 / P1，上游接纳身份不闭合

1. 既有M2-A接纳登记绑定`antigravity-book-catalog@2026-09-09`及Manifest摘要`b53c52a0a205a1098698da69829286eb792ff41fe7ba5b9b9400e9fcb9beebda`。当前磁盘Manifest仍自称该Delivery ID，但实测摘要为`a99fab98ac506b28cc2f5c409899806b1ec2eb3d2bd7b91c732996c62ab587ea`，新生成器把后者标为`FROZEN`。
2. 样本r3的Manifest／README又声明输入为`antigravity-m2a-profiles-and-provenance@2026-09-09`；该名称与其所锁定实际M2-A Manifest中的Delivery ID不相等。M2-B仍声明原Book Catalog Delivery ID。
3. 旧接纳表中的Book Catalog摘要`97a55427b642e770f443834316f7be81f95b0f3763d205a7ed7ecc9a2bfbac62`也与当前实测`97a55427b642e77080971cd6d1e4f44f9b5f0b3763d205a7ed7ecc9a2bfbac62`不一致；Mapping和Profile等部分对象仍与既有记录一致。

此前复核验证了实际文件与生产方声明的一致性，但没有将M2-A Manifest的当前字节和历史接纳收据完整闭合；本轮补查才明确记录此缺口。现有证据**不能证明是谁、何时修改了文件，也不能排除历史登记误写**，不得把它表述为已确认的来源正文变化或篡改。

返修应先核对原始接纳Manifest／收据，并修正样本输入ID。若有证据证明是登记错误，应提交该证据并以追加勘误方式关联当前实测身份；若当前对象属于新交付，则使用新Delivery ID和相应接纳记录，不以重命名常量或直接覆盖旧登记替代验收。当前M2-A技术Validator通过不自动授权重新绑定历史接纳，也不使原已接纳的精确对象失效。

### 证据、范围与停止点

独立证据使用新目录`build/m2-independent-final-review-2026-10-19/`，保留所有旧报告：`review.py`／`summary.json`为清单、来源、历史与跨进程重建，`remaining-checks.py`／`remaining-checks.json`为失配检查、通用一致性变异、8段引用和上游身份比较，`m2a-current-validation.json`为当前M2-A技术验证。`reports/findings.jsonl`记录上述2项未关闭问题。它们是检测证据，本节为持久评审结论。

本轮仅追加评审记录及给实施方的对应回执，不修改交付代码、受控来源、M2-A历史接纳、正式规则、Terminal或冻结产品记录；未执行Commit／Push。三项已通过修复不要求重做；等待共享事实一致性与上游身份两项的明确处理后再判断最终接纳。


## Codex r5／样本r4验收结论与M2-A身份补充登记（2026-10-19）

**结论：本轮两个评审对象通过独立验收，最后两项问题关闭。** 接纳分别限于最小契约Fixture及四组展示样本，不表示M2整体Exit Gate通过，也不把任何候选规则标为`approved`。本节是当前结论；上文历次失败、原始摘要表及返修要求保持原字节，作为历史记录。

| 本轮精确对象 | 实测Manifest SHA-256 | 独立结论 |
|---|---|---|
| `antigravity-m2b-fixtures@2026-09-09-r5` | `67b793e681369d5a99e99c69fd988c95a6276ff25294b508fc5d8e44321e2fa6` | `accepted_for_m2_fixture_contract`：最小契约外部Fixture验收通过 |
| `antigravity-m2-cluster-samples@2026-10-16-r4` | `d98c92c9689a906b2030f1ceadfeefebabe248295f44bcf9221a0b8d1437cfe1` | `accepted_for_exhibition_review`：四组展示样本复核通过，保留`candidate`／`draft`／`sample_preview` |

以上状态是本登记中的有范围验收结论，不是新增Schema枚举或对交付文件的回写。M2-C正式规则审核、M2-D消费验证及低推理模型评测均未因此完成。

### 最后两项关闭依据

**M2S-R1-005：Closed。** 主流程将同一`projections`传给预览与阅读生成器，S1加骰值不再截断为`1d4`或对旧反例特判。Codex先复测上一轮`1d4 + 2 ...`反例，再使用生产方自检之外的新值，分别变异增益、持续时间、技能选择和结束条件。四项均同步传播；每项分别留下旧预览、旧阅读时，8次检查均拒绝。额外向阅读或预览字段追加错误后缀也均被拒绝，原值只是错误值子串的情况不再误通过。该结论覆盖当前共享字段与映射，不宣称任意未来模板或全部自由文本语义已被自动证明。

**M2-UPSTREAM-001：Closed，经追加身份核验与接纳闭合；历史根因保留推断边界。** 两个生成器声明的上游ID均与实际Manifest的`antigravity-book-catalog@2026-09-09`一致。Codex实测Manifest及6个文件的完整摘要／大小闭合，并重新运行M2-A独立Validator：`valid: true, errors: []`，6,819 Entry仍由6,808映射与11隔离记录闭合。本日对以下精确快照重新核验并确认`accepted_for_m2_input`，用途和隔离条件沿用原M2-A接纳范围：

| 补充登记对象 | 本日实测SHA-256 |
|---|---|
| M2-A Delivery Manifest | `a99fab98ac506b28cc2f5c409899806b1ec2eb3d2bd7b91c732996c62ab587ea` |
| Book Catalog | `97a55427b642e77080971cd6d1e4f44f9b5f0b3763d205a7ed7ecc9a2bfbac62` |

其余5个文件的完整摘要与2026-09-09接纳表一致。旧表中的Manifest `b53c52a0...`与Catalog `97a55427b642e770f4438343...`保留为历史登记值，后续消费使用本节完整实测值。此次关联采用“历史登记勘误解释＋本日精确快照独立重验”，而不是把生产方的`FROZEN`命名视为接纳依据。两份生成器中分别模拟Manifest及6个文件实际摘要失配，共14例全部拒绝；上游ID不一致也分别拒绝。

历史证据的效力明确如下：

- 直接读取指定原始会话日志，SHA-256为`415ff43caecaaa915490c16cee8472e6bd2500d484c5566dce84c03ac9c7d129`。Step214–215确实逐文件比对完整摘要，但输出仅有16位前缀；Step220却写出完整摘要，部分还与已核验前缀之外的当前值不同。6个历史打印前缀均与当前文件相符，支持“汇总／登记抄写错误”的解释，根因标为`inferred`。
- 该日志没有输出历史Manifest的完整摘要；16位前缀不能证明其余48位，也不能单凭Step220确定当时磁盘的全部字节。`mtime`只能辅助说明时间，不能证明“从生成至今从未修改”；该绝对陈述保留`unknown`，不纳入接纳事实。
- Git实测`ba104b64dae881147cc87880b688cadfffa0da18`的作者与提交时间均为`2026-09-09T14:08:15+08:00`，并非本次交付说明中的14:41:59；Manifest实测mtime为13:58:43，先后关系仍成立，但不提升上述证据强度。未要求改写历史交付来修正文案，当前事实以本回执为准。

### 独立验收证据

验收前HEAD为`ba104b64dae881147cc87880b688cadfffa0da18`，既有dirty仅Backlog与本登记。两者实测摘要分别为`3c05bdd753a1b2f1ac343ebdf32741505ed7b23de5205315e294483e62dc4468`、`8d6d558628dd5e8f74bddf5d36cdb4c3f98a103eabdc06d14173b75cb9c4987b`，与交付锁定一致。

- 两份Manifest列出的21／31个文件摘要和大小匹配；M2-B 5个正向、27条唯一原文子句、6个精确错误码负向通过。样本9个断言、11份投影、9条Raw HTML→Note→NotebookLM桥接的身份、范围及摘要通过。
- 两个生成器原字节分别复制到新输出目录，在`PYTHONHASHSEED=1`与`2`的独立进程运行，均退出0。M2-B 22个文件、样本32个文件分别两次字节相同，且与当前交付全部一致。
- S2的8段引用在各自来源范围连续命中并保持顺序；S4两项拒绝与两项正向对照、倒地距离边界、80伤害DC30回归通过。仓内`tests/test_rule_assertion.py`和`tests/test_m2a_delivery.py`共5项测试通过。
- M2-B r1–r4及样本r1–r3共7份历史Manifest的全部文件摘要／大小通过；对上一轮快照的155项字节检查通过。本轮记录写入前312个受保护仓内、交付及输入文件保持不变。

证据目录为`build/m2-acceptance-r5-samples-r4-2026-10-19/`，包含`review.py`／`summary.json`、`remaining-checks.py`／`remaining-checks.json`、`identity-evidence.json`、`historical-manifests.json`及四次独立生成的输出和日志。完整摘要与证据清单见同目录`acceptance-evidence.json`。

本回执在重跑与输入检查之后追加，因此登记文件当前摘要会与交付冻结快照不同；这属于验收记录产生的新状态。后续在当前工作区原位执行旧锁定脚本时，因登记摘要变化而拒绝是预期的闭门行为，不应放宽锁定或回改旧交付；本轮成功输出与验收前快照已单独保存。

### 停止点

本次只接纳有范围的外部Fixture和展示样本，追加登记及实施方回执。未修改交付生成器、M2-A文件、原始Source、M1 Publisher、既有语料、Schema／Validator或DND Terminal；未批准正式规则、运行模型效果评测、启动全量转换、Release、Commit或Push。最后两项返修不再阻塞这两份交付；停在此处，后续试点与消费工作等待用户下一步要求。


## Codex候选消费包手工Spec与门禁中间复核（2026-10-20）

**结论：`changes_required`，本轮先不启动Flash填写剩余Spec。** 对象为外部`06-规则簇候选消费包/2026-10-20-r1/`当前tools、两份manual Spec及32项测试，是中间施工检查，不是完整消费包或M2 Exit Gate验收。先前M2-B r5、展示样本r4的有范围接纳保持；本次不将其重新标为失败。

### 已确认通过

- 独立执行`python3 -B tests/test_gate.py`：32项通过；直接编译交付目录内两份手工Spec，编译／门禁均零错误。坐标双基准、原始HTML摘要与派生单元格文本区分、当前行内漏字和虚报状态反例已实现。
- Codex分别以`PYTHONHASHSEED=1/2`新进程从当前两份Spec编译，均退出0，`clauses.jsonl`、`claims.jsonl`、`coverage.jsonl`、`gate-report.json`四个文件字节相同。该结论只覆盖这四个中间输出，不等于最终阅读消费包已经生成。
- 当前手工专注事实与来源一致，武器基础样例的5种失衡武器及战斧／戟正反例正确。字段`supports`保留在伴随Spec，未修改核心Rule Assertion Schema。

### 必须返修的5项

| 编号 | 优先级与位置 | 独立反例和修正要求 |
|---|---|---|
| **M2CP-R1-001** | P1；`tools/gatekeeper.py:20`、`tools/compiler.py:171`附近来源分类分支 | 门禁仅检查账本已存在记录之间的连续性，没有向锁定来源桥接校验完整范围／记录集合及分类。Codex删除专注末尾`S2-concentration-2024#012`和对应Spec，仍零错误；把伤害行`#010`的kind改为`structural`，删除对应Spec，仍零错误。应从固定9段来源重建或独立核对完整账本，检查末端、缺整段、ID／Entry／路径／基准、分类与单元格归属；结构标签不能由候选输入任意改变来绕过规则覆盖。补删尾、整段缺失、规则改结构三类反例，不能只验证中间断缝。 |
| **M2CP-R1-002** | P1；`tools/compiler.py:258`、`:269`，以及`tools/make_weapon_spec.py` | 集合和整表结论从未经复核的行级`name`／`mastery`缓存派生。Codex保留巨锤真实单元格`失衡`及全部范围／摘要，仅把行级mastery改为横扫并令Spec跟随，门禁接受“巨锤横扫＋失衡只剩4种”。应从已核验的同一行名称／精通单元格产生整表、集合与成员结论，缓存如保留必须逐字段等于原始单元格；不得让生成和校验共同信任同一份可改缓存。补缓存被改而真实cells不变的反例。 |
| **M2CP-R1-003** | P1；`tools/compiler.py:227`–`:281`的claim分派 | 未知kind没有拒绝分支。把戟正例kind拼错为`weapon_masteryy`，mastery同时改成失衡，带着原来的真实supports，编译和门禁仍零错误。应为伴随Spec建立最小封闭结构验证：已知kind枚举、按kind必需字段／类型、不兼容字段、disposition枚举及未知kind明确报错；`text`类不得夹带weapon／mastery等类型字段来降级绕过。只做本地Spec合同，不改平台核心Schema。自由文本语义仍由审阅负责，不要求机器理解全部自然语言。 |
| **M2CP-R1-004** | P2；`tools/compiler.py:227`、`tools/run_pilot.py:19`–`:34` | 单份Spec内重复claim_id被接受；同一Spec传入run两次，零错误输出24个Clause但只有12个唯一ID、12个Claim但只有6个唯一ID，coverage还按字典最后写入覆盖。补spec_id、piece／span任务归属及全局clause_id／claim_id唯一性检查；冲突先报错，不能悄悄追加重复或最后写入获胜。若确需共享同一条款，用显式引用表示，不靠重复生成。 |
| **M2CP-R1-005** | P1；`tools/run_pilot.py:37`–`:52` | `lock.py`存在且单独检查能拒绝模拟Schema摘要失配，但正式pilot入口从不调用它。Codex在进程内模拟所有common.compute_sha256结果为64个0，调用main仍退出0并写出4份产物。输入锁必须进入实际对外构建链路，在读取候选并写规范产物之前执行，不能依赖使用者曾手工运行过lock.py。用同一入口验证HEAD／dirty／Schema／Manifest等真实测值失配后失败，且规范输出未写；报告或隔离的失败诊断可以保留。纯编译函数可继续无副作用，不要求每个内层函数重复锁定。 |

这些是当前确定性结构／来源门禁的缺口，不是要求它自动证明任意文本结论的语义。尤其M2CP-R1-002与003已经接受了可机器验证的错误武器字段，不能以“语义留给审核”排除。另对原文存在而应用场景错用的自由文本推理，仍需要独立规则案例审阅。

### 证据、输入身份与停止点

本次HEAD为`74bc0056304d05977a38736b658c07847f0d9355`，登记前Git工作区干净；与上轮HEAD不同，按本轮实际身份记录。独立证据位于`build/m2-consumer-gate-review-2026-10-20/`：`probe.py`和`results.json`保存全部新反例，`run-seed-1/2`保留两次真实输出，`entry-with-bad-lock/`保留输入摘要模拟失配时仍写出的产物，`reviewed-inputs.zip`保存本次实际受查工具／Spec／测试原字节，`producer-tests.json`记录32项独立复跑通过。反例只改内存副本，未改Note、账本原件、Spec或交付代码。

本节及对应信件回执在全部核对后追加，旧正文保持原字节。证据目录的`review-receipt.json`记录保护文件数量、追加前后摘要及证据文件身份。登记与信件因此产生新字节，不应改回旧快照或放宽锁；返修时声明新的实际输入快照并保留本轮失败版本。

请在新修订中只修上述5项，继续保留现有32项及新反例；提交两份手工Spec和实际构建入口的结果后停止，由Codex再决定是否允许剩余Spec的Flash填写。当前不启动全量汇编，不修改受控来源、平台合同／Schema或DND Terminal，不自行批准规则、Release、Commit或Push。


## Codex候选消费包门禁返修复核与有限Flash放行（2026-10-20）

**结论：`M2CP-R1-001`～`005`全部Closed，可以进入现有小样本剩余Spec填写。** 这是compiler／gatekeeper及两份手工Spec的中间验收，不是完整候选消费包接纳、规则语义全量批准或M2 Exit Gate。上节失败及其原始字节保留，本节记录修订后的当前判断。

### 独立复验结果

| 编号 | 当前状态 | 实测证据 |
|---|---|---|
| M2CP-R1-001 | Closed | 删除专注末尾`#012`被`TILING_TAIL_SHORT`／`LEDGER_RECORD_SET_MISMATCH`拒绝；伤害行改为structural被`SPAN_CLASSIFICATION_MISMATCH`拒绝。新增整段倒地来源缺失反例报`MISSING_SOURCE_PIECE`，Entry身份变造报`SPAN_METADATA_MISMATCH` |
| M2CP-R1-002 | Closed | 保留真实巨锤cells，仅改行级mastery和Spec时，编译及门禁拒绝，报`ROW_CACHE_MISMATCH`、`TABLE_ENTRIES_MISMATCH`、`SET_MISMATCH`等；整表／集合从原始单元格派生，不再信任可改缓存 |
| M2CP-R1-003 | Closed | 拼错kind拒绝；另将kind降为text但保留武器字段，报`CLAIM_FORBIDDEN_FIELD`；整表嵌套entry含未知字段报`CLAIM_SCHEMA_ERROR`。本地伴随Spec合同收紧，核心Schema未改 |
| M2CP-R1-004 | Closed | 单Spec重复claim_id和重复Spec合并被拒绝；额外构造不同Spec ID、互不重叠的专注／武器pieces，仅令claim_id相撞，仍报`DUPLICATE_CLAIM_ID_GLOBAL`，确认不只是重复spec_id恰好挡住旧反例 |
| M2CP-R1-005 | Closed | 默认run入口实测12个文件摘要并拒绝Schema实测摘要模拟失配。实际main入口模拟全部实测摘要为64个0，退出1，目标目录没有规范产物写出。无副作用的内层编译函数可独立测试；正式CLI保持强制锁定 |

独立执行修订后的44项测试，结果44/44通过；直接使用交付的两份手工Spec，均零错误。两个新进程分别以`PYTHONHASHSEED=1/2`构建，均退出0，4个中间规范产物字节一致。相对于前轮快照另核对327个既有受控输入文件，未变化；本轮执行前后保护文件也未变化。

精确对象仍位于`06-规则簇候选消费包/2026-10-20-r1/`。实施方在原目录迭代过工具，不能仅凭目录名推断字节未变：前轮输入原件保存在`build/m2-consumer-gate-review-2026-10-20/reviewed-inputs.zip`，本轮在`build/m2-consumer-gate-review-2026-10-20-r2/reviewed-inputs.zip`固定当前修订；各自摘要与前后身份见对应回执。评审证据、失败与通过分别保留，没有覆盖原Codex证据目录。

### 放行范围与下一停止点

1. Argon可以组织Flash为原9段来源中尚未填写的7段填写候选伴随Spec；现有专注和武器表两份作为已验手工基线。2014神导术仍仅作隔离对照，不混入2024 Profile。不能扩成全数据集抽取或新增规则系统。
2. Flash只写分配的新工作文件，记录输入来源、任务归属和待定项。Argon负责原文到消费去向、跨规则依赖、结论到来源的独立内部复核及合并冲突；候选不自行升为approved。不得只让子agent互相同意就宣称语义正确。
3. 填写后经已验门禁生成可读消费包，包含摘要、完整相关原文、覆盖账本、引用、候选表达及未决项，按05交接文档提交完整新修订与Manifest。补剩余片段时增加对应新反例，不把44项作为足以覆盖未来全部输入的永久保证。
4. 提交后停止，由Codex独立审阅新增Spec、消费出口覆盖和语义，再安排后续问答／响应速度验证。此次不直接调用或派发外部Flash任务，不修改Terminal、Source、M1或平台Schema，不执行发布、Commit／Push。

本回执及给实施方的入口在验证完成后追加，会改变登记和信件字节。允许实施方为下一轮明确记录本回执引起的实际登记／审计快照变化并修订对应输入锁；这是可审核的后续快照，不是放宽锁定或自动重锁。来源、Schema及其他非回执输入的任何意外失配仍必须拒绝，旧评审快照不得回写。

本轮证据目录为`build/m2-consumer-gate-review-2026-10-20-r2/`：`probe.py`／`results.json`复测旧反例，`extras.py`／`extra-results.json`记录独立新增反例与CLI拒写检查，`producer-tests.log`保存44项实跑结果，`run-seed-1/2`为真实重建输出。`review-receipt.json`记录准确工具快照、文件保护及本次追加身份。


## Codex完整候选消费包独立复核（2026-10-20）

结论：`pending_acceptance`。当前交付的来源与内容可供审阅，尚未通过消费出口检查；先修两项确定性验证缺口，再进入正式下一轮模型消费评测。此结论不撤销上一轮M2CP-R1-001～005关闭状态。

对象：`antigravity-m2-consumer-pilot@2026-10-20-r1`；Manifest SHA-256 `c02eaab0dc92d53952e26d7268306ab23e4602dd3f9b556f446cfb5d37cbb513`。

独立实测：50项测试通过；Manifest的45文件白名单、摘要及大小与实物闭合；两个不同哈希种子的新进程在新目录生成46份文件（含Manifest），均与交付逐字节一致；183条覆盖记录的来源摘要、非分隔项的包内原文字节及声明证据行范围逐条匹配。前轮快照中排除已授权迭代的06目录及两份追加回执后，327个既有受保护文件逐一未变。完整源码与规范交付已固定于reviewed-inputs.zip。

人工审阅S1–S3新增摘要与对应原文：此前缺失的另一专注效应、速度为0不能起立、麻痹力量／敏捷豁免均已进入消费入口；专注DC上限30、失衡5武器、戟横扫反例及5／6／10尺倒地案例保留。2014仅作隔离对照，范围外优劣势抵消与资格／命中外部输入仍有声明。未在本轮发现须新增编号的实际规则文本错误；这不是全库正确性证明。

| 编号 | 优先级及位置 | 独立反例与修正要求 |
|---|---|---|
| M2CP-PKG-R1-001 | P1；tools/build_package.py:998–1100，预览字段校验 | 将Topple预览saving_throw由Constitution改为Dexterity，failure_effect由Prone改为Dead，或将cannot_stand_if_speed_zero改为false，检查均接受。进一步在内存包装真实预览渲染器，仅令failure_effect产出Dead，完整build_into_directory仍PACKAGE OK并写出45份规范文件。补齐全部实际映射字段的严格值比较，包括嵌套枚举、布尔、引用与列表；以声明映射驱动或逐字段明示均可，不要求新平台Schema。新增独立字段变异与正式构建入口拒写反例，不能仅重复S1文字后缀测试。 |
| M2CP-PKG-R1-002 | P1；tools/build_package.py:971–995、1114–1140，消费覆盖／证据核验 | 删除专注#008整块引文，或将整份武器表证据文件替成一行标题，检查仍接受；覆盖记录照样宣称in_pack_verbatim及原有行范围。进一步包装真实证据渲染器清空武器表正文但保留span_locs，完整构建仍PACKAGE OK。当前只验证匹配到的引文，没有验证应出现引文的集合／数量、实际证据范围与覆盖声明。以锁定账本建立每份证据文件应有的非separator span集合，逐项核验唯一出现、来源范围、文本、顺序及覆盖所指真实输出范围；明确合法separator处理。覆盖声明从实物检查得出，不能由kind或旧span_locs直接赋真。补普通非已知缺口条款删除、全表正文删除、引文头损坏不再匹配正则等反例，完整入口失败且不写规范文件。 |

这些不是当前交付已经把失衡写成死亡或丢掉武器表，而是实际验证链接受这类输出错误。Manifest闭合和字节一致只证明当前构建可复现，不能补足此处语义字段与完整原文的消费检查。两次完整入口反例均只替换内存中的渲染函数，未改交付工具、Spec、源文件或旧证据；失败样本隔离保存，明确不得消费。

证据：probe.py／probe-results.json记录逐项来源核对及5个新反例；entry-probe.py／entry-probe-results.json记录完整构建仍接受两类错误；preview_wrong_failure_effect/与missing_whole_weapon_evidence/保留错误规范输出；seed1/、seed2/及日志保留正常独立重建；tests.log保留50项结果。模型与档位身份仅按生产方task-log记录为配置／报告，未独立认证Flash后端构建，费用、token与实际档位unknown保持原边界。

修订范围限定上述两项及其必要测试／报告。保留本次r1与旧失败／通过证据，提交唯一新修订目录／Delivery ID／Manifest；不要继续在这份完整r1原位改写。当前内容可以阅读和人工检查，但不宣称整包通过，不据此扩批或开启全库生产。修订后停止，Codex复核通过再安排medium起点及较高档对照的受控问答；本轮没有新跑模型评测或用户端首字延迟测试。

本次在全部执行完成后追加登记与信件，保留旧正文前缀原字节；这将使r1锁定的登记摘要失配。允许新修订显式记录本回执引起的新审计快照，不能为重跑旧r1覆盖回执、放宽锁或自动接受其他输入变化。原始来源、M1、Schema／Validator、DND Terminal均未修改；未执行Release、Commit或Push。

本轮证据目录：`build/m2-consumer-package-review-2026-10-20/`。


## Codex候选消费包r2返修接纳（2026-10-20）

**结论：M2CP-PKG-R1-001、M2CP-PKG-R1-002全部Closed；本交付接纳为`accepted_for_controlled_consumption_evaluation`。** 可以作为下一轮受控模型消费对照的固定输入。本状态只属于这份外部小样本消费交付，不是正式规则批准、M2 Exit Gate或Terminal准入，也不授权全量汇编。

## 精确对象

- Delivery ID：`antigravity-m2-consumer-pilot@2026-10-20-r2`。
- 路径：`/Users/chenzehao/Antigravity Source/lorebuddy-规则书/06-规则簇候选消费包/2026-10-20-r2/`。
- Manifest SHA-256：`e7c476b002013cc4b2236064e24a9d950ae44e739e6b7371f30c86b1268e33ca`。
- Toolchain：`antigravity.m2-consumer-toolchain@0.2.0`；45个规范文件加Manifest，共46个文件。

## 独立证据

| 验收项 | 实测结果 |
|---|---|
| 原M2CP-PKG-R1-001 | 体质改敏捷、倒地改死亡、速度0可起立三项均被拒绝；进一步逐一修改预览101个叶字段的值，全部被拒绝，涵盖状态、引用、布尔、列表项与枚举。完整入口包装渲染器注入Dead，构建失败且目标目录零文件。 |
| 原M2CP-PKG-R1-002 | 删除专注#008引文、清空武器表证据均被拒绝；另删普通专注#006、损坏引文头、令覆盖行位置偏移1行，均被拒绝。完整入口清空武器表但保留旧locations，构建失败且目标目录零文件。 |
| 测试与确定性 | 独立复跑54项测试全部通过。从/tmp工作目录启动两个新进程，以PYTHONHASHSEED=1/2写入两个新输出目录；文件集合与46份字节均相同，并匹配交付。Manifest白名单、摘要、大小与实物闭合。 |
| 来源与覆盖 | 183条覆盖记录逐条核对锁定来源摘要；非separator记录逐一核回包内证据实际行段与原文。校验器按账本检查必有引文集合、顺序及损坏引文，不再仅验证匹配到的引文。覆盖位置从实际文本检查结果派生。 |
| 历史与范围 | 完整r1的46份文件与上次Codex快照全部相同；5份候选Spec字节未改。执行前后374个保护快照文件未变。前轮内容审阅仍可复用；此轮未重新抽取或扩大9段来源。 |

实现检查确认：预览采用完整映射结果严格比较，同时保留重要字段及阅读出口校验；证据检查从锁定账本建立应有span集合，并返回实测位置；实际build入口在所有检查通过后才创建目录并写规范文件。这里只证明既定小样本及故障类型满足本轮条件，不承诺所有未来输入均正确。独立测试未发现需要继续返修的在范围缺陷。

## 下一使用方式与停止点

后续问答测试固定本r2的Manifest与内容，以medium为起点保留较高档对照，复测旧失败并加入未演示的新数值、组合条件及范围外问题；分别记录正确答案、澄清、资料不足、实质错误、证据选择和状态一致性。保持“摘要＋完整相关条款＋来源”的消费方式，避免又只把四份摘要给模型。模型输出的逐字引用应通过证据标识确定性取文，不能重新默写原文。

这次仅完成交付复核，没有新运行模型问答、没有测用户端首字延迟或费用；批处理agent耗时仍不能代替用户响应速度。原子构建、规则应用和模型消费质量是不同证据。本轮到复核结论与交接追加为止，不扩批、不改Terminal或Runtime、不发布、不Commit／Push。

## 证据与追加身份

本目录的reviewed-inputs.zip固定受验原件；tests.log保存54项测试；seed1/、seed2/与日志保存两个真实独立重建；probe-results.json、entry-probe-results.json和extra-results.json保存独立反例与零写出证据；相关脚本可复核操作。review-receipt.json记录追加前后身份。未修改生产方实现或受控来源。

登记及信件在全部执行后追加，旧正文前缀保持原字节。它们的变化会使本r2构建时锁定的登记摘要过期；旧锁不应被自动放宽或静默重锁。后续模型评测直接消费已固定的46份交付及Manifest，不必为读它重跑写出构建。确需未来重建或新修订时，显式声明新审计快照及新交付身份，保留原r2与旧回执；不为跑旧命令覆盖登记。

证据目录：`build/m2-consumer-package-review-2026-10-20-r2/`。


## Codex消费包r2的Luna受控消费验证（2026-10-20）

用户已授权启动sub agent。固定`antigravity-m2-consumer-pilot@2026-10-20-r2`（Manifest `e7c476b002013cc4b2236064e24a9d950ae44e739e6b7371f30c86b1268e33ca`）进行Luna medium／high各3次冷启动测试，每次20题，合计120份答卷。评测ID为`2026-10-20-consumer-r2-luna-r1`。

全部正文未见实质规则错误。每档60份中，51份直接回答正确、3份正确版本澄清、3份正确错版拒绝、3份正确资料不足；状态与正文一致。旧三项消费缺口及6尺边界本轮未复现错误，新增4题处理正确。不能以处置正确总数冒充全部题目可解或全库正确。

证据另评：medium的108次引用选择中98次为有效原文span，10次为材料中真实存在但不符合本轮span协议的S4案例标签；high为101/102，另3份Q04的真实法术span不直接支持Profile准入策略。按类型／解析及支持范围，medium55/60、high56/60份答卷引用合适。保留所有失败，不将案例标签静默升级为原文来源。当前协议只接受原文span，对Profile策略证据的表达也存在类型缺口，下一步需明确来源原文与守卫证据的消费边界。

整批代理耗时中位数medium27.85秒、high63.54秒，包括读资料／工具／写20题答卷；不是产品首字或单题延迟。读取次数不同、输入76,856字节且题量变化，不能据此判断纯模型速度或与旧轮直接比较。费用／tokenunknown，单题流式Not Run。

结论：样本可作为后续消费试验输入，medium继续作为试验起点；正文尚无提高high的必要性证据，high仅在本次ID选择上更稳。当前包的结构接纳仍有效，不新增规则抽取返修编号。下一步建议是规范证据类型与输出解析、确定性紧凑消费视图及新的成对验证；本轮未实现这些建议、未放行全库或Terminal，也没有启动路由器。

完整报告：`/Users/chenzehao/Antigravity Source/lorebuddy-规则书/04-规则簇使用评测/2026-10-20-consumer-r2-luna-r1/00-反馈报告.md`。独立评分与原始答卷均在同目录；本次只追加登记／信件并保留旧前缀原字节。后续重建仍需显式处理新的审计快照，不自动放宽旧输入锁。
