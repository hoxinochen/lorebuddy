# LoreBuddy M1 Known Limitations

状态：**M1-C2B Release Candidate 基线**

本文件记录 M1 全量 Markdown 构建中已确认但未在当前阶段修复的限制。它区分 Converter 行为、Source Reality 与产品尚未实现能力，不能用来降低 Fidelity 或掩盖转换缺陷。

## 1. 分类规则

| 分类 | 含义 |
|---|---|
| Converter Bug | Source 中存在应保留内容，但转换结果遗漏或错误表达 |
| Source Missing | Source 引用了 Artifact Inventory 中不存在的对象 |
| Source Broken Link | Source Link 或 Anchor 不能解析到真实目标 |
| Missing Asset | Source 引用的本地 Asset 不存在 |
| Navigation Artifact | 页面主要承担章节入口、占位或导航语义 |
| Intentional Blank | Source 正文本身为空 |
| External Reference | Source 依赖未摄取的网络资源 |
| Metric Artifact | 自动 Fidelity 指标因转义或表达差异产生假阳性 |
| Unknown | 现有证据不足以分类 |

## 2. 已确认限制

| ID | 分类 | 范围 | Fidelity 影响 | Publisher 影响 | Fragment / Knowledge Layer 影响 | Release |
|---|---|---:|---|---|---|---|
| `M1-LIM-004` | Metric Artifact | 6 Entries | 无已证实内容损失 | 不阻断 | 不阻断 | Accepted Limitation |
| `M1-LIM-005` | Navigation Artifact / Source Reality | 74 Entries | 无；自动保留率均为 `1.000` | 不阻断 | 后续应避免机械拆成知识节点 | Accepted Limitation |
| `M1-LIM-006` | Intentional Blank | 1 Entry | 无；Source 正文为空 | 不阻断 | 不应生成 Fragment / Node | Accepted Limitation |
| `M1-LIM-007` | Source Missing / Source Broken Link | 4,403 occurrences | 不影响正文；目标不可用 | 不阻断 Baseline Publisher | 阻断对应 Link Relationship | Accepted Limitation |
| `M1-LIM-008` | Source Broken Link | 135 Anchor occurrences | 不影响正文；Anchor 不存在 | 不阻断 Baseline Publisher | 阻断对应 Address Mapping | Accepted Limitation |
| `M1-LIM-009` | Missing Asset | 134 occurrences | Source 无可保留 Asset 字节 | 不阻断，但页面缺图 | 阻断对应 Asset Mapping | Accepted Limitation |
| `M1-LIM-010` | External Reference | 38 occurrences | 离线构建不含远程图片 | 不阻断，但离线不可见 | 外部资源摄取前不建立 Asset 事实 | Accepted Limitation |

当前 `Unknown`：0。

## 3. 已闭合的 Converter Bug

### M1-LIM-001：实质正文被误判为导航噪声

- Entry ID：`urn:uuid:6c10dc44-6949-5d92-884f-ca5deab978d4`
- Source Path：`斯翠海文：混沌研习/玩家选项/法术.html`
- 输出：`markdown/法术--6c10dc44.md`
- 原因：Source 将完整法术说明与表格放在 `div#winchm_template_top`；现有噪声规则删除整个节点。
- 结果：Source 有实质正文，Markdown 只有标题。
- 修复：仅在页面存在独立 `winchm_template_content` 时把顶层容器视为模板头；该页正文已恢复。
- 状态：已闭合，不再是 Known Limitation。

### M1-LIM-002：Table Caption 遗漏

- 范围：`珊娜萨的万事指南/角色姓名/` 页面族中的 56 个低保留率 Entry。
- 代表 Entry：`urn:uuid:777bd86e-998f-538a-9e46-c67bd4ec0ad2`
- 代表 Source Path：`珊娜萨的万事指南/角色姓名/灰矮人氏族名.htm`
- 原因：Table 转换保留 `tr` / `th` / `td`，但没有输出 `<caption>`。
- 结果：姓名行完整保留，但诸如 `Dwarf Names | Duergar Clan` 的 Caption 丢失。
- 修复：非空可见 Caption 在对应 Table 前忠实输出一次；56 个 Entry 已逐一验证。
- 状态：已闭合，不再是 Known Limitation。

### M1-LIM-003：嵌套 List 遗漏

- Entry ID：`urn:uuid:7a7e28c0-1de3-5edb-9457-5c226d887324`
- Source Path：`珊娜萨的万事指南/地下城主工具/奖励魔法物品/奖励魔法物品.html`
- 原因：外层 `UL` 直接包含内层 `UL`，当前 List Renderer 只处理直接 `LI`，没有继续消费该嵌套结构。
- 遗漏：挑战等级 `0–4`、`5–10`、`11–16`、`17+` 的四条骰次说明。
- 修复：继续遍历缺少父 `LI` 的直接嵌套 List；四条说明按原顺序各保留一次。
- 状态：已闭合，不再是 Known Limitation。

## 4. 低保留率候选的结论

修复前的 63 个候选已按页面族和缺失片段检查：

- 56 个姓名表已恢复 Caption；
- 1 个奖励魔法物品页已恢复嵌套 List；
- 6 个复杂 HTML 页面：正文仍存在于最小 HTML 中，`'` 等字符被编码为 HTML Entity，原始 Exact-Match 指标产生假阳性，对应 `M1-LIM-004`。

修复后只剩 6 个 Metric Artifact，包括两个法术速查表及四个复杂表格页面。对 Markdown 做 HTML Entity 还原并忽略空白后，这 6 页的候选文本保留率为 `1.000`。本结论只用于 Release Gate 分类，不修改报告算法或 Validator。

## 5. 74 个极短正文候选的结论

- 74 页现有自动文本保留率全部为 `1.000`；
- 没有页面触发导航噪声删除；
- 包含明确的“暂未收录”占位页、章节入口、短介绍和 Source 本身很短的内容。

这些页面属于 Navigation Artifact 或 Source Reality。Publisher 可以发布；Knowledge Layer 不应仅因存在 Markdown 就自动把它们提升为独立 Knowledge Node。

## 6. 零正文候选的结论

| Entry | 结论 |
|---|---|
| `空白页模板/纯空白页模板.htm` | Source Body 为空，Intentional Blank，允许进入 Baseline Archive |

`斯翠海文：混沌研习/玩家选项/法术.html` 的实质正文已恢复，不再属于零正文候选。

## 7. Accepted Limitation 原则

Accepted Limitation 必须满足：

1. 不是未修复的 Converter Bug；
2. 不伪造不存在的 Link、Anchor 或 Asset；
3. Source Reality 在报告中可追溯；
4. Publisher 能保持限制可见；
5. 不把缺失内容提升为 Knowledge Layer 事实。

当前活跃限制均满足以上条件。`M1-LIM-001` 至 `M1-LIM-003` 已通过代码修复和真实全量验证闭合，不是被产品策略豁免。
