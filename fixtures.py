import pandas as pd
from datetime import datetime, date
import pytz

ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
EXCEL_PATH = "data/wc2026_fixtures.xlsx"

def load_fixtures() -> pd.DataFrame:
    df = pd.read_excel(EXCEL_PATH)
    # Parse datetime in UTC
    df["datetime_utc"] = pd.to_datetime(
        df["תאריך"].astype(str) + " " + df["שעה (UTC)"].astype(str),
        format="%Y-%m-%d %H:%M"
    ).dt.tz_localize("UTC")
    df["datetime_il"] = df["datetime_utc"].dt.tz_convert(ISRAEL_TZ)
    return df

def get_todays_matches(target_date: date | None = None) -> list[dict]:
    df = load_fixtures()
    if target_date is None:
        target_date = datetime.now(ISRAEL_TZ).date()

    todays = df[df["datetime_il"].dt.date == target_date]

    matches = []
    for _, row in todays.iterrows():
        matches.append({
            "id": row["מזהה משחק"],
            "match_num": row["מספר משחק"],
            "stage": row["שלב"],
            "round": row["סיבוב"],
            "home_he": row["קבוצת בית (עברית)"],
            "away_he": row["קבוצת חוץ (עברית)"],
            "home_en": row["קבוצת בית (אנגלית)"],
            "away_en": row["קבוצת חוץ (אנגלית)"],
            "kickoff_utc": row["datetime_utc"],
            "kickoff_il": row["datetime_il"],
            "kickoff_il_str": row["datetime_il"].strftime("%H:%M"),
        })
    return sorted(matches, key=lambda m: m["kickoff_utc"])
