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


## 9. DND使用反馈：Guidance版本与来源核验（2026-10-13）

- **状态：** 2026-10-16已完成本项差异原因核验，结论见下；出版／翻译／权利身份仍未核实，DND下游准入未发生。本记录不构成M2规则对象批准或后续实施授权。
- **Origin：** User在DND Terminal v0.15.0 AMD-003批注指出本地Guidance与线上条目不一致，并于2026-10-13同意由LoreBuddy处理、记入Backlog。
- **实际观察：** NotebookLM_Version/Lore_01_核心玩家规则.md的Guidance段落描述一次属性检定加d4后结束；D&D Beyond 2024条目描述选定技能并在持续期间适用。本地条目的具体版本／出版映射仍需核验，差异不等于可以认定本地原文错误。
- **参考定位：** 本地标题“神导术｜Guidance”，原导出行17050附近；2024对照 https://www.dndbeyond.com/sources/dnd/br-2024/spell-descriptions#Guidance 。目录名称和页面路径只是定位，不能代替Edition／Entry／Fragment审核。
- **建议方向与替代方案：** 定位对应摄取Artifact／Entry／Fragment，分别核验规则版本、语言与出版声明，再形成可追溯变体／映射和受控候选。采用明确版本候选供DND选择；直接覆盖本地文本虽然快，但会混版、丢失来源，故不采用。
- **启用条件：** 在M2来源映射／规则簇小样本职责内明确输入集合、精确片段和审核对象，并通过对应Profile批准；不扩大为全量法术修正或自动下游采纳。
- **兼容与迁移：** M1 Source、已通过Publisher、原NotebookLM／GPT输出及已批准Node保持原字节；核验发现修正应走新版记录和关系，不能静默改原文。身份／权利未知状态保留，候选结果不得直接改DND正在运行的团。
- **后续验收：** 双方片段有定位及摘要，版本结论有审核依据，候选正文不混版，原来源无变化，下游明确选择且不自动覆盖。
- **跨项目关系：** DND Terminal Design §17.4保留版本依赖；LoreBuddy承担源数据核验。当前只新增这条待办，不处理原资料、不发起其他聊天任务或发布。

### 2026-10-16 Guidance差异核验结论

User本轮明确要求先解决神导术差异、解释原因，随后停止。上方保留2026-10-13的原始问题记录；本节更新其来源差异核验结果，不关闭DND未来条目选择和准入提醒。

**结论：此前引用的NotebookLM第17050行附近是2014规则文本；同一文件第27324行附近已经保存2024规则文本。差异来自用旧版片段对照新版，而非本次发现2024源条目被转写成旧版。** 两段都可以分别追溯到独立的原始HTML Entry，两个原文均无需覆盖或修正。

| 核验项 | 2014文本 | 2024文本 |
|---|---|---|
| NotebookLM定位 | `Lore_01_核心玩家规则.md` 第17050–17058行（含Anchor） | 同文件第27324–27332行（含Anchor） |
| 规则差异 | 一次属性检定可加d4，使用后法术结束 | 施法时选择一项技能，持续期间使用该技能的属性检定加1d4；没有使用一次即结束的条款 |
| Entry ID | `urn:uuid:4f5a2d13-d1fb-5ea2-935e-f1c1e41113b4` | `urn:uuid:aeefb9c1-aff9-5982-98ab-0643f145eba5` |
| 原始Source Path | `玩家手册/魔法/法术详述/戏法.html` | `玩家手册2024/法术详述/0环.htm` |
| M2-A登记 | `phb-2014`，`source_identity_status: claimed` | `phb-2024`，`source_identity_status: claimed` |
| M1-C3完整Note字节范围 | UTF-8 `[5978,6439)`，第107–115行 | UTF-8 `[7201,7598)`，第122–130行 |
| 原始HTML字节范围 | GB18030 `[5026,5441)` | GB18030 `[6146,6513)` |

范围均从文件开头按0计数、结束位置不包含；原始HTML范围以`<H4 id="Guidance">`开始、下一个`<H4 id="Light">`之前结束。M1-C3／NotebookLM片段含Guidance Anchor与标题，不含下一法术和尾部空行；这些是本次检查定位，不是新建或批准的Source Fragment。

证据与检查：

- 两个Entry均属于Artifact `urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408`。本次复算保存的CHM容器摘要，与Artifact Record中的`836eea8912cf6c068687e99db4a1b4b6b915aeb2ef8af35cfb040803184686f2`一致。
- 旧／新HTML全文SHA-256分别为`b4114e9d2d32c6d9cc584db6ca94e93dbdc4c6890389183e3a7253635cced086`、`bf6bad14227eff5ef7e369e8b63b641de14dfa45a2645659988822a10140fc25`，均与摄取Inventory及M1-C3 Publisher Manifest一致；两个Publisher Note全文摘要也与Manifest一致。只读解码原始HTML，确认两套机制已经分别存在于Source。
- NotebookLM整文件SHA-256为`b9c329141af1aecaa32dcb26bed6333d88b9ced935146dc9a5cef47888780be8`。两段分别与对应M1-C3片段唯一匹配；比较只统一CRLF／LF并排除尾部空行，不忽略正文字符或标点。Publisher Manifest与M2-A Mapping摘要仍分别为既有锁定的`d9172ac3befdd0be00547d9d72f9f212e2ead8c16412c96b9a155a32adf56458`、`030a2d30d2d39601a6dc97d1bd293f3742387ca26293f7053e0501755a77bbec`。
- 2026-10-16直接读取[D&D Beyond旧版Guidance](https://www.dndbeyond.com/spells/2132-guidance)和[新版Guidance](https://www.dndbeyond.com/spells/2618971-guidance)。旧页明确标注Legacy／Basic Rules (2014)；两页分别支持上表的旧／新机制差异。此项是官方网页对照，不是冻结的新摄取Artifact，也不据此证明本地中文的官方翻译身份。
- 同一NotebookLM文件包含两个相同`id="Guidance"`及同名标题；只按标题或`#Guidance`定位不能区分规则版本。该歧义可解释错选风险，但本次没有足够历史日志证明最初具体通过哪种搜索、跳转或模型选择路径取到了旧版。
- 可重跑的局部核对脚本与机器结果保存在忽略目录`build/guidance-source-investigation-2026-10-16/verify.py`及`evidence.json`；不复制规则正文。本节为持久核验结论，临时结果不是事实源或正式映射合同。

处置：本项“差异原因未明”已解决。后续若选择D&D 2024神导术，应以已定位的2024 Entry与精确片段为候选依据，并完成独立准入；不得继续把第17050行的旧版机制当作2024预设。保留2014变体，不按同名合并；M2-A出版身份保持`claimed`，翻译与再分发权保持`unknown`。本次未修改Source、M1构建、NotebookLM／GPT输出、DND代码／规则基线／实例或冻结记录，未创建批准规则对象；到此停止，等待User下一步指令。
