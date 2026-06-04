"""Track API usage and costs across services."""
import json
from datetime import datetime
from pathlib import Path

USAGE_FILE = Path("data/usage.json")

# Pricing (USD per 1M tokens) — GPT-4.5
GPT45_INPUT_PRICE  = 75.00
GPT45_OUTPUT_PRICE = 150.00
ODDS_API_MONTHLY_LIMIT = 500


def _load() -> dict:
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {
        "openai":   {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0},
        "odds_api": {"calls": 0, "month": ""},
        "last_updated": ""
    }


def _save(data: dict):
    USAGE_FILE.parent.mkdir(exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _migrate(data: dict) -> dict:
    """Migrate old anthropic key to openai if needed."""
    if "anthropic" in data and "openai" not in data:
        data["openai"] = data.pop("anthropic")
    if "openai" not in data:
        data["openai"] = {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0}
    return data


def track_openai(input_tokens: int, output_tokens: int):
    data = _migrate(_load())
    cost = (input_tokens * GPT45_INPUT_PRICE + output_tokens * GPT45_OUTPUT_PRICE) / 1_000_000
    data["openai"]["input_tokens"]  += input_tokens
    data["openai"]["output_tokens"] += output_tokens
    data["openai"]["calls"]         += 1
    data["openai"]["cost_usd"]      = round(data["openai"]["cost_usd"] + cost, 6)
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
    odds_calls = data["odds_api"]["calls"] if data["odds_api"]["month"] == month else 0
    ai = data["openai"]

    return {
        "ai_calls":       ai["calls"],
        "ai_input":       ai["input_tokens"],
        "ai_output":      ai["output_tokens"],
        "ai_cost":        round(ai["cost_usd"], 4),
        "odds_calls":     odds_calls,
        "odds_remaining": ODDS_API_MONTHLY_LIMIT - odds_calls,
    }
