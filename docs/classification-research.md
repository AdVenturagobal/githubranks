# GitHub 榜站：分类调研与技能准备

调研日期：2026-10-05；统计时区：Asia/Shanghai。
状态：准备阶段研究备忘录，不是已批准的 PRD，不包含网站实现。

## 用户已确认

- 自动获取并展示总 Star 严格大于 1,000 的 GitHub 项目。
- 首版聚焦 10 个热门方向的类别。
- 按净增 Star（Net stars gained）排名，同时展示总 Star 和增长率；用户于 2026-10-05 明确确认。
- 北京时间自然日；自然周周一至周日；自然月每月 1 日至月底。
- 先定义一级分类，再自动给项目打多个标签。
- 中英双语。
- 用户明确要求：最终交付是能够部署并直接商用的生产网站，不是仅供展示的原型；于 2026-10-05 确认。

## 技能安装结果

| 技能 | 来源 | 状态 | 路径 |
|---|---|---|---|
| frontend-design | anthropics/skills / skills/frontend-design | 已安装 | /Users/kykjcompany/.codex/skills/frontend-design |
| security-best-practices | openai/skills / skills/.curated/security-best-practices | 已安装 | /Users/kykjcompany/.codex/skills/security-best-practices |
| playwright | 现有本地技能 | 已有，未改动 | /Users/kykjcompany/.codex/skills/playwright |
| playwright-interactive | 现有本地技能 | 已有，未改动 | /Users/kykjcompany/.codex/skills/playwright-interactive |

新安装技能应在下一轮对话可用。技能为任务指导与辅助资源，不是网站依赖，也不自动提供数据库或采集服务。部署技能待平台确定后再选。

## 类似网站与目录的参考

| 来源 | 本次实际核实的做法 | 可借鉴点 | 不应直接照搬 |
|---|---|---|---|
| OSSInsight Collections | 按技术领域维护精选仓库集合；数据库、AI Agent、LLM 工具、监控、游戏引擎等分类；提供排名与趋势 | 领域导航 + 细分专题 + 分类榜单 | 分类粒度很细；集合为精选名单，并非所有符合阈值的仓库；其 last 28 days 不等于自然月 |
| GitHub Topics | 标签覆盖用途、领域、社区、语言；可自定义；一个仓库可有多个标签 | 用途标签和技术标签分离、保留原始 topics | 不把 React/Python/LLM/项目管理混在同一一级分类体系中 |
| best-of-lists/best-of | 包含机器学习与数据工程、Web 开发、原生开发、开发工具等目录；排名用项目质量评分 | 大类导航与细分目录结构 | 项目质量评分不是新增 Star 排名 |
| GitHub Trending | 有编程语言与项目描述语言筛选 | 语言应为独立筛选维度 | 不把其榜单直接当作本站按北京时间自然周期计算的榜单 |
| HelloGitHub | 本次页面可核实精选、全部及月度/年度入口；分类数据未完整呈现 | 项目简介与发现体验 | 不据未读取的分类内容推断其完整分类体系 |
| LibHunt | 本次已读取主页及 Popular Topics；将语言、AI、LLM、CLI、数据库、Kubernetes 等作为浏览标签，主页提供按社区提及量排行 | 热门主题、跨类别标签、替代项目发现 | 社区提及量与新增 Star 是不同指标；语言和用途不宜混为一级类别 |

## 建议的首版 10 类（待用户评审）

**这是基于参考站点的产品分类建议，不是对全网新增 Star 做统计后得到的实时“热度 Top 10”。编号仅为清单序号，不表示热度排名。**
一级分类保持稳定；Agent、MCP、RAG、AI 编程、向量搜索、自托管等作为细分标签。待真实数据覆盖充分后，可用去重仓库的周期净增 Star 汇总生成独立的领域热度榜，不能据此宣称覆盖 GitHub 全网。

