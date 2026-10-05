import Link from "next/link";
import { notFound } from "next/navigation";
import Nav, { Footer } from "@/components/Nav";
import BoardTable from "@/components/BoardTable";
import InlineSpark from "@/components/InlineSpark";
import { getBoard, getMeta } from "@/lib/data";
import { LANGS, Lang, t } from "@/lib/i18n";

export function generateStaticParams() {
  return LANGS.map((lang) => ({ lang }));
}

const GLYPHS: Record<string, string> = {
  "ai-ml": "AI", "developer-tools": "⌘", "web-frontend": "</>",
  "backend-api": "{}", "data-databases": "▤", "cloud-devops": "☁",
  "security-privacy": "⚿", "productivity-automation": "↻",
  "mobile-desktop": "▣", "games-media": "▶",
};

export default function Home({ params }: { params: { lang: string } }) {
  if (!LANGS.includes(params.lang as Lang)) notFound();
  const lang = params.lang as Lang;
  const tt = t(lang);
  const meta = getMeta();
  const dayBoard = getBoard("global-day");
  const risingDay = getBoard("rising-day");
  const riser = dayBoard?.entries?.[0];

  return (
    <>
      <Nav lang={lang} tt={tt} />
      <main className="wrap" data-pagefind-body>
        <section className="hero">
          <div className="hero-left">
            <div className="eyebrow">{tt.heroEyebrow}</div>
            <h1>{tt.tagline}</h1>
            <p className="sub">
              {tt.sub.replace("{n}", (meta?.tracked_repos ?? 0).toLocaleString())}
            </p>
            <div className="stats mono">
              <div className="stat">
                <div className="stat-num">{(meta?.tracked_repos ?? 0).toLocaleString()}</div>
                <div className="stat-label">{tt.statsTracked}</div>
              </div>
              <div className="stat">
                <div className="stat-num">{meta?.latest_snapshot ?? "—"}</div>
                <div className="stat-label">{tt.statsUpdated}</div>
              </div>
              <div className="stat">
                <div className="stat-num">{meta?.categories.length ?? 0}</div>
                <div className="stat-label">{tt.statsFields}</div>
              </div>
            </div>
          </div>
          {riser && (
            <Link className="riser" href={`/${lang}/repo/${riser.name}/`}>
              <div className="label">{tt.biggestRiser}</div>
              <div className="name">{riser.name}</div>
              <div className="big mono">+{riser.net.toLocaleString()} ★</div>
              <div className="riser-spark">
                <InlineSpark values={riser.spark ?? []} width={240} height={44} />
              </div>
              <div className="why">
                {(lang === "zh" ? riser.sum?.zh : riser.sum?.en) || riser.desc}
              </div>
              {riser.why && (
                <div className="why-line" style={{ marginTop: 10 }}>
                  <span className="why-label">{tt.whyLabel}</span>
                  {lang === "zh" ? riser.why.zh : riser.why.en}
                </div>
              )}
            </Link>
          )}
        </section>

        <section>
          <div className="sec-head" style={{ marginTop: 8 }}>
            <div className="top">
              <div>
                <span className="eyebrow">{tt.fieldsEyebrow}</span>
                <h2>{tt.categories}</h2>
                <p className="sub-note">{tt.fieldsSub}</p>
              </div>
              <Link className="view-all" href={`/${lang}/board/global/`}>{tt.viewAll} ↗</Link>
            </div>
          </div>
          <div className="cat-grid">
            <Link className="cat-card p-5" href={`/${lang}/board/global/`}>
              <span className="glyph">★</span>
              <h3>{tt.global}</h3>
              <span className="count">{(meta?.tracked_repos ?? 0).toLocaleString()} {tt.reposUnit}</span>
            </Link>
            {(meta?.categories ?? []).map((c, i) => (
              <Link key={c.id} className={`cat-card p-${i % 3 === 0 ? 0 : i % 3 === 1 ? 1 : 2}`} href={`/${lang}/board/${c.id}/`}>
                <span className="glyph">{GLYPHS[c.id] ?? "#"}</span>
                <h3>{lang === "zh" ? c.zh : c.en}</h3>
                <span className="count">{(c.repos ?? 0).toLocaleString()} {tt.reposUnit}</span>
              </Link>
            ))}
          </div>
        </section>

        <section>
          <div className="sec-head">
            <div className="top">
              <div>
                <span className="eyebrow">{tt.boardEyebrow}</span>
                <h2>{tt.boardTitle}</h2>
              </div>
              <Link className="view-all" href={`/${lang}/archive/`}>{tt.archiveTitle} ↗</Link>
            </div>
          </div>
          <BoardTable lang={lang} tt={tt} boardKey="global" initial={dayBoard} initialPeriod="day" />
        </section>

        <section id="rising">
          <div className="sec-head">
            <div className="top">
              <div>
                <span className="eyebrow">{tt.risingEyebrow}</span>
                <h2>{tt.risingTitle}</h2>
                <p className="sub-note">{tt.risingSub}</p>
              </div>
            </div>
          </div>
          <BoardTable lang={lang} tt={tt} boardKey="rising" initial={risingDay} initialPeriod="day" />
        </section>
      </main>
      <Footer lang={lang} tt={tt} />
    </>
  );
}
