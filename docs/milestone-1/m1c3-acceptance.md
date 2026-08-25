# M1-C3 人工验收记录

状态：**ACCEPTED**

## 验收结论

用户已完成 Obsidian Baseline Vault 的人工浏览，并确认当前未发现需要继续阻断
M1-C3 的目录、命名或导航问题。

人工验收期间发现并修复：

- 正文目录过于扁平；
- 正文文件名普遍附带短 Entry ID；
- HHC 纯目录节点未完整投影；
- 多导航 Entry 的正文主位置误选；
- “拳斗士/拳斗士”等连续同名父节点与正文节点未忠实呈现。

修正版仍保持一个物理 Entry 只生成一份正文，其他 HHC 位置只链接该正文。

## 自动验收基线

- Note：6,819；
- Asset：104；
- HHC Navigation Node：8,187；
- Books 分层导航索引：1,489；
- Publisher 受控文件：8,427；
- M1-C3 Tree SHA-256：
  `23bae8563e51a0a5db4b2b070fccc4483c31f531a1e460c50322c8f6042a9488`；
- 两份独立构建完整目录零差异；
- 未打开的重跑基线通过 Publisher Validator。

## 打开后本机文件

用户打开首份 Baseline 后，macOS 在输出根目录增加了 `.DS_Store`。该文件不是
Publisher 产物，也未进入 Ownership Manifest，因此严格 Validator 会对这份已打开
副本报告 Ownership Closure 和非 UTF-8 错误。

这不表示 Publisher 正文或 Manifest 发生变化。最终自动验收使用未附加该系统文件的
独立重跑基线。LoreBuddy 不把 `.DS_Store` 纳入所有权，也不在本次收口中静默删除
用户环境产生的文件。

## 退出结论

M1-C3 人工验收与自动验收均已完成，阶段结论为 **PASS**。本记录不授权 M2，
也不改变 Source Reality 与 Known Limitations。
