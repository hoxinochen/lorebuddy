# 架构决策与风险

状态：Draft / 待确认

## 1. 需要修正的核心表述

原原则“官方规则永远是唯一真相”方向正确，但若直接实现为一个全局 `official: true` 或“只保留最新版”，会丢失必要语义。

推荐表述：

> 每个来源版本都是不可篡改的证据。官方正文不得被 LoreBuddy 改写；规范视图由明确的系统、规则版本、语言、日期、可选模块和 Campaign Overlay 决定，不覆盖历史来源。

理由：

- 2014 与 2024 可以是两个合法规则上下文；
- Errata 会修正旧文本，但旧文本仍需追溯；
- 官方 Playtest 是官方发布，却不一定是最终规范规则；
- 官方原文、官方译本和社区译本不是同一权威表达；
- House Rule 对出版商不是官方规则，但在特定 Campaign 内可以具有规范性。

当前 CHM 本身是社区聚合资料，且说明会调整错字和译法。它可以证明“这段文本存在于该 CHM”，不能独立证明“这段中文是官方原文”。

## 2. 架构决策记录

### D-001：Package 是发布与权限边界

**推荐决策**  
使用 `packages/<namespace>/<package-slug>/`。规则系统和版本写入 Manifest。

**为什么**  
Package 需要独立版本、授权、依赖和访问控制。当前 CHM 已证明一个系统目录会混入多版本、多来源和不同权利内容。

**替代方案**  
`packages/dnd5e/` 作为整个系统的唯一 Package。

**未采用原因**  
系统生命周期远长于单个发布包，无法安全容纳私有 Campaign、第三方内容和不同授权。

**未来影响**  
Package 数量增加，但组合、发布、缓存和权限都更清晰。

---

### D-002：保留 Artifact 与全部原始 Entry

**推荐决策**  
同时保存原始 CHM 和解包后每个 Entry 的原始字节、摘要与路径映射。

**为什么**  
CHM 保留容器级证据，Entry 让十年后的工具无需 CHM Decoder 即可读取来源。

**替代方案**

1. 只保存 CHM；
2. 只保存 Markdown；
3. 只保存解包 HTML。

**未采用原因**

- 只保存 CHM 会继续依赖旧容器工具；
- 只保存 Markdown 丢失字节证据；
- 只保存 HTML 丢失容器、导航和提取可验证性。

**未来影响**  
存储量增加，但可以独立验证和重新派生。

---

### D-003：来源使用 Work / Edition / Artifact / Entry / Fragment 分层

**推荐决策**  
出版来源声明和实际摄取证据分别建模，并用有稳定 ID 的 Source Mapping Record 连接 Entry / Fragment 与 Work / Edition。

**为什么**  
一个社区 CHM 可以聚合许多书。路径只能证明文件位置，不能证明出版身份、语言、印次和授权。

**替代方案**  
Node 只记录 `source: 玩家手册/某页.htm`。

**未采用原因**  
无法回答来自哪一版、是否官方翻译、实际处理了哪个文件、源文件后来是否变化。

**未来影响**  
Provenance 较详细，但支持 PDF、网页快照、数据库导出和多载体交叉验证。

---

### D-004：Node ID 与内容和路径解耦

**推荐决策**  
使用 UUIDv7 的 `urn:uuid:`；slug 只用于文件可读性。

**为什么**  
标题、翻译、路径和正文都会变化，ID 必须稳定。

**替代方案**

- 标题或 slug；
- `system:type:title`；
- 正文 SHA-256。

**未采用原因**

- 标题会冲突和改名；
- 系统与类型可能在 Schema 迁移后变化；
- 正文摘要会因勘误和转换修复变化。

**未来影响**  
路径不再是引用协议；需要 Index 为人提供可读查找。

---

### D-005：一个 Node 一个表达版本

**推荐决策**  
正文表达、主要语言、Ruleset、勘误状态、适用范围、权威或规范上下文不同的内容拆为不同 Node。Edition 只是来源维度：若不同 Edition 经审核确认承载完全相同的表达与上下文，可以作为同一 Node 的多条 Provenance，不因 Edition ID 不同机械拆分。

**为什么**  
这样才能独立维护、精确引用和明确追溯。

