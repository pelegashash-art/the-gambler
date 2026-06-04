"""
Fetch team form & odds from API-Football (api-sports.io).
Free tier: 100 requests/day.
Team IDs cached locally to save API calls.
"""
import os
import json
import requests
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from usage_tracker import track_apifootball

load_dotenv()

API_KEY    = os.getenv("APIFOOTBALL_KEY")
BASE_URL   = "https://v3.football.api-sports.io"
HEADERS    = {"x-apisports-key": API_KEY}
CACHE_FILE = Path("data/team_id_cache.json")


# ── Cache ─────────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def _save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


# ── API helpers ───────────────────────────────────────────────────────────

def _api_get(path: str, params: dict) -> list:
    track_apifootball()
    resp = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params, timeout=10)
    if resp.status_code != 200:
        return []
    return resp.json().get("response", [])


def _get_team_id(name_en: str) -> int | None:
    """Return API-Football team ID, using local cache."""
    cache = _load_cache()
    key   = name_en.lower()
    if key in cache:
        return cache[key]
    data = _api_get("/teams", {"search": name_en})
    if not data:
        return None
    team_id = data[0]["team"]["id"]
    cache[key] = team_id
    _save_cache(cache)
    return team_id


# ── Form ──────────────────────────────────────────────────────────────────

def _get_team_form(team_id: int, n: int = 5) -> dict | None:
    fixtures = _api_get("/fixtures", {"team": team_id, "last": n, "status": "FT"})
    if not fixtures:
        return None

    form_chars = []
    goals_for = goals_against = 0

    for f in fixtures:
        teams   = f["teams"]
        goals   = f["goals"]
        is_home = teams["home"]["id"] == team_id
        gf = (goals["home"] if is_home else goals["away"]) or 0
        ga = (goals["away"] if is_home else goals["home"]) or 0
        winner = (teams["home"] if is_home else teams["away"])["winner"]
        goals_for     += gf
        goals_against += ga
        form_chars.append("W" if winner is True else ("L" if winner is False else "D"))

    form_str  = " ".join(form_chars)
    n_actual  = len(form_chars)
    return {
        "form":          "".join(form_chars),
        "goals_for":     goals_for,
        "goals_against": goals_against,
        "form_text":     f"{n_actual} משחקים אחרונים: {form_str} | {goals_for} שערים / {goals_against} ספוגים",
    }


# ── Odds ──────────────────────────────────────────────────────────────────

def _find_fixture_id(home_id: int, away_id: int, match_date: date) -> int | None:
    """Find the API-Football fixture ID for a specific match."""
    date_str = match_date.isoformat()
    # search by home team + date
    fixtures = _api_get("/fixtures", {"team": home_id, "date": date_str})
    for f in fixtures:
        teams = f["teams"]
        if teams["home"]["id"] == home_id and teams["away"]["id"] == away_id:
            return f["fixture"]["id"]
    # fallback: search by away team + date
    fixtures = _api_get("/fixtures", {"team": away_id, "date": date_str})
    for f in fixtures:
        teams = f["teams"]
        if teams["home"]["id"] == home_id and teams["away"]["id"] == away_id:
            return f["fixture"]["id"]
    return None


def _get_fixture_odds(fixture_id: int) -> dict | None:
    """
    Fetch h2h odds for a fixture. Returns {home, draw, away} best odds or None.
    Aggregates across bookmakers and takes the average.
    """
    data = _api_get("/odds", {"fixture": fixture_id, "bet": 1})  # bet 1 = Match Winner
    if not data:
        return None

    home_vals, draw_vals, away_vals = [], [], []

    for bookmaker_entry in data:
        for bm in bookmaker_entry.get("bookmakers", []):
            for bet in bm.get("bets", []):
                if bet.get("name") != "Match Winner":
                    continue
                values = {v["value"]: float(v["odd"]) for v in bet.get("values", [])}
                if "Home" in values:
                    home_vals.append(values["Home"])
                if "Draw" in values:
                    draw_vals.append(values["Draw"])
                if "Away" in values:
                    away_vals.append(values["Away"])

    if not home_vals or not away_vals:
        return None

    def avg(lst): return round(sum(lst) / len(lst), 2)

    return {
        "home_odds": avg(home_vals),
        "draw_odds": avg(draw_vals) if draw_vals else None,
        "away_odds": avg(away_vals),
        "bookmakers": len(home_vals),
    }


def get_apifootball_odds(home_en: str, away_en: str, match_date: date) -> dict | None:
    """
    Public: fetch averaged h2h odds from API-Football for a specific match.
    Returns None if unavailable.
    """
    if not API_KEY:
        return None
    try:
        home_id = _get_team_id(home_en)
        away_id = _get_team_id(away_en)
        if not home_id or not away_id:
            return None

        fixture_id = _find_fixture_id(home_id, away_id, match_date)
        if not fixture_id:
            return None

        return _get_fixture_odds(fixture_id)
    except Exception as e:
        print(f"[football_stats] Odds error for {home_en} vs {away_en}: {e}")
        return None


# ── Public: form + combined odds text ────────────────────────────────────

def get_match_stats(home_en: str, away_en: str) -> str:
    """Form stats string for both teams (injected into GPT prompt)."""
    if not API_KEY:
        return ""
    try:
        home_id = _get_team_id(home_en)
        away_id = _get_team_id(away_en)
        lines   = []
        for label, team_id in [("בית", home_id), ("חוץ", away_id)]:
            if team_id:
                form = _get_team_form(team_id)
                if form:
                    lines.append(f"{label}  — {form['form_text']}")
        return "\n".join(lines)
    except Exception as e:
        print(f"[football_stats] Form error: {e}")
        return ""
