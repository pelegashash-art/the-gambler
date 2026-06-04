import os
import anthropic
from dotenv import load_dotenv
from odds import implied_prob
from usage_tracker import track_anthropic

load_dotenv(override=True)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def analyze_match(match: dict, odds: dict | None) -> str:
    """Use Claude to analyze a match and return a formatted Telegram block."""

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

לפני שתכתוב את הניתוח, חפש חדשות עדכניות על:
1. פציעות והיעדרויות בשתי הקבוצות
2. מידע דרמטי שעלול להשפיע על התוצאה (השעיות, מצב כושר, מוטיבציה)
3. ביצועים אחרונים של הקבוצות

כללים לכתיבה:
- כל נקודת ניתוח: עד 8 מילים, חדה ועובדתית
- שמות שחקנים בעברית בלבד (או השמט)
- אל תכתוב משפטים כלליים
- ביטחון: מספר כוכבים מלאים בלבד (★★★ = שלושה כוכבים)
- ניחוש תוצאה: תוצאה מדויקת כמו 2-1, 1-0 (הכי סבירה סטטיסטית)
- אל תוסיף שום טקסט מחוץ לפורמט

החזר בדיוק:

⚽ *{match['home_he']} נגד {match['away_he']}*
🕐 {match['kickoff_il_str']} | מונדיאל 2026 סיבוב {match['round']}

📊 *יחס הימורים:*
{odds_section}

📋 *ניתוח:*
• [עובדה קצרה על קבוצת הבית]
• [עובדה קצרה על קבוצת החוץ]
• [פציעות / היעדרויות אם רלוונטי]
• [נקודת value מהיחס הימורים]

🎯 *המלצה: [שם הקבוצה בעברית] ([1 או X או 2])*
ביטחון: [★ עד ★★★★★]
⚽ *ניחוש תוצאה: [X-Y]*

💡 *למה:* [משפט אחד, מקסימום 15 מילים]"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 3
        }],
        messages=[{"role": "user", "content": prompt}]
    )

    # Track usage
    if response.usage:
        track_anthropic(response.usage.input_tokens, response.usage.output_tokens)

    # Extract text from response (might have tool_use blocks)
    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text.strip())

    result = "\n".join(text_parts).strip()
    if result:
        return result

    return f"⚽ *{match['home_he']} vs {match['away_he']}*\n🕐 {match['kickoff_il_str']}\n\n{odds_section}"


def build_daily_message(matches: list[dict], analyses: list[str], target_date: str) -> str:
    """Combine all match analyses into one message."""
    separator = "\n\n━━━━━━━━━━━━━━━━\n\n"

    header = f"🌍 <b>מונדיאל 2026 — {target_date}</b>\n"
    body = separator.join(analyses)

    match_list = "\n".join(
        f"  {m['home_he']} vs {m['away_he']} — {m['kickoff_il_str']}"
        for m in matches
    )
    footer = f"\n\n━━━━━━━━━━━━━━━━\n📅 <b>{len(matches)} משחקים היום:</b>\n{match_list}"

    return header + "\n" + body + footer
