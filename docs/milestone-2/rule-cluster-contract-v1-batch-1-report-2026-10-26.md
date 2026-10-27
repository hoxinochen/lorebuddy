# 规则簇合同v1首批生产报告

日期：2026-10-26。依据：[已批准合同v1-r1](rule-cluster-production-consumption-contract-v1-2026-10-26.md)。用户授权原话：“批准修改生产”。

**当前结论：P1–P6完成；Buddy已复核Terminal首轮及最终48题输出，用户于2026-10-26确认P6通过，接受本批内部候选。** 未修改Terminal、原始Source、M1、旧候选或历史题目；未调用新LLM、写Campaign、发布或提交。正式合同已生效，但本批知识对象仍为candidate。

## 1. 实际交付

目录：[规则簇合同v1首批](../../experiments/rule-cluster-contract-v1-batch-1/README.md)。

| 项目 | 结果 |
|---|---|
| 完整对象 | 魅魔、梦魔、2025幽魂、火元素、史拉绿蟾、气元素、土元素、盾卫，共8个 |
| 完整能力 | 45项；保留既有ID、全部原文和关键字段，修订提高，不覆盖旧批次 |
| 法术/公共规则 | 11份完整法术、6份公共规则完整Entry；没有按题目裁剪 |
| 来源 | 20份Entry的Note/原HTML与既有收据匹配，94份证据文本和字节范围核验 |
| 字段来源 | 254项逐JSON Pointer的候选结构化抽取；新法术字段另有具体范围和映射规则绑定 |
| 调用契约 | 13项具体法术调用：11项固有调用＋盾卫储存用途两项，参数拥有者明确 |
| 请求输入 | 24题迁移回归＋24道新题，全部显式携带request_scope；原题面/scene/Gold保持 |
| 新题结构 | 18项现有数值机制范围＋6项边界/缺输入/不合法情况 |
| Schema | 两份有限D&D命名空间Schema及跨记录语义核查，不修改平台Core |
| 可重建性 | 临时目录重建12份规范文件，与当前交付逐字节一致 |

入口：

- [完整人类阅读视图](../../experiments/rule-cluster-contract-v1-batch-1/input/完整规则簇.md)。
- [完整机器语料](../../experiments/rule-cluster-contract-v1-batch-1/input/knowledge.json)。
- [48题题面](../../experiments/rule-cluster-contract-v1-batch-1/input/测试题.md)，[回归现场](../../experiments/rule-cluster-contract-v1-batch-1/input/regression-questions.json)、[新增现场](../../experiments/rule-cluster-contract-v1-batch-1/input/new-questions.json)。
- [实际格式与消费交接](../../experiments/rule-cluster-contract-v1-batch-1/FORMAT.md)。
- [材料检查](../../experiments/rule-cluster-contract-v1-batch-1/reports/material-audit.json)、[重建检查](../../experiments/rule-cluster-contract-v1-batch-1/reports/rebuild-check.json)、[来源/工具清单](../../experiments/rule-cluster-contract-v1-batch-1/intake.json)。

## 2. 本次完成的规范化

`request_scope`从临时按题号的范围旁表迁入场景输入；生产API可以直接读取范围字段。旁表原字节作为本批迁移证据冻结，不成为执行时答案或参数查询表。原24题题面、scene逐项相等，原Gold保持，见[migration.json](../../experiments/rule-cluster-contract-v1-batch-1/migration.json)。

法术本体独立维护施法时间、距离、目标规则、V/S/M、材料说明、持续时间、专注、豁免/攻击及升环文本。调用方单独维护豁免成分、环级、目标覆盖、次数和参数归属；没有把免材料改成免专注，或将绿蟾译注升级成采用值。

本体与调用字段区分已知、未说明、需现场提供、仅原文和部分结构化。采用决定只绑真正受影响的参数或身份映射，防止一条勘误看起来修改整个施法契约。复杂效果完整保留但未全部编译，本批不宣称完整施法合法性判定已实现。

新对象引入的拥有者规则也保留为数据：

