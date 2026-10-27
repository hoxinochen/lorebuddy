# 八对象正式化补齐工作区

用户于2026-10-26授权“正式补齐”。本目录完成本批正式审核材料的装配与验证，**尚未完成正式规则批准或正式转写节点激活**。原P6已接纳交付保持不变。

- [审核入口](review-bundle/REVIEW.md)：70对象原文、结构记录、拥有者与3项采用决定。
- [输入及文件锁](review-bundle/intake.json)：完整输入、P6决定、生成器/验证器/规范锁与全部文件清单。
- [审核队列](review-bundle/metadata/review-queue.json)：每个对象绑定其独立审核记录。
- [包边界提案](review-bundle/metadata/package-plan.json)：audit、common、spells、creatures；不是已发布Package。
- [真实未完成项](review-bundle/metadata/issues/open.json)：审核、claimed映射、规范保真及包策略；不能删掉后冒称通过。
- [验证结果](reports/validation.json)：完整集合、来源/派生坐标、原有254抽取/调用约束、重建及9项错误注入。
- [范围、设计及正式化差距报告](../../docs/milestone-2/rule-cluster-formalization-batch-1-2026-10-26.md)。

从LoreBuddy根目录运行：

```sh
.venv/bin/python experiments/rule-cluster-formalization-batch-1/build.py
.venv/bin/python experiments/rule-cluster-formalization-batch-1/validate.py
```

生成器仅写本工作区，不调用消费者、LLM或联网资源，不改原始Source、M1、P6语料、Gold、Terminal或Campaign。审核正文副本逐字节保持来源Note选段；完整共享Note包含原Front Matter，这是完整来源参考，不是已经通过忠实转写保真的正式原子节点。

`schemas/`四份M2局部审核Schema只描述待审结构。不能把Schema通过当内容批准，不能把whole-entry原始字节Fragment当作规范Source Structure Event Stream或Full Fidelity证明。当前尚无可发布的正式规则包，不能向Terminal发出“正式替换”指令。
