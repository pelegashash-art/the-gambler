"""Track API usage and costs across services."""
import json
from datetime import datetime
from pathlib import Path

USAGE_FILE = Path("data/usage.json")

# Pricing (USD per 1M tokens) — Gemini 2.0 Flash
GEMINI_INPUT_PRICE  = 0.10
GEMINI_OUTPUT_PRICE = 0.40
ODDS_API_MONTHLY_LIMIT   = 500
APIFOOTBALL_DAILY_LIMIT  = 100


def _load() -> dict:
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {
        "gemini":      {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0},
        "odds_api":    {"calls": 0, "month": ""},
        "apifootball": {"calls": 0, "day": ""},
        "last_updated": ""
    }


def _save(data: dict):
    USAGE_FILE.parent.mkdir(exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _migrate(data: dict) -> dict:
    if "gemini" not in data:
        data["gemini"] = {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0}
    if "apifootball" not in data:
        data["apifootball"] = {"calls": 0, "day": ""}
    return data


def track_gemini(input_tokens: int, output_tokens: int):
    data = _migrate(_load())
    cost = (input_tokens * GEMINI_INPUT_PRICE + output_tokens * GEMINI_OUTPUT_PRICE) / 1_000_000
    data["gemini"]["input_tokens"]  += input_tokens
    data["gemini"]["output_tokens"] += output_tokens
    data["gemini"]["calls"]         += 1
    data["gemini"]["cost_usd"]      = round(data["gemini"]["cost_usd"] + cost, 6)
    data["last_updated"] = datetime.now().isoformat()
    _save(data)


def track_apifootball():
    data = _migrate(_load())
    day  = datetime.now().strftime("%Y-%m-%d")
    if data["apifootball"]["day"] != day:
        data["apifootball"]["calls"] = 0
        data["apifootball"]["day"]   = day
    data["apifootball"]["calls"] += 1
    data["last_updated"] = datetime.now().isoformat()
    _save(data)


def track_odds_api():
    data  = _migrate(_load())
    month = datetime.now().strftime("%Y-%m")
    if data["odds_api"]["month"] != month:
        data["odds_api"]["calls"] = 0
        data["odds_api"]["month"] = month
    data["odds_api"]["calls"] += 1
    data["last_updated"] = datetime.now().isoformat()
    _save(data)


def get_stats() -> dict:
    data  = _migrate(_load())
    month = datetime.now().strftime("%Y-%m")
    day   = datetime.now().strftime("%Y-%m-%d")
    g  = data["gemini"]
    fb = data["apifootball"]
    return {
        "gemini_calls":   g["calls"],
        "gemini_input":   g["input_tokens"],
        "gemini_output":  g["output_tokens"],
        "gemini_cost":    round(g["cost_usd"], 4),
        "fb_calls":       fb["calls"] if fb["day"] == day else 0,
        "fb_remaining":   APIFOOTBALL_DAILY_LIMIT - (fb["calls"] if fb["day"] == day else 0),
    }
