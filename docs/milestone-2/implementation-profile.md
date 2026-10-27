# M2 Implementation Profile

状态：**Confirmed**
Profile ID：`m2-rule-cluster-pilot@0.2.0`

## 1. 规则表达边界

M2 的平台最小核心不是七个业务簇，而是以下可组合的 Rule Assertion：

```text
Rule Assertion
├─ Trigger / Condition
├─ Activity / Operation
├─ Effect
├─ Prerequisite
├─ Choice
└─ Source Binding + review status
```

`Weapon Mastery`、D&D 2024 状态、法术和怪物特性是 D&D Profile 扩展；COC 的理智、
线索和社交不属于本 Profile。一个候选对象不等于正式规则对象：只有 Schema、来源范围、
Ruleset 适用性和人工审核均通过后才可标记为 `approved`。

## 2. 阶段

| 阶段 | 状态 | 交付与 Gate |
|---|---|---|
| M2-A Book Catalog 接纳 | `accepted_for_m2_input` | 已锁定 `antigravity-book-catalog@2026-09-09`；6,819 Entry 集合闭合、映射依据、Profile 选择与 11 条隔离队列通过独立验收 |
| M2-B 最小契约 | 设计已启动 | Rule Assertion / Source Binding Schema、候选与批准状态机、Validator fixture |
| M2-C 规则簇试点 | 未开始 | Conditions / 0 HP 与少量 Weapon Mastery 的候选、审核记录和批准对象 |
| M2-D 消费验证 | 未开始 | Rule Card、终端候选包、对照案例、低推理消费质量报告 |

## 3. M2-A 接纳条件

1. 外部交付以独立 Delivery ID、生成器版本、输入 Manifest 摘要和文件摘要登记；
2. 映射 Entry 集合与 M1-C3 Publisher Manifest 完全相等，或明确进入互斥 Review Queue；
3. 每条映射至少有 `entry_id`、`source_path`、`output_path`、`book_id` 与 `mapping_basis`；
4. Book 身份、权威、Rights 和规则采纳状态不得由路径分类自动升级为 `verified` / `approved`；
5. Profile 只决定输入集合及显式 fallback，不暗示跨书冲突已被语义裁决；
6. 接纳检查可重跑，失败不会修改 M1 或下游对象。

## 4. M2-C / M2-D 验收条件

- 每个批准对象都能定位到一个或多个 Entry 和精确正文范围；
- 候选、审核中、批准、拒绝状态不可混淆；
- 相同批准输入生成的 Rule Card 与终端候选包字节一致；
- 人工案例覆盖状态影响、动作/命中触发、资格门禁和至少一个例外/覆盖情形；
- 对照原始长 Markdown，报告输入量、适用 Ruleset、结论、遗漏和无法判定项；
- 未批准对象不会进入终端候选包。

## 5. 明确不做

不主张 LLM 提取天然“零幻觉”或规则执行天然“零漏算”。确定性只适用于冻结的批准对象和
确定性编译器；自然语言抽取始终是可审核候选过程。

## 6. 2026-10-21 有限样本补充授权

用户已授权生成六项怪物能力候选样本，并以 gpt-6-luna medium 主测、high 对照；具体范围、来源与停止点见[六项样本试验约定](monster-ability-sample-pilot-2026-10-21.md)。本批不增加正式 Schema、不形成规则批准或 Terminal 准入，不改变上述整体 Exit Gate，也不授权全量生产。

## 7. 2026-10-22 七卡有限批次授权

用户已批准火／气／土元素、巨魔、盾卫、史拉绿蟾及必需伴随巨魔断肢的候选生产与Luna medium消费测试，范围与停止条件见[七卡合同](finite-production-7cards-contract-2026-10-22.md)。沿用内容主验收、实质问题定向处理及6.1默认关闭；本补充不表示正式规则批准、Schema实施、Terminal准入或M2 Exit。

## 8. 七卡优化与候选迭代路线

用户随后明确继续以候选卡迭代验证，标准成熟后再统一转换，撤回“当前先做转正试点”的建议。本轮批准范围为[七卡优化与对照约定](seven-card-optimization-contract-2026-10-22.md)：整合既有七卡、固定首答对照、收敛候选生产协议；不启动正式化或新增怪物。下一批扩张须依据验证结果及具体范围，不能由本次优化完成自动推定。

## 9. 决定性事实先行的Prompt有限试验

用户批准在现有候选材料上对照“一次回答内先列决定性事实，再给结论”。[本轮约定](facts-first-prompt-contract-2026-10-22.md)固定30题、两种Prompt及两轮独立Luna medium首答，仅变更消费者回答要求，不改候选事实、Schema或Terminal，不默认6.1或全量二次复核。该试验不构成正式化或扩大生产准入。

## 10. 用户指定Luna high同题单轮

