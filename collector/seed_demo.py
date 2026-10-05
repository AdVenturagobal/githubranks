"""DEV FIXTURE ONLY — generates synthetic repos/snapshots so the web app can
be built and reviewed locally without GitHub API credentials.
NEVER run in production workflows; real boards must come from discover.py +
snapshot.py. Output is overwritten by the real pipeline.
Usage: python seed_demo.py
"""
import json
import random
from datetime import date, timedelta

import config

random.seed(42)

DEMO = [
    ("acme/llm-forge", "ai-ml", ["llm", "agent"], "Python", 18400),
    ("acme/agent-os", "ai-ml", ["agent", "mcp"], "Python", 5210),
    ("brightlab/vectorflow", "data-databases", ["vector-search"], "Rust", 8930),
    ("brightlab/pg-lens", "data-databases", [], "Go", 3420),
    ("codewise/ship-cli", "developer-tools", ["cli"], "Rust", 12750),
    ("codewise/lintcraft", "developer-tools", [], "TypeScript", 2180),
    ("pixelforge/ui-prism", "web-frontend", ["react"], "TypeScript", 15300),
    ("pixelforge/css-wind", "web-frontend", [], "CSS", 6640),
    ("servkit/gatekeeper", "backend-api", [], "Go", 7810),
    ("servkit/authd", "backend-api", [], "Go", 4120),
    ("orbitops/kube-pilot", "cloud-devops", ["kubernetes"], "Go", 9950),
    ("orbitops/deploydeck", "cloud-devops", [], "TypeScript", 2890),
    ("sentinelhq/vaultscan", "security-privacy", [], "Python", 5430),
    ("flowdock/taskweave", "productivity-automation", ["self-hosted"], "TypeScript", 11020),
    ("pocketbits/crossnote", "mobile-desktop", [], "Dart", 3760),
    ("pixelplay/ember-engine", "games-media", [], "C++", 8870),
    ("lonesome/unclassified-tool", None, [], "Go", 1500),
    # newcomers: created recently, 100..2000 stars
    ("tinyhq/micro-agent", "ai-ml", ["llm", "agent"], "Python", 620),
    ("tinyhq/promptdeck", "developer-tools", ["llm"], "TypeScript", 340),
    ("freshlab/tailwiki", "web-frontend", ["react"], "TypeScript", 180),
]
NEWCOMERS = {"tinyhq/micro-agent", "tinyhq/promptdeck", "freshlab/tailwiki"}


def main():
    today = date.today()
    repos = []
    for name, cat, tags, lang, stars in DEMO:
        repos.append({
            "full_name": name,
            "description": f"Demo description for {name}",
            "topics": tags, "language": lang, "archived": False,
            "is_fork": False,
            "created_at": ("2026-08-15T00:00:00Z" if name in NEWCOMERS
                           else "2024-01-01T00:00:00Z"),
            "license": "MIT", "discovered_at": "2026-10-01T00:00:00Z",
            "newcomer": name in NEWCOMERS,
            "classification": {"category": cat, "tags": tags,
                               "confidence": 0.9 if cat else 0.0,
                               "version": "demo", "source": "demo"},
        })

    config.DATA_DIR.mkdir(exist_ok=True)
    config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    config.REPOS_FILE.write_text(json.dumps(repos, ensure_ascii=False))
    config.SUMMARIES_FILE.write_text(json.dumps({
        n: {"en": f"A demo project named {n.split('/')[1]} for local preview.",
            "zh": f"演示项目 {n.split('/')[1]}，仅用于本地预览。"}
        for n, *_ in DEMO
    }, ensure_ascii=False))

    base = {n: s for n, _, _, _, s in DEMO}
    for delta in range(15, -1, -1):
        d = today - timedelta(days=delta)
        stars = {n: int(v * (1 - 0.004 * delta) + random.randint(0, 40))
                 for n, v in base.items()}
        # micro-agent: accelerating newcomer (week-over-week growth doubles)
        stars["tinyhq/micro-agent"] = int(620 - (140 if delta <= 7 else 40) * (delta / 15))
        (config.SNAPSHOT_DIR / f"{d.isoformat()}.json").write_text(json.dumps({
            "captured_at": f"{d.isoformat()}T16:30:00+00:00",
            "tz": config.TZ, "stars": stars,
        }))

    # demo "why it rose" facts + narration for the top riser
    config.EVENTS_FILE.write_text(json.dumps({
        "pixelforge/ui-prism": {
            "events": [
                {"type": "release", "tag": "v2.1.0", "title": "v2.1.0 — dark mode",
                 "date": (today - timedelta(days=2)).isoformat()},
                {"type": "hackernews", "title": "Show HN: ui-prism",
                 "points": 312, "url": "https://github.com/pixelforge/ui-prism",
                 "date": (today - timedelta(days=1)).isoformat()},
            ],
            "reason": {
                "en": "Shipped v2.1.0 two days ago and hit the HN front page (312 points) yesterday.",
                "zh": "两天前发布 v2.1.0，昨天登上 HN 首页（312 分）。",
            },
            "sig": "demo", "fetched_at": f"{today.isoformat()}T00:00:00+00:00",
        },
    }, ensure_ascii=False))
    print(f"demo data seeded for {len(DEMO)} repos ({len(NEWCOMERS)} newcomers), 16 snapshots")


if __name__ == "__main__":
    main()