**替代方案**  
在一个 `Concentration.md` 中放入 2014、2024、中英文和 House Rule 多个 Section。

**未采用原因**  
任何更新都会修改一个共享大文件；引用者无法仅凭 Node ID 确定所指表达。

**未来影响**  
Node 数量更多，但 Relationship 可以明确连接 translation、variant、corrects 和 supersedes；相同表达的重印或聚合重复不会制造无意义 Node。

---

### D-006：Core Envelope + 命名空间 Profile

**推荐决策**  
平台只定义稳定 Core；Spell、Monster、Class 等进入系统 Package Schema。

**为什么**  
这些术语跨系统只有表面相似，字段与规则语义不同。

**替代方案**  
建立一个跨所有 TRPG 的万能实体 Schema。

**未采用原因**  
会产生大量无意义可选字段，并把 D&D 假设固化为平台事实。

**未来影响**  
跨系统统一查询需要能力映射层，但新系统不需要修改 Core。

---

### D-007：权威身份、规范性和覆盖范围分离

**推荐决策**  
分别表达来源身份、翻译身份、normativity、applicability、override 关系和访问权利。

**为什么**  
这些维度互不等价，单一权威等级无法表达 Playtest、官方译本和 Campaign House Rule。

**替代方案**  
`authority: official | third_party | homebrew` 并按枚举排序。

**未采用原因**  
排序会错误暗示所有上下文都有同一优先级，也无法表达“官方但非最终规则”。

**未来影响**  
未来 Runtime Resolver 更复杂，但所有决策可解释、可重放。

---

### D-008：Boundary Ledger 是节点边界权威

**推荐决策**  
机器只提出候选，人工批准后分配稳定 Node ID，决策写入声明式 Ledger。

**为什么**  
当前输入有 3,610 页没有任何 Heading、2,250 页含表格、8,187 个导航对象指向 6,813 个不同目标，单一规则无法可靠切分。

**替代方案**

- 一页一个 Node；
- 每个 Heading 一个 Node；
- LLM 自动决定边界。

**未采用原因**  
前两者混淆格式和语义；后者不确定、难复现，且容易改写原文。

**未来影响**  
首次导入需要人审成本，但重跑、迁移和新增版本可以复用已确认决策。

---

### D-009：只维护正向关系

**推荐决策**  
Node 或 Relationship Record 只保存作者断言的方向；每条断言分配稳定 Assertion ID，反向边由 Index 生成并保留该 ID、范围、生命周期和证据。

**为什么**  
一条边若在两端手工维护，会让一次修改影响两个节点并容易漂移。

**替代方案**  
源和目标都保存关系。

**未采用原因**  
违反节点独立维护原则，并需要双文件事务。

**未来影响**  
读取反向关系需要 Index，但事实源更简单可靠。

---

### D-010：Index 完全派生且确定性构建

**推荐决策**  
JSON/JSONL 分片索引可删除重建；规范输出不写当前时间。Content Manifest、Output Manifest 和 Release Manifest 分别固定事实源、派生输出与最终发布组合。Release Archive 只能按白名单从空目录构建，额外文件直接失败。人工 Issue、Exception 和 Review 留在其 Access Domain 的 `metadata/`，运行检测留在不发布的 `reports/`。

**为什么**  
索引技术会变化，事实源必须长期可读。确定性输出使审计和迁移 Diff 可控。

**替代方案**

- 手工维护 Index；
- SQLite 或图数据库作为唯一主存储；
- 每次构建写 `generated_at: now`。

**未采用原因**  
会产生双重事实源、不可读二进制和无意义 Diff。

**未来影响**  
需要单独 Run Report 保存时间和性能信息，但 Package 内容摘要稳定。消费者可分别验证不可重建事实与可重建索引；人工裁决不会因删除报告而丢失。

---

### D-011：私有 Campaign 使用独立 Package

**推荐决策**  
私有内容独立 Package。内容依赖必须通过 Access Domain / Principal 授权，不能仅比较 `public | restricted | private`；两个私有 Campaign 默认互不可见。

**为什么**  
仅给混合 Node 增加 `private: true` 不能阻止 Alias、反向关系、日志和缓存泄漏。

**替代方案**  
公开和私有节点混装在一个 Package。