用户另行指定用Luna high执行同题一次。[单轮约定](facts-first-high-contract-2026-10-22.md)保留两种Prompt各一轮、相同30题及原Gold，共6次独立首答；不改材料、不追加复核，不调用6.1。该指定只适用于本次对照，不改变默认模型档位或扩大生产边界。

## 11. 后续测试默认配置收敛

用户现已指定后续规则候选消费测试默认使用既有“事实优先（事实先行）Prompt＋gpt-6-luna high”。该决定更新§10仅限单轮时的默认配置边界，不改写历史测试结果，不代表总体准确率已获证明。暂停medium通用Prompt搜索，不默认再跑medium对照、第二次完整复核或6.1；另有用户指定时按指定执行。沿用原文、候选与正式批准分离及结论/解释内容验收。

当前只收敛测试配置。下一步建议按候选生产协议开展一批新的有限候选与未见场景，检验协议复用及关系覆盖；具体对象、来源、依赖和批次边界须先固定。本次询问不视为自动启动新增生产或正式卡转换。

## 12. 六卡交叉关系有限生产与首答

用户已批准执行§11所建议的下一有限批次，具体范围锁定于[六卡交叉关系约定](cross-relations-6cards-contract-2026-10-22.md)：幽魂2014/2025、魅魔/梦魔2025、蕈人王/孢子奴仆2025及直接用途依赖。已完成6张完整候选、27道新题与3道旧回归；事实优先＋Luna high新题26/27、旧题3/3，见[结果](cross-relations-6cards-report-2026-10-22.md)。唯一新题失败为漏用豁免成功半伤，保留为模型消费错误，没有失败后加跑。

本批沿用候选身份及来源核查；未正式化、未修改Schema或Terminal，不表示M2 Exit。后续批次仍须明确范围，不由本次完成自动授权。

## 13. 本地计算器边界研究

六卡D09暴露已送达事实漏用后，用户同意研究浏览器本地计算器及“AI草算与工具计算比较、分歧时高级模型处理”的路线；商业方向为可许可复用通用组件、小核心独立实现、内容权利分离。本轮完成[研究稿](local-damage-calculator-research-2026-10-22.md)及46项预期案例，限定单次、单目标、单伤害类型和明确拒算条件。

这只是独立研究，不形成正式Schema、Rule批准、战斗Runtime或Terminal接入；计算器尚未实现，案例未执行。未运行新模型测试或6.1，后续样机不由研究稿自动升级为产品能力或M2 Exit。

## 14. 当前会话继续制作隔离计算器样机

用户明确要求无需转移Terminal，继续当前会话开发。依据§13研究范围，完成`experiments/local-damage-calculator/`小核心、比较逻辑及单文件HTML实验交付，见[样机结果](local-damage-calculator-prototype-2026-10-22.md)。46项原案例及9项补充/错误注入验证通过；浏览器file协议被自动工具阻止，真实浏览器验收Not Run。

此授权限定隔离样机，不启用生产AI Runtime、自动升模、完整战斗引擎或Terminal修改，不把合成模板当approved知识；未调用模型。代码所在地不改变规则事实与消费者实例的责任边界，不表示M2 Exit。

## 15. 2026-10-23比较器两项修补与候选固定

用户限定修复完整现场输入绑定及双方对象/数值完整性，并补回归；不重写核心、不扩充规则。已复现并完成[定向修补](local-damage-calculator-fix-2026-10-23.md)，原55＋新增18组共73项通过。源码、案例及文件摘要固定为`local-damage-calculator@0.1.1-candidate.1`本地Terminal接入候选，尚未获Terminal接纳。

本轮不修改Terminal，不调用模型或自动升模，不写战斗状态，不进行公开Release、Commit或Push。浏览器实际交互仍未验收，单文件构建不冒充浏览器验收。本补充不改变M2 Exit或正式规则批准边界。

## 16. 2026-10-23计算器能力样本准备

用户批准生成计算器纯能力测试题，复用历史LLM答卷对照，不重新调用LLM，不向计算器提供答案。已准备[16项样本及比较口径](calculator-capability-benchmark-2026-10-23.md)：8个历史数值子项、8个边界请求，输入与评分材料分开保存；旧答错误保留，以来源及原Gold核验评分标准。

本轮仅准备并核对材料，计算器执行和响应时间测量Not Run。该样本不修改计算器、Terminal或正式Schema，不构成正式规则批准、公开发布或M2 Exit；后续执行须按文中准确率、覆盖率与时间边界分别报告，不把核心计算耗时与历史多题模型执行时间当同口径速度比。

## 17. 完整规则簇候选形态与读取测试材料

