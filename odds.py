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
    from usage_tracker import track_odds_api
    track_odds_api()
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

# Name aliases: Excel name → possible API names
NAME_ALIASES = {
    # Korea
    "south korea":             ["korea republic", "republic of korea", "korea"],
    "korea republic":          ["south korea", "korea"],
    # Czech
    "czech republic":          ["czechia", "czech"],
    "czechia":                 ["czech republic", "czech"],
    # USA
    "usa":                     ["united states", "united states of america"],
    "united states":           ["usa", "united states of america"],
    # Ivory Coast
    "ivory coast":             ["cote d'ivoire", "côte d'ivoire"],
    "côte d'ivoire":           ["ivory coast", "cote d'ivoire"],
    "cote d'ivoire":           ["ivory coast", "côte d'ivoire"],
    # Congo
    "dr congo":                ["congo dr", "democratic republic of congo"],
    "congo dr":                ["dr congo", "democratic republic of congo"],
    # Bosnia
    "bosnia and herzegovina":  ["bosnia & herzegovina", "bosnia"],
    "bosnia & herzegovina":    ["bosnia and herzegovina", "bosnia"],
    # Turkey
    "türkiye":                 ["turkey"],
    "turkey":                  ["türkiye"],
    # Curacao
    "curacao":                 ["curaçao"],
    "curaçao":                 ["curacao"],
    # Cape Verde
    "cape verde islands":      ["cape verde"],
    "cape verde":              ["cape verde islands", "cabo verde"],
    # Macedonia
    "north macedonia":         ["macedonia"],
}

def _name_variants(name: str) -> list[str]:
    """Return all known variants of a team name."""
    key = name.lower()
    return [key] + NAME_ALIASES.get(key, [])


def find_match_odds(home_en: str, away_en: str, all_odds: list[dict]) -> dict | None:
    """Find odds for a specific match by team name (fuzzy + aliases)."""
    home_variants = _name_variants(home_en)
    away_variants = _name_variants(away_en)

    for event in all_odds:
        h = event.get("home_team", "").lower()
        a = event.get("away_team", "").lower()

        def matches(variants: list[str], api_name: str) -> bool:
            return any(v in api_name or api_name in v for v in variants)

        if matches(home_variants, h) and matches(away_variants, a):
            return parse_odds(event)
        if matches(away_variants, h) and matches(home_variants, a):
            result = parse_odds(event)
            if result:
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
