# 完整规则簇计算器消费试验

状态：材料生产与装配检查完成，计算器消费Not Run。范围与评分见[本批约定](../../docs/milestone-2/full-cluster-calculator-pilot-2026-10-23.md)。

- 人类先读：[完整规则簇](input/完整规则簇.md)、[24道测试题](input/测试题.md)。
- 消费者只读：`input/knowledge.json`完整语料与`input/questions.json`现场题目；每题共用同一完整语料。
- 评分端另读：`evaluator/gold.json`；禁止向消费者提供答案、题型分类或预期处理结果。
- 材料核查：`reports/material-audit.json`。

这里没有逐题request/context。入口若不会读本格式，应记录读取能力缺失，不手工装配后声称通过。

重新生产：`python3 experiments/full-cluster-calculator-pilot/produce.py`。依赖原有本地build候选和来源，迁移脚本不等于迁移全部重建输入。

装配核查：`python3 experiments/full-cluster-calculator-pilot/verify.py`。不调用计算器或模型；五项错误注入只在内存中修改副本，不改交付材料。
