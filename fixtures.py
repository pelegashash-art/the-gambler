import pandas as pd
from datetime import datetime, date, timedelta
import pytz

ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
EXCEL_PATH = "data/wc2026_fixtures.xlsx"

# משחקים שמתחילים לפני שעה זו ביום המחרת נחשבים "משחקי הלילה" של אותה הודעה
NEXT_DAY_CUTOFF_HOUR = 14  # 14:00 ישראל


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
    """
    מחזיר משחקים של יום target_date + משחקי לילה של אותו יום
    (משחקים שמתחילים אחרי חצות עד NEXT_DAY_CUTOFF_HOUR ביום המחרת).
    """
    df = load_fixtures()
    if target_date is None:
        target_date = datetime.now(ISRAEL_TZ).date()

    next_date = target_date + timedelta(days=1)

    # משחקי יום target_date
    same_day = df[df["datetime_il"].dt.date == target_date]

    # משחקי לילה: יום המחרת לפני השעה NEXT_DAY_CUTOFF_HOUR
    next_day_morning = df[
        (df["datetime_il"].dt.date == next_date) &
        (df["datetime_il"].dt.hour < NEXT_DAY_CUTOFF_HOUR)
    ]

    combined = pd.concat([same_day, next_day_morning])

    matches = []
    for _, row in combined.iterrows():
        kickoff_il = row["datetime_il"]
        # תצוגת שעה — אם אחרי חצות, מוסיף ציון "מחר"
        if kickoff_il.date() == next_date:
            time_str = kickoff_il.strftime("%H:%M") + " (מחר)"
        else:
            time_str = kickoff_il.strftime("%H:%M")

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
            "kickoff_il": kickoff_il,
            "kickoff_il_str": time_str,
        })
    return sorted(matches, key=lambda m: m["kickoff_utc"])
