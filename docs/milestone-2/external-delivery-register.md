# M2 外部交付登记

状态：**pending_acceptance**

## D-2026-09-04-antigravity-book-catalog

| 字段 | 当前登记 |
|---|---|
| 提供方 | Antigravity |
| 交付物 | Book Catalog、Entry-to-Book Mapping、Ruleset Profiles、Review Queue、统计报表 |
| 交付标识 | `antigravity-book-catalog@2026-09-04` |
| 声明覆盖 | 6,819 M1-C3 Entry；6,808 映射；11 条隔离队列；92 本候选书籍/独立来源 |
| 当前用途 | M2-A 接纳候选；不得直接作为批准规则、出版身份、Rights 结论或 DND Terminal 输入 |
| 输入身份 | 待提交 M1-C3 Publisher Manifest 摘要与交付文件摘要后锁定 |
| 接纳状态 | `externally_implemented_pending_acceptance` |

交付的逻辑路径为 `lorebuddy-规则书/01-规则集画像与书籍归属/`；该位置属于用户提供的
外部工作区，不是 LoreBuddy 仓库内的事实源。本项目不通过本登记复制或收纳其规则正文。

## 接纳工作

1. 由 Codex 对照锁定的 M1-C3 Manifest 复算集合闭合和路径一致性；
2. Antigravity 提供生成器版本、运行参数、输入 Manifest 摘要及每个交付文件摘要；
3. 将 `authority` 等路径分类字段降为 `claimed` 的来源身份信息，除非另有审核证据；
4. 为每条映射补充或可确定性重建 `mapping_basis`；
5. 通过后在本文件追加接纳结论；失败项仅进入 Review Queue，不回写 M1 Source。
