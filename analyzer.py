import os
import google.generativeai as genai
from dotenv import load_dotenv
from usage_tracker import track_gemini

load_dotenv(override=True)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def analyze_match(match: dict) -> str:
    """Analyze a match using Gemini Flash and return a formatted Telegram message block."""

    home = match["home_he"]
    away = match["away_he"]
    time = match["kickoff_il_str"]
    rnd  = match["round"]

    prompt = f"""תפעל כמומחה לאנליזת כדורגל והימורי ספורט. אני צריך שתספק לי תחזית קצרה, תמציתית וממוקדת למשחק הבא: {home} נגד {away}.

תציג את המידע בפורמט הבא בלבד, תוך שימוש בנקודות וללא הקדמות או סיכומים מיותרים:

⚽ {home} נגד {away}
🕐 {time} | מונדיאל 2026 סיבוב {rnd}

1. פייבוריטית ברורה: [מי הקבוצה שצפויה לנצח]
2. יחסי כוחות (באחוזים ל-1X2): [למשל: 60% ניצחון {home}, 25% תיקו, 15% ניצחון {away}]
3. צפי שערים: [האם צפוי משחק עם הרבה שערים או מעט? Over/Under 2.5]
4. הימור מומלץ/בעל ערך: [הימור אחד פשוט וממוקד שלדעתך הכי הגיוני למשחק הזה]
5. תוצאה מדויקת סבירה ביותר: [התוצאה שלדעתך הכי ריאלית]

שמור על סגנון כתיבה קריא, פשוט ומהיר לסריקה בטלפון. כתוב בעברית בלבד."""

    try:
        response = model.generate_content(prompt)

        if hasattr(response, "usage_metadata"):
            u = response.usage_metadata
            track_gemini(
                getattr(u, "prompt_token_count", 0),
                getattr(u, "candidates_token_count", 0)
            )

        return response.text.strip()

    except Exception as e:
        print(f"[Gemini] Error for {home} vs {away}: {e}")
        return f"⚽ {home} נגד {away}\n🕐 {time} | מונדיאל 2026 סיבוב {rnd}\n\n⚠️ שגיאה בניתוח"


def build_daily_message(matches: list[dict], analyses: list[str], target_date: str) -> str:
    """Combine all match analyses into one Telegram message."""
    separator = "\n\n━━━━━━━━━━━━━━━━\n\n"
    header = f"🌍 מונדיאל 2026 — {target_date}\n"
    body = separator.join(analyses)
    match_lines = "\n".join(
        f"  {m['home_he']} נגד {m['away_he']} — {m['kickoff_il_str']}"
        for m in matches
    )
    footer = f"\n\n━━━━━━━━━━━━━━━━\n📅 {len(matches)} משחקים היום:\n{match_lines}"
    return header + "\n" + body + footer
