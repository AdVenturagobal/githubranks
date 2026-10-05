import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Nav, { Footer } from "@/components/Nav";
import Sparkline from "@/components/Sparkline";
import CopyBox from "@/components/CopyBox";
import { getMeta, getRepo, listRepoPages } from "@/lib/data";
import { LANGS, Lang, t } from "@/lib/i18n";

export function generateStaticParams() {
  const pages = LANGS.flatMap((lang) =>
    listRepoPages().map(({ owner, name }) => ({ lang, owner, name }))
  );
  // output:export forbids an empty param list; emit a sentinel that 404s
  return pages.length ? pages : [{ lang: "en", owner: "_", name: "_" }];
}

export function generateMetadata({
  params,
}: {
  params: { lang: string; owner: string; name: string };
}): Metadata {
  const repo = getRepo(params.owner, params.name);
  const full = `${params.owner}/${params.name}`;
  return {
    title: full,
    description: repo?.sum?.en || repo?.desc || `${full} star history and ranking on GitRise.`,
  };
}

export default function RepoPage({
  params,
}: {
  params: { lang: string; owner: string; name: string };
}) {
  if (!LANGS.includes(params.lang as Lang)) notFound();
  const lang = params.lang as Lang;
  const tt = t(lang);
  const meta = getMeta();
  const repo = getRepo(params.owner, params.name);
  if (!repo) notFound();

  const full = `${params.owner}/${params.name}`;
  const summary = (lang === "zh" ? repo.sum?.zh : repo.sum?.en) || repo.desc;
  const latest = repo.history.at(-1)?.s;
  const cat = meta?.categories.find((c) => c.id === repo.classification.category);

  return (
    <>
      <Nav lang={lang} tt={tt} />
      <main className="wrap" data-pagefind-body>
        <section className="detail-hero">
          <h1>{full}</h1>
          <p style={{ maxWidth: 640, margin: "0 0 12px" }}>
            {summary}
            {lang === "zh" && repo.sum?.zh && (
              <span style={{ color: "var(--faint)", fontSize: 12 }}> · {tt.autoTranslated}</span>
            )}
          </p>
          <div className="meta">
            {latest !== undefined && (
              <span className="star-pill">★ {latest.toLocaleString()}</span>
            )}
            {repo.lang && <span>{repo.lang}</span>}
            {repo.license && <span>{repo.license}</span>}
            {cat && <span>{lang === "zh" ? cat.zh : cat.en}</span>}
            <a href={`https://github.com/${full}`} rel="noopener noreferrer"
              style={{ textDecoration: "underline" }}>
              GitHub ↗
            </a>
          </div>
          <div style={{ marginTop: 10 }}>
            {repo.classification.tags.map((tg) => (
              <span className="tag" key={tg}>{tg}</span>
            ))}
          </div>
        </section>

        <section className="panel">
          <h2 style={{ margin: "0 0 12px", fontSize: 18 }}>{tt.trackedSince}</h2>
          {repo.history.length >= 2
            ? <Sparkline points={repo.history} />
            : <p style={{ color: "var(--ink-soft)" }}>{tt.insufficient}</p>}
        </section>

        {(repo.why || (repo.events && repo.events.length > 0)) && (
          <section className="panel">
            <h2 style={{ margin: "0 0 12px", fontSize: 18 }}>{tt.eventsTitle}</h2>
            {repo.why && (
              <div className="why-line" style={{ marginBottom: 12 }}>
                <span className="why-label">{tt.whyLabel}</span>
                {lang === "zh" ? repo.why.zh : repo.why.en}
              </div>
            )}
            <ul className="event-list">
              {(repo.events ?? []).map((ev, i) => (
                <li key={i}>
                  <span className="mono">{ev.date}</span>
                  {ev.type === "release" && <span>📦 {tt.evRelease.replace("{tag}", ev.tag ?? "")}</span>}
                  {ev.type === "hackernews" && (
                    <span>🔺 {tt.evHN.replace("{points}", String(ev.points ?? ""))}
                      {ev.title ? ` — ${ev.title}` : ""}</span>
                  )}
                  {ev.type === "new_repo" && <span>✨ {tt.evNew}</span>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {repo.badge && (
          <section className="panel">
            <h2 style={{ margin: "0 0 6px", fontSize: 18 }}>{tt.badgeTitle}</h2>
            <p style={{ margin: "0 0 14px", color: "var(--ink-soft)", fontSize: 14 }}>{tt.badgeHint}</p>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={repo.badge.src} alt={repo.badge.label} style={{ display: "block", marginBottom: 14 }} />
            <CopyBox
              text={`[![${repo.badge.label}](https://gitrise.pages.dev${repo.badge.src})](https://gitrise.pages.dev/en/repo/${full}/)`}
              copyLabel={tt.copy} copiedLabel={tt.copied}
            />
          </section>
        )}
      </main>
      <Footer lang={lang} tt={tt} />
    </>
  );
}
