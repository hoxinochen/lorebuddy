# 计算器能力测试样本

仅研究样本；已准备，尚未运行计算器。完整范围、评分、耗时口径和限制见[样本约定](../../docs/milestone-2/calculator-capability-benchmark-2026-10-23.md)。

- `input/`：题面、规则证据、逐题request/context。
- `evaluator/`：Gold、历史答卷及结果空表，**不得传给计算器**。
- `prepare.py`：从本地既有研究材料装配本组样本，不调用计算器或LLM。重建依赖文中所列本地build工件，跨机器仅迁移脚本不足以重建。

未来执行时只向待测核心传入当前题的request/context；先留存输出，再由评分侧读取Gold。不要将整个目录作为模型或工具输入。
