"""Central config for the collector. All tunables in one place."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
REPOS_FILE = DATA_DIR / "repos.json"
SUMMARIES_FILE = DATA_DIR / "summaries.json"
WEB_DATA_DIR = ROOT / "web" / "public" / "data"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Free OpenRouter models, tried in order; all ":free" variants.
OPENROUTER_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]

MIN_STARS = 1000            # strictly greater than this, enforced as > in queries
SNAPSHOT_KEEP_DAYS = 40     # daily snapshots retained (monthly 1st-day kept forever)
SUMMARY_MAX_PER_RUN = 50    # OpenRouter free-tier budget guard per daily run

# Newcomers ("rising" board): young repos below the main star threshold.
NEWCOMER_MIN_STARS = 100
NEWCOMER_MAX_STARS = 2000
NEWCOMER_MAX_AGE_DAYS = 180

# "Why it rose" enrichment (facts only; AI may only narrate given facts).
EVENTS_FILE = DATA_DIR / "events.json"
ENRICH_TOP_N = 10           # top risers per board (day + week) to enrich
EVENT_LOOKBACK_DAYS = 7

TZ = "Asia/Shanghai"
CLASSIFIER_VERSION = "rules-v1"

CATEGORIES = [
    {"id": "ai-ml", "zh": "人工智能与机器学习", "en": "AI & Machine Learning"},
    {"id": "developer-tools", "zh": "开发者工具", "en": "Developer Tools"},
    {"id": "web-frontend", "zh": "Web 前端与 UI", "en": "Web Frontend & UI"},
    {"id": "backend-api", "zh": "后端与 API", "en": "Backend & APIs"},
    {"id": "data-databases", "zh": "数据与数据库", "en": "Data & Databases"},
    {"id": "cloud-devops", "zh": "云原生与 DevOps", "en": "Cloud Native & DevOps"},
    {"id": "security-privacy", "zh": "安全与隐私", "en": "Security & Privacy"},
    {"id": "productivity-automation", "zh": "效率工具与自动化", "en": "Productivity & Automation"},
    {"id": "mobile-desktop", "zh": "移动与桌面应用", "en": "Mobile & Desktop"},
    {"id": "games-media", "zh": "游戏与多媒体", "en": "Games & Multimedia"},
]
CATEGORY_IDS = [c["id"] for c in CATEGORIES]
