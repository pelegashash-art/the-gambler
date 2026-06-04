"""
Fetch team form & stats from API-Football (api-sports.io).
Free tier: 100 requests/day.
We use 2 calls per team (search + last-5 fixtures) → cache team IDs to save calls.
"""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from usage_tracker import track_apifootball

load_dotenv()

API_KEY  = os.getenv("APIFOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS  = {"x-apisports-key": API_KEY}
CACHE_FILE = Path("data/team_id_cache.json")


# ── Cache helpers ─────────────────────────────────────────────────────────

def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def _save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


# ── API calls ─────────────────────────────────────────────────────────────

def _search_team_id(name: str) -> int | None:
    """Search team by name, return API-Football team ID."""
    track_apifootball()
    resp = requests.get(
        f"{BASE_URL}/teams",
        headers=HEADERS,
        params={"search": name},
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    data = resp.json().get("response", [])
    if not data:
        return None
    return data[0]["team"]["id"]


def _get_team_id(name_en: str) -> int | None:
    """Get team ID from cache or API."""
    cache = _load_cache()
    key = name_en.lower()
    if key in cache:
        return cache[key]
    team_id = _search_team_id(name_en)
    if team_id:
        cache[key] = team_id
        _save_cache(cache)
    return team_id


def _get_last_fixtures(team_id: int, n: int = 5) -> list[dict]:
    """Fetch last N finished fixtures for a team."""
    track_apifootball()
    resp = requests.get(
        f"{BASE_URL}/fixtures",
        headers=HEADERS,
        params={"team": team_id, "last": n, "status": "FT"},
        timeout=10,
    )
    if resp.status_code != 200:
        return []
    return resp.json().get("response", [])


# ── Public interface ───────────────────────────────────────────────────────

def get_team_form(name_en: str) -> dict | None:
    """
    Returns a dict with recent form data for a team, or None on failure.
    {
      "form":           "WWDLW",
      "goals_for":      8,
      "goals_against":  3,
      "matches":        5,
      "form_text":      "5 משחקים אחרונים: W W D L W | 8 שערים / 3 ספוגים"
    }
    """
    if not API_KEY:
        return None
    try:
        team_id = _get_team_id(name_en)
        if not team_id:
            return None

        fixtures = _get_last_fixtures(team_id)
        if not fixtures:
            return None

        form_chars = []
        goals_for = goals_against = 0

        for f in fixtures:
            teams  = f["teams"]
            goals  = f["goals"]
            is_home = teams["home"]["id"] == team_id

            gf = (goals["home"] if is_home else goals["away"]) or 0
            ga = (goals["away"] if is_home else goals["home"]) or 0
            winner = (teams["home"] if is_home else teams["away"])["winner"]

            goals_for     += gf
            goals_against += ga
            form_chars.append("W" if winner is True else ("L" if winner is False else "D"))

        form_str  = " ".join(form_chars)
        n = len(form_chars)
        form_text = (
            f"{n} משחקים אחרונים: {form_str} | "
            f"{goals_for} שערים / {goals_against} ספוגים"
        )
        return {
            "form":          "".join(form_chars),
            "goals_for":     goals_for,
            "goals_against": goals_against,
            "matches":       n,
            "form_text":     form_text,
        }
    except Exception as e:
        print(f"[football_stats] Error for {name_en}: {e}")
        return None


def get_match_stats(home_en: str, away_en: str) -> str:
    """
    Returns a formatted stats string for both teams, ready to inject into the prompt.
    Returns empty string if data unavailable.
    """
    home = get_team_form(home_en)
    away = get_team_form(away_en)

    lines = []
    if home:
        lines.append(f"בית  — {home['form_text']}")
    if away:
        lines.append(f"חוץ  — {away['form_text']}")

    return "\n".join(lines)
