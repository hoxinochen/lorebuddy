# LoreBuddy

**Know the rules. Remember the story.**

LoreBuddy 是一个长期维护的 TRPG（Tabletop RPG）知识平台。

它的目标不是把某一种格式转换成 Markdown，也不是把某一种规则系统接入某个特定 AI。LoreBuddy 要保存可验证的原始资料，将其组织为独立、可追溯、可版本化的知识节点（Knowledge Node），并让未来不同的 AI、搜索引擎和知识图谱都能读取同一套知识包（Knowledge Package）。

## 当前状态

当前处于 **Milestone 1-A：Executable Foundation 完成待确认**。

Milestone 0 已建立架构基线，Milestone 1 设计已经确认。本阶段只建立：

- Python Package 骨架；
- M1 最小可执行 Schema 与 Registry；
- 虚构 Fixture 与统一 Validator；
- 稳定 ID、跨平台 Slug 和本地配置工具；
- 不含摄取、转换或发布能力的基础 CLI；
- 自动测试与 M1-A 实施文档。

本阶段不读取或解包真实 CHM，不创建 Package、Entry Inventory 或 Knowledge Node，不访问 Obsidian Vault，也不实现 Publisher、AI、RAG、Embedding、Runtime 或 Campaign。

当前实施入口见 [Milestone 1 设计索引](docs/milestone-1/README.md) 与 [M1-A Executable Foundation](docs/milestone-1/m1a-executable-foundation.md)。

## 核心约束

- 原始来源（Source）不可变，派生知识（Library）不得伪装成原始资料。
- 官方文本不得被总结、改写、简化或静默纠错。
- 每个知识节点必须能够追溯到实际摄取工件、内部资源和精确片段。
- 节点身份不得依赖标题、文件路径或正文摘要。
- Package 是发布、授权、依赖和访问控制边界，不等同于规则系统目录。
- 索引只允许自动生成，删除后必须能够确定性重建。
- 平台核心不得包含 D&D 专属字段；系统特化只能存在于 Package 或命名空间化扩展中。

## 当前输入

仓库中的 `DND五版不全书26.06.30.chm` 是第一个待摄取的来源工件（Source Artifact）。它是包含多个版本、出版物、第三方资料和模组内容的聚合资料，不应被建模为单一规则书。

该文件目前只完成只读结构分析，尚未展开到仓库，也尚未生成任何知识节点。