**未采用原因**  
构建、发布和索引非常容易泄漏私有实体名称与关系。

**未来影响**  
需要按可读 Access Domain 构建索引和实施实际存储权限，但安全边界明确。公开投影只携带批准的 Receipt / Attestation，完整 Lock、Review 和 Locator 保留在受限 Audit Package。

---

### D-012：当前 CHM 先进入受限摄取 Package

**推荐决策**  
整个 Artifact 先进入 `community/dnd5e-cn-compendium-20260630`，采用最严格的未决 Rights 与 Visibility。

**为什么**  
它混合多种来源和版本，且权利与出版映射未审核。Artifact 物理上又是一个整体。

**替代方案**  
按顶层目录立即拆成数十个公开 Package。

**未采用原因**  
目录粒度不一致，过早拆分会把猜测固化，并可能造成授权错误。

**未来影响**  
审核后可以建立更细的派生 Package。跨 Package 引用必须区分 Content Dependency、Build Dependency 和 Provenance Reference；公开 Package 不能把受限 Source 作为内容依赖。完整追溯留在授权 Audit Package，公开侧只能携带批准的 Attested Receipt；若 Rights 或 Disclosure 不允许，派生 Package 必须保持同等或更严格的访问级别。

---

### D-013：公开声明与受限审计证据分离

**推荐决策**  
公开 Package 只保存随机 ID、逐字段批准并绑定当前 Node / Library Root / Release Root 的 Public Receipt / Attestation；私有 Fragment、Decision、Reviewer、Build Lock 与二者的 Audit Binding 保存在独立受限 Audit / Build Package。

**为什么**  
路径和内容摘要本身也可能泄漏私有资料。只删除正文、不删除稳定 ID、版本或 Digest，仍会暴露项目存在性与演进。

**替代方案**  
把完整 Provenance、Rights Decision 和 Build Lock 放进公开 Package，再依赖 UI 隐藏字段。

**未采用原因**  
文件、Index、Log 和第三方工具都可以绕过 UI；同时会让公开 Release 的 Content Root 与私有证据形成不必要的摘要循环。

**未来影响**  
公开消费者能验证 Attestation 属于当前 Release，但不能声称独立复查私有 Source。授权审计方仍可沿 Audit Binding 重放完整链。

---

### D-014：保真由版本化事件协议与稳定映射证明

**推荐决策**  
可见文本、结构比较与 Source Fragment Evidence 使用三个独立事件协议；Raw Source Reference 与 Semantic Address 分层，普通 Link 与 Footnote 对同一 Reference 互斥消费；Source Reference / Semantic Address Occurrence、Asset Usage、Visibility Decision 和允许差异都有稳定 Record ID。正文范围通过 Fidelity Coverage Map 的 Provenance Binding 与 Correspondence Unit 显式连接 Source Event Range；Package 只从逐 Unit 结果生成聚合结论。

**为什么**  
相同文字可能具有不同 List、Table、Link 或 Footnote 结构；原始 URL 与最终 Node URI 又天然不相等。单个“正文摘要”无法证明无损转换。

**替代方案**  
比较渲染文本，或让转换器把 HTML 与 Markdown 直接字符串 Diff。

**未采用原因**  
前者丢失结构和引用，后者把合法格式变化当错误，也无法跨实现重放。

**未来影响**  
协议字段变化必须升版本并增加 Fixture；初期实现成本较高，但十年后仍能解释每个 Pass / Fail，而不是信任某个旧转换器。

---

### D-015：Rights Decision 与最终 Release Binding 分离

**推荐决策**  
Rights Decision 只保存 Claim Universe、语义 Subject Coverage 与权限结论；Release 动作的 Decision 与最终 `core.release-rights-binding@0.1.0` 共同位于目标 Release 之外的授权 Audit Package，Binding 再固定最终 Manifest、Root 和 Payload 字节摘要。目标 Manifest 只携带 Rights Authority Domain 与预分配 Binding ID，不携带 Binding Digest。

**为什么**  
若 Release Decision 或 Binding 属于目标 Content，又引用包含自身的 Content / Payload 摘要，就形成无法求值的摘要递归。把两者共同放入目标外的授权 Audit Package 可以固定同一审核上下文。Claim 选择若由作者列表控制，还可能通过漏掉 `denied` Claim 绕过默认拒绝。

