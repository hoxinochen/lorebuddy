# M1 验收标准

状态：Confirmed

## 1. 验收原则

M1 以可重复的纵向闭环为成功标准，不以转换数量为成功标准。自动检查与人工验收都必须通过；任何 `unknown` 不得被静默当作 Pass。

M1 验收不等于 M0 `Release Ready(public)`，也不证明内容官方性、版权状态或跨设备同步系统正确性。

## 2. 前置条件

- M1 Implementation Profile 已确认；
- D-001 至 D-016 的 M1 状态已确认；
- 当前 CHM SHA-256 与 M0 分析基线一致；
- 本地配置通过未跟踪配置或环境变量提供；
- Vault 验收目标由用户明确授权；
- 当前设备是唯一 Build / Publish Authority；
- 发布前已取得本地发布锁。

## 3. 样本集合

必须生成 5～10 个经人工批准的复杂样本。样本集合合计至少覆盖：

- 无 Heading 或弱结构页面；
- 多级 Heading / List；
- 简单 Table；
- `rowspan` / `colspan` 或需受限 HTML 的复杂 Table；
- 本地图片或附件；
- 内部 Link 与 Anchor；
- 缺失或歧义 Link 的失败案例；
- Pre / Code 或显式保留空白；
- 重复标题或 basename 冲突；
- 至少一种 GBK 可解码但严格 GB2312 失败的 Entry。

单个样本可以覆盖多个条件。不能为了凑数回避 M0 已发现的高风险页面族。

## 4. Source 与 Inventory

1. 原始 CHM 字节、大小和 SHA-256 与 Acquire Record 一致；
2. Inventory 覆盖容器中的全部 Entry，不只覆盖样本；
3. 每个 Entry 保存原始路径证据、安全存储路径、长度和 SHA-256；
4. 原始 Entry 重读摘要与 Inventory 一致；
5. 路径穿越、保留名、大小写冲突、Unicode 冲突和超长路径均产生确定结果；
6. Decoder 不使用替换字符掩盖失败；
7. Source 字节没有被格式化、清洗或回写。

## 5. Boundary、Node 与 Provenance

1. 每个正式样本 Node 都有人工批准的 Boundary Decision；
2. 5～10 个样本均能生成 Markdown Knowledge Node；
3. 一个 Node 只表达一个语言、版本和语义单元；
4. Node ID 稳定，标题、Slug、路径和正文摘要不承担身份；
5. 每个 Node 至少可追溯到 Fragment → Entry → Artifact；
6. Source Mapping 未核实时明确为 `unknown` / `claimed`，不猜测 Work / Edition；
7. 忠实转写正文不含自动摘要、解释、补写或静默纠错；
8. Source / Library / Metadata / Index 没有相互写回。

## 6. Markdown 与 Obsidian

1. Obsidian 可在不安装自定义插件的情况下直接打开全部 Note；
2. YAML Properties 可解析且不存在重复 Key；
3. Properties 只包含 Publish Profile 允许的最小字段；
4. Note Link、Wikilink、Anchor 和附件引用均有效；
5. 图片和附件文件存在，路径为 Vault 相对形式；
6. 生成内容不含设备绝对路径；
7. 文件名不使用 Windows 保留名或非法字符；
8. 不存在尾随空格/句点、大小写等价冲突或 NFC / NFD 冲突；
9. 同名 Note 按确定性规则消歧；
10. 发布结果不依赖 `.obsidian/` 修改或自定义插件。

## 7. 最小 Index

- Node Index 数量与生成 Node 数量相等；
- Alias Index 保留一对多冲突，不自动选唯一目标；
- Relationship Index 的反向边可由正向断言重建；
- Provenance Index 可从 Node 定位 Fragment，也可从 Entry 找到 Node；
- Source Navigation Index 保留样本的 HHC Occurrence 和顺序；
- 删除全部派生 Index 后重建，得到字节一致结果。

## 8. Fidelity 与确定性

1. 每个样本 Source 与 Node 的 Visible Text Digest 相等；
2. 样本实际使用的基础 Structure Event 比较通过；
3. 未支持结构、动态内容、歧义 Reference 或未知 Visibility 必须失败或进入人工批准的例外，不得静默跳过；
4. 相同 CHM、工具版本、Schema、配置和 Boundary Ledger 的第二次构建得到字节一致的规范 Package 输出；
5. 第二次 Obsidian Staging 输出和 Publish Manifest 字节一致；
6. 时间、临时目录和宿主绝对路径不得进入规范摘要；
7. 运行时间与性能信息只进入非规范日志。

## 9. Dry Run 与安全发布

1. `dry-run` 显示新增、修改、删除、保持不变和冲突文件；
2. `dry-run` 不写 Vault；
3. 发布前验证 Vault 根、`.obsidian/`、目标 containment 与 Symbolic Link；
4. Publish Manifest 精确列出 LoreBuddy 拥有文件的相对路径、大小和摘要；
5. 发布器只修改或删除上一份 Manifest 所拥有的文件；
6. `_LoreBuddy-M1` 外的用户内容不会被修改；
7. 目标内未被 Manifest 拥有的文件不会被删除或覆盖，路径冲突会阻塞；
8. 故障注入发生在写入前、文件切换中和 Manifest 提交前时，旧 Manifest 对应的完整结果都能恢复；
9. Publish Manifest 最后原子替换，失败时保留旧 Manifest；
10. 发布日志和错误报告保存在 Workspace，不污染 Vault；
11. 不跟随或发布 Symbolic Link；
12. 同一设备启动第二个发布进程时必须因本地锁而失败。

## 10. 跨设备人工验收

自动门禁只证明发布内容使用可移植路径和文件名，不能证明用户现有同步服务已正确工作。用户必须在至少一个同步后的其他设备上人工确认：

- Note 可见且可打开；
- Properties 显示正常；
- Note Link / Wikilink 可跳转；
- 图片和附件可读取；
- 中文文件名和标题显示正常；
- 链接仍为 Vault 相对形式；
- 未出现大小写或 Unicode 造成的重复文件。

该人工结果记录为 M1 Acceptance Record；LoreBuddy 不读取同步服务内部状态。

## 11. 必须满足的十二项结果

1. 5～10 个复杂样本可生成；
2. Obsidian 可直接打开；
3. YAML Properties 正常；
4. Note Link 和附件有效；
5. 不含绝对路径；
6. 第二次构建结果确定；
7. Dry Run 能显示变更；
8. 发布失败不会破坏旧结果；
9. 不会修改 `_LoreBuddy-M1` 外的用户内容；
10. Publish Manifest 能准确声明所有权；
11. 同步到其他设备后链接仍为 Vault 相对形式；
12. 实际跨设备显示由用户完成并记录人工验收。

## 12. Exit Gate

全部自动检查通过、跨设备人工验收通过、用户确认日常阅读体验可接受，并且没有未批准的 Critical / High 问题时，M1 才能标记完成。任何单项失败都不得用“未来会修”绕过；M1 完成也不自动启动 M2 或改变正式发布目录。
