"use client";

import { usePathname } from "next/navigation";
import { Lang, otherLang } from "@/lib/i18n";

/** Switches /en/... <-> /zh/... while preserving the current page. */
export default function LangSwitch({ lang, label }: { lang: Lang; label: string }) {
  const pathname = usePathname() || `/${lang}/`;
  const alt = otherLang(lang);
  const target = pathname.replace(/^\/(en|zh)(\/|$)/, `/${alt}$2`);
  return (
    <a className="lang-btn" href={target}>{label}</a>
  );
}