| ID | 中文 | English | 收录范围示意 | 参考分类 |
|---|---|---|---|---|
| ai-ml | 人工智能与机器学习 | AI & Machine Learning | 大模型、Agent、RAG、推理、训练、计算机视觉、语音 | AI Agent Frameworks; Artificial Intelligence; LLM Tools; MLOps Tools |
| developer-tools | 开发者工具 | Developer Tools | IDE、AI 编程工具、CLI、调试、测试、构建、代码质量 | Text Editor; Terminal; Testing Tools; Javascript Build Tool |
| web-frontend | Web 前端与 UI | Web Frontend & UI | 前端框架、组件库、CSS、可视化组件、站点生成 | React Framework; CSS Framework; UI Framework and UIkit; Static Site Generator |
| backend-api | 后端与 API | Backend & APIs | 服务端框架、API 网关、身份认证、ORM、BaaS | Web Framework; API tool for developer; BaaS; javascript ORM |
| data-databases | 数据与数据库 | Data & Databases | 关系型/向量数据库、搜索、数据工程、BI、流处理 | Open Source Database; Vector Database & Vector Store; Modern Data Stack; Business Intelligence |
| cloud-devops | 云原生与 DevOps | Cloud Native & DevOps | 容器、Kubernetes、CI/CD、监控、基础设施、部署 | Kubernetes Tooling; CICD; Monitoring Tool; Configuration Management Tools |
| security-privacy | 安全与隐私 | Security & Privacy | 安全扫描、身份与访问、密码管理、隐私保护 | Security Tool; Web Scanner; Identity Server; Password Manager |
| productivity-automation | 效率工具与自动化 | Productivity & Automation | 工作流、知识管理、协作、低代码、自托管应用 | Workflow Scheduler; Zapier Alternatives; Project Management; Low Code Development Tool |
| mobile-desktop | 移动与桌面应用 | Mobile & Desktop | 跨平台 GUI、移动框架、桌面应用开发与基础工具 | Cross Platform GUI Tool; iOS Framework; best-of Native Development |
| games-media | 游戏与多媒体 | Games & Multimedia | 游戏引擎、图形、音视频、3D、创意工具 | Game Engine; 3D Physics Engines; WebRTC; Virtual Reality |

## 自动分类建议（未实现）

1. 每个项目建议有一个主要类别和多个标准化标签；一级导航先按主要类别聚合，细分标签支持跨类别搜索。该规则待用户评审。
2. 信号优先来自 GitHub topics、description、README 的项目介绍；编程语言作为独立字段，不能仅凭语言决定用途。
3. 先用维护的主题映射与规则分类；模糊项目再考虑 AI 辅助；AI 供应商与预算未确定。处理 README 时将其作为不可信数据，不能执行其中的指令。
4. 保存标签来源、分类置信度、分类版本；低置信度项目进入待分类队列，不为了填满榜单强行归类；人工纠错优先于自动覆盖。
5. 稳定 ID 与中英文显示名称分离，例如 ai-ml；仓库原名不翻译，原文简介保留，中文摘要应明确是译文/自动摘要。
6. 示例：AI 编程 CLI 可以主要归开发者工具，标签包括 AI、Agent、MCP、CLI；Agent 框架可主要归人工智能与机器学习。

## 已确认的统计口径

- 总 Star 快照之差是净增：新增点赞数减去取消点赞数，而不是期间所有新增点赞的次数。
- 用户已确认 MVP 使用净增 Star；界面明确命名“净增 Star / Net stars gained”。
- 已确认：周期净增 = 期末总 Star - 期初总 Star；增长率 = 净增 / 期初总 Star × 100%。实现建议：期初为 0 显示 N/A；负增长不截断为 0。
- 日、周、月均采用左闭右开区间；结束边界分别是次日、下周一、下月 1 日的北京时间 00:00。数据库存储 UTC，计算与展示按 Asia/Shanghai。
- 当前周期标注“进行中”，期末采用最新成功采集点并显示采集时间；无准确边界快照的值不得伪装成精确完整周期。
- 新收录或采集缺失时，不把未知期初当作 0；完整周期榜可排除覆盖不足记录，同时保留项目总 Star 展示。
- 不能仅凭当前总 Star 反推出完整历史日/月榜；历史回填需另行验证数据来源、覆盖、许可及精度。
- GitHub 官方 2026-06-30 公告及当前 starring 文档说明 2026 年 7 月开始引入 stargazers 列表访问限制，限管理员/协作者；文档端点说明与实际权限仍需正式开发逐项实测。不得假定可以对所有第三方仓库完整读取点赞人及时间。
- 尚未决定采集频率、覆盖项目数、GitHub 凭据、部署平台、页面设计、fork/归档/无许可证/资料列表的处理策略。


