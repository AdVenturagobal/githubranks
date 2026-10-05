# 部署手册（全免费路径）

预计 30 分钟，按顺序执行。所有资源免费；唯一可选支出是自定义域名（~$10/年，可先用免费的 `*.pages.dev` 上线）。

## 0. 前置

- GitHub 账号；本仓库已 push 为 **public**（Actions 才无限免费）。
- OpenRouter API key（用户已有）。
- Cloudflare 账号（免费注册）。

## 1. 配置 GitHub Secrets

仓库 → Settings → Secrets and variables → Actions，添加：

| Secret | 来源 |
|---|---|
| `OPENROUTER_API_KEY` | OpenRouter 后台 |
| `CLOUDFLARE_API_TOKEN` | Cloudflare → My Profile → API Tokens → 创建，模板 "Edit Cloudflare Workers"，权限含 `Account.Cloudflare Pages: Edit` |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare dashboard 右侧栏 Account ID |

## 2. 首次数据采集（本地或 Actions 手动触发）

本地快速验证（需 Personal Access Token，public_repo 只读即可）：

```bash
cd collector
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxx
python discover.py      # ~20-40 分钟，分片发现 >1000 star 仓库
python snapshot.py      # GraphQL 批量快照
export OPENROUTER_API_KEY=sk-or-xxx
python summarize.py     # 首批 50 个摘要
python build_data.py
```

或在 Actions 页面手动运行 `snapshot-and-build`（discover=true）。注意：**第一天日榜/周榜/月榜会显示"快照历史不足"**，这是预期行为——净增需要两个快照点，次日 00:30 后自动出现。绝不回填假数据。

## 3. Cloudflare Pages 首次部署

Actions 的 `deploy-web` workflow 会自动完成（push 到 main 触发）。首次需要在 Cloudflare Pages 后台确认项目 `gitrise` 已创建；之后每次数据提交自动部署。

免费额度：带宽不限、请求不限、构建 500 次/月（我们每日 1 次）。

## 4. 自定义域名（建议，AdSense 需要）

1. 购买域名（Cloudflare Registrar 价格最低且免隐私保护费，如 `gitrise.dev`）。
2. Pages → Custom domains → 添加，自动签发 SSL。
3. 在 `web/app/layout.tsx` 更新 metadata 的 `metadataBase`。
4. 提交 Google Search Console 验证，添加 `web/public/robots.txt` 指向 sitemap。

## 5. 接入 AdSense（流量变现）

1. 域名上线 + 有 2 周真实内容后申请 AdSense。
2. 审核通过后，在 `app/layout.tsx` 的 `<head>` 加入 AdSense 脚本（一个 `adsense.tsx` 组件即可，代码位见注释）。
3. 广告位建议：榜单表格上方一个自适应横幅 + 项目详情页中部一个。**不要**弹窗。

## 6. 回滚

- 数据错误：`git revert` 对应 data commit 并 push，deploy workflow 自动重新发布上一版榜单。
- 站点错误：Cloudflare Pages → Deployments → 任一历史构建 "Rollback to this deployment"。

## 冒烟测试清单（部署后逐项验证）

- [ ] `/en/` 与 `/zh/` 首页显示榜单与"昨日最大黑马"卡片（含走势图）
- [ ] 分类页 10 个全部可访问，日/周/月 tab 切换正常
- [ ] 顶部搜索框能搜到项目并跳转（Pagefind 索引存在：`/pagefind/pagefind.js` 返回 200）
- [ ] `/archive/` 历史榜单可回看，周/月分组正常
- [ ] 任一项目详情页显示 30 天走势图
- [ ] `/feed.xml` RSS 可访问；`/og.png` 分享图可访问
- [ ] "进行中"徽标与采集时间显示正确
- [ ] 手机端表格不溢出（走势/总 Star 列在小屏隐藏）
- [ ] `data/meta.json` 的 `tracked_repos` 与预期数量级一致
