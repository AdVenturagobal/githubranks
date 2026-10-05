"""Compute net-star-growth boards (day/week/month, Beijing time), historical
archive boards, 7-day sparklines, and an RSS feed — all as static JSON/XML
consumed by the Next.js site.

Period rules (confirmed 2026-10-05):
- Half-open intervals; boundaries at 00:00 Asia/Shanghai. A snapshot dated D
  is captured at D 00:30 Beijing = state at start of day D.
- net = end_snapshot - start_snapshot. growth = net/start*100.
- start==0 or missing -> growth is None ("N/A"), never faked as 0.
- In-progress period: end = latest successful snapshot, flagged
  "in_progress": true with captured_at shown.
- Missing start/end snapshot -> entry omitted ("insufficient coverage"),
  never fabricated.
Usage: python build_data.py
"""
import json
import logging
from datetime import datetime, timezone, timedelta, date
from xml.sax.saxutils import escape

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("build")

BEIJING = timezone(timedelta(hours=8))
BOARD_SIZE = 100
REPO_PAGES = 400          # union of top movers gets a detail page with history
ARCHIVE_SIZE = 20         # entries kept per archived board
ARCHIVE_DAYS = 14         # archived complete days
ARCHIVE_WEEKS = 8         # archived complete weeks
ARCHIVE_MONTHS = 6        # archived complete months
SITE = "https://gitrise.pages.dev"


def load_snapshots() -> dict[date, dict]:
    return {date.fromisoformat(f.stem): json.loads(f.read_text())
            for f in sorted(config.SNAPSHOT_DIR.glob("*.json"))}


def period_plan(latest: date, period: str) -> tuple[date, date, bool, date]:
    """(start_snap_target, end_snap_target, in_progress, label_date).

    A snapshot dated D is captured at D 00:30 Beijing = state at start of
    day D. Therefore:
    - day:   the last COMPLETE day = snap(latest) - snap(latest-1),
             labelled with that day (latest-1). Not in progress.
    - week:  current natural week, start = this Monday's snapshot,
             end = latest. In progress until Sunday.
    - month: current natural month, start = the 1st's snapshot,
             end = latest. In progress until month end.
    """
    if period == "day":
        return latest - timedelta(days=1), latest, False, latest - timedelta(days=1)
    if period == "week":
        monday = latest - timedelta(days=latest.weekday())
        return monday, latest, latest.weekday() != 6, monday
    first = latest.replace(day=1)
    nxt = (first + timedelta(days=32)).replace(day=1)
    return first, latest, latest < nxt - timedelta(days=1), first


def pick_snapshot(snaps: dict[date, dict], target: date, latest: date):
    """Nearest snapshot at or before target (<=2 days back). None if absent."""
    for delta in (0, 1, 2):
        d = target - timedelta(days=delta)
        if d in snaps and d <= latest:
            return d, snaps[d]
    return None


def sparkline(snaps: dict[date, dict], name: str, days: int = 7) -> list[int]:
    out = []
    for d in sorted(snaps)[-days:]:
        v = snaps[d]["stars"].get(name)
        if v is not None:
            out.append(v)
    return out


def window_net(snaps: dict[date, dict], name: str, end_d: date, days: int):
    """Net star change over the `days` window ending at end_d.
    None when either boundary snapshot or the repo value is missing
    (never interpolated, never fabricated)."""
    start = pick_snapshot(snaps, end_d - timedelta(days=days), end_d)
    end = pick_snapshot(snaps, end_d, end_d)
    if not start or not end:
        return None
    s, e = start[1]["stars"].get(name), end[1]["stars"].get(name)
    if s is None or e is None:
        return None
    return e - s


def momentum_state(cur: int | None, prev: int | None) -> str | None:
    """Week-over-week motion: up / flat / down. None when not computable.
    prev<=0 has no meaningful ratio; only flag real motion from a zero base."""
    if cur is None or prev is None:
        return None
    if prev <= 0:
        if cur >= 5:
            return "up"
        if cur < 0:
            return "down"
        return None
    ratio = cur / prev
    if ratio >= 1.5:
        return "up"
    if ratio <= 0.67:
        return "down"
    return "flat"


