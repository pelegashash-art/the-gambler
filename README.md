# 🎲 The Gambler — WC 2026 Match Analysis Bot

בוט טלגרם שמנתח משחקי מונדיאל 2026 ושולח המלצות הימורים יומיות בעברית.

---

## מה הבוט עושה

כל יום ב-**20:00 שעון ישראל**, הבוט:
1. בודק אילו משחקים מתקיימים היום (מתוך קובץ Excel)
2. שולף יחסי הימורים עדכניים (The Odds API)
3. מנתח כל משחק עם Claude (Anthropic)
4. שולח הודעה אחת מרוכזת לערוץ טלגרם

---

## מבנה הפרויקט

```
the-gambler/
├── main.py              ← נקודת כניסה, לוגיקה יומית
├── server.py            ← Flask web server + ממשק ניהול + APScheduler
├── fixtures.py          ← טעינת לוח המשחקים מ-Excel
├── odds.py              ← שליפת יחסי הימורים (The Odds API)
├── analyzer.py          ← ניתוח משחקים עם Claude + בניית הודעה
├── telegram_send.py     ← שליחה לערוץ טלגרם
├── usage_tracker.py     ← מעקב עלויות API
├── gunicorn.conf.py     ← הגדרות Gunicorn + הפעלת Scheduler
├── Dockerfile           ← קונטיינר לדפלוי ב-Railway
├── railway.toml         ← הגדרות Railway
├── requirements.txt
└── data/
    ├── wc2026_fixtures.xlsx   ← לוח 72 משחקי שלב הבתים
    └── usage.json             ← נוצר אוטומטית, מעקב שימוש
```

---

## משתני סביבה

```env
ANTHROPIC_API_KEY=       # Claude API key
TELEGRAM_BOT_TOKEN=      # טוקן הבוט מ-@BotFather
TELEGRAM_CHANNEL_ID=     # מזהה הערוץ (מינוס, למשל: -1001234567890)
ODDS_API_KEY=            # The Odds API key (500 קריאות/חודש בחינם)
ADMIN_PASSWORD=          # סיסמת כניסה לממשק הניהול
ADMIN_SECRET=            # מפתח סודי ל-Flask session
PORT=8080                # פורט השרת (ברירת מחדל: 8080)
```

---

## ממשק ניהול

פנל ניהול ב-web:
- **סטטיסטיקת שימוש**: עלויות Anthropic, קריאות Odds API
- **לוח משחקים**: כל המשחקים הקרובים מקובצים לפי יום
- **שליחה ידנית**: כפתור "שלח ניתוח" לכל יום בנפרד

---

## הפעלה מקומית

```bash
pip install -r requirements.txt

# הרצה לתאריך ספציפי
python main.py --date 2026-06-11

# הרצת השרת
python server.py
```

---

## דפלוי ב-Railway

1. צור שירות חדש מ-GitHub repo
2. Railway יזהה את ה-Dockerfile אוטומטית
3. הגדר את כל משתני הסביבה (ENV vars) ב-Railway Settings
4. ב-Railway Networking — ודא שה-port מוגדר ל-**8080**
5. ב-Railway Settings → Teardown — **הפעל** (כדי שדפלוי חדש יחליף את הישן)

הבוט ירוץ כשרת Flask עם scheduler מובנה — לא נדרש cron חיצוני.

---

## פורמט ההודעה

```
🌍 מונדיאל 2026 — 11/06/2026

⚽ ארגנטינה נגד קנדה
🕐 22:00 | מונדיאל 2026 סיבוב 1

📊 יחסי הימורים:
ארגנטינה: x1.45 (69%)
תיקו: x4.20 (24%)
קנדה: x7.00 (14%)

📋 ניתוח:
• ארגנטינה ניצחה ב-8 מתוך 10 משחקים אחרונים.
• קנדה הפסידה לכל הנבחרות מדורגות בשנה האחרונה.
• יחס של 1.45 משקף שליטה ברורה של ארגנטינה.

🎯 המלצה: ארגנטינה (1)
⭐ ביטחון: ★★★★
🔢 ניחוש תוצאה: 3-0

💡 בקצרה: ארגנטינה דומיננטית, קנדה חסרת ניסיון בזירה הגדולה.
```

---

## מקורות נתונים

| מקור | שימוש | עלות |
|------|--------|------|
| Excel מקומי | לוח המשחקים | חינם |
| [The Odds API](https://the-odds-api.com) | יחסי הימורים 1/X/2 | חינם עד 500/חודש |
| [Anthropic Claude](https://anthropic.com) | ניתוח + עברית | ~$0.005 להודעה |
| [Telegram Bot API](https://core.telegram.org/bots/api) | שליחת הודעות | חינם |