用户明确下一批应先按未来生产方式的候选形态搭建完整规则簇，保留未用内容，然后出能力内占多数、兼有能力外的题目；不再以逐题request/context测试代替读取。已生产[五对象完整语料及24题](full-cluster-calculator-pilot-2026-10-23.md)：30项能力、11份完整法术、6份公共规则完整Entry，18项数值机制内题与6项范围外/缺输入题，Gold隔离。

该授权只含本批候选及测试材料生产、装配核查，不修改Terminal、不实现读取器或扩充核心、不调用LLM；消费结果Not Run。数据读取、绑定、数值和关联效果须分别评价，入口不支持完整材料时不得人工逐题装配后冒充通过。仍不是正式Schema、Package发布或M2 Exit。

## 18. 2026-10-26有限生产与计算消费合同起草

用户同意进入第一份正式生产合同的起草阶段，已形成[契约v1 draft-1](rule-cluster-production-consumption-contract-v1-2026-10-26.md)。草案提出八对象有限首批、统一请求范围、法术调用契约、完整生产及消费验收；该精确修订仍待审阅，不从起草授权推导数据生产、Schema实施或Terminal修改授权。

§17的Not Run为当时材料交付状态。Terminal后续获单独授权补齐读取/绑定，2026-10-26报告并提供24题输出；本会话核对18项数值及阶段符合固定Gold，5项unsupported、1项needs_input，全部applied=false。此证据支持合同收敛，不代表正式Independent Review、规则对象批准或M2 Exit。

## 19. 2026-10-26合同批准及八对象首批生产

用户随后明确“批准修改生产”，§18草案以[合同v1-r1](rule-cluster-production-consumption-contract-v1-2026-10-26.md)生效，授权八对象有限生产、D&D命名空间扩展及本会话可执行验证。已完成8对象45能力、11法术、6个公共规则完整Entry，统一请求范围、13项调用契约和254项逐Pointer抽取；原24题迁移回归及新24题已准备。来源/字段/有限Schema、11项错误注入及12文件字节一致重建通过，见[生产报告](rule-cluster-contract-v1-batch-1-report-2026-10-26.md)。

新格式`lorebuddy.dnd2024.rule-cluster-contract-1`明确要求消费者适配；只读探测确认旧入口安全拒绝该版本。48题消费、Terminal准入及本批整体接纳Pending，不修改Terminal或跨会话发送指令，不将数据生产通过当消费/正式规则批准。未改平台Core/Source/M1，未调用新模型、Release、Commit或Push。

## 20. 2026-10-26首批P5消费复核与P6建议

§19的48题Pending是生产交付时状态。Terminal后续完成calculator-corpus-2适配并封存首轮与最终结果；Buddy以当前交付及固定Gold逐项复核，两轮均读取绑定48/48、数值36/36（原/新各18）、边界12/12（原/新各6），完整现场快照、范围、拥有者及来源匹配，全部applied=false。最终源码14文件与封存清单匹配，见[首批报告§6](rule-cluster-contract-v1-batch-1-report-2026-10-26.md#6-p5消费收据复核与p6接纳建议)及其机器收据。

P5完成；P6建议接受本批内部候选，用户决定Pending。保留全部未支持机制、来源/权利及正式批准边界，不自动扩产或转正式节点；本次只复核与登记，不修改Terminal、Source、语料、题目或Gold，不调用新模型，不发布或提交。

## 21. 2026-10-26用户确认P6内部候选接纳

用户明确“p6确认通过”，本批登记为`accepted_internal_candidate_batch`，见[首批报告§7](rule-cluster-contract-v1-batch-1-report-2026-10-26.md#7-用户确认p6通过)。该后续决定承接§20的用户Pending，不改写P5历史收据或已消费材料。规则对象仍candidate；正式化准备与正式批准须分别核查现行Schema、Source Binding/Mapping、Ruleset适用性和人工审核，当前阶段询问不等同于转换实施、正式批准或下一批生产授权。

## 22. 2026-10-26八对象正式化补齐授权与准备结果

用户明确“正式补齐”，授权在已接纳P6八对象上补足来源、审核、Schema与包边界准备，不扩大生产。本轮装配70个待审对象、20条claimed映射与20个原始整页draft审计Fragment，保留94份派生证据、254项抽取及3项采用决定；四份局部审核Schema、完整集合/来源坐标/语义约束、654文件重建及9项错误注入通过，见[正式化材料与差距报告](rule-cluster-formalization-batch-1-2026-10-26.md)。

查明规范Source/Library事件与逐Unit Fidelity Coverage Map尚未在本批完成，不能用旧实验Fragment Schema或派生Note摘要代替。当前只是审核准备完成；正式批准数0，忠实转写节点激活、来源关联审核及包组装仍有明确门禁。未修改Core、M1、P6输入/Gold或Terminal，未调用模型、公开Release、Commit或Push；不因本轮工作自动改变M2 Exit或规则approved状态。
