# Milestone 1-B：受控摄取与来源清单

状态：**COMPLETED_AWAITING_ARCHITECTURE_CONFIRMATION**
Profile：`m1-profile@0.1.0`
范围：Acquire、Entry Inventory、Preserve Source

## 1. 目标与当前结论

M1-B 只验证 Source 层事实：原件摘要、受控解包、完整 Entry 枚举、原始字节保存、路径映射、媒体与编码线索、重复报告、跨 Record 校验和确定性重跑。

实现基础、合成纵向测试和两次真实摄取已经完成。真实 CHM 的大小与 SHA-256 已通过 M0 基线核对；两次运行均保存 7,148 个 Entry，来源语义 Validator 通过，规范 Inventory 与保存字节逐文件一致。

## 2. 真实原件事实

| 字段 | 值 |
|---|---|
| Workspace 相对路径 | `DND五版不全书26.06.30.chm` |
| 字节数 | `36,787,743` |
| SHA-256 | `836eea8912cf6c068687e99db4a1b4b6b915aeb2ef8af35cfb040803184686f2` |
| M0 摘要匹配 | 是 |
| Artifact ID | `urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408` |
| Git 状态 | 被 `*.chm` 忽略，不提交 |

Artifact ID 由 Artifact 类型和 CHM SHA-256 通过 M1-A 的 UUIDv5 工具确定性派生。文件名、当前时间、临时目录与文件系统枚举顺序不参与身份。

## 3. CHM Backend

实现后端：`SevenZipBackend`。

候选可执行文件按固定顺序检查 `7zz`、`7z`。后端：

- 使用参数列表调用外部命令，`shell=False`；
- 捕获标准输出、标准错误和退出码；
- 设置显式超时；
- 记录工具名称、版本、可执行文件名和二进制 SHA-256；
- 不访问网络；
- 不在原件相邻目录直接解包；
- 不把第三方二进制提交进仓库；
- 不以进程退出码代替解包结果枚举和字节校验。

依赖来源应由用户从 7-Zip 官方发行渠道或可信本机包管理渠道选择并安装。LoreBuddy 不自动下载、安装或请求管理员权限。

实际命令路径：`/opt/homebrew/bin/7zz`。该路径是指向 `/opt/homebrew/Cellar/sevenzip/26.02/bin/7zz` 的 Homebrew symlink。实际版本为 `7-Zip 26.02 arm64`，版本输出明确列出 CHM 格式读取能力；二进制 SHA-256 为 `2f412eded2d37f2cc52f26138e6964bd205ea0bf2ee6a70b8b990a18107e784d`。

CLI 通过 `--executable /opt/homebrew/bin/7zz` 显式注入后端，不修改系统 PATH，不创建软链接，也不回退到其他 Backend。

## 4. Acquire 流程

```text
inspect CHM
→ 校验大小与 SHA-256
→ 派生 Artifact ID
→ 校验受控目录 Ownership Marker
→ 在临时 owned 目录保存 CHM 原始字节副本
→ Backend 解包到 staging/
→ 独立 lstat 枚举
→ 路径规划与冲突隔离
→ copyfile 保存每个普通 Entry
→ 来源与保存副本分别计算长度和 SHA-256
→ 生成 Inventory / Path Map / Duplicate Report
→ Schema 与 Source Semantics 验证
→ 验证通过后原子切换
```

已有旧结果仅在 Ownership Marker 与 Artifact ID 完全匹配时允许替换。新结果全部验证成功后才切换；切换失败时恢复上一份结果。未知目录不会被清理。

## 5. 构建目录

默认目标为：

```text
build/acquisition/<artifact-uuid-hex>/
├── .lorebuddy-acquisition.json
├── artifact/
│   └── original.chm
├── extracted/
│   └── entries/
├── inventory/
│   ├── package.json
│   ├── artifact.json
│   ├── entries.jsonl
│   ├── path-map.jsonl
│   ├── duplicate-report.json
│   ├── acquisition-report.json
│   └── validation-report.json
├── logs/
│   └── backend-execution.json
└── staging/
```

`build/` 已被 Git 忽略。`staging/` 在原始 Entry 保存并验证后清空。日志允许记录执行耗时和本地命令参数，不参与规范确定性摘要。

## 6. Inventory 合同

`entries.jsonl` 每行是一个 `core.source-entry@0.1.0`。不修改 M1-A 已确认核心 Schema。M1-B 事实放入 `extensions.m1b-acquisition`：

- `normalized_path`；
- `entry_kind`，M1-B 保存成功的 Entry 为 `regular-file`；
- `preserved_path`；
- `path_status`；
- `safety_remapped`；
- `conflict_kind`；
- declared / detected media type 与 confidence；
- declared / candidate encoding、confidence、conflict 与 evidence；
- `duplicate_status`；
- `source_order`，无法可靠取得时为 `null`；
- warnings 与 errors。

基础 Schema 字段保存 Entry ID、Artifact ID、原始路径、实际保存路径、字节数、SHA-256、媒体类型、编码摘要、提取状态和生命周期。

采用 Extension 的原因是本轮真实事实可以无损表达，同时不需要修改已确认的 active Core Schema。替代方案是直接扩展 Core Schema；该方案会扩大 M1-A 合同并触发架构门禁，因此未采用。

## 7. 路径安全

路径处理覆盖：绝对路径、Windows 盘符、反斜杠、重复分隔符、`.`、`..`、URL 编码穿越、Null Byte、控制字符、Unicode NFC、大小写等价、Windows 保留名和非法字符、尾随空格或句点、超长路径。

