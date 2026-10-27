# 本地伤害计算器隔离样机

本会话继续开发；代码放在LoreBuddy实验目录。不是生产Runtime、正式Package或Terminal功能。

2026-10-23修补：`local-damage-calculator@0.1.1-candidate.1`；比较接口`research-draft-2`要求双方分别携带创建时的`input_snapshot`，不兼容无快照的旧草案。规则Profile仍为`draft-1`，规则范围和运算顺序未变。当前结果见[两项定向修补](../../docs/milestone-2/local-damage-calculator-fix-2026-10-23.md)。

## 打开

先构建，然后用本地浏览器打开生成的 `build/local-damage-calculator-research-2026-10-22/index.html`。单文件不依赖服务端、CDN、模型或网络；本轮自动浏览器工具拒绝file协议，真实浏览器交互尚未实测。不能把静态扫描说成已观察到零请求。

```sh
python3 -B experiments/local-damage-calculator/build.py
node --test experiments/local-damage-calculator/test.mjs experiments/local-damage-calculator/compare-regression.test.mjs
node experiments/local-damage-calculator/check-bundle.mjs
```

无第三方运行时依赖；构建使用Python标准库，验证用Node内置test。这些实验标签不承担正式知识身份。固定的本地接入候选及SHA-256清单位于`build/local-damage-calculator-candidate-2026-10-23-r1/`，不是Commit、正式Package或公开Release。

## 结构与边界

- `profile.mjs`：系统专属词汇、操作上限和规则引用，不是平台Core。
- `engine.mjs`：校验、固定顺序、逐阶段数值及关联减损；不修改输入或实例状态。
- `compare.mjs`：核对目标/事件/修订、防御快照、数值与阶段；只返回路由建议，不调用模型。
- `snapshot.mjs`：分别捕获请求及实际使用的选定定义、目标防御和现场范围；分离复制、深冻结、验证及规范比较。不是摘要签名或真实事实的证明。
- `synthetic-fixtures.json`：来自研究阶段的四个合成模板，与能力UUID一并预加载；不是实际怪物库。
- `demo.mjs`、`index.template.html`：手工输入现场事实和模拟AI草案；草案先捕获，工具再运算。不是实际模型盲测。
- `test.mjs`：执行固定46案例、额外边界和4个实际错误实现注入。
- `build.py`：明确五模块内联，不修改M1或既有怪物候选。
- `compare-regression.test.mjs`：两项缺陷的18组回归，不改原46案例Gold。
- `candidate-revision.json`、`freeze-candidate.py`：固定本地接入候选修订、源码、案例和文件摘要，已存在候选拒绝覆盖。
- `check-bundle.mjs`：构建语法、静态资源/网络API扫描与Node运算基准，不代替浏览器验收。

研究中扁平的`defenses`只存在于测试Gold。正式样机函数`calculate(request, context)`不允许调用请求覆盖固定防御；由用户/消费者预加载到context。界面上的防御勾选是人工构造合成现场，不是AI获得改写防御的权限。现场动态防御尚无独立生产适配器。

context不是秘密，也不是安全沙箱。`verified_facts`可以核对独立现场输入；若调用方把模型编造的数据当作context，双向比较仍可能一致地错。预加载定义和现场事实的接入责任不能省略。

`input_snapshot`必须在草案创建时捕获并随草案保存。工具在执行时独立捕获自己的输入；比较器不接收当前context来补绑旧草案，不给缺字段填默认值。数字先做完整性/类型校验，`linked_reduction`只有能力明确无关联减损时才允许显式null，省略该字段不合法。演示页需先点击“固定这份模拟草案”，之后修改现场输入不会更新旧快照。

目前只支持单事件、单目标、单伤害类型；未知/未支持字段拒算。多个问题保留完整issues，失败不返回默认伤害0。免疫只作数值归零，不判断其他触发时序。HP扣除、长休、临时HP、混合伤害、2014和其他例外均未支持。

## 来源与许可

未复制或安装Foundry、Battlecast、dnd-srd-engine或骰子库；本批独立实现，仅参考已确认规格。没有引入第三方代码许可证，也未替用户决定本项目自有代码的开源许可。

系统规则根据SRD5.2.1改编为数值操作与合成模板；页面内保留SRD要求的署名和CC BY 4.0链接，并说明改编。没有打包CHM正文、中文怪物卡或历史答卷。此样机没有经过公开Release Rights审核，不能把本次代码测试当作商业发行许可。

具体范围、测试结果与限制见[样机报告](../../docs/milestone-2/local-damage-calculator-prototype-2026-10-22.md)。
