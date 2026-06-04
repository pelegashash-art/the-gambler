#!/usr/bin/env python3
"""
The Gambler — WC 2026 Daily Match Alert Bot
Runs daily at 20:00 Israel time (via Railway cron: 0 17 * * *)
Usage: python main.py [--date YYYY-MM-DD]
"""
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import argparse
from datetime import date, datetime
import pytz
from dotenv import load_dotenv

load_dotenv(override=True)

from fixtures import get_todays_matches
from odds import get_wc_odds, find_match_odds
from analyzer import analyze_match, build_daily_message
from telegram_send import send_long_message

ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")


def run(target_date: date | None = None):
    today_str = (target_date or datetime.now(ISRAEL_TZ).date()).strftime("%d/%m/%Y")
    print(f"[The Gambler] Running for {today_str}")

    # 1. Get today's matches
    matches = get_todays_matches(target_date)
    if not matches:
        print(f"[The Gambler] No matches today ({today_str})")
        send_long_message(f"🏖️ אין משחקי מונדיאל היום ({today_str})")
        return

    print(f"[The Gambler] Found {len(matches)} matches")

    # 2. Fetch all odds once
    print("[The Gambler] Fetching odds...")
    all_odds = get_wc_odds()
    print(f"[The Gambler] Got odds for {len(all_odds)} events")

    # 3. Analyze each match with Claude
    analyses = []
    for match in matches:
        print(f"[The Gambler] Analyzing: {match['home_he']} vs {match['away_he']}")
        odds = find_match_odds(match["home_en"], match["away_en"], all_odds)
        analysis = analyze_match(match, odds)
        analyses.append(analysis)

    # 4. Build and send daily message
    message = build_daily_message(matches, analyses, today_str)
    print(f"[The Gambler] Sending message ({len(message)} chars)...")
    success = send_long_message(message)

    if success:
        print("[The Gambler] Done!")
    else:
        print("[The Gambler] Failed to send message")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Target date YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    target = date.fromisoformat(args.date) if args.date else None
    run(target)
