# 规则簇生产原则：七个开源项目的文档与源码调查

调查日期：2026-10-26。状态：**研究结论／待讨论建议，不修改已确认合同、Schema、规则事实或Terminal。**

## 1. 结论与证据范围

当前路线可以继续：保留完整可读规则，以稳定身份维护事实，通过可复用机制描述支持确定性计算，复杂部分显式保留并说明能力边界。调查最需要补充的不是更多“每只怪物一个算法”，而是**规则内容、机制定义、执行计划、运行实例四者的边界，以及覆盖、错误和版本策略**。

对“近7000份材料”的问题，需要同时回答两件事：怎样把内容整理为可审核知识；怎样把其中适合程序执行的部分编译为受支持操作。所查项目为第二件事提供了丰富实现；在所审读路径中，没有找到能证明任意整本自然语言规则书可以自动、无人工语义决策地转换的通用方案。这个结论限于本次检查，不能推论所有项目都没有这类研究。

本轮查阅项目官方文档，取得7个仓库的固定Git提交，保存62份源码/数据/测试/许可证快照，建立32项可定位实现证据。重点是实际路径，不以README宣传、星数或测试数量估计正确率。外部项目的测试只阅读、没有执行；没有导入外部代码到LoreBuddy或Terminal，没有运行LLM或改动既有规则候选。

- [机器证据索引](../../build/rule-principles-research-2026-10-26/evidence-index.json)：固定提交、路径、定位行及观察。
- [文件清单](../../build/rule-principles-research-2026-10-26/files-manifest.json)：62份成功取得的文件及其摘要。
- GitHub匿名API曾返回限流；最终使用只读Git元数据取得提交和目录，以该提交的原始文件交叉核查。未将搜索缓存的分支版本当作所审读源码版本。

| 项目 | 本次重点 | 固定提交 |
|---|---|---|
| Card-Forge/forge | 卡牌脚本、替换事件及顺序 | `3b247698cdeda7236381ebc948539633c8ec9ffc` |
| avrae/avrae | 自动化树、参数覆盖及失败策略 | `cec0c9362e9b27cfd098657371701421bd4aae40` |
| foundryvtt/dnd5e | 能力/活动/法术调用及真实盾卫数据 | `93ba0dc3e837b66864ec385b8419882009b12e4e` |
| foundryvtt/pf2e | Rule Element、条件、授予关系及迁移 | `be4ab21be8ffed44385c0038c05d41b61dceb68b` |
| jleclanche/fireplace | 炉石数据与执行脚本分离、组合和交互回归 | `47a2572a000db66645bb74a425a090d51f1004fa` |
| open5e/open5e-api | 文档身份、对象/能力归属及引用候选 | `e69ac13b49dae6a9d84abf38fc674fe1db5b392b` |
| wesnoth/wesnoth | 回合制能力宏、作用域、叠加和依赖 | `514fbeb797fb887ac6de9f14ded81aaf0bedb8f2` |

## 2. 各项目实际如何处理

### 2.1 Foundry D&D5e：一个对象包含多种活动，法术调用引用独立本体

