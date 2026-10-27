# 合同v1首批：有限D&D数据格式与消费约定

本规范落实已批准合同`m2-rule-cluster-production-consumption-v1 / v1-r1`。它是内部候选交付的有限扩展，不是平台Core或公开Package规范；机器结构以本目录`schemas/`为准，跨记录约束由`validate.py`检查。

## 1. 身份、版本与输入

| 字段/文件 | 约定 |
|---|---|
| `knowledge.format_revision` | `lorebuddy.dnd2024.rule-cluster-contract-1`，与旧研究格式明确不同 |
| `schema_revision` | `1.0.0`，有限Schema修订，不是规则版本或Package版本 |
| `contract_id / contract_revision` | 本批生产依据，不升级来源权威 |
| `delivery_id / delivery_revision` | 本次内部交付身份和修订；不是对象ID、标题或发布版本 |
| `cards / spells / shared_rules` | 八对象45能力、11份法术、六份公共Entry完整内容，各自拥有事实 |
| `relations / clusters` | 关系与八个完整对象规则簇，引用稳定ID；所有题共用整个语料 |
| `evidence / sources` | 94份既有证据、20个实际Entry；保留原文范围及工件字节收据 |
| `mapping_rules / structured_extractions` | 映射方法与254项逐JSON Pointer候选抽取，绑定拥有者、具体值、证据和适用采用决定 |
| `alias_registry / alias_records` | 可重建的旧符号映射及语言声明；本批符号使用BCP47 `zxx`，符号不是身份 |

消费输入分别是`input/knowledge.json`、`input/regression-questions.json`及`input/new-questions.json`。题号只供关联输出/评分，生产绑定不得读取题号选择能力或答案。

`candidate_revision`提高，原对象和能力ID保持；旧文件原样保留。`critical_fields`、`mechanics.clauses`及原有数值表达是从既有候选投影的兼容表示，校验要求一致，不是可分别手工修改的事实。

## 2. 请求范围与现场事实

两个题集共48题，均在题对象顶层带`request_scope`：`damage_and_linked`、`full_ability`、`hp_settlement`、`source_state_change`、`instance_migration`。作用同已验证消费API的独立参数，调用端可直接传`question.request_scope`，不再依赖按题号查询的旁表。字段不存在时报告缺输入，不默认扩大/缩小请求。

原24题的题面、scene和Gold保持；只添加请求范围并更新交付标签/Envelope。本批冻结了原`explicit-scope-adapter-2`的JSON证据，生产不再依赖Terminal配置未来的变化。核查见`migration.json`。

现场原型引用只选来源，不能把印刷HP复制成当前HP；未知防御不等于没有防御。新题的`entity_kind`明确区分creature/object/structure，构装生物仍是creature。缺少该事实且无法从受选原型证明时，不能默认攻城规则不适用。

## 3. 命名空间扩展

本批D&D专属新字段位于`extensions["lorebuddy.dnd2024"]`，不进入平台Core。每张卡具有`identity_traits`及内容覆盖说明；全部能力保留原文、原有字段、来源和拥有者。

### 法术本体

每份法术的`casting_contract`结构化以下内容：

- `base_level / activation / range / targeting`：基础环级、施法时间、距离及直接目标规则。
- `components`：V/S/M是否列出、材料文字、消耗与价值是否说明。未说明消耗不伪装成false。
- `duration / concentration / save_attack / upcast`：持续时间、专注标记、豁免/攻击及升环文字。
- `effects / coverage`：数值表达引用与尚未编译的完整正文，不能因有头部字段就宣称完整施法合法性已实现。

每个事实使用`{state,value,binding}`。`state`区分`known`、`unknown`、`not_stated`、`not_applicable`、`requires_runtime`、`verbatim_only`和`partially_structured`。`binding`给出证据ID、Entry ID、Note字节范围、映射规则及采用决定。`known`不能携带null。

专注bool由已选规则环境下持续时间头的专注标记投影；完整正文保留。材料价值只记录来源实际写出的材料文字/币值，不推出额外消耗。复杂效果或条件仍明确声明未编译，用户确认的合法事件数值结算与完整施法合法性分开。

### 调用方

拥有者能力的`casting_calls`引用稳定法术ID，维护施法属性/DC/攻击加值、采用环级、成分豁免、目标覆盖、次数及资格。字段同样有来源状态与绑定。