def compute_entries(repos, snaps, summaries, category, start, end,
                    size, with_spark=False, events_map=None, latest=None):
    events_map = events_map or {}
    entries = []
    if not (start and end and start[0] < end[0]):
        return entries
    s_map, e_map = start[1]["stars"], end[1]["stars"]
    for r in repos:
        if category and r["classification"].get("category") != category:
            continue
        s, e = s_map.get(r["full_name"]), e_map.get(r["full_name"])
        if s is None or e is None:
            continue  # insufficient coverage: omit, never fake
        net = e - s
        entry = {
            "name": r["full_name"], "net": net, "start": s, "end": e,
            "growth": round(net / s * 100, 2) if s > 0 else None,
            "lang": r.get("language"),
            "cat": r["classification"].get("category"),
            "tags": r["classification"].get("tags", []),
            "sum": summaries.get(r["full_name"]) or {},
            "desc": (r.get("description") or "")[:200],
        }
        if with_spark:
            entry["spark"] = sparkline(snaps, r["full_name"])
        if latest is not None:
            entry["mom"] = momentum_state(
                window_net(snaps, r["full_name"], latest, 7),
                window_net(snaps, r["full_name"], latest - timedelta(days=7), 7))
        ev = events_map.get(r["full_name"])
        if ev:
            entry["why"] = ev.get("reason")
            if ev.get("events"):
                entry["events"] = ev["events"]
        entries.append(entry)
    entries.sort(key=lambda x: (-x["net"], x["name"]))
    entries = entries[:size]
    for i, e in enumerate(entries):
        e["rank"] = i + 1
    return entries


def build_board(period, repos, snaps, summaries, category, events_map=None):
    latest = max(snaps)
    start_t, end_t, in_progress, label = period_plan(latest, period)
    start = pick_snapshot(snaps, start_t, latest)
    end = pick_snapshot(snaps, end_t, latest)
    entries = compute_entries(repos, snaps, summaries, category,
                              start, end, BOARD_SIZE, with_spark=True,
                              events_map=events_map, latest=latest)
    return {
        "period": period, "category": category,
        "status": "ok" if entries else "insufficient",
        "in_progress": in_progress,
        "label_date": label.isoformat(),
        "start_date": start[0].isoformat() if start else None,
        "end_date": end[0].isoformat() if end else None,
        "captured_at": end[1]["captured_at"] if end else None,
        "entries": entries,
    }


