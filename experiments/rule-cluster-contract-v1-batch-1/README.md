# 规则簇合同v1首批

已批准合同的八对象数据生产和P5消费验证完成；Buddy复核首轮/最终48题通过，用户已确认P6通过，本批内部候选接纳完成。完整结果见[生产报告](../../docs/milestone-2/rule-cluster-contract-v1-batch-1-report-2026-10-26.md)。

- [完整规则簇](input/完整规则簇.md)：八对象45能力、11法术和六份公共规则全文。
- [全部题面](input/测试题.md)：24道回归＋24道新题；现场事实见同目录两个questions JSON。
- [格式与交接](FORMAT.md)：字段状态、施法本体/调用方覆盖、拥有者修正、兼容和消费要求。
- `input/`仅供消费者；`schemas/`和本格式说明供接入实现。`evaluator/`与含答案的`prepare_questions.py`不得送入消费工作进程。
- `intake.json`固定来源集合和工具；`migration.json`说明旧题/请求范围迁移，原Gold保持。

在LoreBuddy仓库根目录执行：

```sh
.venv/bin/python experiments/rule-cluster-contract-v1-batch-1/produce.py
.venv/bin/python experiments/rule-cluster-contract-v1-batch-1/prepare_questions.py
.venv/bin/python experiments/rule-cluster-contract-v1-batch-1/validate.py
.venv/bin/python experiments/rule-cluster-contract-v1-batch-1/check_rebuild.py
```

`probe-consumer.mjs`与其报告是适配前旧消费者拒绝新格式的历史证据，当前入口已升级，不再把该探测列为当前验证命令。

核对已收到的消费输出：

```sh
.venv/bin/python experiments/rule-cluster-contract-v1-batch-1/verify_consumer_receipt.py
```

脚本读取Terminal已封存证据及隔离Gold进行评分，不再次执行消费者。当前收据见[consumer-receipt.json](reports/consumer-receipt.json)；生产阶段的issues/兼容报告和输入中Pending声明保持历史字节，后续状态由此收据承接。

重建依赖intake中列出的本地来源及旧候选，不联网抓取最新资料。迁移到其他机器须同时保留受限来源/旧批次或可解析的授权位置；不是只搬脚本就可重建。

P6用户决定见[batch-acceptance.json](reports/batch-acceptance.json)，承接P5收据中的历史Pending；对象仍candidate，正式规则批准另行审核。
