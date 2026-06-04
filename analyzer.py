import os
from openai import OpenAI
from dotenv import load_dotenv
from odds import implied_prob
from usage_tracker import track_openai
from football_stats import get_match_stats

load_dotenv(override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """אתה מומחה הימורי כדורגל בכיר. אתה כותב בעברית תקנית, בהירה וקולחת.
חוקים מוחלטים:
- כתוב בעברית בלבד, ללא מילים באנגלית
- כל משפט: קצר, חד, עובדתי — מקסימום 10 מילים
- אסור לכתוב משפטים סתמיים כמו "קבוצה חזקה" או "משחק מעניין"
- שמות שחקנים: בעברית או לא בכלל
- ביטחון: כוכבים מלאים בלבד ★ (לא ☆)
- החזר את הפורמט המבוקש בדיוק, ללא הוספות"""


def analyze_match(match: dict, odds: dict | None) -> str:
    """Analyze a match using GPT-4o and return a formatted Telegram message block."""

    if odds:
        hp = implied_prob(odds["home_odds"])
        dp = implied_prob(odds.get("draw_odds") or 0)
        ap = implied_prob(odds["away_odds"])
        odds_text = (
            f"{match['home_he']}: x{odds['home_odds']} ({hp}%)\n"
            f"תיקו: x{odds.get('draw_odds', 'N/A')} ({dp}%)\n"
            f"{match['away_he']}: x{odds['away_odds']} ({ap}%)"
        )
    else:
        odds_text = "יחס הימורים אינו זמין"

    # Form stats from API-Football (last 5 matches)
    stats_text = get_match_stats(match["home_en"], match["away_en"])
    stats_section = f"\nנתוני ביצועים אחרונים:\n{stats_text}" if stats_text else ""

    prompt = f"""נתח את המשחק הבא ובנה הודעה לפי הפורמט המדויק.

פרטי המשחק:
- {match['home_he']} (בית) מול {match['away_he']} (חוץ)
- מונדיאל 2026, שלב הבתים, סיבוב {match['round']}
- שעת קיקאוף (ישראל): {match['kickoff_il_str']}

יחסי הימורים:
{odds_text}
{stats_section}

בנה את ההודעה בפורמט הבא (החלף את הסוגריים המרובעים בתוכן אמיתי):

⚽ {match['home_he']} נגד {match['away_he']}
🕐 {match['kickoff_il_str']} | מונדיאל 2026 סיבוב {match['round']}

📊 יחסי הימורים:
{odds_text}

📋 ניתוח:
• [עובדה משמעותית על קבוצת הבית]
• [עובדה משמעותית על קבוצת החוץ]
• [למה הניחוש הזה מוצדק לפי היחסים]

🎯 המלצה: [שם הקבוצה או "תיקו"] ([1 / X / 2])
⭐ ביטחון: [★ עד ★★★★★]
🔢 ניחוש תוצאה: [X-Y]

💡 בקצרה: [משפט אחד מנומק, מקסימום 12 מילים]"""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=600,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    usage = response.usage
    if usage:
        track_openai(usage.prompt_tokens, usage.completion_tokens)

    content = response.choices[0].message.content
    if content:
        return content.strip()

    return f"⚽ {match['home_he']} נגד {match['away_he']}\n🕐 {match['kickoff_il_str']}\n\n{odds_text}"


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
