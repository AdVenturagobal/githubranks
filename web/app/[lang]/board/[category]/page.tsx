import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Nav, { Footer } from "@/components/Nav";
import BoardTable from "@/components/BoardTable";
import { getBoard, getMeta } from "@/lib/data";
import { LANGS, Lang, t } from "@/lib/i18n";

export function generateStaticParams() {
  const meta = getMeta();
  const cats = ["global", ...(meta?.categories ?? []).map((c) => c.id)];
  return LANGS.flatMap((lang) => cats.map((category) => ({ lang, category })));
}

export function generateMetadata({
  params,
}: {
  params: { lang: string; category: string };
}): Metadata {
  const meta = getMeta();
  const cat = meta?.categories.find((c) => c.id === params.category);
  const name = cat ? cat[params.lang === "zh" ? "zh" : "en"] : "All projects";
  return {
    title: `${name} — GitHub ${params.category === "global" ? "rankings" : "category rankings"}`,
    description: `Daily, weekly and monthly net-star-growth GitHub rankings: ${name}. Transparent numbers, Beijing-time periods.`,
  };
}

export default function CategoryBoard({
  params,
}: {
  params: { lang: string; category: string };
}) {
  if (!LANGS.includes(params.lang as Lang)) notFound();
  const lang = params.lang as Lang;
  const tt = t(lang);
  const meta = getMeta();
  const cat = meta?.categories.find((c) => c.id === params.category);
  if (params.category !== "global" && !cat) notFound();

  const board = getBoard(`${params.category}-day`);
  const title = params.category === "global"
    ? tt.global
    : cat![lang === "zh" ? "zh" : "en"];

  return (
    <>
      <Nav lang={lang} tt={tt} />
      <main className="wrap" data-pagefind-body>
        <nav className="chips" aria-label={tt.categories}>
          <Link className={`chip ${params.category === "global" ? "active" : ""}`} href={`/${lang}/`}>
            {tt.global}
          </Link>
          {(meta?.categories ?? []).map((c) => (
            <Link key={c.id}
              className={`chip ${params.category === c.id ? "active" : ""}`}
              href={`/${lang}/board/${c.id}/`}>
              {lang === "zh" ? c.zh : c.en}
            </Link>
          ))}
        </nav>
        <div className="page-head" style={{ padding: "24px 0 0" }}>
          <span className="eyebrow">{tt.boardEyebrow}</span>
          <h1>{title}</h1>
        </div>
        <BoardTable lang={lang} tt={tt} boardKey={params.category}
          initial={board} initialPeriod="day" />
      </main>
      <Footer lang={lang} tt={tt} />
    </>
  );
}
