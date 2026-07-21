# M1 Obsidian Publish Profile

状态：Confirmed  
Profile ID：`obsidian-publish@0.1.0`

## 1. 目的与边界

本文定义 LoreBuddy Workspace 向 Obsidian Vault 发布 M1 样本阅读视图的合同。Vault 是消费端，不是 Package、事实源、构建缓存或中间目录。

M1 不实现 Obsidian 插件、双向同步、用户修改合并或 LoreBuddy 自有多设备同步。发布结果必须在标准 Obsidian 中直接阅读。

## 2. 本地目标

当前唯一 Build / Publish Authority 是用户当前 Mac。当前真实 Vault Root 已由用户在本轮提供，但由于设备绝对路径被禁止进入 Git 跟踪文件和可移植产物，本规范不重复保存其字面值；未来验收时由未跟踪的 `config.local.toml` 或 `LOREBUDDY_OBSIDIAN_VAULT` 注入并与用户声明值核对。

固定的 Vault 相对子目录为：

- M1 测试发布：`_LoreBuddy-M1`；
- 未来正式发布：`LoreBuddy`。

本轮不会读取、创建或修改 Vault Root、上述子目录或 `.obsidian/`。

“文档必须写明真实根目录”与“私人绝对路径不得进入 Git 跟踪文件”存在字面冲突。本 Profile 选择后者作为安全约束，把真实值降为本地验收配置；该取舍需要架构确认。

## 3. 本地配置模型

未来未跟踪配置：

```toml
[obsidian]
vault_root = "<absolute-local-vault-path>"
test_publish_subdirectory = "_LoreBuddy-M1"
publish_subdirectory = "LoreBuddy"
```

解析优先级：

1. 显式 CLI 参数；
2. `LOREBUDDY_OBSIDIAN_VAULT`；
3. `config.local.toml`；
4. 缺失即失败，不使用平台默认值。

CLI / 环境变量只覆盖 `vault_root`；发布子目录仍必须通过已审核的相对配置或 Profile 选择。`config.local.toml` 已加入 `.gitignore`。未来可以提供 `config.local.toml.example`，但只能使用占位符。

设备绝对路径禁止进入：Git 跟踪文件、Knowledge Node Front Matter、Node / Package Metadata、Index、Obsidian Note Properties、Publish Manifest 和规范摘要输入。绝对路径只允许出现在本机非规范运行日志中，日志默认脱敏。

## 4. Workspace、Staging 与 Vault

```text
LoreBuddy Workspace
  ├── Package / Library / Metadata / Index      # 事实与规范派生物
  ├── build/obsidian-staging/<build-id>/        # 完整候选视图
  ├── build/obsidian-backup/<transaction-id>/   # 发布事务回滚副本
  ├── build/publish-journal/                     # 非规范事务日志
  └── build/locks/obsidian-publish.lock          # 本地发布锁

Obsidian Vault
  └── _LoreBuddy-M1/                             # M1 消费视图
```

`build/` 不进入 Git。Staging 必须完整生成并验证后才能接触 Vault；禁止以 Vault 为当前工作目录边生成边修改。

## 5. 发布视图布局

```text
_LoreBuddy-M1/
    Home.md
    Notes/
        <kind>/
            <stable-slug>--<short-id>.md
    Assets/
        <digest-prefix>/
            <digest>.<safe-ext>
    _lorebuddy/
        publish-manifest.json
```

- `Home.md` 是生成的测试入口，不承担事实源职责；
- `kind` 来自锁定的有限目录注册表，未知 Kind 使用 `reference`，不得直接成为任意路径；
- `stable-slug` 在 Boundary Approval 时写入 Metadata，之后标题变化不自动改名；
- `short-id` 是稳定 Node UUID 的无连字符前 8 个十六进制字符，只用于消歧，不承担身份；
- Asset 以内容摘要寻址；不同 Usage 的 Alt / Caption 保存在 Note 投影中；
- `_lorebuddy/publish-manifest.json` 是发布所有权清单，不是 Knowledge Node、Package Manifest 或 M0 Release Manifest。

## 6. 文件名与路径规则

生成路径必须满足所有条件：

