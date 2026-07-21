# Milestone 0：知识包规范设计索引

状态：**Draft / 待架构确认**  
规范目标版本：`0.1.0`  
当前输入：`DND五版不全书26.06.30.chm`

## 1. 本里程碑的交付物

| 文档 | 内容 |
|---|---|
| [CHM 结构分析](chm-analysis.md) | 容器、资源、导航、编码、链接与内容边界的只读取证 |
| [知识包规范草案](knowledge-package-spec.md) | Package 边界、目录、身份、来源、版本与确定性构建 |
| [Markdown 与元数据规范](markdown-metadata-spec.md) | 知识节点正文、Front Matter、可追溯与关系表达 |
| [Schema 提案](schema-proposal.md) | 平台核心 Schema、通用 Profile 与系统特化边界 |
| [索引规范](index-spec.md) | Manifest、Alias、Relationship、Navigation 与 Provenance Index |
| [完整性与事件协议](integrity-protocols.md) | 可见文本、结构保真、Fragment 摘要与稳定 Candidate / Occurrence Key |
| [权利、访问与发布规范](rights-release-spec.md) | Access Domain、Rights 合并、公开回执、Lock 投影与 Release Payload 白名单 |
| [CHM 转换策略](chm-conversion-strategy.md) | 分阶段转换、人审、保真验证、质量门禁与幂等要求 |
| [架构决策与风险](decisions-and-risks.md) | 推荐决策、替代方案、权衡、风险及待确认事项 |

根级 [AGENTS.md](../../AGENTS.md) 将这些原则转化为后续协作约束。

## 2. 本里程碑不包含

- CHM 全量解包入库；
- 正式知识节点生成；
- AI、Agent、RAG、Embedding 或向量数据库；
- 搜索、知识图谱或 Runtime；
- Campaign、Session、NPC Memory；
- 对外发布或授权判断。

只读分析曾在临时目录展开 CHM，用于统计和抽样；临时展开内容不是项目资产，也不是转换结果。

## 3. 推荐架构结论

### 3.1 Package 不是规则系统目录

不采用长期固定的 `packages/dnd5e/` 单层结构。推荐：

```text
packages/<namespace>/<package-slug>/
```

知识包（Knowledge Package）是独立发布、授权、依赖和访问控制边界。规则系统、版本、世界与 Campaign 是 Manifest 中的适用范围，不是 Package 的物理父目录。

### 3.2 当前 CHM 是聚合工件

当前 CHM 同时包含多个规则年代、出版物、第三方内容、模组和在线资料。它只能先作为一个受限的摄取工件（Acquisition Artifact）保存，不能整体声明为一本官方规则书。

### 3.3 来源事实分层

来源模型采用：

```text
Knowledge Node ──Provenance──> Fragment ──> Entry ──> Artifact
                                    │
                                    └──经审核的多对多来源映射──> Edition ──> Work
```

`Fragment → Entry → Artifact` 是实际摄取证据；`Fragment / Entry → Edition → Work` 是需要证据支持的多对多来源断言。两者不得混为一谈，也不得把一个 Artifact 限制为只能属于一个 Edition。

### 3.4 “官方唯一真相”必须带上下文

不同官方版本、勘误、语言和可选规则可能同时有效。LoreBuddy 保存所有不可变来源表达，不覆盖历史版本。未来的“当前有效规则”必须由明确的规则上下文（Rules Context）选择，不能在 Milestone 0 静默固化。

### 3.5 平台核心保持小而稳定

平台只定义 Package、Node、Source、Provenance、Relationship、Redirect、Tombstone 和 Index 等核心结构。

Spell、Monster、Class、Condition 等不是跨系统同义概念，必须作为命名空间化的系统 Profile，不进入平台核心。

### 3.6 Index 完全派生

Manifest、Alias、反向关系、导航、来源覆盖等索引都由事实源生成。它们可删除、可重建、不可手工维护，也不得泄漏未授权 Package 的信息。

Content Manifest 对事实源分片并分别计算 `content_root_digest` 与非递归 `library_root_digest`；Output Manifest 固定全部派生索引；根级 Release Manifest 组合 Content、Library 与 Index Root。人工 Issue、Exception 与 Review 属于 Metadata，检测运行日志属于 Reports，二者不能混用。

## 4. 请求确认的架构决策

开始真正转换前，需要确认以下决策：

1. `D-001`：Package 是发布、授权、依赖和访问控制边界，不是规则系统目录。
2. `D-002`：同时保留原始 Artifact 与全部原始 Entry、路径证据和摘要。
3. `D-003`：采用 Work / Edition / Artifact / Entry / Fragment 分层，并以 Source Mapping 连接出版声明与摄取证据。
4. `D-004`：规范 Record 使用稳定 UUIDv7；标题、slug、路径和内容摘要不承担身份。
5. `D-005`：一个 Node 只承载一个语言、表达版本与权威上下文；相同 Edition 不机械拆分。
6. `D-006`：采用“Core Envelope + 命名空间 Profile”，不建立万能 Spell / Monster Schema。
7. `D-007`：来源权威、规范性、适用范围、Override 和 Rights 分开表达，由规则上下文选择有效视图。
8. `D-008`：节点边界账本（Boundary Ledger）是人工确认知识边界的权威输入。
9. `D-009`：只维护带稳定 Assertion ID 的正向关系；反向关系完全由 Index 生成。
10. `D-010`：Index 完全派生且确定性构建；Content、Library、Index 与 Release 使用明确摘要边界。
11. `D-011`：私有 Campaign 使用独立 Package，并按 Access Domain / Principal 授权。
12. `D-012`：当前 CHM 先进入最严格访问级别的受限摄取 Package，审核后再拆分。
13. `D-013`：Public Package 只携带绑定当前内容的最小 Attestation；完整 Decision、Reviewer、Lock 与 Audit Binding 留在受限 Audit / Build Package。
14. `D-014`：可见文本、结构比较和 Source Fragment 使用独立版本化事件协议；Fidelity Coverage Map 以稳定 Unit 显式绑定 Provenance、正文 Range 与 Source Event Range。
15. `D-015`：Rights Decision 只保存 Claim / 语义 Coverage；最终 Release 字节由目标包外的 Release Rights Binding 固定，Claim 必须从受控 Universe 闭包扫描。
16. `D-016`：Rights Authority Domain 管签发责任，Access Domain 管读取权限；Public Release 与受限 Audit Context 通过 Delegation 和锁定上下文连接。

以上是 [D-001 至 D-016](decisions-and-risks.md) 的确认摘要。确认这些决策不等于授权对外发布，也不等于确认 CHM 内文本的官方性或版权状态。

无论是否一次确认全部决策，实际转换仍先做 5～10 个复杂样本和双向保真验证；样本门禁通过前不运行全量转换。

## 5. 确认后的下一步

获得确认后才进入转换准备：

1. 固化核心 JSON Schema 与注册表；
2. 建立当前 CHM 的摄取 Package；
3. 保存原始 CHM、原始 Entry 和完整 Inventory；
4. 完成来源文档与授权分类账本；
5. 选择复杂样本，提出候选节点边界；
6. 人工确认后生成第一批 Library 节点；
7. 通过质量门禁后再决定是否全量转换。