- 土元素攻城怪物作用于物件/建筑，对构装生物不自动翻倍；攻击能力声明对这一拥有者修正的依赖。
- 气元素旋风保留体型/空间资格、充能范围、推离和倒地，不只留伤害。
- 盾卫拳击保留钝击与力场两个分量；连接保留本护符身份、距离、向上取整转伤；储法保留单槽、原施法者参数与释放消耗。没有把这些机制删掉以适配单类型核心。

新增数值题让三项增量对象都参与真实组合；盾卫既是受击目标，也通过边界题检验混合伤害、转伤和储法。没有为了把盾卫算作“能力内”而只取拳击的一种伤害。新增边界题还检查建筑双倍、超出触及及防御信息缺失。

## 3. 已执行验证

执行命令在[批次README](../../experiments/rule-cluster-contract-v1-batch-1/README.md)，使用项目已有Python/jsonschema依赖，未安装新服务或联网内容。运行结果：

- 两份Draft 2020-12 Schema有效；八对象语料及两个24题集通过结构校验。
- 45项能力身份/原有关键字段、卡文/能力文/法术文、六个公共Entry全文、依赖与归属闭合；源Note/原HTML摘要和94份证据范围匹配。
- 254项逐Pointer值与拥有者字段相等；法术头字段/成分/专注投影与正文一致；调用环级/DC/攻击值/成分覆盖与既有采用一致。
- 旧24题的id、题面、scene保持；scope来自固定r2旁表；原Gold未变。
- 11项错误注入均被拦截：缺未出题能力、缺共享法术、错归属、重复身份、混版、成分覆盖冲突、未知表达、抽取值冲突、缺请求范围、骰果越界、缺现场actor字段。
- 同一来源/工具/人工采用下，临时目录重建12份规范文件字节一致。

这些是结构、来源、迁移和所列语义约束的证据，不是所有自然语言解释都已独立人工验收。Gold由根AI核对来源及固定标准后编写，不是从消费者输出反推。

## 4. 生产交付时的兼容检查及后续状态

新格式为`lorebuddy.dnd2024.rule-cluster-contract-1`。这是显式接口升级：请求范围成为输入，法术本体/调用契约可被消费，拥有者修正及混合分量等语义不可被忽略。它不能冒用旧`research-full-cluster-1`身份。

生产交付时，本会话只读调用当时Terminal `calculator-corpus-1`的加载函数，确认以`unsupported_corpus_environment`安全拒绝新格式，见[兼容探测](../../experiments/rule-cluster-contract-v1-batch-1/reports/consumer-compatibility.json)。没有运行48道场景，也未改写Terminal测试报告。

这与上一轮“没有任何读取入口”不同：读取入口已经存在并验证过旧格式，本次需要它显式接纳新契约及新增条件，不能只改版本白名单后静默忽略新字段。当时默认运行命令仍读取旧五对象/24题，也不能作为本批验收。

| 项目 | 当前状态 | 下一责任 |
|---|---|---|
| P1来源/字段设计 | 完成 | Buddy已交付 |
| P2五对象规范化 | 完成 | Buddy已交付 |
| P3三对象迁移 | 完成 | Buddy已交付 |
| P4生产校验、题目与Gold | 完成 | Buddy已交付 |
| P5新格式读取/绑定及48题数值/边界/耗时 | 完成；首轮与最终均通过，Buddy复核通过 | 收据见§6 |
| P6整批接纳 | 用户已确认通过；内部候选接纳完成 | 决定见§7，不自动扩大下一批或批准正式规则 |

[问题清单](../../experiments/rule-cluster-contract-v1-batch-1/reports/issues.json)列出新消费格式适配及尚未编译的完整施法效果。这是生产时清单；其中消费格式适配现已由§6收据解决，完整施法效果未编译仍保留。未重写准备阶段清单及输入字节，当前状态由后续收据承接。

## 5. 原Terminal交接要求（后续执行见§6）

向Terminal提供本批`input/`、`schemas/`及FORMAT.md，不向消费工作进程提供`evaluator/`、生成Gold的脚本或历史答案。评分阶段才能读取两个Gold文件。

请按Terminal自身有效Design/AMD与授权执行：

