# 华为云码道（CodeArts）使用提示词清单

> 用途：解决华为智能体创新赛「码道深度使用 **25 分**」这一唯一卡点。
> 官方评分细则逐字：「码道在开发全流程的覆盖度（**环境搭建、代码生成、调试排错、文档生成**等）」＋「Prompt 设计质量与工具使用效率」＋「使用证明材料的完整性与真实性」。
> 本清单严格按这四项编排。**每条执行一次 → 截图一次**，全部截图放入 `codearts_proof/`。

---

## 操作方式

1. 登录华为云码道：`https://developer.huaweicloud.com/codeartsco.html`
2. 在码道中打开 PayPilot 工程目录（或把对应文件内容贴给它）。
3. **逐条复制下面「提示词」框内原文**粘贴发送。
4. 每条保存 3 张图：① 对话与 Prompt 原文 ② 码道回答/生成的代码 ③ 本地执行结果终端。
5. 同时保留码道 IDE 插件的**操作日志与记录**（官方明确列为证明材料）。

---

## A. 环境搭建（覆盖第 1 项）

### A1 — 生成一键安装与环境自检脚本

**提示词：**
```
这是我的项目 PayPilot（纯 Python 标准库，零第三方依赖的 AI 购物支付智能体）。
目录结构：paypilot/（agent.py catalog.py policy.py reasoning.py paypal.py
mock_paypal.py receipts.py renewals.py grid.py web.py cli.py api.py context.py）、
eval.py、server.py、openapi.yaml、requirements.txt。

请帮我生成两个文件：
1) scripts/setup.sh —— 一键环境搭建脚本，要求：检测 Python 版本 >= 3.9、创建
   虚拟环境、安装 requirements.txt、打印环境自检结果。
2) scripts/doctor.py —— 环境自检脚本，检查 Python 版本、必需模块是否可导入、
   eval.py 是否可执行，全部检查项以 PASS/FAIL 打印并以退出码反映结果。

约束：只使用 Python 标准库；脚本要能在 Windows 与 Linux 都可运行（Windows 用
python 命令）。输出完整文件内容。
```

**截图**：对话 + 生成脚本 + 跑 `python scripts/doctor.py` 的终端输出。

---

## B. 代码生成（覆盖第 2 项）

### B1 — 为策略引擎新增一道真实护栏

**提示词：**
```
阅读 paypilot/policy.py（现有 Policy 类、PolicyDecision 类、check(policy, product,
daily_spent=0.0) 函数）。

请为策略引擎新增一道护栏「商户黑名单模糊匹配」：
- 需求：Policy 增加字段 blocked_merchant_patterns（字符串列表，支持子串匹配）。
- check() 在判定前先做模糊匹配：若 product 的 merchant 命中任一 pattern（大小写
  不敏感），返回 DENY，decision 的 reason_code 用 MERCHANT_BLOCKED_FUZZY。
- 必须保持现有五道闸（单笔上限、日累计上限、类目白名单、商户黑名单精确匹配、
  人工审批阈值）行为不变，且**新增逻辑不得引入任何可被 LLM 覆写的参数**。

约束：纯标准库；改动后 `python eval.py` 必须仍是 172 passed, 0 failed（若断言数
变化请说明原因）。请给出：① 修改后的完整 policy.py ② 新增的断言代码（追加到
eval.py，用来覆盖新护栏）。
```

**截图**：对话 + 生成代码 + 跑 `python eval.py` 的新结果终端。

### B2 — 为目录检索增加可解释性字段

**提示词：**
```
阅读 paypilot/catalog.py 与 paypilot/reasoning.py。

需求：商品检索排序目前只给出命中信号数。请为候选商品增加「命中明细」
match_details 字段，记录每个匹配信号来自哪个字段（name / category / tags /
price_range），并让 reasoning 生成的解释里引用这些字段作为证据。

约束：纯标准库；保持零依赖；不得改动 POLICY 判定路径；给出完整改动代码与
对应的新增断言。改完说明 `python eval.py` 的断言数变化。
```

**截图**：对话 + 生成代码 + 终端结果。

---

## C. 调试排错（覆盖第 3 项）

### C1 — 制造并修复一个真实缺陷

**提示词：**
```
我在 paypilot/renewals.py（订阅续费管理模块，约 565 行）里遇到一个缺陷：
当日累计消费刚好等于日上限时，边界判定不稳定——有时 ALLOW 有时 DENY。

请：
1) 定位导致边界不稳定的具体代码位置（给出行号与原因，例如浮点比较或未定义的
   等号归属）；
2) 给出修复方案（建议引入显式边界语义并统一浮点比较为定点分（cents）或带容差
   比较）；
3) 给出修复后的完整代码片段；
4) 给出一条回归断言，锁死「日累计 == 日上限」必须 DENY 的行为。
```

**截图**：对话 + 码道定位与修复代码 + 修复后终端输出。

### C2 — 让码道解释并优化一段现有代码

**提示词：**
```
这是 paypilot/agent.py 的片段（粘贴文件全文或关键函数）。
请：① 逐步解释 PERCEIVE→SEARCH→SELECT→POLICY→EXPLAIN→EXECUTE→CAPTURE 这条
决策链的实现；② 指出其中「策略引擎覆写路径对 LLM 不可见」是如何做到的；
③ 若有可优化点（异常处理、日志、可读性）请给出具体改动建议。
```

**截图**：对话 + 解释与建议。

---

## D. 文档生成（覆盖第 4 项）

### D1 — 生成 OpenAPI 文档与架构说明

**提示词：**
```
阅读 openapi.yaml 与 paypilot/api.py。
请生成：① 一份中文 API 使用文档（每个端点的用途、请求示例、响应示例、错误码）；
② 一份架构说明（模块依赖图 + 数据流 + 策略引擎隔离设计），要求能直接放进
readme/ 目录。输出 Markdown 格式。
```

**截图**：对话 + 生成的 Markdown。

### D2 — 生成部署运行说明

**提示词：**
```
阅读 render.yaml、server.py、paypilot/web.py。
请生成部署运行说明文档，包含：环境依赖清单、一键安装脚本、本地启动步骤
（python -m paypilot serve 等）、云端部署步骤、健康检查端点说明、常见问题排查。
输出 Markdown，要求按文档可完整复现运行。
```

**截图**：对话 + 生成的文档。

---

## 交付自检（打包前逐项确认）

- [ ] A 组 ≥1 条，含脚本与执行输出截图
- [ ] B 组 ≥2 条，含生成代码与 `python eval.py` 结果截图
- [ ] C 组 ≥1 条，含定位过程与修复后结果截图
- [ ] D 组 ≥2 条，含生成的 Markdown 文档
- [ ] 码道 IDE 插件**操作日志/记录**已导出
- [ ] 全部图片命名可读（如 `codearts_proof/B1_policy_fuzzy_01.png`）
- [ ] 所有截图为**真实操作记录**，不做任何合成或伪造

---

## 打包结构（严格按官方 5 文件夹）

```
PayPilot_<队名>_v1.0_<联系方式>.zip
├── ppt/                     # HUAWEI_PPT.html 打印为 PDF
├── project/                 # 可运行 Demo（源码 + 一键脚本）
├── video/                   # paypilot_demo.mp4（21.53s，<3min）
├── codearts_proof/          # 本清单执行产生的全部截图 + IDE 日志
└── readme/                  # 说明文档（依赖/安装/部署/开源组件/码道应用总结）
```

> 官方命名规范要求：`作品名称+队伍名称+版本号+联系方式`。