安全路径保存在 `entries/<normalized-path>`。不安全或冲突路径使用来源路径摘要确定性隔离到 `entries/_remapped/`；原始路径、规范化路径、保存路径、原因和冲突类型同时记录。不得静默改名或覆盖。

枚举使用 `lstat` 语义，不跟随 Symbolic Link；硬链接在保存层写成独立普通文件字节，不依赖宿主链接关系；其他特殊文件拒绝并进入报告。

## 8. Source Preservation

- 原始 CHM 复制到受控 Artifact 目录后重新计算长度与 SHA-256；
- 每个普通 Entry 使用二进制复制，不转码、不改换行、不格式化 HTML、不处理图片；
- 来源文件和保存文件分别计算长度与 SHA-256并要求完全一致；
- 重复内容保留不同 Entry ID 与路径事实，不做静默去重；
- 保存文件缺失、额外文件、摘要漂移或路径逃逸都会使语义 Validator 失败。

## 9. 媒体类型、编码与重复

媒体检测组合扩展名与有限文件头。文件头只覆盖常见 HTML、XML、图片和字体签名；没有强证据时使用 `extension-only`、`low` 或 `unknown`，不把猜测升级为确认事实。

编码只读取 BOM、HTML charset、XML declaration 和严格解码可行性。当前仅产生候选与证据，不统一转码。GBK/GB2312 声明与 GB18030 严格解码候选的兼容关系保留为线索，不修改原字节。

重复报告区分字节完全相同、同名不同内容、大小写等价冲突、Unicode 规范化冲突和重复路径。物理去重不属于 M1-B。

## 10. CLI

```bash
lorebuddy acquire inspect <chm-path> [--json]
lorebuddy acquire run <chm-path> [--output build/acquisition] [--backend 7zip] [--executable /absolute/path/to/7zz] [--timeout 300] [--dry-run] [--json]
lorebuddy acquire validate <artifact-dir> [--json]
lorebuddy acquire report <artifact-dir> [--json]
```

所有命令只访问显式 CHM 或显式 Artifact 目录，不读取本地 Obsidian 配置，不访问 Vault。

## 11. 验证与测试

执行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -p no:cacheprovider
.venv/bin/pip check
```

当前结果：60 项测试通过，`pip check` 通过。覆盖路径穿越、NFC/大小写冲突、Windows 文件名、Entry ID、媒体与编码线索、重复检测、原始字节保存、Symbolic Link 拒绝、后端缺失、外部命令失败、超时、显式 Backend 路径、CLI 退出码、Profile Schema、Source Semantics、篡改检测和两次合成摄取确定性比较。

两次真实摄取的 `inventory/`、Artifact 副本和全部 `extracted/` 文件逐字节一致。最终语义 Inventory SHA-256 均为 `8f4762753632362591e34d788139468342aa840481be5d18c39107919ea822df`。非确定性字段仅存在于 Backend Log 的执行耗时和运行目录参数；日志不参与规范语义摘要。

## 12. 真实 Entry 统计与已知异常

| 指标 | 结果 |
|---|---:|
| Entry 总数 | 7,148 |
| 保存成功 / 失败 / 跳过 | 7,148 / 0 / 0 |
| Entry 总字节 | 128,218,186 |
| 每次运行含 CHM 容器的 Source 总字节 | 165,005,929 |
| 零字节 Entry | 1 |
| 非普通文件 | 0 |
| 路径异常 / 路径冲突 | 0 / 0 |
| 唯一 Entry ID / Storage Path | 7,148 / 7,148 |
| 字节完全相同组 | 23 组，涉及 207 个 Entry |
| 同名但内容不同组 | 686 组，涉及 1,994 个 Entry |

媒体类型统计：HTML 6,819；XML 136；Office Theme 67；JPEG 70；GIF 22；PNG 16；CSS 2；纯文本 1；`application/octet-stream` 15。媒体识别置信度为 high 178、extension-only 6,954、low 1、unknown 15。

编码声明统计：GB2312 6,787、GBK 1、UTF-8 68、unknown 292。检测候选为 GB18030 6,807、UTF-8 141、unknown 200；声明与候选冲突 2。所有结果都是线索，不修改来源字节。

`source_order` 无法从当前 7-Zip 解包结果可靠获得，全部 7,148 条显式记录为 `null`。这不是推测顺序。

M1-B 新增 6 个 `experimental` Profile Schema，覆盖 Path Map、Duplicate Report、Acquisition Report、Validation Report、Ownership Marker 和 Backend Log；没有修改或提升 M1-A Core Schema。Path Map 被验证为 Inventory 的一对一确定性投影。

## 13. 明确未实现

- Source Fragment；
- Boundary Candidate 或人工确认；
- Knowledge Node、Markdown Library；
- Relationship、Alias Index、Node Index；
- Obsidian Staging、Publisher、Vault 写入；
- Runtime、RAG、Embedding、向量数据库；
- Rights Authority、Claim Lineage、Release Rights Binding、Public Attestation；
- 完整 Fidelity Coverage Map；
- M1-C 或全量语义转换。

## 14. 后续门禁

M1-B 的真实 Inventory、Source Semantics 与两次确定性重跑已经通过，结果足以支持后续选择 5～10 个复杂样本。进入下一阶段仍需单独的架构确认；本轮不生成 Fragment、Boundary、Knowledge Node、Library 或 Obsidian Publish View。

当前 Package 仍是 `restricted`、`experimental` 的受限 Acquisition 结果。M0 的更高 Source Complete 上限还要求独立提取实现交叉验证与 CHM Directory 原始路径字节证据；这些未被 M1 Implementation Profile 激活，不应把本轮结果表述为公开发布级 Source Complete。
