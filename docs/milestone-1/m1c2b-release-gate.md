# M1-C2B：Release Gate & Product Baseline

状态：**Release Gate 已通过**

## 1. Gate 对象

- Artifact ID：`urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408`
- 输入根：`build/m1c2a-full/`
- Manifest：`markdown-manifest.jsonl`
- Markdown：6,819
- Asset：104
- 两次独立构建：完整目录零差异
- M1-C2A Validator：两次均通过

本 Gate 评估修复后的全量构建是否可作为 M1-C3 Publisher Release Candidate。修复只涉及三个已确认的 Converter Bug 家族，没有修改 Source、Validator、Manifest 契约或输出布局。

## 2. 工程分类

| 分类 | 是否属于 Converter | 是否属于 Source | 阻断 Publisher | 阻断 Knowledge Layer | 建议未来修复 | Accepted Limitation |
|---|---|---|---|---|---|---|
| Converter Bug | 是 | 否 | 是 | 是，至少阻断受影响 Entry | 是，进入 M1-C3 前 | 否 |
| Source Missing | 否 | 是 | 否 | 只阻断对应引用 | 有新 Source 时处理 | 是 |
| Source Broken Link | 否 | 是 | 否 | 只阻断对应 Link / Address | 可按使用价值处理 | 是 |
| Missing Asset | 否 | 是 | 否，但页面缺图 | 只阻断对应 Asset Mapping | 有来源时摄取 | 是 |
| Navigation Artifact | 否 | 是 | 否 | 不应自动生成 Node | 不建议改写正文 | 是 |
| Intentional Blank | 否 | 是 | 否 | 不生成 Fragment / Node | 否 | 是 |
| External Reference | 否 | 是 | 否，但离线不可见 | 摄取前不建立 Asset 事实 | 可选单独摄取 | 是 |
| Metric Artifact | 否 | 否 | 否 | 否 | 未来改善报告算法 | 是 |
| Unknown | 未知 | 未知 | 默认阻断 | 默认阻断 | 先调查 | 否 |

具体限制和证据见 [LoreBuddy M1 Known Limitations](m1-known-limitations.md)。

## 3. Release Checklist

| Gate | 结果 | 证据 |
|---|---|---|
| Deterministic Build | PASS | 两次独立构建完整目录零差异 |
| Validator | PASS | 两份构建均 `valid: true` |
| Manifest | PASS | 6,819 个唯一 Entry 与 6,819 份 Markdown 闭合 |
| Source Path | PASS | Front Matter、Manifest 与 M1-B `Entry.original_path` 一致 |
| Navigation Path | PASS | HHC 顺序与一对多关系保留，不复制正文 |
| Assets | PASS WITH LIMITATIONS | 104 个本地 Asset 已校验；134 个缺失、38 个外部引用已报告 |
| Reports | PASS | Build、Encoding、Fidelity、Link、Asset、Navigation 报告齐全 |
| Known Limitations | PASS | 活跃限制只包含 Source Reality、Intentional Blank、External Reference 与 Metric Artifact |
| Converter Fidelity | PASS | 58 个受影响 Entry 全部闭合；无剩余或新增 Converter 异常 |
| 允许进入 M1-C3 | **YES** | Publisher Input Contract 成立 |

## 4. Release Decision

M1-C2A 当前构建正式标记为 M1-C3 Publisher Release Candidate。

三个原阻断 Bug 家族均已局部修复：

1. `winchm_template_top` 只在存在独立 `winchm_template_content` 时作为模板头整体删除；不存在独立正文容器时保留其内容，内部已知模板子节点仍独立清理；
2. 非空可见 `<caption>` 在对应 Markdown 或最小 HTML Table 前输出一次，空 Caption 不生成正文；
3. 缺少父 `LI` 的直接嵌套 List 按当前层级继续遍历，正常 `LI` 下的嵌套层级保持不变。

机器复核结果：

- 原受影响 Entry：58；
- 已修复：58；
- 仍异常：0；
- 新异常：0；
- 低保留率候选：6，均为既有 Metric Artifact；
- 极短正文：74，保留率均为 `1.000`；
- 零正文：1，仅 `空白页模板/纯空白页模板.htm`。

两次独立真实全量构建均为 6,819 成功、0 失败，Validator 均通过，完整目录零差异。4,403 个缺失目标、135 个缺失 Anchor、134 个缺失 Asset 和 38 个 External Reference 保持为已报告的 Accepted Limitation。

## 5. 验证证据

- 回归 Fixture：`fixtures/m1c2b/substantive-template-top.html`、`template-top-with-content.html`、`table-caption.html`、`nested-list.html`；
- 自动测试：69 项全部通过；
- 依赖检查：`pip check` 通过；
- 定向真实验证：“法术”正文恢复；代表姓名表 Caption 恢复且只生成一次；“奖励魔法物品”四条说明按顺序各生成一次；标准 WinCHM 模板页眉未重新进入 Markdown；
- 机器复核：56 个 Caption Entry、1 个正文误删 Entry、1 个嵌套 List Entry，共 58 个全部修复；
- 机器复核产物：`build/m1c2b-remediation-review.json`，属于 Git 忽略的本地 Gate 报告；
- 两次真实全量构建分别消费两份独立 M1-B 摄取产物，完整目录零差异。

## 6. M1-C3 Publisher Input Contract

该 Contract 已生效。Publisher 不依赖 Acquisition 目录、CHM、Release Gate 文档、进程缓存、当前工作目录或其他隐式状态，只消费一个显式传入的 M1-C2A Build Root。Release Gate 负责授权哪个 Build Root 可以交给 Publisher，但不是 Publisher 的运行时输入。

### Required Input

```text
<build-root>/
├── .lorebuddy-m1c2a.json
├── README.md
├── markdown-manifest.jsonl
├── markdown/
├── assets/
└── reports/
    ├── entries.jsonl
    ├── build-report.json
    ├── encoding-report.json
    ├── fidelity-report.json
    ├── link-report.json
    ├── asset-report.json
    └── navigation-report.json
```

### Preconditions

1. `.lorebuddy-m1c2a.json` 的 Artifact ID 与 Manifest 一致；
2. `lorebuddy markdown validate <build-root>` 返回成功；
3. Manifest 中每个 Entry ID 唯一，每个 `output_path` 唯一；
4. Manifest 与 `markdown/`、`assets/` 闭合。

### Publisher Consumption Rules

- 逐行读取 `markdown-manifest.jsonl`，不得扫描文件名推断身份；
- 以 `entry_id` 作为发布身份，以 `output_path` 定位正文；
- 保留 `source_path`，不得用 Navigation Path 替代；
- 保留 `navigation_paths` 的顺序和一对多关系；
- 只复制 Manifest / Asset Report 声明的文件；
- 可为 Vault 重新规划目录，但必须确定性重写受影响的相对 Link / Image；
- 不按多个 Navigation Path 复制正文；
- 未解析引用保持报告状态，不生成伪目标；
- Publisher 自己生成的 Ownership Manifest 与 M1-C2A `markdown-manifest.jsonl` 分离；
- 不读取或写入 M1-C2A Build Root 之外的隐式输入。

## 7. 当前结论

- M1-C2B Fidelity Remediation 与工程分类完成；
- 58 个受影响 Entry 全部闭合；
- Known Limitations 只保留可接受项；
- Publisher Input Contract 已定义；
- Release Gate：**PASS**；
- M1-C3 Ready：**YES**；
- 下一步可以按独立 Prompt 开始最小 Obsidian Baseline Publisher，但本轮未开始实现。
