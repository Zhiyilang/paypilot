# PayPilot → GitHub 推送（PayPal 必需，Gitee 不算）

> **为什么必须推 GitHub**：PayPal 官方规则要求 repo 必须在 **GitHub / GitLab / Bitbucket**，
> **Gitee 链接评委不接受**。当前 `github.com/Zhiyilang/paypilot` 是 10-18 旧代码，
> 必须覆盖为当前版（本地已验证 **172/172** 通过）。
> Gitee 版本仅作备份，不计入资格。

## 你只需做（约 5 分钟，浏览器登录即凭证，无需 PAT）

打开 **Git Bash**（或任意终端），整段粘贴：

```bash
cd "/d/桌面/part-time jobs/GitHub/paypilot"

# 若首次连接该仓（本地仓暂无 remote）：
git remote add origin https://github.com/Zhiyilang/paypilot.git

# 若提示 remote 已存在，改用：
# git remote set-url origin https://github.com/Zhiyilang/paypilot.git

# 推送当前版，覆盖 GitHub 上的旧代码
git push -u origin main --force
```

- 弹窗登录 GitHub → 用 **Zhiyilang** 账号登录即可（OAuth，无需 Personal Access Token）。
- `--force` 是因为旧仓有不同历史，我们要用当前版整仓覆盖（这是提交仓，安全）。

## 推送后请回我「pushed」

我会自动：
1. 匿名核验 `https://api.github.com/repos/Zhiyilang/paypilot` 返回 `200`；
2. 确认默认分支含当前代码（`paypilot/web.py` 10-22 更新）；
3. 把 `PAYPILOT_SUBMISSION.md` 的 Repo 链接改为 GitHub 主链。

## 兜底：若 GitHub 默认分支是 master 而非 main

旧仓可能默认分支是 `master`。若上面 `git push` 后评委打开看到的是空/旧内容，运行：

```bash
git push -u origin main:master --force
```

并在 GitHub 仓库 **Settings → Branches** 把 default branch 设为 `main`（或保持 `master`，只要默认分支是推上去的那条即可）。

## 验收标准（推送成功后评委可见面）

- `git clone https://github.com/Zhiyilang/paypilot.git` 能拿到当前代码；
- `python eval.py` → **172 passed, 0 failed**；
- README 顶部有 MIT License 标识（PayPal 硬规则：public + license visible）。
