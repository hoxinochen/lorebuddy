# Milestone 1-A：Executable Foundation

状态：Implementation Complete / 待确认  
实施 Profile：`m1-profile@0.1.0`  
代码版本：`0.1.0.dev0`

## 1. 目标

M1-A 把 M1 的最小数据合同转化为可执行基础设施，为后续受限摄取和样本验证提供稳定边界。本阶段不读取真实 CHM、不建立正式 Package、不生成 Knowledge Node，也不访问 Obsidian Vault。

采用模块化 Python Package，而不是一次性脚本，原因是 Registry、验证、身份、Slug 和配置会被 M1-B / M1-C 共同复用。替代方案是先写一个转换脚本，但它会在 Schema 尚未可执行时把临时数据形状固化，并混合摄取与验证职责。

## 2. 交付物

```text
src/lorebuddy/
    cli.py
    config.py
    ids.py
    slugs.py
    registry/schema_registry.py
    validation/result.py
    validation/schema_validator.py

schemas/
    registry.yaml
    *.schema.json

fixtures/m1a/
    valid/
    invalid/

tests/
    test_*.py
```

项目使用 `pyproject.toml` 声明 Python 3.11+、`jsonschema`、`PyYAML` 和开发依赖 `pytest`。CLI 使用标准库 `argparse`，没有引入 Web、数据库、异步、插件或 Obsidian API。

## 3. Schema 清单

| Schema ID | Registry 状态 | M1-A 职责 |
|---|---|---|
| `core.package-manifest@0.1.0` | active | 受限 Package 最小身份和生命周期 |
| `core.source-artifact@0.1.0` | active | 不可变摄取容器事实 |
| `core.source-entry@0.1.0` | active | Artifact 内 Entry 清单记录 |
| `core.source-fragment@0.1.0` | experimental | 基础 Provenance 片段和 Locator |
| `core.knowledge-node@0.1.0` | experimental | 最小 Knowledge Node Envelope |
| `core.source-mapping@0.1.0` | experimental | Entry / Fragment 到 Work / Edition Claim |
| `core.boundary-record@0.1.0` | experimental | 边界候选与人工决定 |
| `core.relationship@0.1.0` | experimental | 稳定单向关系断言 |

`active` 表示 M1-A 数据边界已足以支撑下一阶段基础摄取；`experimental` 表示字段仍需 5～10 个样本验证。两种状态都不代表 Public Release 稳定性。

所有 Schema 使用 JSON Schema Draft 2020-12，明确 `$id`、`title`、`type`、`required` 和 `additionalProperties: false`。扩展只允许进入显式 `extensions` 命名空间。Rights Authority、Claim Lineage、Release Rights Binding、Public Attestation 和完整 Fidelity Coverage Map 没有进入 Schema。

## 4. Registry 规则

`schemas/registry.yaml` 是 Schema ID 到文件的唯一 M1-A 映射，记录 Version、Path、Status、Profile 和 Description。

加载时必须验证：

1. Registry 文件和 `schemas` 数组存在；
2. 每条记录字段集合精确；
3. Schema ID 唯一；
4. 状态属于 `active | experimental | deprecated`；
5. Path 不逃逸 `schemas/`；
6. Schema 文件存在且为 JSON Object；
7. 文件 `$id`、Version、Profile 与 Registry 相等；
8. Schema 本身通过 Draft 2020-12 Meta-Schema 检查。

Registry 损坏会抛出明确错误，不回退到目录扫描或猜测 Schema。

## 5. Fixture 规则

每个 Schema 有一个合法和一个非法 JSON Fixture，共 16 个。Fixture 全部使用虚构内容，不含真实 CHM 文本、路径或摘要。

非法 Fixture 分别覆盖：

- 缺少 Package ID；
- 非法 Artifact Digest；
- Entry Storage Path 穿越；
- Fragment Locator 不完整；
- Knowledge Node 未定义字段；
- Source Mapping 不支持的状态；
- Approved Boundary 缺少 Node / Reviewer ID；
- Relationship Target 不完整。

Fixture 的 `schema` 字段用于批量验证时选择 Registry ID。批量命令要求合法目录全部通过、非法目录全部失败；“非法 Fixture 因另一个非预期错误失败”仍应由单元测试的路径断言补充约束。

## 6. Validator

统一 Validator 支持 JSON 和 YAML：

- 按 Schema ID 从 Registry 加载；
- 拒绝 JSON / YAML 重复 Key；
- 返回 `valid`、`schema_id`、`errors[]`、`file`、`summary`；
- Error 包含 JSON Pointer Path、稳定 Code、Message 和 Validator 类型；
- 未知 Schema ID 返回 `UNKNOWN_SCHEMA`；
- 文档读取失败返回 `DOCUMENT_LOAD_ERROR`；
- Registry / Schema 损坏不会被当成普通数据错误吞掉。

M1-A 只做单 Record Schema Validation。跨 Record 唯一性、引用存在性、`end > start`、Digest 重算和完整 Traceability 属于后续语义 Validator。

## 7. 稳定 ID

`stable_id(kind, natural_key)` 使用固定 LoreBuddy Namespace 和 UUIDv5，从显式、不透明的输入确定性派生 UUID URN。相同输入得到相同 ID，不同类型通过 `kind` 隔离。

