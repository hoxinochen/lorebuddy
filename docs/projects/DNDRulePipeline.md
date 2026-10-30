# DNDRulePipeline：D&D规则生产工作区

该项目从LoreBuddy的试点与方法论材料独立建立，用于D&D全库只读普查、机制候选分组及后续生产工具；LoreBuddy的平台Core继续跨TRPG，正式知识接纳仍按母项目合同执行。

| 入口 | 位置／状态 |
|---|---|
| 本机工作区 | `/Users/chenzehao/Projects/DNDRulePipeline` |
| 接手文档 | [START_HERE](/Users/chenzehao/Projects/DNDRulePipeline/docs/START_HERE.md) |
| 项目待办主本 | [BACKLOG](/Users/chenzehao/Projects/DNDRulePipeline/BACKLOG.md)（独立维护；登记不等于实施授权） |
| 当前优先：数值与条件性数值 | [职责与研究优先级](/Users/chenzehao/Projects/DNDRulePipeline/docs/decisions/adr-001-calculator-numeric-priority-2026-10-28.md)（计算无关内容标记保留；不要求计算器理解全部叙述） |
| 阶段1需求主本 | [计算层需求与缺口](/Users/chenzehao/Projects/DNDRulePipeline/docs/requirements/stage-1-calculation-layer.md)（Pipeline负责配方/契约/样本，Terminal决定呈现；r2已被Terminal接纳，本批对接、产品Review及Release/Archive均完成，阶段1首批闭环收口） |
| 阶段1固定交付 | [stage-1-damage-r2](/Users/chenzehao/Projects/DNDRulePipeline/docs/deliveries/stage-1-damage-r2.md)（r1历史阻塞在r2关闭；本批对接及Terminal产品Release/Archive完成，不自动变为正式规则批准） |
| 阶段1独立对接验收 | [2026-10-29验收收据](/Users/chenzehao/Projects/DNDRulePipeline/docs/reports/terminal-stage1-acceptance-2026-10-29.md)（44项＋新增8项、隔离新入口与正常持久化/撤销通过；保留首次驱动失败及Not Run） |
| 新Work交接 | [阶段1收口与阶段2讨论入口](/Users/chenzehao/Projects/DNDRulePipeline/docs/handoffs/stage1-closed-stage2-start-2026-10-29.md)（本批闭环结束；阶段2仅待讨论，不自动开工） |
| 全局导航框架 | [总体框架与横向选样](/Users/chenzehao/Projects/DNDRulePipeline/docs/research/global-mechanism-coverage-framework-2026-10-28.md)（待审去向已建；系统语义分类未完成） |
| 第一轮粗筛校准 | [9份完整页结果](/Users/chenzehao/Projects/DNDRulePipeline/docs/reports/semantic-coarse-screening-wave1-2026-10-28.md)（作者首读/复读完成；第二轮未执行，非独立审核或正式接纳） |
| 最新：修补与第二轮粗筛 | [10任务／9页结果](/Users/chenzehao/Projects/DNDRulePipeline/docs/reports/semantic-coarse-screening-wave2-2026-10-28.md)（两轮17份不同完整页；作者候选，暂停自动扩大） |
| 已有局部构件研究 | [恢复当前生命值对照](/Users/chenzehao/Projects/DNDRulePipeline/docs/research/component-discovery-healing-2026-10-28.md)（作者归纳与反例；不是最终原子目录） |
| 可组合构件有限验证 | [样本扩展结果](/Users/chenzehao/Projects/DNDRulePipeline/docs/reports/rule-component-expansion-2026-10-27.md)（作者案例；正式契约与下游接入未完成） |
| 轻量候选生产试验 | [作者表与模板编译](/Users/chenzehao/Projects/DNDRulePipeline/docs/reports/light-authoring-pilot-2026-10-28.md)（协议草案；不等于正式生产） |
| 项目互通约定 | [PROJECT_LINKS](/Users/chenzehao/Projects/DNDRulePipeline/docs/PROJECT_LINKS.md) |
| 机器可读定位 | [project-links.json](/Users/chenzehao/Projects/DNDRulePipeline/docs/project-links.json) |
| Obsidian镜像 | `/Users/chenzehao/Vaults/obsidian/obisidian/理工学习相关/DNDRulePipeline` |
| GitHub仓库 | [hoxinochen/DNDRulePipeline](https://github.com/hoxinochen/DNDRulePipeline)（Private，已建空仓库；尚未推送项目文件） |

当前已完成W1首版只读材料地图及再生族17页有限作者候选试点；全族整理、独立语义审核与正式规则生产未完成。继承P6是内部候选接纳，正式规则批准数仍为0。具体进度以子项目README/ROADMAP为准，本页仅作路由。

母项目保留原材料；子项目`reference/lorebuddy/`是固定快照，不自动跟随本仓改动。更新规范须显式引入，子项目成果返回LoreBuddy须另行验收，不因镜像或计算通过自动采纳。涉及D&D生产工具工作时先读取子项目AGENTS与接手入口；涉及平台规范时以母项目现行AGENTS及合同为准。发现冲突须显式记录，不猜测已同步。

文档镜像由子项目主本单向同步到Vault。本机路径不适用于其他机器；GitHub仓库地址已核验；本地origin已配置。首批本地提交已获用户授权；推送仍待单独确认，子项目文件及本页尚未同步到GitHub，远端文档互通仍待推送后核验。

## 当前设计入口（2026-10-27）

子项目已形成[W1只读全库普查设计提案](/Users/chenzehao/Projects/DNDRulePipeline/docs/design/corpus-census-v1.md)，对应输入账本、结构坐标、线索统计三个实施小步。本轮仅设计与文档镜像同步，程序尚未实施，不产生规则批准；后续状态以子项目为准。

## W1首版材料地图交付（2026-10-27后续）

用户随后授权脚本、自动化测试后直接全量执行；首版已完成，当前状态见[材料地图与验证报告](/Users/chenzehao/Projects/DNDRulePipeline/docs/reports/census-2026-10-27.md)。6,819份Note进入完整观察账本，56项测试及独立机械回读通过。保留HTML等检测盲区，不代表全库语义正确；W2/W3和正式规则生产未启动，正式批准仍为0。该状态承接前文设计阶段，未改变本仓M2准入或自动采用子项目数据。

语言目标已明确为简体中文、英语和日语；子项目新增[语言预留与兼容约定](/Users/chenzehao/Projects/DNDRulePipeline/docs/design/multilingual-reservation-v1.md)，不把显示名、词形语言或同名关系当规则身份与翻译批准。现有v1地图保留，未开始英日规则库或全量翻译。

再生族首批已完成，[结果与边界](/Users/chenzehao/Projects/DNDRulePipeline/docs/reports/regeneration-pilot-2026-10-27.md)：259候选页中审读17页，242页待审；全页去向和正反例保留。作者候选不等于独立审核或正式批准，本仓未自动接纳这些对象。
