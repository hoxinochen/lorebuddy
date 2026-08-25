# M1-C4：GPT Project Export

状态：**实现、检索路由优化与自动验收完成**

## 1. 目标

把已通过 Validator 的 M1-C3 Obsidian Baseline 转换成低文件数、适合上传到
ChatGPT Project 的只读 Markdown 资料，同时给用户后续上传其他文件保留名额。

该导出是产品视图，不是 Fragment、Knowledge Node、Library、RAG 或向量数据库。

## 2. 输入合同

唯一输入是显式传入且通过 M1-C3 Validator 的 Baseline Root。导出器只读取：

- `.lorebuddy/publish-report.json`；
- `.lorebuddy/publisher-manifest.jsonl`；
- Manifest 声明的 6,819 份 `Notes/` 正文。

不读取 CHM、M1-B、M1-C2A、Obsidian Vault、本地配置或当前目录中的隐式文件。

## 3. 文件预算

当前 Profile 固定：

- 上传文件最多 20 个；
- 控制文件 2 个；
- 内容包最多 18 个；
- 每个内容包最多 1,950,000 UTF-8 bytes。

实际导出恰好 20 个文件：`00-README.md`、`01-CONTENTS.md` 和 18 个内容包。
在 40 文件 Project 中保留 20 个位置，在 25 文件 Project 中保留 5 个位置。
文件与 Token 限制可能由产品套餐调整，因此上传前仍应以当前 ChatGPT 界面为准。

字节预算是保守的本地预检，不冒充精确 Token Count。当前没有新增 Tokenizer
依赖。

## 4. 内容语义

- 每个 M1-C3 Note 的原始 UTF-8 字节完整嵌入一次；
- Note 自身的 Front Matter 继续保存 Entry ID、物理 `source_path`、
  `navigation_paths` 和来源摘要；
- 内容包边界只记录 Entry ID 和原 Note 字节长度；
- 不总结、改写、语义切分或合并 Entry；
- 不复制 Books 导航索引、Reports 或图片二进制；
- 原相对链接保留为来源文本，但合并内容包后不承诺可点击；
- 这是受限本地导出，不表示允许公开或再分发。

每个内容包开头增加由 Publisher 输出路径确定性生成的内容导航：

- 顶层来源及 Entry 数；
- 每个来源的主要导航主题；
- 高频 Navigation 组件；
- 只检索当前问题直接相关 Entry 的节制说明。

`01-CONTENTS.md` 提供角色创建、通用规则、法术与能力、怪物与遭遇、
DM / 冒险准备和版本比较的全局路由。`00-README.md` 与每个内容包同时声明：
同一规则存在明确新旧版本时默认采用最新适用版本；旧版只用于新版缺项、
历史比较或用户明确指定的旧版 Campaign；第三方和 Homebrew 不按日期自动
覆盖官方规则。

上述说明完全由路径、标题和计数机械派生，不总结或解释官方正文。

优先按 M1-C3 规范输出路径连续装箱；若连续装箱超过文件预算，则使用稳定的
Best Fit Decreasing 分配，并在每个内容包内恢复规范路径顺序。该策略只影响
Entry 所在内容包，不改变身份和正文。

## 5. CLI

```bash
PYTHONPATH=src .venv/bin/python -m lorebuddy.cli gpt-export build \
  build/m1c3-obsidian-baseline-rerun \
  --output build/lorebuddy-gpt-project-routed \
  --json

PYTHONPATH=src .venv/bin/python -m lorebuddy.cli gpt-export validate \
  build/m1c3-obsidian-baseline-rerun \
  build/lorebuddy-gpt-project-routed \
  --json
```

## 6. Validator

Validator 对照显式 M1-C3 输入检查：

- Export Marker 与 Artifact / Publisher Manifest 身份一致；
- 文件数量与单包字节预算；
- 仅存在 2 个控制文件和声明格式的内容包；
- 6,819 个 Entry 恰好各出现一次；
- 每份嵌入 Note 与 M1-C3 原字节一致；
- UTF-8；
- 不包含私人绝对路径；
- 不接受 Symbolic Link 或未知额外文件。

## 7. 真实结果

- Artifact ID：`urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408`；
- Entry：6,819；
- Source Note 原字节：33,382,625；
- 内容包：18；
- 控制文件：2；
- 上传文件总数：20；
- 最大内容包：1,943,383 bytes；
- 路由、控制文件和包级内容说明：58,126 bytes；
- 导出 Tree SHA-256：
  `753d24fdaf5a1545df1b4362e2e4aa4978e2750413ac9edd315c2a7b07d21fd2`；
- Publisher Manifest SHA-256：
  `sha256:d9172ac3befdd0be00547d9d72f9f212e2ead8c16412c96b9a155a32adf56458`；
- 两次独立导出均通过 Validator，完整目录零差异。

输出位于 Git 忽略目录：

- `build/lorebuddy-gpt-project-routed/`；
- `build/lorebuddy-gpt-project-routed-rerun/`。
