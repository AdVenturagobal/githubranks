"""GitHub REST/GraphQL client with rate-limit aware retries.

Treats all remote data as untrusted input. Never raises on rate limit
without exhausting retries; raises RateLimitExhausted so callers can
abort the run cleanly (no fabricated data).
"""
import time
import logging
import requests

log = logging.getLogger("gh")
API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"


class RateLimitExhausted(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str):
        self.s = requests.Session()
        self.s.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "gitrise-collector/1.0",
        })
        if token:
            self.s.headers["Authorization"] = f"Bearer {token}"

    def _request(self, method: str, url: str, **kw):
        for attempt in range(6):
            r = self.s.request(method, url, timeout=30, **kw)
            remaining = int(r.headers.get("X-RateLimit-Remaining", "1") or 1)
            if r.status_code == 403 and remaining == 0:
                reset = int(r.headers.get("X-RateLimit-Reset", "0") or 0)
                wait = max(reset - int(time.time()), 1)
                if attempt >= 4 or wait > 900:
                    raise RateLimitExhausted(f"rate limit, reset in {wait}s")
                log.warning("rate limited, sleeping %ds", min(wait, 120))
                time.sleep(min(wait, 120))
                continue
            if r.status_code in (502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r
        raise RateLimitExhausted("retries exhausted")

    def search_count(self, query: str) -> int:
        r = self._request("GET", f"{API}/search/repositories",
                          params={"q": query, "per_page": 1})
        return r.json()["total_count"]

    def search_repos(self, query: str, max_results: int = 1000):
        """Yield repo items for a search query (<=1000 accessible per query)."""
        fetched = 0
        for page in range(1, 11):
            if fetched >= max_results:
                return
            r = self._request("GET", f"{API}/search/repositories", params={
                "q": query, "sort": "stars", "order": "desc",
                "per_page": 100, "page": page,
            })
            items = r.json().get("items", [])
            if not items:
                return
            for it in items:
                yield it
                fetched += 1
                if fetched >= max_results:
                    return

    def graphql(self, query: str, variables: dict):
        r = self._request("POST", GRAPHQL, json={"query": query, "variables": variables})
        payload = r.json()
        if payload.get("errors") and not payload.get("data"):
            raise RuntimeError(f"graphql errors: {payload['errors'][:2]}")
        return payload.get("data", {})

    def batch_stargazer_counts(self, full_names: list[str]) -> dict[str, int | None]:
        """Fetch stargazer counts for up to N repos via GraphQL aliasing.
        100 repos per query => ~600 requests for 60k repos, well within
        the 5000 points/hr free allowance. Deleted/renamed repos -> None."""
        out: dict[str, int | None] = {}
        for i in range(0, len(full_names), 100):
            chunk = full_names[i:i + 100]
            fields = []
            for j, fn in enumerate(chunk):
                owner, name = fn.split("/", 1)
                fields.append(
                    f'r{j}: repository(owner:"{owner}", name:"{name}")'
                    "{ stargazerCount }"
                )
            data = self.graphql("query { " + " ".join(fields) + " }", {})
            for j, fn in enumerate(chunk):
                node = data.get(f"r{j}")
                out[fn] = node["stargazerCount"] if node else None
            time.sleep(0.3)  # be polite, smooth secondary limits
        return out