UUIDv5 是 M1-A 的基础设施选择，不取代 D-004 对最终语义身份的样本验证。未来正式 Node 可以在 Boundary Approval 时分配 UUIDv7；M1-A 派生 ID 主要适用于可重建候选和基础记录。标题、Slug、文件路径和正文摘要不得作为未声明的自然键。

`short_id` 从 UUID Hex 确定性取得前缀，并提供批量冲突检测。Short ID 只用于文件名消歧，不承担身份。

## 8. Slug

Slug 工具执行 NFC、Case Fold、空格/标点清理、Windows 保留名防护、尾随空格/句点清理、长度限制、空值回退和 Short ID 消歧。

M1 Obsidian Profile 要求 ASCII Lowercase Slug，因此 M1-A 不引入拼音或 Transliteration 依赖。英文标题保留可读 Slug；纯中文标题安全回退为 `node--<short-id>.md`。这牺牲部分文件名可读性，但避免拼音库版本改变路径。M1 样本阶段需要决定是否接受该体验，或采用人工批准并持久化的 ASCII Slug。

## 9. 本地配置

`config.local.toml.example` 只包含通用占位路径。真实 `config.local.toml` 已被 `.gitignore` 排除。

配置读取支持：

- `[obsidian]` 与 `[build]` 必需 Table；
- `LOREBUDDY_OBSIDIAN_VAULT` 覆盖 `vault_root`；
- Vault Root 必须为绝对路径；
- 发布子目录和 Staging Root 必须为无 `..` 的相对路径；
- 清晰的缺失和 TOML 错误。

`config check` 只验证语法和路径形状，不调用 `exists()`、`realpath()` 或读取 `.obsidian/`，因此 M1-A 不访问真实 Vault。

## 10. CLI

可用命令：

```text
lorebuddy schemas list
lorebuddy schemas validate <schema-id> <file>
lorebuddy fixtures validate
lorebuddy config check
```

示例：

```shell
.venv/bin/lorebuddy schemas list
.venv/bin/lorebuddy schemas validate core.source-entry@0.1.0 fixtures/m1a/valid/entry.json
.venv/bin/lorebuddy fixtures validate
```

数据验证失败退出 `1`；Registry / Config 基础设施错误退出 `2`；成功退出 `0`。`ingest`、`unpack`、`convert`、`publish` 等命令没有注册，调用时由 `argparse` 以非零状态拒绝。

## 11. 测试

使用隔离 Python 3.12 环境：

```shell
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

当前自动测试共 34 项，覆盖 Registry、全部 Fixture、错误路径、重复 YAML Key、未知 Schema、ID 确定性与冲突、Slug 跨平台规则、配置缺失/覆盖/路径穿越、CLI 退出码和未实现命令。

测试只使用仓库内虚构 Fixture 和 pytest 临时目录，不读取 CHM、不访问 Vault、不依赖网络。首次安装依赖可能需要访问 Python Package Index；测试运行本身不需要网络。

## 12. 已知限制

- 没有依赖 Lockfile；`pyproject.toml` 使用受控版本范围，锁定策略在进入可复现构建前确认；
- 系统默认 Python 可能低于 3.11，必须使用符合 `pyproject.toml` 的隔离环境；
- 部分 macOS 环境可能把 editable install 生成的 `.pth` 标记为 hidden，导致 Python 3.12 跳过该路径；出现时应重建环境或清除该本地文件标志，该问题不进入仓库产物；
- JSON Schema 不能替代跨 Record 语义验证；
- `Fragment.locator.end > start` 尚未由自定义 Validator 检查；
- UUIDv5 / UUIDv7 的最终适用边界仍需 M1 样本验证；
- 中文 Slug 当前采用安全回退，阅读体验未验证；
- Config Check 不验证 Vault 存在或 `.obsidian/`，该检查只允许在未来发布阶段启用；
- 没有 Package Lock、Content Manifest、Fidelity Coverage Map、Rights 或 Release 实现。

## 13. M1-B 依赖项

进入 M1-B 前必须确认：

1. 8 个 Schema 的最小字段能承载受限 Acquisition Package；
2. Registry ID 和 Profile Version 不再改名；
3. Entry Storage Path 与原始路径字段的分工；
4. UUIDv5 适用对象与 UUIDv7 分配时点；
5. 下一阶段只做 Acquire、Inventory、Preserve Source，不生成 Knowledge Node；
6. 新增语义 Validator 的明确范围。

M1 Implementation Profile 要求 Package Lock，但 M1-A 明确只实现上述 8 个 Schema，因此 Package Lock 延至后续 M1 子阶段。这是子阶段裁剪，不是删除 M0 能力。

## 14. 明确未实现

- 真实 CHM 打开、解包、解析或摘要读取；
- 正式 Package、Artifact、Entry Inventory 或 Source 字节写出；
- Boundary Candidate 生成或人工审核 UI；
- Knowledge Node、Index 或 Fidelity 生成；
- Obsidian Staging、Dry Run、Publisher、Manifest Ownership 或 Vault 写入；
- Rights、Public Release、Runtime、RAG、Embedding、Campaign 或同步。

M1-A 完成后必须停止，等待确认，不能自动进入 M1-B。