def _add_month(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return date(y, m, 1)


def build_archives(repos, snaps, summaries) -> list[dict]:
    """Completed past periods, global board only (top 20 each).

    Daily: label = the complete day, covered by snap(label) -> snap(label+1).
    Weekly: complete Mon-Sun weeks, covered by snap(monday) -> snap(next monday).
    Monthly: complete months, covered by snap(1st) -> snap(next 1st).
    Periods lacking boundary snapshots are skipped, never estimated."""
    latest = max(snaps)
    ranges: list[tuple[str, date, date, date]] = []  # (period, label, start, end)
    for i in range(1, ARCHIVE_DAYS + 1):
        label = latest - timedelta(days=i)
        ranges.append(("day", label, label, label + timedelta(days=1)))
    cur_monday = latest - timedelta(days=latest.weekday())
    for i in range(1, ARCHIVE_WEEKS + 1):
        end_b = cur_monday - timedelta(days=7 * (i - 1))
        ranges.append(("week", end_b - timedelta(days=7),
                       end_b - timedelta(days=7), end_b))
    first = latest.replace(day=1)
    for i in range(1, ARCHIVE_MONTHS + 1):
        end_b = _add_month(first, -(i - 1))
        start_b = _add_month(end_b, -1)
        ranges.append(("month", start_b, start_b, end_b))

    index = []
    for period, label, start_t, end_t in ranges:
        start = pick_snapshot(snaps, start_t, latest)
        end = pick_snapshot(snaps, end_t, latest)
        entries = compute_entries(repos, snaps, summaries, None,
                                  start, end, ARCHIVE_SIZE)
        if not entries:
            continue
        fname = f"board-arc-{period}-{label.isoformat()}.json"
        (config.WEB_DATA_DIR / fname).write_text(json.dumps({
            "period": period, "category": None, "status": "ok",
            "in_progress": False, "label_date": label.isoformat(),
            "start_date": start[0].isoformat(), "end_date": end[0].isoformat(),
            "captured_at": end[1]["captured_at"], "entries": entries,
        }, ensure_ascii=False))
        index.append({"period": period, "label": label.isoformat(),
                      "start": start[0].isoformat(), "end": end[0].isoformat(),
                      "file": fname, "count": len(entries)})
    (config.WEB_DATA_DIR / "archive-index.json").write_text(
        json.dumps(index, ensure_ascii=False))
    return index


def build_feed(board: dict, path, title, desc):
    """RSS 2.0 feed from the global day board (top 20)."""
    items = []
    for e in board.get("entries", [])[:20]:
        title = f"#{e['rank']} {e['name']} — +{e['net']:,} stars"
        link = f"{SITE}/en/repo/{e['name']}/"
        desc = escape((e.get("sum") or {}).get("en") or e.get("desc") or "")
        items.append(f"<item><title>{escape(title)}</title><link>{link}</link>"
                     f"<guid>{link}#{board.get('label_date')}</guid>"
                     f"<description>{desc}</description></item>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        f"<title>{escape(title)}</title>"
        f"<link>{SITE}/en/</link>"
        f"<description>{escape(desc)}</description>"
        + "".join(items) + "</channel></rss>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml)


def build_badges(boards, cat_names):
    """Static README badge for repos with a notable rank. Maintainer embeds
    it -> backlink + self-propagation. One badge per repo, best rank wins."""
    ranks = {}
    # week board is empty on Monday morning (start==end); fall back to day board
    g_period = "week" if boards["global-week"]["entries"] else "day"
    g_label = "this week" if g_period == "week" else "today"
    for i, e in enumerate(boards[f"global-{g_period}"]["entries"][:20], 1):
        ranks.setdefault(e["name"], (i, f"#{i} {g_label}"))
    for cat in config.CATEGORY_IDS:
        label = cat_names.get(cat, cat)
        c_period = "week" if boards[f"{cat}-week"]["entries"] else "day"
        c_label = "this week" if c_period == "week" else "today"
        for i, e in enumerate(boards[f"{cat}-{c_period}"]["entries"][:5], 1):
            if e["name"] not in ranks or i < ranks[e["name"]][0]:
                ranks[e["name"]] = (i, f"#{i} in {label} {c_label}")
    bdir = config.WEB_DATA_DIR.parent / "badges"
    bdir.mkdir(exist_ok=True)
    out = {}
    for name, (rank, text) in ranks.items():
        fn = name.replace("/", "--")
        label = f"GitRise · {text}"
        w = 24 + len(label) * 8
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="32">'
            f'<rect x="1.5" y="1.5" width="{w - 3}" height="29" rx="8" '
            f'fill="#faf5ec" stroke="#1a1712" stroke-width="2.5"/>'
            f'<text x="{w // 2}" y="21" font-family="ui-monospace, Menlo, monospace" '
            f'font-size="12" font-weight="bold" fill="#1a1712" text-anchor="middle">'
            f'{escape(label)}</text></svg>'
        )
        (bdir / f"{fn}.svg").write_text(svg)
        out[name] = {"src": f"/badges/{fn}.svg", "label": label}
    return out


def main():
    repos = json.loads(config.REPOS_FILE.read_text())
    summaries = (json.loads(config.SUMMARIES_FILE.read_text())
                 if config.SUMMARIES_FILE.exists() else {})
    events_map = (json.loads(config.EVENTS_FILE.read_text())
                  if config.EVENTS_FILE.exists() else {})
    snaps = load_snapshots()
    if not snaps:
        raise SystemExit("no snapshots; run snapshot.py first")

    config.WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cat_names = {c["id"]: c["en"] for c in config.CATEGORIES}
    boards = {}
    for period in ("day", "week", "month"):
        boards[f"global-{period}"] = build_board(period, repos, snaps, summaries, None, events_map)
        for c in config.CATEGORY_IDS:
            boards[f"{c}-{period}"] = build_board(period, repos, snaps, summaries, c, events_map)

    # "Rising" board: newcomers only (young repos, 100..2000 stars)
    newcomers = [r for r in repos if r.get("newcomer")]
    for period in ("day", "week", "month"):
        boards[f"rising-{period}"] = build_board(period, newcomers, snaps, summaries, None, events_map)
        boards[f"rising-{period}"]["category"] = "rising"

    for key, board in boards.items():
        (config.WEB_DATA_DIR / f"board-{key}.json").write_text(
            json.dumps(board, ensure_ascii=False))

    badges = build_badges(boards, cat_names)

    # repo detail pages: union of board entries + 30-day star history
    movers = {e["name"] for b in boards.values() for e in b["entries"][:REPO_PAGES // 10]}
    meta_map = {r["full_name"]: r for r in repos}
    days = sorted(snaps)[-30:]
    rdir = config.WEB_DATA_DIR / "repos"
    rdir.mkdir(exist_ok=True)
    for name in movers:
        r = meta_map.get(name)
        if not r:
            continue
        history = [{"d": d.isoformat(), "s": snaps[d]["stars"].get(name)}
                   for d in days if snaps[d]["stars"].get(name) is not None]
        ev = events_map.get(name, {})
        detail = {
            "name": name, "desc": r.get("description") or "",
            "lang": r.get("language"), "license": r.get("license"),
            "created_at": r.get("created_at"),
            "classification": r["classification"],
            "sum": summaries.get(name) or {},
            "history": history,
            "events": ev.get("events", []),
            "why": ev.get("reason"),
            "badge": badges.get(name),
        }
        owner, repo_name = name.split("/", 1)
        sub = rdir / owner
        sub.mkdir(exist_ok=True)
        (sub / f"{repo_name}.json").write_text(json.dumps(detail, ensure_ascii=False))

    archives = build_archives(repos, snaps, summaries)

    # feeds: global + per-category + rising
    build_feed(boards["global-day"], config.WEB_DATA_DIR.parent / "feed.xml",
               "GitRise — GitHub net star growth, daily",
               "Daily GitHub rankings by real net star growth.")
    feeds_dir = config.WEB_DATA_DIR.parent / "feeds"
    for c in config.CATEGORIES:
        build_feed(boards[f"{c['id']}-day"], feeds_dir / f"{c['id']}.xml",
                   f"GitRise — {c['en']}, daily",
                   f"Daily {c['en']} rankings by real net star growth.")
    build_feed(boards["rising-day"], feeds_dir / "rising.xml",
               "GitRise — Rising newcomers, daily",
               "Young repos (100–2,000 stars) ranked by real net star growth.")

    latest = max(snaps)
    cat_counts = {}
    for r in repos:
        c = r["classification"].get("category")
        if c:
            cat_counts[c] = cat_counts.get(c, 0) + 1
    categories = [dict(c, repos=cat_counts.get(c["id"], 0)) for c in config.CATEGORIES]
    (config.WEB_DATA_DIR / "meta.json").write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "latest_snapshot": latest.isoformat(),
        "captured_at": snaps[latest]["captured_at"],
        "tracked_repos": len(repos),
        "newcomer_repos": len(newcomers),
        "categories": categories,
        "min_stars": config.MIN_STARS,
    }, ensure_ascii=False))
    log.info("built %d boards (%d newcomers), %d repo pages, %d archives, %d badges",
             len(boards), len(newcomers), len(movers), len(archives), len(badges))


if __name__ == "__main__":
    main()