**替代方案**  
让 Decision 或 Release Manifest 同时保存对方摘要；或者让 `rights_claim_ids[]` 直接决定参与合并的 Claim。

**未采用原因**  
前者没有合法计算顺序，后者把安全闭包退化为可漏项白名单。

**未来影响**  
发布流程增加一个受限 Audit Package 和两阶段 Candidate 审核，但 Direct / Public 两种模式共享同一无环模型；Claim Universe、Selected Set 与最终字节分别可以独立复核。

---

### D-016：Rights Authority Domain 与 Access Domain 分离

**推荐决策**  
使用权利治理域（Rights Authority Domain）确定谁可以签发 Claim、Decision 与 Binding；继续用访问域（Access Domain）决定谁可以读取 Package。目标 Release 与受限 Audit Package 通过 Authority Delegation 和锁定 Audit Context 连接，不要求共享 Access Domain。

**为什么**  
Public Package 必须允许匿名读取，包含合同、Reviewer 和 Claim 的 Audit Package 必须受限。若把“同域”解释为同一 Access Domain，两者无法同时成立；若完全依赖外部约定，又无法唯一判断哪个 Binding 有权审核当前 Release。

**替代方案**  
要求 Public Package 与 Audit Package 共用 Access Domain，或把某个 Audit Package 设为全局隐式权威。

**未采用原因**  
前者会公开审计证据或使 Public Package 不再公开；后者没有可锁定的授权范围、动作和失效条件，也不适合多维护者与私有 Campaign。

**未来影响**  
Package Manifest 与 Release Manifest 增加 `rights.authority_domain_id`；受限 Audit Package 增加 Authority Delegation 和 Audit Context Lock。发布验证成本提高，但授权责任、可读范围和 Binding 唯一解析不再互相混淆。

## 3. 风险登记

