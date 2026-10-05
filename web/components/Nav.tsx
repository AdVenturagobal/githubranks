import Link from "next/link";
import { Lang, T } from "@/lib/i18n";
import SearchBox from "./SearchBox";
import LangSwitch from "./LangSwitch";

export default function Nav({ lang, tt }: { lang: Lang; tt: T }) {
  return (
    <header className="nav">
      <div className="wrap nav-inner">
        <Link href={`/${lang}/`} className="wordmark">
          <span className="logo-tile">G</span>Git<em>Rise</em>
        </Link>
        <Link className="dim" href={`/${lang}/board/global/`}>{tt.global}</Link>
        <Link className="dim" href={`/${lang}/#rising`}>{tt.risingNav}</Link>
        <Link className="dim" href={`/${lang}/archive/`}>{tt.archive}</Link>
        <Link className="dim" href={`/${lang}/about/`}>{tt.methodology}</Link>
        <span className="nav-spacer" />
        <SearchBox lang={lang} tt={tt} />
        <LangSwitch lang={lang} label={tt.langSwitch} />
      </div>
    </header>
  );
}

export function Footer({ lang, tt }: { lang: Lang; tt: T }) {
  return (
    <footer>
      <div className="wrap">
        <p>
          GitRise — {tt.tagline}{" "}
          Data: GitHub REST/GraphQL API, snapshots daily at 00:30 Beijing time.{" "}
          <Link href={`/${lang}/about/`}>{tt.methodology}</Link>
          {" · "}
          <a href="/feed.xml">RSS</a>
        </p>
        <p>Not affiliated with GitHub, Inc. Repository names and descriptions belong to their owners.</p>
      </div>
    </footer>
  );
}
