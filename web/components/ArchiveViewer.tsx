"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { ArchiveItem, Board, BoardEntry } from "@/lib/data";
import type { Lang, T } from "@/lib/i18n";

function Row({ e, lang, tt }: { e: BoardEntry; lang: Lang; tt: T }) {
  const summary = (lang === "zh" ? e.sum?.zh : e.sum?.en) || e.desc;
  return (
    <tr>
      <td className={`rank mono ${e.rank <= 3 ? "top" : ""}`}>{e.rank}</td>
      <td>
        <Link className="repo" href={`/${lang}/repo/${e.name}/`}>{e.name}</Link>
        <div className="sum">{summary}</div>
      </td>
      <td className={`net mono r ${e.net >= 0 ? "up" : "down"}`}>
        {e.net >= 0 ? "+" : ""}{e.net.toLocaleString()}
      </td>
      <td className="total mono r">{e.end.toLocaleString()}</td>
      <td className="r"><span className="growth mono">
        {e.growth === null ? "N/A" : `${e.growth > 0 ? "+" : ""}${e.growth}%`}
      </span></td>
    </tr>
  );
}

export default function ArchiveViewer({
  lang, tt, index,
}: {
  lang: Lang; tt: T; index: ArchiveItem[];
}) {
  const [selected, setSelected] = useState<ArchiveItem | null>(index[0] ?? null);
  const [board, setBoard] = useState<Board | null>(null);
  const [loading, setLoading] = useState(false);

  const load = async (item: ArchiveItem) => {
    setSelected(item);
    setLoading(true);
    try {
      const r = await fetch(`/data/${item.file}`);
      setBoard(r.ok ? await r.json() : null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (index.length > 0) load(index[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const groups = (["day", "week", "month"] as const).map((p) => ({
    period: p, items: index.filter((i) => i.period === p),
  }));

  return (
    <div className="archive-layout">
      <aside className="archive-list">
        {groups.map((g) => g.items.length > 0 && (
          <div key={g.period} className="archive-group">
            <div className="archive-group-title mono">{tt[g.period]}</div>
            {g.items.map((i) => (
              <button key={i.file}
                className={`archive-item ${selected?.file === i.file ? "on" : ""}`}
                onClick={() => load(i)}>
                {i.label}
              </button>
            ))}
          </div>
        ))}
      </aside>
      <div className="archive-board" style={{ opacity: loading ? 0.4 : 1 }}>
        {!board ? (
          <div className="empty">{index.length === 0 ? tt.insufficient : "…"}</div>
        ) : (
          <div className="board-card">
            <table className="board">
              <thead>
                <tr>
                  <th>{tt.rank}</th><th>{tt.project}</th>
                  <th className="r">{tt.net}</th><th className="r">{tt.total}</th>
                  <th className="r">{tt.growth}</th>
                </tr>
              </thead>
              <tbody>
                {board.entries.map((e) => <Row key={e.name} e={e} lang={lang} tt={tt} />)}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
