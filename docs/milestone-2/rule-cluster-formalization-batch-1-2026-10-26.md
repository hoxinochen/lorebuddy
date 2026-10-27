# 八对象正式化补齐：审核材料与真实剩余门禁

日期：2026-10-26。用户授权：“正式补齐”。承接合同v1-r1及已确认P6，不扩大对象集合。

**结论：70个对象的正式审核准备材料已装配并验证；正式化整体未完成，正式批准数为0。** 查明原始来源到Library的规范保真链尚无本批通过证据，不能仅凭48题消费成功、派生Markdown字节一致或旧实验Schema通过，把整批改成approved。

## 1. 已完成的具体补齐

[工作区与命令](../../experiments/rule-cluster-formalization-batch-1/README.md)，[完整审核入口](../../experiments/rule-cluster-formalization-batch-1/review-bundle/REVIEW.md)。

| 项目 | 本轮结果 |
|---|---|
| 审核对象 | 8张完整卡视图、45项能力、11份法术、6份完整共享来源参考，共70项；原语义ID保持 |
| 原文 | 每项独立保留正文原字节，与原Note精确UTF-8范围核对，不增换行、清理或拼接 |
| 结构化事实 | 保留原候选快照、254项抽取、映射规则、表达式、关系、规则簇和3项采用决定；重跑原全语料语义校验，不限题目涉及字段 |
| 原始来源链 | 对20个原Entry锁定完整Inventory及Artifact记录，核对Entry ID、原始字节、保存路径；另建20个draft whole-entry审计Fragment |
| 出版声明链 | 两组Work/Edition声明、20个独立Mapping；身份claimed，翻译与权利unknown，审核pending，没有因目录名自动核验 |
| 审核记录 | 每对象单独绑定正文、候选快照及摘要；70项human_decision均为空，状态in_review/awaiting_review |
| 局部Schema | 四份封闭M2审核Schema；复用现有Fragment/Mapping/Boundary Schema进行实验结构核查，不修改Core或旧版本 |
| 包边界 | 四个私有包的边界提案、内容/构建依赖方向及访问域前提；没有建立正式Package或移动Source |
| 重建与拒识 | 654文件完整集合、临时目录逐字节重建通过；9项错误注入全部阻塞 |

原始Source、M1 Publisher及GPT Export、原P6输入和Gold保持；未修改Terminal、调用LLM、执行新消费测试、发布或提交。项目现有Rule Assertion/M1-B Schema/M2-A验证器相关6项测试通过。

## 2. 为什么采用审核工作区

当前最小Rule Assertion只有六类`{kind,text}` Clause及Entry范围；它不表达本批完整拥有者、施法覆盖及各类部分编译状态。将整张卡或整份术语页强塞成一条Clause，会让结构校验通过却误表事实边界。因此保留已验证D&D表达，在独立M2审核Envelope中绑定来源、原文、依赖和审核记录；不改动旧Schema，不把D&D字段提升到平台核心。

替代方案一是直接修改P6语料的review_status。这会使已消费字节和审核对象发生漂移，且缺少对应人工决定，故不采用。替代方案二是同时重做整个平台Core、完整规则引擎和所有包机制。这超出本批需要，故不采用。当前采用工作区只生成待审材料；它不冒充最终Library格式或正式Package。

语义对象沿用原70个ID，审查、映射、审计Fragment与出版声明分别分配独立ID。原对象不删除或合并，不需要重定向；未来若发现某项边界需拆分，再记录新ID及迁移关系。此轮没有改变事实拥有者、Core或已批准发布边界，无需重复创建同原则ADR。

## 3. 必须区分的两种坐标与两种保真

当前94份来源证据精确定位于M1派生Note。它们能够证明“本批正文来自哪份Note的哪段字节”，不能把这些offset直接放到原始HTML中使用。

本轮20个审计Fragment选择原始HTML Entry的完整原始字节范围，关联Artifact、Entry及claimed Mapping。其范围明确、原字节可复核，但它只是整页审计包络；不是45条能力的逐条原始语义边界，也不证明从HTML到某一Library正文的文字/结构一一对应。

