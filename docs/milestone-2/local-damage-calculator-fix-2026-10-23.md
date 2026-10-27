# 计算器两项修补与Terminal接入候选

日期：2026-10-23。本轮严格限定用户指出的输入绑定与结果完整性两项缺陷，保留现有算术核心与规则范围。状态：修补验证通过；本地接入候选已固定；Terminal接纳及浏览器验收未进行。

## 1. 复现与修补

| 缺陷 | 修前实际观察 | 修后 |
|---|---|---|
| 同事件输入未完整绑定 | 12和13在相同豁免/抗性下都算3，比较matched | 双方分别携带创建时的完整支持范围输入快照，返回input_mismatch |
| 双方缺最终数值 | 删除damage_taken及linked_reduction，仍matched | 工具缺项返回invalid_tool_result；草案缺项返回invalid_draft |
| 工具缺binding | 抛出TypeError | 返回invalid_tool_result，不抛异常、不自动请求模型 |

[修前观察记录](../../build/local-damage-calculator-fix-2026-10-23/prepatch-reproduction.json)来自改动前实际执行；没有给未冻结的旧工作区追补虚构源码摘要。测试日志中的原问题保持为失败证据，不把此前55项通过当作覆盖了这两项。

`snapshot.mjs`负责捕获、分离复制、深冻结、完整性验证与按值比较。快照包含原始请求的全部支持字段，以及实际选定的能力定义、目标防御、范围声明、核实输入和修订；不携带无关能力库。对象键顺序不影响比较，数值类型、缺字段或不支持的非JSON值不能被规范化成相同null。

`engine.mjs`只新增执行时的输入快照，不改计算分支、取整、范围或返回数值。`compare.mjs`先检查工具及草案的binding、快照、阶段和最终字段，再核对身份与输入，最后比较数值。linked_reduction只有能力明确不产生关联减损时允许显式null；字段缺失、字符串、布尔值、负数、小数、非有限数等不能进入matched。结构损坏的工具结果先返回修复工具结果指示，不误走高级模型规则核查。

演示页单独增加“固定这份模拟草案”操作。固定时捕获草案自己的输入；后来改12/13或成功/失败不会重绑旧草案。点击“计算并核对”只读取既存草案并让工具独立捕获当前输入，不再在比较时给旧数字套上当前现场。创建新草案需再次显式固定。没有扩充规则或加入真实AI。

## 2. 回归结果

`node --test experiments/local-damage-calculator/test.mjs experiments/local-damage-calculator/compare-regression.test.mjs`：**73/73通过**，其中原有55项全部通过，新增18组回归。组内包含多侧、多类型负例，不把循环组合数虚报成独立模型样本。

新增覆盖同值不同原伤害、零伤害下不同豁免、旧快照不可变、同标签但实际防御/定义改变、JSON传输与键序、双方/单方缺最终字段、错误数值类型、正确null边界、缺工具binding/阶段、缺/残缺快照、工具binding与自身快照矛盾、损坏的失败包、范围输入缺项及循环值。原X06/X07只提供身份，测试适配器补入其先前固定Gold中的数值以满足新完整性契约，没有修改原46案例Gold、降低断言或从当前工具结果反填数值。

新旧测试结果见[完整TAP日志](../../build/local-damage-calculator-fix-2026-10-23/tests.tap)。原4项算术故障注入仍通过。构建语法、静态离线约束及同输入重复构建验证通过；HTML当前35,065字节，约34.2 KiB。

浏览器实际操作仍Not Run；本轮未尝试绕过此前file协议策略。演示页操作改变已按代码路径核查，不冒充浏览器点击验证。没有运行真实AI、自动升模或战斗状态写入。

## 3. 固定交付与兼容性

源码修订：`local-damage-calculator@0.1.1-candidate.1`。
比较接口修订：`research-draft-2`。
输入快照修订：`input-snapshot-1`。
规则Profile修订保持`draft-1`。

这是实验接口的有意收紧：旧的无快照草案须从原现场创建新草案，不能从当前现场补绑；不得给缺失的最终数值默认0或null。此更改不修改LoreBuddy平台Schema或旧来源；无需迁移正式节点，因为还没有正式发布节点或计算器Runtime接纳。

固定候选目录：[local-damage-calculator-candidate-2026-10-23-r1](../../build/local-damage-calculator-candidate-2026-10-23-r1/)。

- [candidate-manifest.json](../../build/local-damage-calculator-candidate-2026-10-23-r1/candidate-manifest.json)：源码修订、验证边界、逐文件大小及SHA-256；payload保留相对路径，独立复制后可运行Node测试。
- [SHA256SUMS](../../build/local-damage-calculator-candidate-2026-10-23-r1/SHA256SUMS)：覆盖payload及Manifest，不包含自身，避免摘要循环。
- payload中固定源码、原46案例、新回归脚本、合成模板、HTML、修前观察与本轮测试/构建凭据。白名单复制，不包含CHM、真实怪物库、历史模型答卷、凭据或其他项目内容。

已存在候选拒绝覆盖；可用`python3 -B experiments/local-damage-calculator/freeze-candidate.py --verify build/local-damage-calculator-candidate-2026-10-23-r1`重新核对。后续修订另建候选，不能修改此固定副本。源工作区可以继续开发，但不能据工作区新状态宣称旧候选已升级。

这是本地集成交付快照，不是签名、Git Commit、正式Package、商业Rights批准或公开Release。历史权利与事实边界保持不变。

## 4. 给Terminal的使用边界

候选供之后“伤害输入旁计算助手”设计与独立验收使用，本轮不修改Terminal、不向其他会话发送消息。接入方需在草案创建时保存其快照，由工具执行生成另一份，先核对现场一致再使用比较结果；必须保留缺输入、未支持、工具格式错误及规则分歧的区别。

候选仍只处理单次/单目标/单类型。真实AI、自动升模、浏览器实际验收和战斗状态写入分别安排；matched只表示两份完整数据在支持范围内一致，仍不能发现共同编造的现场事实，也不能证明整段自然语言正确。本轮到候选固定与摘要核验停止。
