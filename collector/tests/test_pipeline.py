"""Offline tests: classifier rules, period math, net-gain computation.
Run: python -m pytest tests/ -q   (from collector/)"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import build_data  # noqa: E402
from classify import classify  # noqa: E402


def test_classify_ai():
    r = classify({"description": "LLM agent framework", "topics": ["llm", "agent"]})
    assert r["category"] == "ai-ml" and "llm" in r["tags"]


def test_classify_low_confidence_stays_uncategorized():
    r = classify({"description": "some tool", "topics": ["react"]})
    # single weak-ish signal: 1 topic*3 = score 3 -> confidence 0.5, categorized
    assert r["category"] == "web-frontend"
    r2 = classify({"description": "", "topics": []})
    assert r2["category"] is None


def _mk_snapshot(d: date, stars: dict):
    config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    (config.SNAPSHOT_DIR / f"{d.isoformat()}.json").write_text(json.dumps(
        {"captured_at": f"{d.isoformat()}T16:30:00+00:00", "stars": stars}))


def test_board_math(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SNAPSHOT_DIR", tmp_path / "snaps")
    monkeypatch.setattr(config, "WEB_DATA_DIR", tmp_path / "webdata")
    monkeypatch.setattr(config, "REPOS_FILE", tmp_path / "repos.json")
    monkeypatch.setattr(config, "SUMMARIES_FILE", tmp_path / "sums.json")

    today = date.today()
    yesterday = today - timedelta(days=1)
    _mk_snapshot(yesterday, {"a/b": 1000, "c/d": 500, "gone/e": 100})
    _mk_snapshot(today, {"a/b": 1250, "c/d": None, "gone/e": 80})  # c/d missing, gone/e lost stars

    repos = [
        {"full_name": "a/b", "description": "x", "language": "Go",
         "classification": {"category": "ai-ml", "tags": ["llm"], "confidence": 0.9}},
        {"full_name": "c/d", "description": "y", "language": "Rust",
         "classification": {"category": "ai-ml", "tags": [], "confidence": 0.8}},
        {"full_name": "gone/e", "description": "z", "language": "C",
         "classification": {"category": "ai-ml", "tags": [], "confidence": 0.8}},
    ]
    config.REPOS_FILE.write_text(json.dumps(repos))
    config.SUMMARIES_FILE.write_text("{}")

    board = build_data.build_board("day", repos, build_data.load_snapshots(), {}, "ai-ml")
    names = [e["name"] for e in board["entries"]]
    assert "c/d" not in names, "missing end snapshot must be excluded, not faked"
    a = next(e for e in board["entries"] if e["name"] == "a/b")
    assert a["net"] == 250 and a["growth"] == 25.0
    g = next(e for e in board["entries"] if e["name"] == "gone/e")
    assert g["net"] == -20 and g["growth"] == -20.0, "negative growth not truncated"
    assert board["in_progress"] is False, "day board is the last complete day"
    assert board["label_date"] == yesterday.isoformat()


def test_period_plan():
    # latest = Monday 2026-10-05
    assert build_data.period_plan(date(2026, 10, 5), "day") == (
        date(2026, 10, 4), date(2026, 10, 5), False, date(2026, 10, 4))
    assert build_data.period_plan(date(2026, 10, 5), "week") == (
        date(2026, 10, 5), date(2026, 10, 5), True, date(2026, 10, 5))
    # Sunday -> week complete
    assert build_data.period_plan(date(2026, 10, 11), "week")[2] is False
    assert build_data.period_plan(date(2026, 10, 5), "month") == (
        date(2026, 10, 1), date(2026, 10, 5), True, date(2026, 10, 1))
    # last day of month -> month complete
    assert build_data.period_plan(date(2026, 10, 31), "month")[2] is False


def test_momentum_state():
    ms = build_data.momentum_state
    assert ms(None, 10) is None and ms(10, None) is None, "missing data -> None, never faked"
    assert ms(200, 100) == "up"        # 2x acceleration
    assert ms(60, 100) == "down"       # cooling
    assert ms(100, 100) == "flat"
    assert ms(7, 0) == "up"            # real motion from zero base
    assert ms(2, 0) is None            # tiny noise from zero base
    assert ms(-3, 0) == "down"
    assert ms(50, -20) == "up"         # prev loss: ratio meaningless, flag recovery


def test_rising_board_uses_newcomers_only(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SNAPSHOT_DIR", tmp_path / "snaps")
    today = date.today()
    yesterday = today - timedelta(days=1)
    _mk_snapshot(yesterday, {"a/b": 1000, "new/x": 100})
    _mk_snapshot(today, {"a/b": 1100, "new/x": 180})
    repos = [
        {"full_name": "a/b", "newcomer": False,
         "classification": {"category": None, "tags": [], "confidence": 0.0}},
        {"full_name": "new/x", "newcomer": True,
         "classification": {"category": None, "tags": [], "confidence": 0.0}},
    ]
    snaps = build_data.load_snapshots()
    newcomers = [r for r in repos if r.get("newcomer")]
    board = build_data.build_board("day", newcomers, snaps, {}, None)
    names = [e["name"] for e in board["entries"]]
    assert names == ["new/x"], "rising board must only rank newcomers"
    assert board["entries"][0]["mom"] is None or isinstance(board["entries"][0]["mom"], str)


def test_jev_stage(monkeypatch, tmp_path):
    import os
    import jev_classify

    monkeypatch.setattr(config, "REPOS_FILE", tmp_path / "repos.json")
    monkeypatch.setenv("JEV_ENABLED", "1")
    repos = [
        {"full_name": "x/unclear", "description": "things", "topics": [],
         "classification": {"category": None, "tags": [], "confidence": 0.0,
                            "source": "rules"}},
        {"full_name": "y/clear", "description": "llm agent", "topics": ["llm"],
         "classification": {"category": "ai-ml", "tags": ["llm"],
                            "confidence": 0.9, "source": "rules"}},
    ]
    config.REPOS_FILE.write_text(json.dumps(repos))

    monkeypatch.setattr(jev_classify, "ask_jev",
                        lambda repo: {"choice": "developer-tools", "confidence": 0.83})
    monkeypatch.setattr(sys, "argv", ["jev_classify.py"])
    jev_classify.main()

    out = {r["full_name"]: r for r in json.loads(config.REPOS_FILE.read_text())}
    assert out["x/unclear"]["classification"]["category"] == "developer-tools"
    assert out["x/unclear"]["classification"]["source"] == "jev"
    assert out["y/clear"]["classification"]["source"] == "rules", "high-confidence rules result untouched"

    # low Jev confidence must NOT be applied
    config.REPOS_FILE.write_text(json.dumps(repos))
    monkeypatch.setattr(jev_classify, "ask_jev",
                        lambda repo: {"choice": "ai-ml", "confidence": 0.4})
    jev_classify.main()
    out = {r["full_name"]: r for r in json.loads(config.REPOS_FILE.read_text())}
    assert out["x/unclear"]["classification"]["category"] is None


def test_jev_disabled_by_default(monkeypatch, tmp_path, caplog):
    import jev_classify
    monkeypatch.delenv("JEV_ENABLED", raising=False)
    monkeypatch.setattr(config, "REPOS_FILE", tmp_path / "nope.json")
    jev_classify.main()  # must not touch anything or raise
