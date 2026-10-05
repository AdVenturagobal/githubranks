"""Discover all repos with stars > MIN_STARS via sharded Search API.

Search returns max 1000 results per query, so we recursively split star
ranges until each shard's total_count fits. Merges into data/repos.json;
existing entries keep their classification until topics change.
Usage: python discover.py
"""
import json
import logging
from datetime import datetime, timezone, timedelta

import config
from github_client import GitHubClient, RateLimitExhausted
from classify import classify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("discover")


def shards(client: GitHubClient, lo: int, hi: int | None, extra: str = ""):
    """Yield (lo, hi) star-range shards each containing <=1000 repos."""
    q = f"stars:{lo}..{hi}" if hi else f"stars:>{lo}"
    q = f"{q} {extra}".strip()
    n = client.search_count(q)
    log.info("shard %s -> %d repos", q, n)
    if n == 0:
        return
    if n <= 950:
        yield lo, hi, n
        return
    if hi is None:  # open-ended too big: find split point
        hi = lo * 2
        while client.search_count(f"stars:>{hi} {extra}".strip()) > 950:
            hi *= 2
    if hi - lo <= 1:
        # extremely dense range; accept and take first 1000 (stars change slowly)
        yield lo, hi, n
        return
    mid = (lo + hi) // 2
    yield from shards(client, lo, mid, extra)
    yield from shards(client, mid + 1, hi, extra)


def _make_record(it: dict, prev: dict) -> dict:
    record = {
        "full_name": it["full_name"],
        "description": it.get("description") or "",
        "topics": it.get("topics") or [],
        "language": it.get("language"),
        "archived": bool(it.get("archived")),
        "is_fork": bool(it.get("fork")),
        "created_at": it.get("created_at"),
        "license": (it.get("license") or {}).get("spdx_id"),
        "newcomer": prev.get("newcomer", False),
        "discovered_at": prev.get("discovered_at")
        or datetime.now(timezone.utc).isoformat(),
    }
    if prev.get("_topic_sig") == repr(sorted(record["topics"])) and prev.get("classification"):
        record["classification"] = prev["classification"]
    else:
        record["classification"] = classify(record)
    record["_topic_sig"] = repr(sorted(record["topics"]))
    return record


def main():
    client = GitHubClient(config.GITHUB_TOKEN)
    existing = {}
    if config.REPOS_FILE.exists():
        existing = {r["full_name"]: r for r in json.loads(config.REPOS_FILE.read_text())}

    repos: dict[str, dict] = {}
    try:
        for lo, hi, n in shards(client, config.MIN_STARS + 1, None):
            q = f"stars:{lo}..{hi}" if hi else f"stars:>{lo}"
            for it in client.search_repos(q):
                repos[it["full_name"]] = _make_record(it, existing.get(it["full_name"], {}))

        # Newcomer pass: young, lower-star repos for the "rising" board.
        cutoff = (datetime.now(timezone.utc).date()
                  - timedelta(days=config.NEWCOMER_MAX_AGE_DAYS)).isoformat()
        extra = f"created:>{cutoff}"
        nc_shards = shards(client, config.NEWCOMER_MIN_STARS,
                           config.NEWCOMER_MAX_STARS, extra)
        for lo, hi, n in nc_shards:
            q = f"stars:{lo}..{hi} {extra}"
            for it in client.search_repos(q):
                fn = it["full_name"]
                if fn in repos:
                    repos[fn]["newcomer"] = True
                else:
                    rec = _make_record(it, existing.get(fn, {}))
                    rec["newcomer"] = True
                    repos[fn] = rec
    except RateLimitExhausted:
        if repos:
            log.error("rate limit; partial discovery (%d repos) NOT saved to avoid clobbering", len(repos))
        raise SystemExit(1)

    # repos that dropped below threshold or vanished: keep 30 days grace via existing data
    for fn, prev in existing.items():
        if fn not in repos:
            repos[fn] = prev  # snapshot job marks missing; ranking excludes gracefully

    out = sorted(repos.values(), key=lambda r: r["full_name"].lower())
    config.DATA_DIR.mkdir(exist_ok=True)
    config.REPOS_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=None))
    log.info("saved %d repos -> %s", len(out), config.REPOS_FILE)


if __name__ == "__main__":
    main()
