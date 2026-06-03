import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4"

# Sport keys to try for WC 2026
SPORT_KEYS = ["soccer_fifa_world_cup", "soccer_international_friendlies"]

def get_wc_odds() -> list[dict]:
    """Fetch all available WC match odds."""
    for sport_key in SPORT_KEYS:
        url = f"{BASE_URL}/sports/{sport_key}/odds"
        params = {
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal",
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return data
    return []

def find_match_odds(home_en: str, away_en: str, all_odds: list[dict]) -> dict | None:
    """Find odds for a specific match by team name (fuzzy)."""
    home_lower = home_en.lower()
    away_lower = away_en.lower()

    for event in all_odds:
        h = event.get("home_team", "").lower()
        a = event.get("away_team", "").lower()
        # Partial match to handle name variations
        if (home_lower in h or h in home_lower) and (away_lower in a or a in away_lower):
            return parse_odds(event)
        if (away_lower in h or h in away_lower) and (home_lower in a or a in home_lower):
            result = parse_odds(event)
            if result:
                # Swap home/away since we found reversed
                result["home_odds"], result["away_odds"] = result["away_odds"], result["home_odds"]
            return result
    return None

def parse_odds(event: dict) -> dict | None:
    """Extract best h2h odds from an event."""
    bookmakers = event.get("bookmakers", [])
    if not bookmakers:
        return None

    # Use first available bookmaker
    for bm in bookmakers:
        for market in bm.get("markets", []):
            if market["key"] == "h2h":
                outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                home = event["home_team"]
                away = event["away_team"]
                home_odds = outcomes.get(home)
                away_odds = outcomes.get(away)
                draw_odds = outcomes.get("Draw")
                if home_odds and away_odds:
                    return {
                        "home_odds": home_odds,
                        "away_odds": away_odds,
                        "draw_odds": draw_odds,
                        "bookmaker": bm["title"],
                    }
    return None

def implied_prob(decimal_odds: float) -> int:
    """Convert decimal odds to implied probability %."""
    if not decimal_odds:
        return 0
    return round((1 / decimal_odds) * 100)
