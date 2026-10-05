"""Rule-based classifier: one primary category + multiple tags.

Signals: GitHub topics > description keywords. Language is NEVER used to
decide purpose. Low-confidence repos stay uncategorized (excluded from
category boards, still visible in global board) rather than force-filled.
"""
import re
from config import CLASSIFIER_VERSION

# category id -> (strong topic signals, description keyword patterns)
RULES: dict[str, tuple[set[str], list[str]]] = {
    "ai-ml": (
        {"llm", "large-language-model", "ai", "artificial-intelligence", "machine-learning",
         "deep-learning", "agent", "ai-agents", "rag", "mcp", "model-context-protocol",
         "transformer", "diffusion", "computer-vision", "nlp", "text-to-image",
         "speech-recognition", "mlops", "fine-tuning", "inference", "pytorch",
         "tensorflow", "neural-network", "chatbot"},
        [r"\bllm\b", r"\bagent(s)?\b", r"\brag\b", r"\bmcp\b", r"machine learning",
         r"deep learning", r"\binference\b", r"fine-?tun", r"neural", r"\bchatbot\b"],
    ),
    "developer-tools": (
        {"cli", "command-line", "terminal", "editor", "ide", "vscode-extension", "linter",
         "formatter", "debugger", "testing", "code-review", "code-quality", "build-tool",
         "bundler", "git", "developer-tools", "devtools", "ai-coding", "tui"},
        [r"\bcli\b", r"command[- ]line", r"\bterminal\b", r"code editor", r"\bide\b",
         r"\blint", r"\bdebug", r"\btest(ing)? framework", r"build tool", r"AI (coding|pair)",
         r"code completion"],
    ),
    "web-frontend": (
        {"react", "vue", "svelte", "angular", "nextjs", "nuxt", "frontend", "css",
         "tailwindcss", "component-library", "ui-components", "ui-kit", "design-system",
         "animation", "data-visualization", "charts", "static-site-generator",
         "web-components", "astro", "remix"},
        [r"\breact\b", r"\bvue\b", r"\bsvelte\b", r"component library", r"\bcss\b",
         r"front[- ]end", r"\bui kit\b", r"design system", r"static site"],
    ),
    "backend-api": (
        {"api", "rest-api", "graphql", "web-framework", "backend", "microservices",
         "authentication", "oauth", "orm", "http-server", "websocket", "grpc", "baas",
         "backend-as-a-service", "serverless", "api-gateway", "middleware"},
        [r"\bapi\b", r"web framework", r"back[- ]end", r"\borm\b",
         r"auth(entication|orization)?", r"\bgrpc\b", r"graphql", r"http server",
         r"microservice"],
    ),
    "data-databases": (
        {"database", "sql", "nosql", "postgres", "mysql", "sqlite", "mongodb", "redis",
         "vector-database", "vector-search", "elasticsearch", "search-engine", "etl",
         "data-pipeline", "data-engineering", "data-warehouse", "analytics",
         "stream-processing", "kafka", "spark", "dbms", "time-series", "olap", "duckdb"},
        [r"\bdatabase\b", r"\bsql\b", r"vector (store|database|search)", r"search engine",
         r"\betl\b", r"data pipeline", r"data warehouse", r"\bolap\b", r"time[- ]series"],
    ),
    "cloud-devops": (
        {"kubernetes", "k8s", "docker", "container", "devops", "ci-cd", "cicd", "terraform",
         "infrastructure-as-code", "iac", "monitoring", "observability", "prometheus",
         "grafana", "helm", "service-mesh", "deployment", "ansible", "gitops",
         "platform-engineering"},
        [r"kubernetes|k8s", r"\bdocker\b", r"\bci/?cd\b", r"\bdevops\b", r"monitoring",
         r"observability", r"infrastructure as code", r"\bterraform\b", r"\bgitops\b"],
    ),
    "security-privacy": (
        {"security", "cybersecurity", "pentest", "penetration-testing", "vulnerability",
         "ctf", "malware", "encryption", "privacy", "password-manager", "infosec",
         "forensics", "osint", "vpn", "cryptography", "secrets-management", "2fa"},
        [r"security (tool|scanner|audit)", r"pen(test|etration)", r"vulnerabilit",
         r"\bencrypt", r"\bprivacy\b", r"password manager", r"\bosint\b"],
    ),
    "productivity-automation": (
        {"automation", "workflow", "productivity", "note-taking", "notes", "knowledge-base",
         "knowledge-management", "pkm", "wiki", "low-code", "no-code", "n8n",
         "project-management", "kanban", "calendar", "self-hosted", "selfhosted",
         "home-assistant", "crm", "collaboration", "todo"},
        [r"\bautomation\b", r"workflow (engine|automation)", r"note[- ]taking",
         r"knowledge (base|management)", r"low[- ]code", r"no[- ]code", r"self[- ]hosted",
         r"project management"],
    ),
    "mobile-desktop": (
        {"android", "ios", "swiftui", "flutter", "react-native", "electron", "tauri",
         "desktop-app", "cross-platform", "mobile", "expo", "qt", "gtk", "macos-app"},
        [r"\bandroid\b", r"\bios\b", r"\bflutter\b", r"react native", r"\belectron\b",
         r"\btauri\b", r"desktop (app|application)", r"cross[- ]platform (app|gui|framework)"],
    ),
    "games-media": (
        {"game", "game-engine", "gamedev", "unity", "unreal", "godot", "bevy", "3d",
         "graphics", "opengl", "vulkan", "webgl", "shader", "video", "audio", "ffmpeg",
         "streaming", "webrtc", "image-processing", "music", "emulator", "vr",
         "virtual-reality", "blender"},
        [r"game (engine|development|dev)", r"\bgamedev\b", r"\b3d\b",
         r"video (player|editor|processing)", r"\bffmpeg\b", r"audio (player|processing)",
         r"\bemulator\b", r"\bwebrtc\b"],
    ),
}