现有可执行`core.source-fragment@0.1.0`实验Schema仅有字符串digest、简单locator等字段；规范[Fragment结构](../milestone-0/schema-proposal.md#48-source-fragment-与-provenance-locator)及[保真协议](../milestone-0/integrity-protocols.md)要求原始结构事件流、独立文件摘要/语义摘要、解析/解码收据，以及逐Unit的Fidelity Coverage Map。**旧Schema结构通过不等于已实现这些规范要求。** 本轮明确标记raw-byte摘要，未冒用事件协议摘要或Full Fidelity。

六份共享参考继续完整保存，包括一页中未出题的主题；它们不是已经批准的六条原子规则。后续正式Library拆分必须有独立语义边界和对应保真单元，不得从本轮文件数量反推节点数量。

## 4. 包边界提案

[机器提案](../../experiments/rule-cluster-formalization-batch-1/review-bundle/metadata/package-plan.json)按当前最小可维护范围区分：

| 包 | 维护内容 | 内容依赖 |
|---|---|---|
| audit | 原始工件/完整Inventory的锁定引用、来源声明、证据与审核 | 无 |
| common | 六份完整共享来源参考及其后续独立规则表达 | 无 |
| spells | 11份法术本体与施法契约 | common |
| creatures | 八对象及45个拥有者能力、调用覆盖 | common、spells |

非audit包将audit作为受限构建依赖提案，不能把它伪装成公开可读内容。四者暂以同一local-owner访问域为前提，实际Access Policy尚待确认；只写private标签不能代替访问域/Principal判定。命名、版本化范围、语言、规则环境、来源声明和所需Schema都记录在提案中，Rights unknown不授予再分发许可。未来转公开包须单独满足Disclosure、Rights及公开Receipt要求，本轮不处理公开发布。

魅魔与梦魔互相引用在creatures包内，不产生包级循环。模块划分与出版分类分别维护，common不因为收录MM条目便把其他事实改属MM。包大小可在正式组装前调整，不改变事实ID。

## 5. 现在仍未完成什么

[机器可读问题清单](../../experiments/rule-cluster-formalization-batch-1/review-bundle/metadata/issues/open.json)记录四类剩余门禁：

1. **规则内容终审**：70个待审对象及254项字段的正式采用决定；既有3项采用判断保留原依据和适用范围，不重写原文。此前P6仅确认内部候选，不替代此决定。
2. **来源关联审核**：20条claimed Mapping可按“接受该关联声明但不升级verified”的范围审核；仍不得把译文变成官方中文或声称未知出版资料已查明。
3. **规范保真实施与验证**：本批尚无通过的Source/Library事件、Coverage Map及引用/地址/可见性裁决链。这是实际技术缺口，不能仅靠用户说“同意”消除。正式忠实转写节点激活及Full声明保持阻塞。
4. **包策略确认**：具体私有发布边界、同域Principal及依赖提案尚待确认；当前不组装正式Package。

因此，本报告不请求用户对一个尚未满足保真门禁的正式包进行整体批准。规则内容可以先审阅，但尚不能宣布“正式补齐全部完成”或发送正式替换指令。

## 6. 可复核的验证与下一施工边界

[本轮验证报告](../../experiments/rule-cluster-formalization-batch-1/reports/validation.json)分别报告材料检查Passed、正式对象批准0、Full Fidelity Not Run。9项错误注入覆盖缺未出题对象、伪造批准、伪造Full、升级来源身份/权利、未知依赖、原始/派生坐标混淆、删除保真阻断及包循环；都修改内存副本，不覆盖原始失败或来源。

下一施工目标应严格限于本批的规范保真链：先让一个含表格/引用/调用依赖的实际对象跑通Source与Library事件、精确选择范围和Coverage Map，再扩到本批其他对象；源脚本/CSS等不执行，未知可见性不能自动删除。遇到真实文字/结构差异保留阻断，不篡改M1或来源。协议字段与已存在实验Schema不一致处应采用独立版本并保留旧验证器；若改变已确认契约则补相应规范/ADR。这个缺口关闭后，再汇总真正可批准的规则集合和包组装范围。
