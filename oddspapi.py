"""
OddsPapi integration — https://oddspapi.io
300+ bookmakers, real-time odds.
Auth: apiKey query param.
"""
import os
import json
import requests
from datetime import date, datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from usage_tracker import track_oddspapi

load_dotenv()

API_KEY  = os.getenv("ODDSPAPI_KEY")
BASE_URL = "https://v5.oddspapi.io/en"
CACHE_FILE = Path("data/oddspapi_cache.json")

# Outcome IDs for Match Winner market
OUTCOME_HOME = 111
OUTCOME_DRAW = 112
OUTCOME_AWAY = 113


# ── Cache ─────────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {"sport_id": None, "tournament_id": None}


def _save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


# ── API helper ────────────────────────────────────────────────────────────

def _get(path: str, params: dict = {}) -> dict | list | None:
    track_oddspapi()
    try:
        resp = requests.get(
            f"{BASE_URL}{path}",
            params={"apiKey": API_KEY, **params},
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"[OddsPapi] {path} → {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json()
    except Exception as e:
        print(f"[OddsPapi] Request error: {e}")
        return None


# ── Sport & Tournament IDs ────────────────────────────────────────────────

def _get_soccer_sport_id() -> int | None:
    cache = _load_cache()
    if cache.get("sport_id"):
        return cache["sport_id"]
    data = _get("/sports")
    if not data:
        return None
    sports = data if isinstance(data, list) else data.get("sports", data.get("data", []))
    for s in sports:
        name = (s.get("name") or s.get("title") or "").lower()
        if "soccer" in name or "football" in name:
            sid = s.get("id") or s.get("sportId")
            cache["sport_id"] = sid
            _save_cache(cache)
            return sid
    return None


def _get_wc_tournament_id(sport_id: int) -> int | str | None:
    cache = _load_cache()
    if cache.get("tournament_id"):
        return cache["tournament_id"]
    data = _get("/tournaments", {"sportId": sport_id})
    if not data:
        return None
    tournaments = data if isinstance(data, list) else data.get("tournaments", data.get("data", []))
    for t in tournaments:
        name = (t.get("name") or t.get("title") or "").lower()
        if "world cup" in name or "fifa" in name or "mondial" in name:
            tid = t.get("id") or t.get("tournamentId")
            cache["tournament_id"] = tid
            _save_cache(cache)
            return tid
    return None


# ── Fixture lookup ────────────────────────────────────────────────────────

def _epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def _find_fixture(home_en: str, away_en: str, match_date: date) -> str | None:
    """Search for a fixture by teams + date, return fixtureId."""
    sport_id = _get_soccer_sport_id()
    if not sport_id:
        return None

    # Search window: midnight to midnight of match_date (UTC)
    start = datetime(match_date.year, match_date.month, match_date.day, 0, 0, 0)
    end   = start + timedelta(days=1)

    params = {
        "startTimeFrom": _epoch(start),
        "startTimeTo":   _epoch(end),
    }

    tid = _get_wc_tournament_id(sport_id)
    if tid:
        params["tournamentId"] = tid

    data = _get("/fixtures", params)
    if not data:
        return None

    fixtures = data if isinstance(data, list) else data.get("fixtures", data.get("data", []))

    home_l = home_en.lower()
    away_l = away_en.lower()

    for f in fixtures:
        participants = f.get("participants") or f.get("teams") or []
        names = [
            (p.get("name") or p.get("title") or "").lower()
            for p in participants
        ]
        if len(names) < 2:
            continue
        h, a = names[0], names[1]
        if (home_l in h or h in home_l) and (away_l in a or a in away_l):
            return f.get("fixtureId") or f.get("id")
        if (away_l in h or h in away_l) and (home_l in a or a in home_l):
            return f.get("fixtureId") or f.get("id")

    return None


# ── Odds parsing ──────────────────────────────────────────────────────────

def _parse_odds(data: dict, home_en: str, away_en: str) -> dict | None:
    """
    Parse odds response. Averages across all active bookmakers for
    home / draw / away outcomes.
    """
    odds_raw = data.get("odds") or data.get("data") or data
    home_vals, draw_vals, away_vals = [], [], []

    def collect(entry: dict):
        oid = entry.get("outcomeId")
        price = entry.get("price") or entry.get("odd")
        active = entry.get("active", True)
        if not price or not active:
            return
        try:
            price = float(price)
        except Exception:
            return
        if oid == OUTCOME_HOME:
            home_vals.append(price)
        elif oid == OUTCOME_DRAW:
            draw_vals.append(price)
        elif oid == OUTCOME_AWAY:
            away_vals.append(price)

    if isinstance(odds_raw, dict):
        for bm_data in odds_raw.values():
            if isinstance(bm_data, dict):
                for entry in bm_data.values():
                    if isinstance(entry, dict):
                        collect(entry)
    elif isinstance(odds_raw, list):
        for entry in odds_raw:
            collect(entry)

    if not home_vals or not away_vals:
        return None

    def avg(lst): return round(sum(lst) / len(lst), 2)

    return {
        "home_odds":  avg(home_vals),
        "draw_odds":  avg(draw_vals) if draw_vals else None,
        "away_odds":  avg(away_vals),
        "bookmakers": len(home_vals),
    }


# ── Public interface ──────────────────────────────────────────────────────

def get_oddspapi_odds(home_en: str, away_en: str, match_date: date) -> dict | None:
    """
    Fetch h2h odds from OddsPapi for a specific match.
    Returns averaged odds dict or None if unavailable.
    """
    if not API_KEY:
        return None
    try:
        fixture_id = _find_fixture(home_en, away_en, match_date)
        if not fixture_id:
            print(f"[OddsPapi] Fixture not found: {home_en} vs {away_en} on {match_date}")
            return None

        data = _get("/fixtures/odds", {"fixtureId": fixture_id, "mainLine": "true", "marketActive": "true"})
        if not data:
            return None

        result = _parse_odds(data, home_en, away_en)
        if result:
            print(f"[OddsPapi] ✓ {home_en} vs {away_en}: {result}")
        return result
    except Exception as e:
        print(f"[OddsPapi] Error for {home_en} vs {away_en}: {e}")
        return None
