# LoreBuddy

**Know the rules. Remember the story.**

LoreBuddy 是一个长期维护的 TRPG（Tabletop RPG）知识平台。

它的目标不是把某一种格式转换成 Markdown，也不是把某一种规则系统接入某个特定 AI。LoreBuddy 要保存可验证的原始资料，将其组织为独立、可追溯、可版本化的知识节点（Knowledge Node），并让未来不同的 AI、搜索引擎和知识图谱都能读取同一套知识包（Knowledge Package）。

## 当前状态

`v0.1.0` 已冻结 M1-C4 本地产品基线：受控摄取、全量 Markdown、独立 Obsidian
Baseline Vault 和低文件数 GPT Project Export 均已有自动或人工验收。GPT 特化稿与
NotebookLM 优化稿的实际使用，已在建卡、怪物数据、技能合规和角色卡合规等 DND
Terminal 工作流中证明下一阶段需求。

当前为 `v0.2.0.dev0 / M2 Rule Cluster Pilot`：以 Antigravity 的外部 Book Catalog
交付为候选输入，先验证 D&D 2024 小样本的规则候选、审核对象、Rule Card 与终端候选包。
它不授权全量 Rule Object、Runtime、RAG 或直接修改 DND Terminal。

当前实施入口见 [Milestone 1 索引](docs/milestone-1/README.md)、
[M1 使用反馈与 v0.2 需求依据](docs/milestone-1/m1-usage-feedback-and-v02-requirements.md)、
[M2 启动授权](docs/milestone-2/abc.md) 与 [项目 Roadmap](ROADMAP.md)。

## 核心约束

- 原始来源（Source）不可变，派生知识（Library）不得伪装成原始资料。
- 官方文本不得被总结、改写、简化或静默纠错。
- 每个知识节点必须能够追溯到实际摄取工件、内部资源和精确片段。
- 节点身份不得依赖标题、文件路径或正文摘要。
- Package 是发布、授权、依赖和访问控制边界，不等同于规则系统目录。
- 索引只允许自动生成，删除后必须能够确定性重建。
- 平台核心不得包含 D&D 专属字段；系统特化只能存在于 Package 或命名空间化扩展中。

## 当前输入

首个来源工件是包含多个版本、出版物、第三方资料和模组内容的聚合资料；它不得被
建模为单一规则书。M1 已对其执行受控摄取和只读 Markdown / 发布视图构建，但来源
身份、版权与再分发范围仍保持 `unknown` 或 `claimed`，不因构建通过而升级为权威结论。

## 相关生产工作区

D&D规则生产工具已独立到[DNDRulePipeline](docs/projects/DNDRulePipeline.md)。入口记录本机路径、Obsidian镜像与GitHub配置状态；平台规范和正式知识接纳仍属于LoreBuddy。
