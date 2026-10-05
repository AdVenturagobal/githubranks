"""Daily star snapshot for all tracked repos. Idempotent per Beijing date.

Output: data/snapshots/YYYY-MM-DD.json
  {"captured_at": <utc iso>, "stars": {"owner/repo": 12345, ...}}
Missing/deleted repos are recorded as null and excluded from net-gain
computations (never treated as 0). Also prunes old daily snapshots beyond
SNAPSHOT_KEEP_DAYS, keeping month-start snapshots forever.
Usage: python snapshot.py
"""
import json
import logging
from datetime import datetime, timezone, timedelta

import config
from github_client import GitHubClient, RateLimitExhausted

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("snapshot")

BEIJING = timezone(timedelta(hours=8))


def beijing_date() -> str:
    return datetime.now(BEIJING).strftime("%Y-%m-%d")


def prune():
    files = sorted(config.SNAPSHOT_DIR.glob("*.json"))
    cutoff = datetime.now(BEIJING).date() - timedelta(days=config.SNAPSHOT_KEEP_DAYS)
    for f in files:
        d = datetime.strptime(f.stem, "%Y-%m-%d").date()
        if d.day == 1 or d >= cutoff:
            continue
        f.unlink()
        log.info("pruned %s", f.name)


def main():
    if not config.REPOS_FILE.exists():
        raise SystemExit("repos.json missing; run discover.py first")
    repos = json.loads(config.REPOS_FILE.read_text())
    names = [r["full_name"] for r in repos]
    log.info("snapshotting %d repos", len(names))

    client = GitHubClient(config.GITHUB_TOKEN)
    try:
        counts = client.batch_stargazer_counts(names)
    except RateLimitExhausted:
        log.error("rate limit exhausted; no snapshot written (never fabricate)")
        raise SystemExit(1)

    config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    day = beijing_date()
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "tz": config.TZ,
        "stars": counts,
    }
    out = config.SNAPSHOT_DIR / f"{day}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False))
    ok = sum(1 for v in counts.values() if v is not None)
    log.info("snapshot %s: %d ok, %d missing -> %s", day, ok, len(counts) - ok, out)
    prune()


if __name__ == "__main__":
    main()
