"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Board, BoardEntry } from "@/lib/data";
import type { Lang, T } from "@/lib/i18n";
import InlineSpark from "./InlineSpark";

const PERIODS = ["day", "week", "month"] as const;

function fmt(n: number) {
  return n.toLocaleString("en-US");
}

function Row({ e, lang, tt }: { e: BoardEntry; lang: Lang; tt: T }) {
  const [owner, name] = e.name.split("/");
  const summary = (lang === "zh" ? e.sum?.zh : e.sum?.en) || e.desc;
  const translated = lang === "zh" && e.sum?.zh;
  const why = e.why ? (lang === "zh" ? e.why.zh : e.why.en) : null;
  const momLabel = e.mom === "up" ? tt.momUp : e.mom === "down" ? tt.momDown : e.mom === "flat" ? tt.momFlat : null;
  return (
    <tr>
      <td className={`rank mono ${e.rank <= 3 ? "top" : ""}`}>{e.rank}</td>
      <td>
        <Link className="repo" href={`/${lang}/repo/${owner}/${name}/`}>{e.name}</Link>
        {momLabel && <span className={`mom mom-${e.mom}`}>{momLabel}</span>}
        <div className="sum">
          {summary || tt.noSummary}
          {translated && <span className="tr"> · {tt.autoTranslated}</span>}
        </div>
        {why && (
          <div className="why-line">
            <span className="why-label">{tt.whyLabel}</span>{why}
          </div>
        )}
        <div>
          {e.lang && <span className="tag">{e.lang}</span>}
          {e.tags.slice(0, 4).map((tg) => <span className="tag" key={tg}>{tg}</span>)}
        </div>
      </td>
      <td className="spark-cell"><InlineSpark values={e.spark ?? []} /></td>
      <td className={`net mono r ${e.net >= 0 ? "up" : "down"}`}>
        {e.net >= 0 ? "+" : ""}{fmt(e.net)}
      </td>
      <td className="total mono r">{fmt(e.end)}</td>
      <td className="r">
        <span className="growth mono">
          {e.growth === null ? "N/A" : `${e.growth > 0 ? "+" : ""}${e.growth}%`}
        </span>
      </td>
    </tr>
  );
}

export default function BoardTable({
  lang, tt, boardKey, initial, initialPeriod,
}: {
  lang: Lang; tt: T; boardKey: string; initial: Board | null; initialPeriod: string;
}) {
  const [period, setPeriod] = useState<(typeof PERIODS)[number]>(initialPeriod as any);
  const [board, setBoard] = useState<Board | null>(initial);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (period === initialPeriod) { setBoard(initial); return; }
    setLoading(true);
    fetch(`/data/board-${boardKey}-${period}.json`)
      .then((r) => (r.ok ? r.json() : null))
      .then((b) => { setBoard(b); setLoading(false); })
      .catch(() => setLoading(false));
  }, [period, boardKey, initial, initialPeriod]);

  const note = board
    ? board.period === "day" && board.label_date
      ? tt.dayNote.replace("{d}", board.label_date)
      : board.in_progress && board.start_date && board.captured_at
        ? tt.inProgress
            .replace("{since}", board.start_date)
            .replace("{at}", board.captured_at.slice(0, 16).replace("T", " ") + " UTC")
        : null
    : null;

  return (
    <div>
      <div className="sec">
        <div className="tabs" role="tablist">
          {PERIODS.map((p) => (
            <button key={p} role="tab" aria-selected={period === p}
              className={period === p ? "on" : ""} onClick={() => setPeriod(p)}>
              {tt[p]}
            </button>
          ))}
        </div>
        {board?.in_progress && <span className="badge">LIVE</span>}
        {note && <span className="note">{note}</span>}
      </div>

      {!board || board.status !== "ok" ? (
        <div className="empty">{tt.insufficient}</div>
      ) : (
        <div className="board-card">
          <table className="board">
            <thead>
              <tr>
                <th>{tt.rank}</th><th>{tt.project}</th>
                <th>{tt.trend7d}</th>
                <th className="r">{tt.net}</th><th className="r">{tt.total}</th>
                <th className="r">{tt.growth}</th>
              </tr>
            </thead>
            <tbody style={{ opacity: loading ? 0.4 : 1 }}>
              {board.entries.map((e) => <Row key={e.name} e={e} lang={lang} tt={tt} />)}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