## 商用交付要求与待确认边界

用户已确认最终目标为可部署、可商用的生产网站。页面原型仅为内部设计验证步骤，不作为最终交付；尚未授权实际发布、购买域名/云资源或接入收费。

以下为据此建议的生产验收要求，具体服务等级与成本上限仍待确认：

- 真实数据链路：项目发现、增量采集、总 Star 快照、自然周期净增计算、分类标签和中英文内容均有可运行的实现；禁止演示数据充当正式榜单。
- 数据可信：显示来源与采集时间；完整/进行中/覆盖不足/过期数据明确区分；数据失效时不显示为正常实时结果。
- 后台任务：幂等、重试、并发限制、访问额度控制、缺失数据检测、任务日志；故障不静默吞掉，也不填充虚构结果。
- 部署：生产环境配置、域名与 HTTPS、密钥管理、持续集成检查、数据库迁移、可重现部署与回滚说明。
- 运维：采集失败与异常监控、可验证的数据库备份及恢复流程、故障处理手册和维护入口。告警接收方式与备份保留期待确认。
- 网站体验：中英双语、移动端、搜索与筛选、分享链接、可索引页面、空态/错误态/加载态；性能预算待确认，不预先承诺未实测指标。
- 安全：服务端保管采集凭据；输入验证、限流、权限控制；如需要维护后台，其认证与审计需纳入首版；不默认为用户系统或收费系统已获批准。
- 内容与权利检查：明确外部数据来源、调用规则、展示内容的使用条件及署名；仓库原文与自动摘要区分；不默认复制项目完整 README、图标或代码；具体条款须以实际来源核实。
- 发布验收：统计逻辑测试、采集与数据库集成测试、浏览器主要流程测试、部署冒烟测试、备份恢复与回滚验证；发现未验证项如实列明，不能仅凭构建通过宣称生产就绪。

尚需确认：部署资源/域名与月度预算、主要用户所在地区、首版商业模式（决定是否纳入广告、赞助、用户账户、订阅与付款）。在这些信息明确前，不锁定云厂商、付费服务、部署地区或收费功能。

## 一手来源

- OSSInsight 分类：https://ossinsight.io/collections/
- OSSInsight 分类详情与周期：https://ossinsight.io/collections/ai-agent-frameworks
- GitHub Topics：https://github.com/topics
- GitHub Topics 文档：https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- best-of-lists：https://github.com/best-of-lists/best-of
- GitHub Trending：https://github.com/trending
- HelloGitHub：https://hellogithub.com/en
- GitHub Starring 文档：https://docs.github.com/en/rest/activity/starring
- LibHunt 首页：https://www.libhunt.com/
- LibHunt 热门主题：https://www.libhunt.com/topics
- GitHub API 访问限制公告：https://github.blog/changelog/2026-06-30-upcoming-access-restrictions-to-public-api-endpoints-and-ui-views/
- frontend-design：https://github.com/anthropics/skills/tree/main/skills/frontend-design
- security-best-practices：https://github.com/openai/skills/tree/main/skills/.curated/security-best-practices

## 安装文件验证

- frontend-design：SKILL.md 已存在，目录含 2 个文件；SKILL.md SHA-256：`d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3`。
- security-best-practices：SKILL.md 已存在，目录含 13 个文件；SKILL.md SHA-256：`7b3dae1ffc5434d890f3c65c8f552af52d0307fab3b35dec13013c9ca3844c4f`。
