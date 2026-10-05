# GitRise — GitHub 净增 Star 榜（中英双语）

**GitHub Trending 告诉你什么在热，GitRise 告诉你什么在真正崛起。**
按领域分类、按北京时间自然日/周/月统计的真实净增 Star 榜单，附 AI 中文摘要。全免费架构，纯流量变现。

## 为什么是 GitRise（解决的痛点）

GitHub 官方 Trending：算法黑盒无数字、无历史榜、无分类、仅英文、看不出增长势头。
GitRise：透明净增数字 + 日/周/月可回溯 + 10 个领域分类 + 中英双语 + 增长率。

详见 [docs/core-value.md](docs/core-value.md)。

## 架构（全免费）

```
GitHub Actions (cron, 公开仓库免费无限)
  ├─ discover.py    每周发现 star>1000 的仓库 (Search API 星标分片)
  ├─ snapshot.py    每日 00:30 北京时间 GraphQL 批量快照
  ├─ summarize.py   OpenRouter 免费模型生成中英摘要 (每日 ≤50, 幂等)
  ├─ jev_classify.py (可选) Jev 结构化决策模型补分类低置信度仓库
  └─ build_data.py  计算净增/增长率 → 静态 JSON
        │
Cloudflare Pages (免费: 全球 CDN, 带宽不限) ← Next.js 静态导出
```

无数据库：数据即 git 仓库中的 JSON，天然版本化、可回滚。
详见 [docs/architecture.md](docs/architecture.md)（含免费额度核算）。

## 功能清单

- 日/周/月净增 Star 榜（全球榜 + 10 个领域榜），中英双语
- **智能搜索**：Pagefind（构建期静态索引，零服务器，支持中英文）
- **历史榜单**：日榜 14 天 / 周榜 8 周 / 月榜 6 个月可回看（仅完整周期）
- 项目详情页 30 天走势图；榜单行内 7 日迷你走势
- RSS 订阅（`/feed.xml`）、OG 分享卡、sitemap、移动端适配
- AI 中文摘要（OpenRouter 免费模型）+ 可选 Jev 二级分类

## 本地开发

```bash
# 采集器测试（离线）
cd collector && pip install -r requirements.txt pytest
python -m pytest tests/ -q

# 生成演示数据并构建榜单 JSON（仅本地预览，非生产数据）
python seed_demo.py && python build_data.py

# 启动前端
cd ../web && npm install && npm run dev    # http://localhost:3000/en/
```

## 部署

见 [docs/deployment.md](docs/deployment.md)。30 分钟从零到上线，三个 Secrets 即可。

## 数据口径（不可妥协）

- 净增 = 期末快照 − 期初快照；期初缺失 → 条目不出现，绝不编造
- 期初为 0 → 增长率显示 N/A；负增长如实显示
- 日榜 = 最近完整北京时间自然日；周/月榜进行中时标注采集时间
- 采集失败 → 自动开 issue 告警，榜单停更而非显示假数据

## 变现

不注册、不付费。Google AdSense（主力）+ 分类赞助位（中期）。见 core-value.md。

## 引流渠道

- **SEO**：静态页 + sitemap + 分类×周期×语言×项目详情页矩阵。
- **dev.to 周报**（已自动化）：每周一从真实周榜生成数据周报，`canonical_url` 指回本站（借 dev.to 权重曝光、链接权重归我们）。默认发布为 draft 人工确认。分析见 [docs/traffic-devto.md](docs/traffic-devto.md)。
