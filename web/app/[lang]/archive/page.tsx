import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Nav, { Footer } from "@/components/Nav";
import ArchiveViewer from "@/components/ArchiveViewer";
import { getArchiveIndex, getMeta } from "@/lib/data";
import { LANGS, Lang, t } from "@/lib/i18n";

export function generateStaticParams() {
  return LANGS.map((lang) => ({ lang }));
}

export const metadata: Metadata = {
  title: "Archive",
  description: "Past GitHub net-star-growth boards: complete days, weeks and months.",
};

export default function ArchivePage({ params }: { params: { lang: string } }) {
  if (!LANGS.includes(params.lang as Lang)) notFound();
  const lang = params.lang as Lang;
  const tt = t(lang);
  const index = getArchiveIndex();

  return (
    <>
      <Nav lang={lang} tt={tt} />
      <main className="wrap" data-pagefind-body>
        <div className="page-head" style={{ paddingBottom: 16 }}>
          <span className="eyebrow">{tt.boardEyebrow}</span>
          <h1>{tt.archiveTitle}</h1>
          <p className="note">{tt.archiveNote}</p>
        </div>
        <ArchiveViewer lang={lang} tt={tt} index={index} />
      </main>
      <Footer lang={lang} tt={tt} />
    </>
  );
}