- `mode=intrinsic_spell_call`才是本卡固有调用。
- `mode=stored_spell_instance`用于盾卫储存的具体法术；需要现场储存实例和原施法者参数，不能当作盾卫随意会施展的法术。
- `parameter_owner`为当前施法实例或原储存施法者；卡载DC14/+6照实保留，不用译注15/+7覆盖。
- 免M或免V/S/M仅覆盖所列成分；`concentration_override=not_stated`表示继续读取法术本体，不是免专注。
- `mapping_adoption_ids`说明法术身份/调用映射的采用上下文；逐参数/逐Pointer的采用决定仅绑真正受影响字段。
- `cast_level=not_stated`与`requires_runtime`不能当作自动采用基础环级；题目明确给环级时读取场景值。

本批共13个具体调用：原固有调用11项、盾卫储存样本两项。完整规则仍允许满足资格的其他储法；它们需要独立法术材料及现场实例，不在本批自动闭合。

### 数值与未支持机制

`mechanics.damage`继续描述单次伤害；骰式与固定值二选一。气元素雷鸣猛击/旋风、土元素猛击/岩石射击有来源明确的表达。旋风资格和附带效果完整保留，不能仅计算半伤就声称完整旋风完成。

新增的拥有者规则也有结构表达：

| 字段 | 意义 | 当前消费边界 |
|---|---|---|
| 土元素`passive_numeric_rules`及能力`owner_modifier_dependencies` | 对object/structure伤害在抗性前乘2；构装生物不适用 | 须证明不适用才可直接走普通生物伤害；物件/建筑分支不在既有核心能力内 |
| 盾卫拳击`damage_components` | 同一命中含11钝击及7力场（或各自骰式） | 当前单类型核心不得只取其中一种 |
| 连接`transfer_contract` | 本护符/本盾卫、60尺、伤害一半向上取整 | 当前不实现转伤或HP写入 |
| 法术储存`stored_spell_contract` | 单槽、四环以下、原施法者参数、释放后清空 | 不是固有施法；不实现资源状态写入 |

完整数据可以包含未支持结构。读取器须识别其存在、保留来源并正确报告范围，不能通过删除字段来变得兼容。结果区分数值、HP损失及关联减损，保留尚未执行的条件性效果。

## 4. 兼容与消费要求

生产交付时旧`calculator-corpus-1`明确要求`research-full-cluster-1`，本批不冒用该格式。只读探测确认旧入口以`unsupported_corpus_environment`拒绝新格式，见`reports/consumer-compatibility.json`。这是预期格式门禁，不是48题算错或来源数据损坏。

以下是原接入要求；Terminal后续已完成本批适配与48题执行，Buddy复核见`reports/consumer-receipt.json`：

1. 校验新Schema/引用，保持全部对象/能力/依赖，不按题裁剪；接受显式`request_scope`。
2. 消费结构化法术及调用覆盖，核对兼容投影一致；未编译资格/效果仍不猜测执行。
3. 读取土元素拥有者修正，识别生物与物件差异；只支持范围内路径，物件双倍等新增机制明确停止。
4. 保留盾卫混合分量、储法参数拥有者和资源效果；未支持时给正确原因，不伪造固有施法权限。
5. 同一完整语料依次执行24回归/24新题，先封存输出，再由评分端读Gold；固定分母分别报告，首次/预热与加载/绑定/核心/总耗时分开。

当前`run-full-cluster-pilot.mjs`支持`--input`与`--questions regression-questions.json,new-questions.json`，须显式指定本批路径；省略参数仍是旧批次默认值。实际消费request_scope来自题对象，不按题号查询旁表。

## 5. 验证边界

`validate.py`执行有限Schema、精确来源/抽取范围、原文/ID/能力集合、调用覆盖、共享依赖、现场引用、骰式值域及旧题语义检查；11项错误注入均作用于内存副本。原始Source和旧批次不变。

`check_rebuild.py`在临时目录重建12份规范输出并逐字节比较，证明在相同来源/工具/决定下可重跑；它不证明自然语言语义全部正确。Gold仍为根AI对来源复核，不是独立人工最终批准。

来源、形式Schema及装配已验证；Terminal适配和本批48题消费已完成，Buddy复核首轮/最终均36项数值及12项边界通过，用户已确认P6整批内部候选接纳，见`reports/batch-acceptance.json`。所有对象仍candidate，未公开发布、未写Campaign。