1. 只使用 Vault 相对 POSIX 路径，分隔符为 `/`；
2. 拒绝空段、`.`、`..`、绝对路径、Drive Prefix、UNC Path 和 NUL；
3. 不使用 Windows 保留名，包括带扩展名的 `CON`、`PRN`、`AUX`、`NUL`、`COM1`～`COM9`、`LPT1`～`LPT9`；
4. 不使用 `< > : " / \\ | ? *` 或控制字符；
5. 路径段不以空格或句点结尾；
6. 规范输出使用 Unicode NFC；
7. 冲突检测同时比较原字符串、NFC、NFD 和 Unicode Case Fold；
8. 单个文件名建议不超过 120 UTF-8 bytes，发布根内相对路径不超过 200 UTF-8 bytes；
9. 扩展名使用锁定的小写白名单；
10. 任何碰撞都在写出前阻塞，不通过自动追加不稳定序号修复。

`stable-slug` 使用经审核、锁定版本的 ASCII Lowercase Slug 算法；若中文标题无法生成稳定可读 Slug，回退为 `node-<short-id>`，而不是依赖可变的自动拼音库。同名 Note 由稳定短 ID 确定性消歧。

## 7. Note、链接与附件

生成 Note 默认使用 Vault 相对标准 Markdown Link：

```markdown
[专注](../rule/concentration--0123abcd.md)
![示意图](../../Assets/ab/abcdef....png)
```

选择原则：

- 标准 Markdown Link 是 M1 默认，因为可移植、可被普通 Markdown 工具和未来 AI 直接读取；
- Link Text 使用目标标题，Target 使用稳定相对文件路径；
- Obsidian Wikilink 只作为样本验证后的可选 Publish Renderer，不进入规范 Node；
- 不依赖“最短路径解析”、同名自动猜测或 Vault 全局 Alias 唯一；
- Fragment Link 使用明确的已验证 Heading Anchor；无法稳定解析时保留问题，不猜测；
- 外部 URL 保留为标准绝对 Web URL，但本地 `file://` 和设备绝对路径禁止发布；
- Asset 必须先进入 Staging 并通过摘要、MIME 与存在性检查。

## 8. Properties 最小字段集

M1 Publish View 只投影以下 Obsidian Properties：

```yaml
---
lorebuddy_id: "urn:uuid:..."
title: "专注"
aliases:
  - "Concentration"
kind: "rule"
language: "zh-Hans"
ruleset: "dnd5e-2014"
lorebuddy_revision: 1
lorebuddy_status: "draft"
tags:
  - "trpg/rules"
---
```

- `aliases` 与 `tags` 使用 Obsidian 原生 Properties 习惯；
- `ruleset` 未审核时为 `unknown`，不能从目录猜测；
- 空数组使用 `[]`，未知值使用明确字符串 `unknown` 或按 Schema 省略，不能混用；
- `package_id`、Schema URI、Artifact / Entry / Fragment ID、Digest、Locator、Build Lock、内部 Relationship、Review、Issue 和宿主路径不得污染 Properties 面板；
- 完整字段仍保存在 Workspace 的规范 Node / Metadata 中。

## 9. 阅读视图中的来源呈现

规范转写正文在生成 Note 中使用固定内容边界：

```markdown
<!-- lorebuddy:content:start -->
来源正文……
<!-- lorebuddy:content:end -->

---

> [!info] 来源
> 来源状态：未核实
> 来源条目：可读显示名
> LoreBuddy ID：`urn:uuid:...`
```

来源卡片是由 Provenance 派生的 Publish View，不属于忠实转写正文，也不参与 Visible Text / Structure Fidelity 比较。它只显示用户可理解的最小信息，不显示原始绝对路径、内部 Locator、Digest 或未经核实的官方身份。完整 Traceability 留在 Workspace。

## 10. Publish Manifest Ownership

`_lorebuddy/publish-manifest.json` 至少包含：

- Schema / Profile ID；
- 确定性的 `build_id`，由规范输入摘要导出；
- Package ID / Version；
- 发布子目录相对路径；
- Renderer ID / Version / Digest；
- 按 Path UTF-8 bytes 排序的 `{path,size,sha256,role,owner_id}`；
- 文件数量与记录流摘要；
- 前一份 Manifest Digest，首版为 `null`。

Manifest 不含生成时间、设备名、用户名、Vault Root 或其他绝对路径。运行时间只进入 Workspace 日志。

只有上一份有效 Manifest 列出的文件才是 LoreBuddy Owned。新 Manifest 未列出的旧 Owned 文件可以删除；未被拥有的文件不得覆盖或删除。若未拥有文件与候选路径冲突，发布阻塞并请求用户处理。