**观察。** Item下可以维护多个Activity；共同数据包含激活、消耗、效果及目标等，具体Activity具有各自类型。Cast通过UUID引用法术，用带来源标记的缓存副本承载运行中的修改；对激活、持续、距离和目标逐项检查override，另外处理施法属性、攻击加值/DC和被忽略的法术属性。缓存是派生运行对象，不能据此把两份可独立编辑副本都当作法术事实源。[Activity共同数据](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/module/data/activity/base-activity.mjs#L63)、[Cast实现](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/module/documents/activity/cast.mjs#L130)、[Cast数据约束](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/module/data/activity/cast-data.mjs#L33)。

官方[Cast文档](https://github.com/foundryvtt/dnd5e/wiki/Activity-Type-Cast)还明确提示：仅去掉Concentration属性不足以取消专注，持续时间也要相应覆盖。这是“字段之间有关联约束”的具体例子；不能把一个免除标记推成整个施法要求消失。[Forward](https://github.com/foundryvtt/dnd5e/wiki/Activity-Type-Forward)可以转调同一Item上的另一活动，仅改变消耗与缩放，提供了用途包装而非重写本体的例子。

**真实数据核查。** 该提交的2024盾卫Spell Storing有完整描述，但其`activities`为空、effects为空。它直接证明：在这份数据中，这项能力被收录，不等于其储法、调用和资源清空都具有可执行Activity。不能扩大成“Foundry所有模块都不支持储法”的结论。[盾卫实际数据](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/packs/_source/actors24/construct/shield-guardian.yml#L730)。Fireball的2014/2024表达分别存于不同集合，不能仅按同名合并；本次查看了2024描述与Activity共存的实际记录。[2024 Fireball](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/packs/_source/spells24/3rd-level/fireball.yml#L1)。

**适用建议。** 保留完整能力这个语义单位，内部引用多个可执行活动；法术本体只维护自身事实，怪物/物品调用维护明确覆盖。整卡可做组合视图，不必把每个算术步骤升级成独立公开知识节点。Foundry是执行系统；其缓存、Actor写入和文档格式不能直接提升为LoreBuddy平台Core。

### 2.2 Foundry PF2e：有限机制注册表＋选择范围＋适用条件

**观察。** Rule Element有明确的类型注册表；不同机制由各自类解释，Item维护这些指令。共同基类检查适用Actor类型、predicate及参数；失败可发出警告并将该指令标为ignored。类型未知或构造失败时，分派器也可能警告后继续构造其他指令。[类型注册与分派](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/rules/index.ts#L50)、[失败处理](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/rules/rule-element/base.ts#L183)。

其官方[Rule Element指南](https://github.com/foundryvtt/pf2e/wiki/Quickstart-guide-for-rule-elements)区分：selector/definition选取作用对象，predicate决定何时生效。这是两个维度。实际Bless效果同时组合Aura与FlatModifier，且链接回法术；不需要为每个提供同种加值的对象都重写数值引擎。[Bless效果记录](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/packs/pf2e/spell-effects/spell-effect-bless.json#L40)。

**来源特定状态。** GrantItem将granter与grantee的实例ID关联，并独立声明删除动作；Condition还能追索appliedBy/来源。这比只存“恐慌=true”更能表达谁施加、哪一条应移除。其默认删除动作包含cascade/detach等，是PF2e运行时选择；LoreBuddy应维护规则规定的终止语义，不能直接采用这些默认动作作为其他规则系统的规则。[授予与删除关系](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/rules/rule-element/grant-item/rule-element.ts#L145)、[Condition来源](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/item/condition/document.ts#L45)。

**适用建议。** 我们需要同样明确的“对谁生效”“何时生效”“做什么”；需要稳定的机制ID及版本。还应借鉴它按版本排序的迁移结构。[迁移执行器](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/migration/runner/base.ts#L35)。但不能照搬“指令失败后忽略”的整体成功含义：若忽略的是决定最终伤害的规则，本次所求结果就应停止。

### 2.3 Avrae：最接近“规则配置交给程序执行”的参考，同时暴露成功标记问题

**观察。** [自动化文档](https://avrae.readthedocs.io/en/stable/automation_ref.html)把一次动作组织为树：选择目标、攻击或豁免、分支、伤害、效果、资源和文字说明。源码按节点type分派；CastSpell引用明确法术ID，并允许环级、DC、攻击及施法调整值覆盖。[节点分派](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/__init__.py#L39)、[法术调用实现](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/castspell.py#L119)。

**必须警惕的两项行为。**

- Condition的默认errorBehaviour是false，求值异常可以走false分支。文档允许raise、both等其他策略。这是工具的可配置行为，不能成为“未知即条件不成立”的规则依据。[默认值与异常分支](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/condition.py#L7)。
- 引用法术没有automation时，CastSpell可以输出法术说明，最后仍返回success=True。这种success表示调用流程完成，不能替代“所求机械效果已完成”。[无automation分支与返回值](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/castspell.py#L119)。

效果还可以关联parent，测试中覆盖效果按钮和属性；这对将点燃等持续效果的说明与后续执行入口分开很有参考价值。[效果父关系](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/ieffect.py#L135)、[效果测试](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/tests/e2e/automation_effects_test.py#L147)。我们应采用它的结构化调用思路，明确增加所求范围、已执行操作、待执行效果和停止原因；不照搬默认失败语义或把整个树当成源规则权威。

### 2.4 Open5e：内容库有独立价值，但描述字段不是执行语义

**观察。** Document、Publisher、GameSystem及License分别建模，内容通过FromDocument归属于来源文档；CreatureAction有明确parent，Spell同时保留正文和部分结构化字段。[来源对象模型](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/api_v2/models/document.py#L11)、[能力归属模型](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/api_v2/models/creature.py#L213)、[法术模型](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/api_v2/models/spell.py#L25)。

它还有明确的引用处理流程：按文档范围找候选、检查报告、调整黑名单、dry-run，再决定是否写入引用。由此可借鉴“文本匹配只产生引用候选”，不能把同名自动当同一版本或同一事实。[交叉引用工作流](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/scripts/crossreference/README.md#L25)。

**适用建议。** 来源身份和对象归属可以先独立做好，即使暂时没有完整计算。其多个Boolean字段默认false，适合其既有内容装配约定；我们从不确定材料抽取时，需要额外保留unknown/not_stated，不能把默认值原样当来源事实。Document分类也不等于LoreBuddy所要求的原始Artifact→Entry→Fragment及审核Mapping全链。

### 2.5 Forge：复用操作、显式替换事件和执行顺序

**观察。** Lightning Bolt同时有展示用Oracle文本和明确的DealDamage脚本，伤害值/目标由参数提供；引擎不需要从这句展示文字猜算式。Pariah的转伤被表示为DamageDone事件的替换，而非在普通伤害之外再独立追加一次伤害。[普通伤害实卡](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-gui/res/cardsfolder/l/lightning_bolt.txt#L4)、[转伤实卡](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-gui/res/cardsfolder/p/pariah.txt#L6)。

ReplacementHandler实际遍历ReplacementLayer、收集候选、由控制者选择，并用已运行记录限制重复应用；某些更新会重新进入替换处理。该设计提醒我们，例外不仅是“又加了一条公式”，还涉及替换什么、何时替换、是否重复和谁作选择。[替换顺序实现](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-game/src/main/java/forge/game/replacement/ReplacementHandler.java#L246)。AbilityFactory对缺少API的脚本抛错，并通过显式SubAbility等字段组合动作。[脚本构造与失败](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-game/src/main/java/forge/game/ability/AbilityFactory.java#L147)。

**适用建议。** 使用“机制模板＋参数＋组合”生产常见能力；少量新机制才扩充受控操作库。未来转伤/替换可以借鉴其事件与顺序思想，但不能复制万智牌的Layer列表给D&D当规则顺序，也不需要本阶段建设完整卡牌栈或任意脚本引擎。

### 2.6 Wesnoth：拥有者、受影响者、叠加和版本必须分别表达

**观察。** [AbilitiesWML](https://wiki.wesnoth.org/AbilitiesWML)区分单位能力与武器特效，并讨论self、attacker、defender、teacher/student等不同角色。能力还维护id/unique_id、过滤器、数值运算、叠加和覆盖优先级；这些不是单一“伤害加值”能完整表达的。其实际Schema具有这些维度，公共能力通过命名宏复用。[公共能力宏](https://github.com/wesnoth/wesnoth/blob/514fbeb797fb887ac6de9f14ded81aaf0bedb8f2/data/core/macros/abilities.cfg#L26)、[能力Schema](https://github.com/wesnoth/wesnoth/blob/514fbeb797fb887ac6de9f14ded81aaf0bedb8f2/data/schema/units/abilities.cfg#L32)。

源码回归专门添加两个同类型但不同ID的能力，再用id与tag过滤移除其中一个，并检查另一效果保留。这种正确例与反例的组织方式可以直接启发我们的来源特定状态和拥有者过滤测试。[精确移除回归](https://github.com/wesnoth/wesnoth/blob/514fbeb797fb887ac6de9f14ded81aaf0bedb8f2/data/test/scenarios/wml_tests/ScenarioWML/EffectWML/test_remove_ability_by_filter.cfg#L6)。

[插件发布描述](https://wiki.wesnoth.org/PblWML)明确列出依赖与版本信息；[模块加载说明](https://wiki.wesnoth.org/AddonsWML)还处理宏与加载上下文。我们可借鉴Manifest与能力版本约束，但不必采用文本宏的展开顺序作为知识事实优先级。

AbilitiesWML文档还列出不同引擎版本的计算行为差异，以及为避免多人失步而保留某些已知行为的情况。这支持“存档锁定规则/算法版本”，不支持自动把最新引擎或资料覆盖进进行中的团。它是该项目的版本行为，不构成我们保留已知错误的决定。

### 2.7 Fireplace：数据存在、脚本存在和交互正确是三件事

**观察。** CardDB把CardXML数据与按卡ID提供的脚本合成。找不到脚本时，部分play/events等成员可以得到空动作列表；因此不能仅凭卡牌可加载推断其特殊效果已实现。[合成与空默认值](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/__init__.py#L58)。

实际Fireball调用共享Hit操作；另有卡通过控制者规则将治疗转为伤害，交互测试检查它与圣盾及其他牌的组合。[Fireball脚本](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/classic/mage.py#L104)、[治疗替换规则](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/classic/priest.py#L51)、[交互回归](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/tests/test_auchenai_soulpriest.py#L14)。这说明复用机制和逐卡配置可以共存；也说明单一伤害算式通过，不足以覆盖事件替换和其他效果的组合。

**适用建议。** 新内容可以配置已有机制，而不必全部新增程序。但我们不应把“无实现→空效果”作为正式消费者默认：应明确区分不存在的效果、尚未实现的效果和被规则条件排除的效果。Fireplace是历史炉石模拟器，不是跨TRPG知识标准。

## 3. 对此前六条生产原则的具体修订建议

以下均为研究建议，尚未写入已批准合同。

| 原则 | 外部证据带来的具体写法 | 对现有方向的影响 |
|---|---|---|
| 对象准入 | 分开内容单元、执行活动、最小程序操作；完整能力可以包含多个操作，不为适配程序把每一步都变成知识节点 | 补充对象类型及转换目标，不推翻拥有者设计 |
| 拆分粒度 | 以独立维护/引用/审核的语义为边界；内部条件、分支、结果通过明确结构关联；叙事和整页参考无需硬变成可执行规则 | 避免“一段一节点”和“一页一规则”两种机械拆分 |
| 复用/变体/覆盖 | 稳定对象ID＋来源/规则版本；引用本体并逐字段覆盖；覆盖操作、适用范围和约束必须可查 | 保留本体/调用分离，增加覆盖冲突和约束检查 |
| 规则簇完整性 | 分别检查正文完整、知识依赖闭合和所求执行依赖闭合；解释链接不自动要求装入其全文 | 将“完整”拆成多个可验证维度，防止无限追全书 |
| 机器执行准入 | 只编译到消费者明确支持的机制/表达式版本；缺现场输入或求值失败不能默认为false/0/无效果 | 必须有能力声明、预检和明确停止结果 |
| 正式批准 | 规则内容审核、来源保真、发布授权、执行覆盖分别记录；语义批准不承诺全部自动化，执行成功不替代语义批准 | 沿用现有门禁，补充可读的逐效果覆盖账本 |

最应改变我前面表达的一点：**完整保留规则书，与把每条规则全部编译成计算程序，不应绑定为同一个完成条件。** Foundry盾卫的真实数据是直接例子。我们仍需满足自身的来源保真和审核要求，但不需要等整本书都可执行后才交付已审核知识。

## 4. 建议明确维护的四层

这是一种职责划分，不是本轮新建四套平台Schema：

1. **来源层。** 保留Artifact、Entry、原文范围、版本/译文/权利声明及审核证据。外部游戏引擎的成品卡库不能代替这一层。
2. **知识层。** 怪物、能力、法术、公共规则、覆盖、来源特定状态及依赖关系；同时给人和AI阅读。完整但尚未编译的段落仍可存在。
3. **执行描述层。** 该规则可编译成哪些受控机制及其参数、条件、顺序和输入要求；标明未编译条款。相当于Avrae的显式树、Foundry的Activity或PF2e的Rule Element所承担的部分职责，但不是直接复制其格式。
4. **运行实例层。** 实际actor/target、骰果、豁免、当前资源、具体来源效果与玩家选择；由Terminal或其他消费者绑定，计算后生成可审议提案，再依产品权限应用。

计算器拥有算法实现；知识层拥有“在什么条件下采用哪条规则”的事实。新机制进入操作库时，需为实现、输入约束和版本建立测试；新怪物仅使用已有机制时，主要工作转为来源抽取、参数绑定及组合验证。AI可以辅助提取、定位或解释，不应自由生成未经登记的可执行脚本。

## 5. 应新增的四条横向约束

### 5.1 未知和不成立必须分开

建议表达至少三种判定：条件成立、条件不成立、必要事实不足。Avrae的错误分支默认和Open5e的Boolean默认说明，成熟项目的默认值也有特定使用前提，不能无条件迁移到我们的不确定抽取/现场输入。

例：缺少“目标是生物还是建筑”时，不能把攻城怪物判为不适用。若当前请求的最终伤害依赖这一事实，应返回缺输入，而不是按普通生物路径继续。

### 5.2 覆盖要区分增加、替换、禁止、选择和后续效果

这些操作具有不同关系：增加一个伤害分量，不等于替换原分量；转伤不等于额外伤害；令玩家选择一条效果，不等于两条都执行；免材料不等于免专注。Forge的替换处理说明，后续支持复杂机制时，需要明确适用顺序、互斥/选择及重复应用限制。

不建议现在设计万能优先级数字。先按已支持机制列出明确的有依据顺序；冲突无法证明时保留待审。规则来源的采用优先级与程序操作顺序也是两种事实。

### 5.3 同名状态之外，需要具体效果实例与来源角色

知识层维护“谁能施加、何时结束、是否可叠加/替换”；运行层维护这一次效果由谁、哪一次调用、在何时施加。来源模板、来源生物实例、施法参数拥有者和实际执行者不能互相代替。PF2e的granter/grantee及Avrae的parent关系提供了可验证参考。

对解除某梦魔来源的诅咒，测试必须同时有另一来源的同名诅咒，检查只移除应移除的一项。无需因此现在实现状态写入；先确保规则表达及未来执行契约不会丢掉这些身份。

### 5.4 成功必须带所求范围与效果覆盖

至少分别报告：材料是否读通、规则是否定位、依赖和输入是否齐全、所求数值是否完成、哪些效果未执行、是否应用。Avrae无自动化仍success和Fireplace空脚本的例子，正好说明单一success标记不足。

这与当前Terminal保留request_scope、pending_effects和applied=false的路线一致。建议把它提升为后续生产/消费契约的一贯要求；不是现在扩充完整战斗Runtime。

## 6. 用本项目真实对象检查借鉴是否合适

下表是拟定的验收方向，不是新增已执行测试或新Gold。

| 对象 | 应复用的结构 | 正确情况 | 必须识别的错误情况 |
|---|---|---|---|
| 魅魔汲命之吻 | 目标资格＋豁免分支＋伤害调整＋关联结果引用 | 上限减损引用最终damage_taken；资格绑定这只魅魔 | 用原始伤害作减损；把其他来源魅惑当作合格 |
| 土元素攻城怪物 | 拥有者修正＋作用对象过滤 | 对已证明为生物的构装目标不翻倍；建筑分支按支持情况执行或停止 | 把construct误当structure；缺entity_kind仍给成功数值 |
| 盾卫储法 | 法术引用＋储存实例＋原施法者参数＋资源后续效果 | 明确当前储存的法术和参数来源；资源未实现则保留停止边界 | 将储存法术当盾卫固有权限；DC从错误拥有者读取；展示说明就声称释放完成 |
| 盾卫连接 | 来源关系＋条件＋伤害替换/分配＋取整 | 保留本护符、本盾卫和向上取整；未支持时停止整体请求 | 当作普通减伤公式叠加；忽略适用身份或重复转伤 |
| 梦魔来源诅咒 | 效果类型＋来源实例＋结束条件 | 结束A来源效果时保留X来源效果 | 仅按状态名称批量删除 |
| 火球术 | 独立法术＋调用覆盖＋选定目标范围＋未处理区域效果 | 返回所求目标伤害并说明其他区域/资源未处理 | 单目标伤害正确就报告整个法术完整完成 |

这类样本的意义在于检验机制组合和错误分派，而非继续增加同一路径下的伤害数值排列。

## 7. 具体借鉴顺序、替代方案和代价

**建议优先做三件事。**

第一，把生产协议补成“对象类型与语义边界＋机制模板与字段拥有者＋依赖与执行覆盖”的有限规范。用现有八对象做逐条回查，区分已有模板配置、已有模板组合及真正需要新操作的例外。暂不承诺这些类型能覆盖全书，也不估算未经统计的复用百分比。

第二，为消费者现有能力登记明确的机制/表达式版本及输入、输出、停止条件。现有代码可复用，缺的是稳定声明与生产端对应关系。能力外内容继续完整生产、明确未编译，不以删掉复杂条款换取更高通过率。

第三，将来源保真验证作为独立工程轨道补齐，和语义机制回查并行规划。外部规则引擎的Activity、Rule Element或卡牌脚本均不能证明我们的中文HTML到Library的保真。前一轮发现的规范事件流/Coverage Map缺口仍成立，但它不意味着组织规则的所有原则都未确定。

**不建议的替代方案。**

- 每个怪物写一个专用程序：首批直接，但同一半伤/抗性等机制易重复和漂移。
- 把所有原文立即翻成任意脚本：新规则初看灵活，审核、错误隔离、解释与迁移成本高，偏离当前有限计算器目标。
- 直接采用某个引擎作为知识模型：省去部分执行设计，却把Foundry Actor、PF2e加值规则或MTG层顺序带进跨TRPG平台。
- 先等全书完全自动化才正式交付：将知识完整性与执行覆盖绑定，扩大每批门槛；实际项目的部分自动化记录表明这不是唯一合理路径。

**代价。** 需要维护一份受控机制目录、每类机制的关键正反例、参数/覆盖约束及版本迁移；语料作者需要逐条声明哪些内容已经结构化、哪些还未编译。收益是常见新内容主要配置已有机制，跨对象组合可统一测试，遇到陌生机制可明确停止。尚无本项目全书机制分布数据，不能据本次代码阅读给出工期、自动化覆盖率或准确率提升百分比。

## 8. 代码复用与许可观察

本轮仅研究，未把外部实现复制进产品。固定提交中观察到的顶层许可证分别为D&D5e的MIT样式文本、PF2e的Apache-2.0、Avrae/Forge的GPLv3文本、Wesnoth的GPLv2文本、Fireplace的AGPLv3文本；Open5e使用Modified MIT并显式排除部分图片和第三方SRD内容。顶层许可证不能单独代表所有规则正文和资源的许可。

本报告的优先建议是参考职责边界和机制设计，自行实现满足本项目有限需求的部分；若选择具体代码复用，再按该文件、依赖及数据许可核对。本轮没有作出商用许可接纳决定。

## 9. 可直接回查的实现证据

- **D1** Item-owned activities carry activation, consumption and effects. [module/data/activity/base-activity.mjs:63](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/module/data/activity/base-activity.mjs#L63)。
- **D2** Linked spell cache records origin and applies explicitly selected field overrides. [module/documents/activity/cast.mjs:130](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/module/documents/activity/cast.mjs#L130)。
- **D3** Spell UUID and type validation; referenced spell facts remain distinct from caller configuration. [module/data/activity/cast-data.mjs:33](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/module/data/activity/cast-data.mjs#L33)。
- **D4** Real 2024 spell data; complete description and structured activities coexist. [packs/_source/spells24/3rd-level/fireball.yml:1](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/packs/_source/spells24/3rd-level/fireball.yml#L1)。
- **D5** Real shield guardian data includes textual storage ability; presence alone is not evidence of full stored-spell execution. [packs/_source/actors24/construct/shield-guardian.yml:730](https://github.com/foundryvtt/dnd5e/blob/93ba0dc3e837b66864ec385b8419882009b12e4e/packs/_source/actors24/construct/shield-guardian.yml#L730)。
- **P1** Finite Rule Element registry and explicit dispatch. [src/module/rules/index.ts:50](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/rules/index.ts#L50)。
- **P2** Validation failure warns and sets ignored; not global all-or-nothing evaluation. [src/module/rules/rule-element/base.ts:183](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/rules/rule-element/base.ts#L183)。
- **P3** Grant relationships bind granter and grantee IDs and deletion actions. [src/module/rules/rule-element/grant-item/rule-element.ts:145](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/rules/rule-element/grant-item/rule-element.ts#L145)。
- **P4** A real spell effect composes Aura and FlatModifier and refers to its source. [packs/pf2e/spell-effects/spell-effect-bless.json:40](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/packs/pf2e/spell-effects/spell-effect-bless.json#L40)。
- **P5** Condition origin and appliedBy are distinct from a condition slug. [src/module/item/condition/document.ts:45](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/item/condition/document.ts#L45)。
- **P6** Version-ordered migrations; not silent mutation of old interpretation. [src/module/migration/runner/base.ts:35](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/src/module/migration/runner/base.ts#L35)。
- **P7** Inspect predicate tests; not executed in this research. [tests/module/system/predication.test.ts:3](https://github.com/foundryvtt/pf2e/blob/be4ab21be8ffed44385c0038c05d41b61dceb68b/tests/module/system/predication.test.ts#L3)。
- **A1** Effects are explicitly dispatched from typed nodes. [cogs5e/models/automation/effects/__init__.py:39](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/__init__.py#L39)。
- **A2** Condition evaluation errors may execute a configured branch; false is default. [cogs5e/models/automation/effects/condition.py:7](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/condition.py#L7)。
- **A3** No automation can yield description output and success=True; success is not mechanical coverage. [cogs5e/models/automation/effects/castspell.py:119](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/castspell.py#L119)。
- **A4** Effect instances can be linked to parent effects. [cogs5e/models/automation/effects/ieffect.py:135](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/cogs5e/models/automation/effects/ieffect.py#L135)。
- **A5** Real effect/button tests; inspection only. [tests/e2e/automation_effects_test.py:147](https://github.com/avrae/avrae/blob/cec0c9362e9b27cfd098657371701421bd4aae40/tests/e2e/automation_effects_test.py#L147)。
- **O1** Document/License/Publisher/GameSystem and document ownership are distinct records. [api_v2/models/document.py:11](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/api_v2/models/document.py#L11)。
- **O2** Creature action has explicit parent. [api_v2/models/creature.py:213](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/api_v2/models/creature.py#L213)。
- **O3** Description and partial structured fields; booleans default false in curated API schema. [api_v2/models/spell.py:25](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/api_v2/models/spell.py#L25)。
- **O4** Reference candidates and dry-run before writes; title matching is not identity approval. [scripts/crossreference/README.md:25](https://github.com/open5e/open5e-api/blob/e69ac13b49dae6a9d84abf38fc674fe1db5b392b/scripts/crossreference/README.md#L25)。
- **F1** Card prose and explicit DealDamage script are separate. [forge-gui/res/cardsfolder/l/lightning_bolt.txt:4](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-gui/res/cardsfolder/l/lightning_bolt.txt#L4)。
- **F2** Damage redirection represented as event replacement, not a second ordinary damage action. [forge-gui/res/cardsfolder/p/pariah.txt:6](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-gui/res/cardsfolder/p/pariah.txt#L6)。
- **F3** Layer ordering, chosen replacement and hasRun guard. [forge-game/src/main/java/forge/game/replacement/ReplacementHandler.java:246](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-game/src/main/java/forge/game/replacement/ReplacementHandler.java#L246)。
- **F4** Unknown or missing effect API is a parse failure, not prose inference. [forge-game/src/main/java/forge/game/ability/AbilityFactory.java:147](https://github.com/Card-Forge/forge/blob/3b247698cdeda7236381ebc948539633c8ec9ffc/forge-game/src/main/java/forge/game/ability/AbilityFactory.java#L147)。
- **W1** Named reusable macro composes presentation and typed ability fields. [data/core/macros/abilities.cfg:26](https://github.com/wesnoth/wesnoth/blob/514fbeb797fb887ac6de9f14ded81aaf0bedb8f2/data/core/macros/abilities.cfg#L26)。
- **W2** Ability identity, stacking and priority are explicit schema dimensions. [data/schema/units/abilities.cfg:32](https://github.com/wesnoth/wesnoth/blob/514fbeb797fb887ac6de9f14ded81aaf0bedb8f2/data/schema/units/abilities.cfg#L32)。
- **W3** Regression removes one ability by ID/tag and retains the other; inspection only. [data/test/scenarios/wml_tests/ScenarioWML/EffectWML/test_remove_ability_by_filter.cfg:6](https://github.com/wesnoth/wesnoth/blob/514fbeb797fb887ac6de9f14ded81aaf0bedb8f2/data/test/scenarios/wml_tests/ScenarioWML/EffectWML/test_remove_ability_by_filter.cfg#L6)。
- **H1** CardXML facts merge with script definitions; missing scripts receive empty default action lists. [fireplace/cards/__init__.py:58](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/__init__.py#L58)。
- **H2** Fireball script composes shared Hit primitive rather than parsing card prose. [fireplace/cards/classic/mage.py:104](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/classic/mage.py#L104)。
- **H3** Healing-to-damage replacement is represented through an explicit controller rule. [fireplace/cards/classic/priest.py:51](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/classic/priest.py#L51)。
- **H4** Interaction regression covers healing replacement plus divine shield; not executed here. [tests/test_auchenai_soulpriest.py:14](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/tests/test_auchenai_soulpriest.py#L14)。

研究结论不构成新生产合同确认、规则对象批准、Terminal修改授权或公开发布；本轮没有更改P6接纳结论。后续如采纳建议，应将明确条款写入生产协议，并继续在既有批次和少量未见机制上验证。
