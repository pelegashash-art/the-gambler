import os
import anthropic
from dotenv import load_dotenv
from odds import implied_prob

load_dotenv(override=True)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def analyze_match(match: dict, odds: dict | None) -> str:
    """Use Claude to analyze a match and return a formatted WhatsApp block."""

    if odds:
        home_prob = implied_prob(odds["home_odds"])
        draw_prob = implied_prob(odds.get("draw_odds") or 0)
        away_prob = implied_prob(odds["away_odds"])
        odds_section = (
            f"• {match['home_he']}: x{odds['home_odds']} ({home_prob}%)\n"
            f"• תיקו: x{odds.get('draw_odds', 'N/A')} ({draw_prob}%)\n"
            f"• {match['away_he']}: x{odds['away_odds']} ({away_prob}%)"
        )
    else:
        odds_section = "• יחס הימורים לא זמין — בדוק ידנית"

    prompt = f"""אתה מומחה הימורי כדורגל. כתוב ניתוח קצר וחד בעברית בלבד.

משחק: {match['home_en']} vs {match['away_en']}
מונדיאל 2026, שלב בתים סיבוב {match['round']}
שעה (ישראל): {match['kickoff_il_str']}

יחס הימורים:
{odds_section}

כללים לכתיבה:
- כל נקודת ניתוח: עד 8 מילים, חדה ועובדתית
- שמות שחקנים בעברית בלבד (או השמט)
- אל תכתוב משפטים כלליים כמו "קבוצות חזקות משחקות בזהירות"
- ביטחון: מספר כוכבים מלאים בלבד (★★★ = שלושה כוכבים)
- אל תוסיף שום טקסט מחוץ לפורמט

החזר בדיוק:

⚽ *{match['home_he']} נגד {match['away_he']}*
🕐 {match['kickoff_il_str']} | מונדיאל 2026 סיבוב {match['round']}

📊 *יחס הימורים:*
{odds_section}

📋 *ניתוח:*
• [עובדה קצרה על קבוצת הבית]
• [עובדה קצרה על קבוצת החוץ]
• [נקודת value מהיחס הימורים או יתרון טקטי]

🎯 *המלצה: [שם הקבוצה בעברית] ([1 או X או 2])*
ביטחון: [★ עד ★★★★★]

💡 *למה:* [משפט אחד, מקסימום 15 מילים]"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )

    for block in response.content:
        if hasattr(block, "text"):
            return block.text.strip()

    return f"⚽ *{match['home_he']} vs {match['away_he']}*\n🕐 {match['kickoff_il_str']}\n\n{odds_section}"


def build_daily_message(matches: list[dict], analyses: list[str], target_date: str) -> str:
    """Combine all match analyses into one WhatsApp message."""
    separator = "\n\n━━━━━━━━━━━━━━━━\n\n"

    header = f"🌍 *מונדיאל 2026 — {target_date}*\n"
    body = separator.join(analyses)

    match_list = "\n".join(
        f"  {m['home_he']} vs {m['away_he']} — {m['kickoff_il_str']}"
        for m in matches
    )
    footer = f"\n\n━━━━━━━━━━━━━━━━\n📅 *{len(matches)} משחקים היום:*\n{match_list}"

    return header + "\n" + body + footer
