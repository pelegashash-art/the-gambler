"""
Fetch team form from API-Football (api-sports.io).
Free tier: 100 requests/day. Supports seasons 2022-2024.
Team IDs cached locally to save API calls.
"""
import os
import json
import requests
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

    n_actual = len(form_chars)
    form_str = " ".join(form_chars)
    return {
        "form":      "".join(form_chars),
        "form_text": f"{n_actual} משחקים אחרונים: {form_str} | {goals_for} שערים / {goals_against} ספוגים",
    }


# ── Public ────────────────────────────────────────────────────────────────

def get_match_stats(home_en: str, away_en: str) -> str:
    """Form stats string for both teams, ready to inject into GPT prompt."""
    if not API_KEY:
        return ""
    try:
        lines = []
        for label, name in [("בית", home_en), ("חוץ", away_en)]:
            team_id = _get_team_id(name)
            if team_id:
                form = _get_team_form(team_id)
                if form:
                    lines.append(f"{label}  — {form['form_text']}")
        return "\n".join(lines)
    except Exception as e:
        print(f"[football_stats] Error: {e}")
        return ""