| ID | 风险 | 等级 | 影响 | 缓解策略 |
|---|---|---:|---|---|
| R-001 | CHM 无法证明官方出版来源 | Critical | 社区文本被误标为官方 | 分离实际 Artifact 与 Edition Claim；逐区域来源审核 |
| R-002 | 版权与再分发范围未知 | Critical | 无法合法发布 Package | 默认 restricted；逐 Work / Edition 记录 Rights；发布前法律/授权确认 |
| R-003 | 2014/2024/2025 与 Legacy 混合 | High | 规则冲突、错误覆盖 | Ruleset 显式化；独立 Node；使用版本关系 |
| R-004 | HTML 声明 GB2312 但实际超集 | High | 解码损坏且难察觉 | Entry 级严格检测；保留字节；禁止 replacement character |
| R-005 | Markdown 无法表达复杂表格和 Office 结构 | High | 正文或结构丢失 | 受限 HTML 回退；语义文本事件流；复杂样本人审 |
| R-006 | Script 或隐藏 DOM 中存在正文 | High | 静态转换遗漏内容 | 禁止执行；分类 Script；动态内容问题门禁；必要时隔离分析 |
| R-007 | 远程图片与 `file:///` 临时路径 | High | Package 非自包含、内容随时间消失 | 保留原 URL；独立 Acquire；缺失资产报告；不静默下载 |
| R-008 | 坏链接与缺失 Anchor | Medium | 导航和关系错误 | Source Reference Graph；原始 URL 与解析结果并存；不猜测修复 |
| R-009 | 标题、basename 与正文重复 | High | ID 冲突、错误去重 | UUID ID；重复只生成候选；人工确认语义身份 |
| R-010 | 自动切分算法变化导致 ID 漂移 | High | 关系和历史引用失效 | Boundary Ledger；稳定 ID；Redirect / Tombstone |
| R-011 | 100,000 文件影响 Git 与工具 | Medium | 操作缓慢、索引内存压力 | 稳定分片；JSONL 流式构建；未来可选只读发布归档 |
| R-012 | 平台 Core 被 D&D 字段污染 | High | 新系统难接入 | Core + Profile；跨多个系统验证后才提升字段 |
| R-013 | YAML Parser 差异 | Medium | 不同工具理解不一致 | YAML 1.2 子集；禁止 Tag/Anchor/重复键；JSON Schema 验证 |
| R-014 | Index 成为第二事实源 | High | 数据漂移、无法审计 | 禁止手改；删除重建测试；规范输入摘要 |
| R-015 | 私有 Campaign 信息通过索引泄漏 | Critical | 未授权信息暴露 | 独立 Package；Access Domain / Principal 判定；公开索引隔离测试 |
| R-016 | Schema 迁移静默改正文 | Critical | 官方原文失真 | 显式迁移；正文摘要门禁；格式迁移与内容修订分离 |
| R-017 | 单一 CHM Decoder 静默解包错误 | Medium | 长期 Source 证据损坏 | 锁定工具；独立实现交叉验证；长度与摘要对比 |
| R-018 | 外部依赖“最新版”导致不可重现 | High | 同输入产生不同输出 | Package Lock；构建禁网；依赖精确摘要 |
| R-019 | 分析只有人读报告、没有机器回执 | High | 十年后无法复算统计或解释差异 | Analysis Receipt 锁定工具、脚本、配置、输入与明细摘要 |
| R-020 | 人工裁决只保存在生成报告 | High | 重建或清理报告后丢失治理事实 | Issue / Exception / Review 进入 Metadata 与 Content Manifest |
| R-021 | Index 生成后缺少完整输出封条 | High | 单个索引被篡改而 Release 身份不变 | Output Manifest + Release Manifest；Content 与 Index 分根摘要 |
| R-022 | 相同 Asset 的不同语境被内容去重合并 | Medium | `alt`、图注或引用位置丢失 | Asset Record 与 Asset Usage / Occurrence 分离 |
| R-023 | 公开 Provenance 复制受限 Locator 或摘要 | Critical | Source 路径、文本和内容指纹泄漏 | `embedded-fragment` / `external-public-receipt` 联合类型；Disclosure Profile 默认拒绝 |
| R-024 | 直接归档 Working Tree 把 Report 或私有 Lock 带入发布 | Critical | 日志、人员、路径、依赖身份泄漏 | 从空目录按 Release Payload 白名单生成；额外文件即失败 |
| R-025 | Rights `unknown` 被 Visibility `public` 掩盖 | Critical | 未授权再分发 | 权限分项、默认拒绝合并、`Release Ready(public)` 布尔门禁 |
| R-026 | Public Lock 暴露受限 Package ID / Version / Digest | Critical | 私有项目存在性与演进指纹泄漏 | 完整 Lock 放受限 Audit Package；公开侧仅随机 Attestation 与逐字段 Approval |
| R-027 | Receipt 被误当成可独立复查的 Source | High | 夸大 Traceability | 明确 `full | attested`；公开 Receipt 声明审计结论而非 Source 替代品 |
| R-028 | Disclosure Approval 只批准字段名、未固定值 | Critical | 批准后可替换成敏感内容 | Subject Digest + `approved_projection_digest`；任一值或 Revision 变化重新审批 |
| R-029 | Rights / Access 判断依赖可变外部状态 | Critical | 同一 Release 在不同时间得到不同授权结论 | 显式 `evaluation_as_of`；Policy / Claim Digest；Access Decision Receipt 与 Audit Binding |
| R-030 | Archive Header 或特殊文件泄漏宿主信息 | Critical | UID、用户名、路径、时间或越界 Link 进入发布 | 只允许规范目录/普通文件；Header 默认拒绝并清零宿主元数据 |
| R-031 | 不同 Parser 产生不同事件或 Front Matter 值 | High | 摘要与 Schema 结论跨实现漂移 | YAML JSON 子集；版本化事件协议；JCS；跨实现 Fixture |
| R-032 | Rights Decision 引用包含自身的 Release / Payload 摘要 | Critical | 摘要递归，Direct Release 永远无法构造 | Decision 只绑定语义 Coverage；最终字节由外部 Release Rights Binding 固定 |
| R-033 | Claim 输入列表漏掉适用 `denied` | Critical | 未授权发布通过门禁 | 扫描 Claim Universe；Selected Set 集合全等；反向 ID 仅做一致性检查 |
| R-034 | 多 Provenance 与多正文 Range 仅用平行数组 | High | 无法证明哪段来源对应哪段正文 | Coverage Map + 稳定 Unit + Source Event Record Range；逐 Unit 比较 |
| R-035 | 公开投影复用私有 Party / Evidence ID | Critical | 即使删字段仍泄漏受限身份与跨版本关联 | 公开 Record 使用随机新 ID；由受限 Audit Binding 连接私有 Record |
| R-036 | 仅按 Attribute 名派发引用 | High | Image / Resource / Link 被错误分类，摘要与映射失真 | Element Context Dispatcher；未知组合阻塞；协议版本与 Fixture 固定 |
| R-037 | Footnote 与普通 Link / Anchor 重复消费同一 Reference | High | 比较事件重复、链接图失真或脚注配对绕过 | Raw Reference 与 Semantic Address 分层；消费集合全等；零消费或双重消费阻塞 |
| R-038 | Rights Subject Closure 漏掉容器中的非 Active Entry、Edition / Work 或 Asset | Critical | 对遗漏 Subject 的 `denied` Claim 不进入 Selected Set | 对物理 Inventory Entry 做不依赖 Lifecycle 的传递闭包；未决边阻塞 |
| R-039 | Binding 字段存在但未与 Decision、Manifest 和实际 Archive 强制相等 | Critical | 合法 Decision 可被拼接到另一 Payload | `core.release-rights-binding-validation@0.1.0` 逐字段重算并验证全部等式 |
| R-040 | 把 Rights Authority Domain 当成 Access Domain | Critical | Public Release 无法安全连接受限审核，或错误接受未授权 Binding | 独立 Authority Domain、Delegation 与锁定 Audit Context；Binding 唯一解析 |
| R-041 | Receipt / Attestation 被派发为普通 Metadata | High | 绕过 `publish_receipt` 权限 | 封闭 Schema Class 成员表；Source Receipt 路径优先；Registry 版本化 |
| R-042 | Source Fragment Event Stream 被当成普通 Metadata | Critical | 精确来源原文绕过 `redistribute_source` | 专用 `source-fragment-evidence` 角色；Fragment → Entry → Work 传递闭包 |
| R-043 | 内联 Public Rights Attestation 没有独立文件角色 | High | `publish_receipt: denied` 未参与 Release Manifest 权限 | Public 模式为 `release-manifest` 条件性增加 `publish_receipt` 与 Attestation Subject |
| R-044 | Pending 或未授权 Claim 直接提供 `allowed` | Critical | 目标 Package 可自行抬高再分发权限 | Claim Authority / Delegation / Issuer / Approved Review；失败按 `unknown` 阻塞 |
| R-045 | 新 Claim Source 版本静默删除旧 `denied` | Critical | 当前 Universe 无法发现历史权利约束 | 追加式 Claim Lineage；锁定前驱 Root；撤回只能追加授权 Tombstone |
| R-046 | Direct Audit Lock 引用最终 Release Manifest | Critical | `Manifest → Decision → Lock → Manifest` 摘要环 | 专用 `rights-target` Candidate Lock 明确排除最终 Root / Manifest / Payload 摘要 |

## 4. 当前最重要的非技术阻塞

### 4.1 来源审核

需要确定每个顶层区域和 HHC 分支实际对应的 Work / Edition、语言和翻译身份。当前目录只能作为候选证据。

### 4.2 权利策略

“必须保留官方全文”是数据完整性要求，不代表拥有再分发权。必须明确：

- 原始 CHM 是否能进入 Git；
- 解包 HTML 是否能提交或只保存在受限存储；
- Library 转写是否允许对外发布；
- 图片与第三方内容是否使用不同策略。

### 4.3 审核责任

需要定义谁可以批准：

- Work / Edition 映射；
- 官方/社区/第三方身份；
- 节点边界；
- 版本与重复关系；
- 权利与公开发布状态。

没有责任边界时，自动化只能产生 Draft，不得进入 Release Ready。

## 5. 建议确认方式

建议一次确认 D-001 至 D-016 的总体方向，并对任何不同意项逐条修改。确认后将：

1. 把 Draft 文档固化为 `spec/`；
2. 编写可执行 JSON Schema 与注册表；
3. 建立受限摄取 Package；
4. 只做代表性样本；
5. 样本通过后再次请求是否开始全量转换。

即使本轮确认，也不会直接启动全量 CHM 转换。