# Tag normalization: canonical tag -> aliases seen in topics
TAG_ALIASES = {
    "llm": {"llm", "large-language-model", "llms"},
    "agent": {"agent", "ai-agents", "agents", "ai-agent"},
    "mcp": {"mcp", "model-context-protocol"},
    "rag": {"rag", "retrieval-augmented-generation"},
    "cli": {"cli", "command-line"},
    "self-hosted": {"self-hosted", "selfhosted"},
    "vector-search": {"vector-database", "vector-search", "vector-store"},
    "kubernetes": {"kubernetes", "k8s"},
    "react": {"react", "reactjs"},
    "ai-coding": {"ai-coding", "copilot", "code-assistant"},
}


def classify(repo: dict) -> dict:
    """repo: {description, topics[], language}. Returns classification record."""
    topics = {t.lower() for t in (repo.get("topics") or [])}
    desc = (repo.get("description") or "").lower()

    scores: dict[str, int] = {}
    for cat, (strong, patterns) in RULES.items():
        score = 3 * len(topics & strong)
        score += sum(1 for p in patterns if re.search(p, desc))
        if score:
            scores[cat] = score

    tags = sorted({canon for canon, aliases in TAG_ALIASES.items() if topics & aliases})

    if not scores:
        return {"category": None, "tags": tags, "confidence": 0.0,
                "version": CLASSIFIER_VERSION, "source": "rules"}
    best, best_score = max(scores.items(), key=lambda kv: kv[1])
    confidence = min(1.0, best_score / 6.0)
    if confidence < 0.34:
        return {"category": None, "tags": tags, "confidence": round(confidence, 2),
                "version": CLASSIFIER_VERSION, "source": "rules"}
    return {"category": best, "tags": tags, "confidence": round(confidence, 2),
            "version": CLASSIFIER_VERSION, "source": "rules"}

