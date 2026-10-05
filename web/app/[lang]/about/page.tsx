import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Nav, { Footer } from "@/components/Nav";
import { getMeta } from "@/lib/data";
import { LANGS, Lang, t } from "@/lib/i18n";

export function generateStaticParams() {
  return LANGS.map((lang) => ({ lang }));
}

export const metadata: Metadata = { title: "Methodology" };

const EN = [
  ["What we track", "Every public GitHub repository with more than 1,000 stars. Our collector discovers them through the official GitHub Search API (sharded by star range) and re-verifies membership weekly."],
  ["How rankings are computed", "We snapshot the total star count of every tracked repository daily at 00:30 Beijing time via the GitHub GraphQL API. Net stars gained = end-of-period total − start-of-period total. Growth rate = net ÷ start × 100%. If the start value is 0 or missing we show N/A; negative growth is shown as-is."],
  ["Periods", "Day = the last complete Beijing-time calendar day. Week = Monday to Sunday, Beijing time. Month = the 1st to month end, Beijing time. Week and month boards are marked “in progress” with the latest capture time until the period closes."],
  ["Why not GitHub Trending", "GitHub Trending is a black box: no numbers, no history, no categories. We publish the exact inputs of every rank so you can verify them yourself."],
  ["Missing data policy", "If a snapshot fails or a repository is temporarily unreachable, affected entries are omitted from the board and flagged — we never estimate or fabricate numbers."],
  ["Categories and summaries", "Repositories are classified by rules over topics and descriptions (version rules-v1), with confidence scores; low-confidence projects stay unlisted in category boards. Chinese summaries are machine-generated via an AI model and marked “auto-translated”; original descriptions are kept verbatim."],
  ["Data source and rights", "All data comes from the official GitHub API under its terms of use. Repository names and descriptions belong to their owners. This site is not affiliated with GitHub, Inc."],
] as const;

const ZH = [
  ["追踪范围", "所有 Star 数大于 1,000 的 GitHub 公开仓库。采集器通过 GitHub 官方 Search API（按 Star 区间分片）发现项目，每周重新核验名单。"],
  ["排名如何计算", "我们每天北京时间 00:30 通过 GitHub GraphQL API 快照所有追踪仓库的总 Star 数。净增 Star = 期末总数 − 期初总数；增长率 = 净增 ÷ 期初 × 100%。期初为 0 或缺失时显示 N/A；负增长如实展示。"],
  ["统计周期", "日榜 = 最近一个完整的北京时间自然日；周榜 = 北京时间周一至周日；月榜 = 北京时间每月 1 日至月底。周榜与月榜在周期结束前标注“进行中”并显示最近采集时间。"],
  ["与 GitHub Trending 的区别", "GitHub Trending 是黑盒：没有数字、没有历史、没有分类。我们公开每个名次的具体输入数字，你可以自行核验。"],
  ["缺失数据策略", "快照失败或仓库暂时不可达时，受影响的条目会从榜单中略去并明确标注——我们绝不估算或编造数字。"],
  ["分类与摘要", "项目按 topics 与描述的规则体系分类（版本 rules-v1），带置信度；低置信度项目不进入分类榜单。中文摘要由 AI 模型生成并标注“自动翻译”；英文原文描述逐字保留。"],
  ["数据来源与权利", "全部数据来自 GitHub 官方 API，遵守其使用条款。仓库名称与描述归其所有者所有。本站与 GitHub, Inc. 无关联。"],
] as const;

export default function About({ params }: { params: { lang: string } }) {
  if (!LANGS.includes(params.lang as Lang)) notFound();
  const lang = params.lang as Lang;
  const tt = t(lang);
  const meta = getMeta();
  const sections = lang === "zh" ? ZH : EN;

  return (
    <>
      <Nav lang={lang} tt={tt} />
      <main className="wrap" data-pagefind-body>
        <section className="page-head" style={{ paddingBottom: 8 }}>
          <span className="eyebrow">{tt.heroEyebrow}</span>
          <h1>{tt.methodology}</h1>
        </section>
        {sections.map(([h, body]) => (
          <section className="panel" key={h}>
            <h2 style={{ margin: "0 0 8px", fontSize: 18 }}>{h}</h2>
            <p style={{ margin: 0, color: "var(--ink-soft)" }}>{body}</p>
          </section>
        ))}
      </main>
      <Footer lang={lang} tt={tt} />
    </>
  );
}
