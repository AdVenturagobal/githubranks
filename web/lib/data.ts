import fs from "node:fs";
import path from "node:path";

const DATA = path.join(process.cwd(), "public", "data");

export type Summary = { en?: string; zh?: string };
export type BoardEntry = {
  rank: number; name: string; net: number; start: number; end: number;
  growth: number | null; lang: string | null; cat: string | null;
  tags: string[]; sum: Summary; desc: string; spark?: number[];
  mom?: "up" | "flat" | "down" | null; why?: Summary | null; events?: RepoEvent[];
};
export type RepoEvent = {
  type: "release" | "hackernews" | "new_repo";
  date: string; tag?: string; title?: string; points?: number; url?: string;
};
export type Badge = { src: string; label: string };
export type ArchiveItem = {
  period: string; label: string; start: string; end: string;
  file: string; count: number;
};
export type Board = {
  period: string; category: string | null; status: "ok" | "insufficient";
  in_progress: boolean; label_date: string | null;
  start_date: string | null; end_date: string | null;
  captured_at: string | null; entries: BoardEntry[];
};
export type Meta = {
  generated_at: string; latest_snapshot: string; captured_at: string;
  tracked_repos: number; min_stars: number; newcomer_repos?: number;
  categories: { id: string; zh: string; en: string; repos?: number }[];
};
export type RepoDetail = {
  name: string; desc: string; lang: string | null; license: string | null;
  created_at: string | null; sum: Summary;
  classification: { category: string | null; tags: string[] };
  history: { d: string; s: number }[];
  events?: RepoEvent[]; why?: Summary | null; badge?: Badge | null;
};

function readJson<T>(...parts: string[]): T | null {
  const p = path.join(DATA, ...parts);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8")) as T;
}

export const getMeta = () => readJson<Meta>("meta.json");
export const getArchiveIndex = () => readJson<ArchiveItem[]>("archive-index.json") ?? [];
export const getBoard = (key: string) => readJson<Board>(`board-${key}.json`);
export const getRepo = (owner: string, name: string) =>
  readJson<RepoDetail>("repos", owner, `${name}.json`);

export function listRepoPages(): { owner: string; name: string }[] {
  const dir = path.join(DATA, "repos");
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).flatMap((owner) =>
    fs
      .readdirSync(path.join(dir, owner))
      .filter((f) => f.endsWith(".json"))
      .map((f) => ({ owner, name: f.replace(/\.json$/, "") }))
  );
}
