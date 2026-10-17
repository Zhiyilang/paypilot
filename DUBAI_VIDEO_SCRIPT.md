# PayPilot 3 分钟演示视频 — 录屏脚本（PayPal 黑客松 + 迪拜大赛共用）

> 用途：PayPal AI Hackathon（要求 ≤3 分钟 YouTube 公开视频）+ 迪拜 Create AI Agents Championship（演示视频三件套之一）。
> 工具：任选录屏软件（Win+G Xbox Game Bar / OBS / 浏览器插件），麦克风可有可无（建议加，不加也能过）。
> 总时长控制：2:30–3:00。语速正常即可，不要赶。
> 命令已实测可跑（2026-10-16）：`python -m paypilot demo` 四场景全过、`python -m paypilot serve --port 8780` HTTP 200、`python eval.py` → **172 passed, 0 failed**。

---

## 录制前准备（1 分钟）

1. 打开项目目录：`D:\桌面\part-time jobs\GitHub\paypilot`
2. 终端字号调到 16–18（录出来评委看得清）
3. 关掉无关窗口和通知
4. 先空跑一遍 `python -m paypilot demo` 确认能跑（再跑 `python eval.py` 确认 172 passed 再录）
5. 开始录屏

## 脚本（照着念/打字即可）

### 【0:00–0:25】开场钩子
（终端，黑色背景，光标闪烁）
> "This is PayPilot — an AI shopping agent that spends money, but cannot be talked into a bad purchase."
> "Most AI agents today will happily rationalize a purchase you never authorized. PayPilot separates reasoning from authorization: the model proposes, and a hard-coded policy engine disposes."
> "It's pure Python standard library — zero dependencies. Everything you're about to see runs offline in mock mode, and the same code path executes real PayPal sandbox payments."

### 【0:25–0:55】场景 1：正常购买（顺利路径）
输入：
```
python -m paypilot demo
```
（让 Scenario 1 跑完：给妈妈买 50 美元以内园艺礼物）
> "First, the happy path. I ask for a birthday gift for my mom under fifty dollars, she loves gardening."
> "The agent parses my intent, ranks the catalog with evidence — price, rating, matched tags — and picks the garden tool set at thirty-four ninety-nine."
> "The policy engine checks: within the per-order limit, category allowed, daily budget fine. It creates a PayPal order and captures the payment. Here's the capture ID, and the full decision trail."

### 【0:55–1:20】场景 2 + 场景 3：护栏发力（视频高潮）
> "Now the important part — what happens when the request breaks the rules."
> "This one asks for a five-hundred-dollar luxury watch."
> （等 Scenario 3 输出 BLOCKED）
> "Blocked. Category not in the allowlist. No order was created, no money moved. And the model can't talk its way past this — the policy is code, not a prompt."
> "There's also a hold path: purchases above the approval threshold wait for a human. Scenario four shows an order held, then paid only after approval."

### 【1:20–1:50】Web 演示界面
新开一个终端：
```
python -m paypilot serve --port 8780
```
浏览器打开 `http://127.0.0.1:8780`
> "There's also a web console. I type the same request…"
> （提交表单，等结果）
> "…and you see the whole agent loop: intent, ranked candidates, the policy decision, the payment, and the receipt — every step with its evidence."

### 【1:50–2:15】测试与可信度
```
python eval.py
```
（让 172 passed 滚出来）
> "The project ships with one hundred seventy-one automated assertions covering every guardrail and the full payment loop, and CI runs green across three Python versions. Anyone can clone the repo and run the entire agent in thirty seconds — no keys, no setup."

### 【2:15–2:45】收尾
> "PayPilot is open source, MIT licensed, built for the PayPal AI Hackathon and the Dubai Create AI Agents Championship. The thesis is simple: an agent that can spend money should have to show its work — and a policy engine it cannot argue with."
> "Link in the description. Thanks for watching."

（停止录屏）

---

## 录制检查清单
- [ ] Scenario 1 出现 COMPLETED + MOCK-CAPTURE id
- [ ] Scenario 3 出现 BLOCKED / CATEGORY_NOT_ALLOWED
- [ ] Scenario 4 出现 HOLD → human approved → COMPLETED
- [ ] Web 界面表单提交后出现完整 decision trail
- [ ] eval.py 出现 "172 passed, 0 failed"
- [ ] 总时长 ≤ 3:00（超了就删减解说，别删演示）
- [ ] 上传 YouTube（公开），链接贴到 Devpost 提交表单 + 迪拜平台

## 上传后
- YouTube 标题建议：`PayPilot — an AI shopping agent with policy guardrails (PayPal sandbox)`
- 描述里放仓库链接：https://github.com/Zhiyilang/paypilot
- 把 YouTube 链接发给 AI（贴到对话里），我写进 Devpost/迪拜提交材料
