"""Track API usage and costs across services."""
import json
from datetime import datetime
from pathlib import Path

USAGE_FILE = Path("data/usage.json")

# Pricing (USD per 1M tokens)
SONNET_INPUT_PRICE  = 3.00
SONNET_OUTPUT_PRICE = 15.00
ODDS_API_MONTHLY_LIMIT = 500


def _load() -> dict:
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {
        "anthropic": {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0},
        "odds_api":  {"calls": 0, "month": ""},
        "last_updated": ""
    }


def _save(data: dict):
    USAGE_FILE.parent.mkdir(exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def track_anthropic(input_tokens: int, output_tokens: int):
    data = _load()
    cost = (input_tokens * SONNET_INPUT_PRICE + output_tokens * SONNET_OUTPUT_PRICE) / 1_000_000
    data["anthropic"]["input_tokens"]  += input_tokens
    data["anthropic"]["output_tokens"] += output_tokens
    data["anthropic"]["calls"]         += 1
    data["anthropic"]["cost_usd"]      = round(data["anthropic"]["cost_usd"] + cost, 6)
    data["last_updated"] = datetime.now().isoformat()
    _save(data)


def track_odds_api():
    data  = _load()
    month = datetime.now().strftime("%Y-%m")
    if data["odds_api"]["month"] != month:
        data["odds_api"]["calls"] = 0
        data["odds_api"]["month"] = month
    data["odds_api"]["calls"] += 1
    data["last_updated"] = datetime.now().isoformat()
    _save(data)


def get_stats() -> dict:
    data  = _load()
    month = datetime.now().strftime("%Y-%m")
    if data["odds_api"]["month"] != month:
        odds_calls = 0
    else:
        odds_calls = data["odds_api"]["calls"]

    return {
        "anthropic_calls":   data["anthropic"]["calls"],
        "anthropic_input":   data["anthropic"]["input_tokens"],
        "anthropic_output":  data["anthropic"]["output_tokens"],
        "anthropic_cost":    round(data["anthropic"]["cost_usd"], 4),
        "odds_calls":        odds_calls,
        "odds_remaining":    ODDS_API_MONTHLY_LIMIT - odds_calls,
    }