1. 新修订显式准入与字段映射；直接读取request_scope，不按题号查范围。
2. 读取本体/调用字段并检查旧投影一致，保留未编译效果；盾卫stored模式不得当固有施法。
3. 对土元素拥有者修正证明适用/不适用；对混合分量、转伤、资源写入维持当前能力边界。不能用只接受新格式名的补丁替代语义接入。
4. 新运行命令接受本批路径和两个题集；同一完整语料执行回归24/新增24，输出分开封存后评分。
5. 报告读取/绑定、18＋18项数值子任务、6＋6项边界及完整耗时；保留所有未执行效果。若接入发现真正数据缺口，给稳定对象ID、字段及来源依据回传Buddy。

本次没有获得跨会话发送消息或Terminal改码授权，因此仅交付可操作交接，不自动调度另一会话。未新建正式Package、正式知识节点或公开Release；来源声明及权利状态保持claimed/unknown。

## 6. P5消费收据复核与P6接纳建议

2026-10-26收到Terminal适配报告后，Buddy读取Authority中的首轮及最终原始输出，直接对照本批固定Gold复核，而非仅复述汇总。见[Buddy消费复核收据](../../experiments/rule-cluster-contract-v1-batch-1/reports/consumer-receipt.json)及[可重跑核对脚本](../../experiments/rule-cluster-contract-v1-batch-1/verify_consumer_receipt.py)。脚本只核对已有证据，不运行消费者，不给消费进程提供Gold。

| 检查 | 复核结果（首轮与最终均成立） |
|---|---|
| 输入与答案身份 | 语料、两份题集及两份固定Gold摘要一致；48题集合完整，无重复或漏题 |
| 数值及阶段 | 回归18/18、新增18/18；各阶段、伤害及关联减损逐字段符合Gold |
| 边界及缺输入 | 回归6/6、新增6/6；合计unsupported 9、needs_input 2、invalid 1，原因与题意一致 |
| 归属及现场绑定 | 完整scene快照、request_scope、actor原型、能力拥有者及来源证据匹配；数值快照对应实际核心请求 |
| 未执行部分 | Gold要求的附带效果保留；全部applied=false，没有将数值成功当成HP/状态/资源已应用 |
| 执行版本 | 最终源码清单14文件与封存副本及当前Terminal文件相符 |

终端最终性能收据记录完整加载14.374毫秒、读取并执行48题23.646毫秒、4800次预热采样单题总响应p50约0.049毫秒。该口径不含进程启动、写盘、评分、UI或网络；首轮较早计时口径不同，保留原样，不用于宣称提速倍数。414项Node、75项Vitest及类型检查/隔离构建通过已有日志，本次未重复运行项目全量检查。

**P6建议：接受本批八对象为合同v1-r1下的内部候选生产基线。** 现有证据没有发现会使已支持路径返回错误数值或归属的阻断项；证明范围是这48题及合同规定的材料检查。未覆盖的内容不由这一通过率保证，Gold仍是基于来源的AI复核，非独立人工最终批准。

混合伤害、建筑双倍、转伤、储法资源、HP/临时HP、状态写入、实例迁移与完整施法合法性仍保持明确边界。暂无证据要求修改本批生产方向或重写核心；下一批范围另定，不自动全库扩产。此前P6建议已由§7用户决定承接；本报告不代替正式规则对象批准、Package发布或M2 Exit。未修改Terminal或本批输入/Gold。

## 7. 用户确认P6通过

用户于2026-10-26明确：“p6确认通过.接下来是否进入正式规则的批准阶段”。据此登记[本批接纳决定](../../experiments/rule-cluster-contract-v1-batch-1/reports/batch-acceptance.json)，P6状态为`accepted_internal_candidate_batch`。§6及P5收据中的Pending是当时审查状态，由本次后续决定承接，原记录保留。

本批作为已接纳的内部候选基线；规则对象的review_status仍为candidate，不修改已消费语料和Gold。后续建议进入本批正式化前的差距核查与批准材料准备，明确Source Binding/审核Mapping、正式Schema与逐事实采用、依赖/Package范围及人工审核记录；当前询问不视为已批准对象或自动启动转换。