## 11. 发布前验证

发布器必须按顺序验证：

1. 配置的 Vault Root 存在且是目录；
2. Root 直接包含真实目录 `.obsidian/`；
3. Root、目标和所有现有祖先经过 `realpath` 后仍满足 containment；
4. 目标路径没有 `..`、绝对段或 Symbolic Link；
5. Staging 只含普通目录与普通文件，不含 Symbolic / Hard Link 或特殊文件；
6. YAML Properties 可解析、无重复 Key、符合字段白名单；
7. 所有 Markdown Link、Wikilink 和 Anchor 按当前 View 解析；
8. 所有图片和附件存在且摘要匹配；
9. 文本与 Metadata 不包含宿主绝对路径或 `file://`；
10. 文件名通过跨平台规则；
11. 不存在大小写或 Unicode 规范化冲突；
12. Publish Manifest 与 Staging 实际文件集合完全一致；
13. 当前旧 Manifest 可解析，且待修改/删除集合不超出其所有权；
14. 本地发布锁仍由当前进程持有。

## 12. Dry Run

`dry-run` 在完成全部 Staging 验证后比较候选 Manifest 与当前 Manifest，输出：

- `ADD`；
- `UPDATE`；
- `DELETE_OWNED`；
- `UNCHANGED`；
- `CONFLICT_UNOWNED`；
- `BLOCKED`。

每项只显示 Vault 相对路径和内容摘要，不显示 Vault Root。Dry Run 不创建目录、不写 Manifest、不获取删除权限，也不修改 `.obsidian/`。

## 13. 增量发布与失败恢复

M1 使用 Manifest-last 的本地事务：

1. 以原子创建方式取得 Workspace 本地锁；
2. 为所有待修改或删除的 Owned 文件建立 Workspace 回滚副本；
3. 将新文件复制到目标同目录临时名，`fsync` 后以单文件 Rename 替换；
4. 删除动作先移动到 Workspace 事务备份，不直接销毁；
5. 所有文件成功后，最后原子替换 Publish Manifest；
6. 提交成功后再清理可恢复备份；
7. 任一步失败，按 Journal 恢复旧文件和旧 Manifest。

Manifest 是逻辑提交点。该方案不声称提供跨文件系统或同步服务级全局原子性；M1 的单发布设备假设使其足以验证本地安全。M3 若需要更强一致性，应评估版本目录或平台特定原子目录切换。

不得通过清空发布目录再复制实现更新。优先复用摘要相同文件，只处理 Manifest 差异。

## 14. 本地发布锁

锁文件位于 Workspace `build/locks/obsidian-publish.lock`，使用原子 Exclusive Create。内容可含 PID、进程启动标识、目标配置摘要和非规范时间；这些字段不进入发布产物。

发现已有锁时默认失败。只有确认原进程不存在、锁的目标与当前配置一致并由用户批准后，才能清理 Stale Lock。M1 不实现跨设备锁、Leader Election 或分布式租约。

## 15. 生成内容与用户内容

- `_LoreBuddy-M1` 和未来 `LoreBuddy` 中 Manifest Owned 文件是可重建只读产物；
- 用户重要笔记、Campaign、House Rule 和评论应放在发布目录外，例如 `TRPG Notes/`；
- M1 不阻止用户编辑生成文件，但下一次 Dry Run 必须把摘要漂移报告为 `USER_MODIFIED_OWNED` 并阻塞覆盖，除非用户明确选择丢弃修改；
- 用户创建且未被 Manifest 拥有的文件永不自动删除；
- 双向同步、Annotation Overlay 与用户修改合并进入 Backlog。

## 16. 手工验收

发布器自动检查通过后，用户在当前 Mac 上确认：

1. `Home.md` 和全部样本 Note 可打开；
2. Properties 面板字段数量与值可接受；
3. 内部 Link、Anchor、图片和附件可跳转；
4. 来源卡片不会与正文混淆；
5. 生成目录不会干扰现有 Vault 导航；
6. Dry Run 的变更列表与预期一致；
7. 用户自建文件不会被管理。

随后由用户在至少一个同步设备上执行 [M1 验收标准](acceptance-criteria.md) 的跨设备检查。LoreBuddy 不修改 `.obsidian/`，也不尝试配置同步。
