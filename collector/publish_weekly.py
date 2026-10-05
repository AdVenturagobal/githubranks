"""Weekly dev.to roundup publisher (traffic channel, see docs/traffic-devto.md).

Builds a data-journalism article from our own weekly board JSON: real
numbers in a table, AI only writes one-line factual blurbs (input is our
JSON, never freeform). Publishes as DRAFT by default — human hits publish.
Idempotent: skips if this week's article for the category already exists.

Usage: python publish_weekly.py [--dry-run]
Env: DEV_TO_API_KEY (optional; without it, only the markdown archive is
written), OPENROUTER_API_KEY (optional; blurbs fall back to summaries).
"""
import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("devto")

ARTICLES_DIR = config.DATA_DIR / "articles"
SITE = "https://gitrise.pages.dev"

# dev.to allows max 4 tags per article
DEVTO_TAGS = {
    "ai-ml": ["ai", "machinelearning", "llm", "opensource"],
    "developer-tools": ["devtools", "productivity", "opensource", "programming"],
    "web-frontend": ["webdev", "frontend", "javascript", "opensource"],
    "backend-api": ["api", "backend", "opensource", "programming"],
    "data-databases": ["database", "dataengineering", "opensource", "sql"],
    "cloud-devops": ["devops", "kubernetes", "cloud", "opensource"],
    "security-privacy": ["security", "privacy", "opensource", "infosec"],
    "productivity-automation": ["productivity", "automation", "opensource", "selfhosted"],
    "mobile-desktop": ["mobile", "desktop", "opensource", "appdev"],
    "games-media": ["gamedev", "gaming", "opensource", "media"],
}

COMMENT_PROMPT = """One-sentence factual comment (max 18 words) on why a developer \
might care about this repo, based ONLY on this data; no hype, no invented \
features. Data: name={name}, description={desc}, weekly net stars=+{net}, \
growth={growth}%. Reply with the sentence only."""


def pick_category() -> str:
    """Rotate categories by ISO week so every field gets covered."""
    week = date.today().isocalendar()[1]
    order = config.CATEGORY_IDS
    return order[week % len(order)]


def ai_blurb(entry: dict) -> str:
    fallback = (entry.get("sum") or {}).get("en") or entry.get("desc") or ""
    if not config.OPENROUTER_API_KEY:
        return fallback
    prompt = COMMENT_PROMPT.format(
        name=entry["name"], desc=(entry.get("desc") or "")[:300],
        net=entry["net"], growth=entry.get("growth") or 0)
    for model in config.OPENROUTER_MODELS:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"},
                json={"model": model, "temperature": 0.3, "max_tokens": 60,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=45)
            if r.status_code != 200:
                continue
            text = r.json()["choices"][0]["message"]["content"].strip().strip('"')
            return text.split("\n")[0][:200]
        except Exception as e:  # noqa: BLE001
            log.warning("blurb failed (%s): %s", model, e)
    return fallback

def build_article(cat_id: str, board: dict) -> tuple[str, str]:
    cat = next(c for c in config.CATEGORIES if c["id"] == cat_id)
    label = board.get("label_date") or ""
    board_url = f"{SITE}/en/board/{cat_id}/"
    title = f"Top 10 fastest-growing {cat['en']} repos on GitHub this week (real net stars)"
    rows = []
    for e in board["entries"][:10]:
        growth = "N/A" if e["growth"] is None else f"+{e['growth']}%"
        rows.append(
            f"| {e['rank']} | [{e['name']}](https://github.com/{e['name']}) "
            f"| +{e['net']:,} | {e['end']:,} | {growth} | {ai_blurb(e)} |"
        )
    body = f"""*Data: daily star snapshots of {config.MIN_STARS}+ projects via the official GitHub API. Full methodology and live board: [{SITE}]({board_url})*

| # | Repo | Net stars (week) | Total stars | Growth | Why it matters |
|---|------|-----------------|-------------|--------|----------------|
{chr(10).join(rows)}

**Methodology, briefly:** net stars gained = end-of-week total minus start-of-week total, Beijing-time natural weeks. No black-box algorithm, no estimates — entries with missing snapshots are excluded rather than guessed.

Full board (top 100, daily/weekly/monthly, with Chinese summaries): {board_url}
"""
    return title, body


def main():
    dry = "--dry-run" in sys.argv
    cat_id = pick_category()
    log.info("category this week: %s", cat_id)
    board_file = config.WEB_DATA_DIR / f"board-{cat_id}-week.json"
    if not board_file.exists():
        raise SystemExit(f"missing {board_file}; run build_data.py first")
    board = json.loads(board_file.read_text())
    if board["status"] != "ok":
        log.warning("board insufficient coverage; skipping publish (never pad with filler)")
        return

    week = date.today().isocalendar()
    slug = f"{week[0]}-W{week[1]:02d}-{cat_id}"
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    archive = ARTICLES_DIR / f"{slug}.md"
    if archive.exists():
        log.info("article %s already exists; idempotent skip", slug)
        return

    title, body = build_article(cat_id, board)
    canonical = f"{SITE}/en/board/{cat_id}/"
    archive.write_text(f"---\ntitle: {title}\ncanonical: {canonical}\n---\n\n{body}")
    log.info("archived %s", archive)

    import os
    key = os.environ.get("DEV_TO_API_KEY", "")
    if dry or not key:
        log.info("%s — not posting to dev.to", "dry run" if dry else "no DEV_TO_API_KEY")
    else:
        r = requests.post("https://dev.to/api/articles",
            headers={"api-key": key, "Content-Type": "application/json"},
            json={"article": {
                "title": title, "body_markdown": body, "published": False,
                "tags": DEVTO_TAGS[cat_id], "canonical_url": canonical,
            }}, timeout=30)
        r.raise_for_status()
        log.info("dev.to draft created: %s", r.json().get("url"))
    post_telegram()


def post_telegram():
    """Weekly top-5 digest to a Telegram channel. Free bot API; skipped
    entirely when secrets are absent (never fails the run for this)."""
    import os
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        log.info("no TELEGRAM_BOT_TOKEN/CHAT_ID; skipping telegram digest")
        return
    board_file = config.WEB_DATA_DIR / "board-global-week.json"
    if not board_file.exists():
        return
    board = json.loads(board_file.read_text())
    if board["status"] != "ok":
        return
    lines = [f"GitRise · Top risers this week ({board.get('label_date', '')})"]
    for e in board["entries"][:5]:
        mom = {"up": "↑", "down": "↓", "flat": "→"}.get(e.get("mom") or "", "")
        lines.append(f"#{e['rank']} {e['name']}  +{e['net']:,}★ {mom}")
    lines.append(f"\nFull board: {SITE}/en/")
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": "\n".join(lines),
              "disable_web_page_preview": True}, timeout=30)
    r.raise_for_status()
    log.info("telegram digest sent")


if __name__ == "__main__":
    main()
