#!/usr/bin/env python3
"""
The Gambler — Web Server with daily scheduler.
"""
import os
import threading
from datetime import date
from dotenv import load_dotenv

load_dotenv(override=True)

from flask import Flask, request, redirect, session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from main import run

app = Flask(__name__)
app.secret_key = os.getenv("ADMIN_SECRET", "changeme123")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "gambler2026")
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")


# ── Routes ───────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["auth"] = True
            return redirect("/")
        error = "סיסמה שגויה"
    return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head><meta charset="UTF-8"><title>כניסה</title>
<style>body{{font-family:Arial;background:#0f172a;color:#f1f5f9;
  display:flex;align-items:center;justify-content:center;height:100vh;margin:0}}
  .box{{background:#1e293b;padding:40px;border-radius:16px;text-align:center;width:300px}}
  input{{width:100%;padding:10px;margin:10px 0;border-radius:8px;border:1px solid #334155;
         background:#0f172a;color:white;box-sizing:border-box;font-size:15px}}
  button{{background:#10b981;color:white;border:none;padding:12px 30px;
          border-radius:8px;cursor:pointer;font-size:15px;width:100%}}
  .err{{color:#f87171;margin-top:8px}}</style>
</head>
<body><div class="box">
  <h2>🎲 The Gambler</h2>
  <form method="POST">
    <input type="password" name="password" placeholder="סיסמה" autofocus>
    <button>כניסה</button>
    <p class="err">{error}</p>
  </form>
</div></body></html>"""


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


def get_schedule_html():
    """Return HTML for the full match schedule grouped by date."""
    try:
        from fixtures import load_fixtures
        import pandas as pd
        df = load_fixtures()
        today = date.today()
        df = df[df["datetime_il"].dt.date >= today].copy()
        df = df.sort_values("datetime_utc")

        # Group by date
        rows_by_date = {}
        for _, row in df.iterrows():
            d = row["datetime_il"].date()
            if d not in rows_by_date:
                rows_by_date[d] = []
            rows_by_date[d].append(row)

        html = ""
        for d, matches in rows_by_date.items():
            date_str = d.strftime("%d/%m/%Y")
            iso = d.isoformat()
            match_lines = "".join(
                f'<div class="match">⚽ {r["קבוצת בית (עברית)"]} נגד {r["קבוצת חוץ (עברית)"]} '
                f'<span class="time">{r["datetime_il"].strftime("%H:%M")}</span></div>'
                for r in matches
            )
            html += f"""
<div class="day-card">
  <div class="day-header">
    <span>📅 {date_str} &nbsp;·&nbsp; {len(matches)} משחקים</span>
    <form method="POST" action="/test" style="display:inline">
      <input type="hidden" name="date" value="{iso}">
      <button type="submit" class="btn-send">שלח ניתוח 🚀</button>
    </form>
  </div>
  {match_lines}
</div>"""
        return html or "<p style='color:#64748b'>אין משחקים קרובים</p>"
    except Exception as e:
        return f"<p style='color:#f87171'>שגיאה בטעינת לוח: {e}</p>"


@app.route("/")
def index():
    if not session.get("auth"):
        return redirect("/login")
    from usage_tracker import get_stats
    s = get_stats()
    odds_bar = 0  # odds API no longer used
    schedule_html = get_schedule_html()

    return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>🎲 The Gambler</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f1f5f9;
           max-width: 650px; margin: 40px auto; padding: 20px; }}
    h1 {{ color: #10b981; margin-bottom: 4px; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 20px; margin: 16px 0; }}
    .logout {{ float: left; color: #64748b; text-decoration: none; font-size: 13px; }}
    .stat {{ display: flex; justify-content: space-between; padding: 7px 0;
             border-bottom: 1px solid #334155; font-size: 14px; }}
    .stat:last-child {{ border-bottom: none; }}
    .val {{ color: #10b981; font-weight: bold; }}
    .bar-bg {{ background: #334155; border-radius: 4px; height: 6px; margin: 6px 0 10px; }}
    .bar-fill {{ background: #10b981; border-radius: 4px; height: 6px; }}
    .flow {{ display: flex; flex-direction: column; gap: 0; }}
    .flow-step {{ display: flex; align-items: flex-start; gap: 12px; padding: 10px 0;
                  border-bottom: 1px solid #334155; font-size: 13px; }}
    .flow-step:last-child {{ border-bottom: none; }}
    .flow-icon {{ font-size: 20px; min-width: 28px; text-align: center; margin-top: 1px; }}
    .flow-body {{ flex: 1; }}
    .flow-title {{ font-weight: bold; color: #f1f5f9; margin-bottom: 2px; }}
    .flow-desc {{ color: #94a3b8; line-height: 1.5; }}
    .flow-tag {{ display: inline-block; background: #0f172a; border: 1px solid #334155;
                 border-radius: 4px; padding: 1px 7px; font-size: 11px; color: #64748b;
                 margin-top: 4px; margin-left: 4px; }}
    .day-card {{ background: #1e293b; border-radius: 10px; padding: 14px 16px; margin: 10px 0; }}
    .day-header {{ display: flex; justify-content: space-between; align-items: center;
                   margin-bottom: 8px; font-weight: bold; }}
    .btn-send {{ background: #10b981; color: white; border: none; padding: 6px 14px;
                 border-radius: 6px; cursor: pointer; font-size: 13px; }}
    .btn-send:hover {{ background: #059669; }}
    .match {{ font-size: 13px; color: #94a3b8; padding: 3px 0; }}
    .time {{ color: #64748b; margin-left: 6px; }}
    /* floating how-it-works */
    .fab {{ position: fixed; top: 16px; left: 16px; background: #1e293b;
            border: 1px solid #334155; color: #94a3b8; border-radius: 10px;
            padding: 7px 13px; cursor: pointer; font-size: 13px; z-index: 100;
            display: flex; align-items: center; gap: 6px; }}
    .fab:hover {{ background: #334155; color: #f1f5f9; }}
    .fab-label {{ font-size: 12px; }}
    .panel-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,.55);
                      z-index: 200; align-items: flex-start; justify-content: flex-start; }}
    .panel-overlay.open {{ display: flex; }}
    .panel-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 14px;
                  margin: 14px; width: 340px; max-height: calc(100vh - 28px);
                  overflow-y: auto; padding: 20px; position: relative; }}
    .panel-close {{ position: absolute; top: 12px; left: 12px; background: none;
                    border: none; color: #64748b; font-size: 18px; cursor: pointer; }}
    .panel-close:hover {{ color: #f1f5f9; }}
  </style>
</head>
<body>

  <!-- floating button -->
  <button class="fab" onclick="document.getElementById('flowPanel').classList.add('open')">
    ⚙️ <span class="fab-label">איך זה עובד?</span>
  </button>

  <!-- overlay panel -->
  <div class="panel-overlay" id="flowPanel"
       onclick="if(event.target===this)this.classList.remove('open')">
    <div class="panel-box">
      <button class="panel-close" onclick="document.getElementById('flowPanel').classList.remove('open')">✕</button>
      <h3 style="margin-top:0;margin-bottom:14px">⚙️ איך התהליך עובד</h3>
      <div class="flow">

        <div class="flow-step">
          <div class="flow-icon">📂</div>
          <div class="flow-body">
            <div class="flow-title">שלב 1 — לוח המשחקים</div>
            <div class="flow-desc">הבוט קורא קובץ Excel מקומי עם 72 משחקי שלב הבתים של מונדיאל 2026, וסולן אילו מהם מתקיימים היום לפי שעון ישראל (UTC+3).</div>
            <span class="flow-tag">📁 wc2026_fixtures.xlsx</span>
            <span class="flow-tag">ללא API</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">🤖</div>
          <div class="flow-body">
            <div class="flow-title">שלב 2 — ניתוח Gemini Flash</div>
            <div class="flow-desc">לכל משחק — קריאה נפרדת ל-<strong>Gemini 2.0 Flash</strong> עם שמות הקבוצות ושעת הקיקאוף. Gemini מחזיר ניתוח בעברית: פייבוריטית, יחסי כוחות (1X2%), צפי שערים (Over/Under 2.5), הימור מומלץ ותוצאה סבירה.</div>
            <span class="flow-tag">🌐 generativelanguage.googleapis.com</span>
            <span class="flow-tag">gemini-2.0-flash</span>
            <span class="flow-tag">~$0.0001 למשחק</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">📨</div>
          <div class="flow-body">
            <div class="flow-title">שלב 3 — שליחה לטלגרם</div>
            <div class="flow-desc">כל הניתוחים מחוברים להודעה יומית אחת מסודרת ונשלחים לערוץ הטלגרם הפרטי. הודעות מעל 4,000 תווים מפוצלות אוטומטית.</div>
            <span class="flow-tag">🌐 api.telegram.org</span>
            <span class="flow-tag">ללא מגבלה</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">🌙</div>
          <div class="flow-body">
            <div class="flow-title">שלב 4 — כיסוי משחקי לילה</div>
            <div class="flow-desc">מכיוון שרוב משחקי המונדיאל מתקיימים בשעות הלילה של ישראל, ההודעה של 20:00 כוללת גם את משחקי אחרי חצות — כל משחק שמתחיל לפני <strong>14:00 ביום המחרת</strong>. משחקים כאלה מסומנים עם "(מחר)" ליד השעה.</div>
            <span class="flow-tag">חלון: 20:00 היום — 14:00 מחר</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">⏰</div>
          <div class="flow-body">
            <div class="flow-title">שלב 5 — תזמון אוטומטי</div>
            <div class="flow-desc">כל יום ב-<strong>20:00 שעון ישראל</strong> — APScheduler המובנה בשרת Flask מפעיל את כל התהליך. ניתן גם להפעיל ידנית מכל יום בלוח המשחקים.</div>
            <span class="flow-tag">APScheduler</span>
            <span class="flow-tag">Asia/Jerusalem (UTC+3)</span>
          </div>
        </div>

      </div>
    </div>
  </div>

  <h1>🎲 The Gambler</h1>
  <a class="logout" href="/logout">יציאה</a>

  <div class="card">
    <h3 style="margin-top:0">📊 שימוש ב-APIs</h3>
    <div class="stat"><span>🤖 Gemini Flash — קריאות</span><span class="val">{s['gemini_calls']}</span></div>
    <div class="stat"><span>🤖 Gemini Flash — עלות</span><span class="val">${s['gemini_cost']}</span></div>
    <div class="stat"><span>🤖 Gemini Flash — טוקנים</span><span class="val">{s['gemini_input']:,} in / {s['gemini_output']:,} out</span></div>
    <div class="stat"><span>📨 Telegram</span><span class="val">∞</span></div>
  </div>

  <div class="card">
    <h3 style="margin-top:0">📅 לוח משחקים — שלח ניתוח</h3>
    <p style="color:#64748b;font-size:13px;margin-top:0">כפתור "שלח ניתוח" ישלח לטלגרם את ניתוח המשחקים של אותו יום</p>
    {schedule_html}
  </div>

  <div style="text-align:center;margin-top:16px">
    <a href="/odds-check" style="color:#64748b;font-size:12px;text-decoration:none;
       border:1px solid #334155;padding:6px 14px;border-radius:8px;display:inline-block;margin-bottom:10px">
      📈 בדוק כיסוי Odds API
    </a>
    <div style="color:#64748b;font-size:12px;margin-top:6px">⏰ שליחה אוטומטית כל יום ב-20:00 שעון ישראל</div>
  </div>
</body>
</html>"""


@app.route("/test", methods=["POST"])
def test():
    if not session.get("auth"):
        return redirect("/login")
    target = request.form.get("date")
    target_date = date.fromisoformat(target) if target else None
    threading.Thread(target=run, args=(target_date,), daemon=True).start()
    return redirect("/")


@app.route("/odds-check")
def odds_check():
    if not session.get("auth"):
        return redirect("/login")

    from fixtures import load_fixtures
    from odds import get_wc_odds, find_match_odds

    df = load_fixtures()
    df = df.sort_values("datetime_utc")

    all_odds = get_wc_odds()
    odds_teams = set()
    for e in all_odds:
        odds_teams.add(e.get("home_team", ""))
        odds_teams.add(e.get("away_team", ""))

    rows = ""
    covered_odds = 0
    total = len(df)

    for _, row in df.iterrows():
        home_en    = row["קבוצת בית (אנגלית)"]
        away_en    = row["קבוצת חוץ (אנגלית)"]
        date_str   = row["datetime_il"].strftime("%d/%m/%Y %H:%M")

        found_odds = find_match_odds(home_en, away_en, all_odds)
        if found_odds: covered_odds += 1
        s1 = "✅" if found_odds else "❌"
        c1 = "#10b981" if found_odds else "#f87171"

        rows += f"""<tr>
          <td style="color:#94a3b8;font-size:12px">{date_str}</td>
          <td>{home_en}</td>
          <td>{away_en}</td>
          <td style="color:{c1};font-weight:bold;text-align:center">{s1}</td>
        </tr>"""

    api_names = "".join(
        f'<span style="display:inline-block;background:#0f172a;border:1px solid #334155;'
        f'border-radius:4px;padding:2px 8px;margin:3px;font-size:12px;color:#94a3b8">{t}</span>'
        for t in sorted(odds_teams) if t
    )

    return f"""<!DOCTYPE html>
<html dir="ltr" lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Odds Coverage Check</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f1f5f9;
           max-width: 960px; margin: 30px auto; padding: 20px; }}
    h2 {{ color: #10b981; }}
    .back {{ color: #64748b; text-decoration: none; font-size: 13px; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 20px; margin: 16px 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th {{ text-align: center; color: #64748b; padding: 6px 8px; border-bottom: 1px solid #334155; }}
    th:nth-child(1), th:nth-child(2), th:nth-child(3) {{ text-align: left; }}
    td {{ padding: 6px 8px; border-bottom: 1px solid #1e293b; }}
    td:nth-child(4), td:nth-child(5), td:nth-child(6) {{ text-align: center; }}
    tr:hover td {{ background: #334155; }}
    .summary {{ display:flex; gap:24px; flex-wrap:wrap; margin-bottom:12px; font-size:14px; }}
    .sum-item {{ background:#0f172a; border-radius:8px; padding:8px 14px; }}
    .sum-val {{ font-size:20px; font-weight:bold; color:#10b981; }}
  </style>
</head>
<body>
  <a class="back" href="/">← חזרה</a>
  <h2>📊 Odds Coverage Check</h2>

  <div class="summary">
    <div class="sum-item">
      <div class="sum-val">{covered_odds}/{total}</div>
      <div style="color:#64748b;font-size:12px">The Odds API</div>
    </div>
    <div class="sum-item">
      <div class="sum-val">{len(all_odds)}</div>
      <div style="color:#64748b;font-size:12px">אירועים ב-Odds API</div>
    </div>
  </div>

  <div class="card">
    <h3 style="margin-top:0">כיסוי לפי משחק</h3>
    <table>
      <tr>
        <th>תאריך</th><th>בית</th><th>חוץ</th><th>Odds?</th>
      </tr>
      {rows}
    </table>
  </div>

  <div class="card">
    <h3 style="margin-top:0">שמות קבוצות ב-Odds API ({len(odds_teams)})</h3>
    <div>{api_names}</div>
  </div>

</body>
</html>"""


@app.route("/api-debug")
def api_debug():
    if not session.get("auth"):
        return redirect("/login")

    import os, requests as req, json

    results = {}

    # ── OddsPapi ──────────────────────────────────────────────────────────
    op_key = os.getenv("ODDSPAPI_KEY", "")
    results["oddspapi_key"] = op_key[:8] + "..." if op_key else "❌ NOT SET"
    if op_key:
        try:
            r = req.get("https://v5.oddspapi.io/en/sports",
                        params={"apiKey": op_key}, timeout=10)
            results["oddspapi_sports_status"] = r.status_code
            results["oddspapi_sports_body"]   = r.text[:2000]
        except Exception as e:
            results["oddspapi_sports_error"] = str(e)

    # ── API-Football ──────────────────────────────────────────────────────
    fb_key = os.getenv("APIFOOTBALL_KEY", "")
    results["apifootball_key"] = fb_key[:8] + "..." if fb_key else "❌ NOT SET"
    if fb_key:
        try:
            headers = {"x-apisports-key": fb_key}
            # Test: fixtures for Mexico on 11 June 2026 (first WC match)
            r = req.get("https://v3.football.api-sports.io/fixtures",
                        headers=headers,
                        params={"team": 16, "date": "2026-06-11", "league": 1, "season": 2026},
                        timeout=10)
            results["apifootball_fixture_status"] = r.status_code
            results["apifootball_fixture_body"]   = r.text[:2000]
        except Exception as e:
            results["apifootball_fixture_error"] = str(e)

        try:
            # Test: odds for fixture (use a known upcoming fixture if exists)
            r2 = req.get("https://v3.football.api-sports.io/odds",
                         headers=headers,
                         params={"league": 1, "season": 2026, "next": 5},
                         timeout=10)
            results["apifootball_odds_status"] = r2.status_code
            results["apifootball_odds_body"]   = r2.text[:2000]
        except Exception as e:
            results["apifootball_odds_error"] = str(e)

    def fmt(v):
        if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
            try:
                return json.dumps(json.loads(v), indent=2, ensure_ascii=False)
            except:
                pass
        return str(v)

    rows = "".join(
        f'<tr><td style="color:#94a3b8;width:200px;vertical-align:top;padding:8px">{k}</td>'
        f'<td><pre style="margin:0;font-size:11px;white-space:pre-wrap;color:#f1f5f9">{fmt(v)}</pre></td></tr>'
        for k, v in results.items()
    )

    return f"""<!DOCTYPE html>
<html dir="ltr"><head><meta charset="UTF-8"><title>API Debug</title>
<style>body{{font-family:monospace;background:#0f172a;color:#f1f5f9;padding:20px}}
h2{{color:#10b981}}.back{{color:#64748b;text-decoration:none;font-size:13px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
tr{{border-bottom:1px solid #334155}}
td{{padding:6px 8px;vertical-align:top}}
</style></head><body>
<a class="back" href="/">← חזרה</a>
<h2>🔧 API Raw Debug</h2>
<table>{rows}</table>
</body></html>"""


@app.route("/health")
def health():
    return {"status": "ok"}


# ── Scheduler ────────────────────────────────────────────────────────────

def scheduled_job():
    print("[Scheduler] Running daily job...")
    run()


def start_scheduler():
    scheduler = BackgroundScheduler(timezone=ISRAEL_TZ)
    scheduler.add_job(scheduled_job, CronTrigger(hour=20, minute=0, timezone=ISRAEL_TZ))
    scheduler.start()
    print("[Scheduler] Started — daily job at 20:00 Israel time")


if __name__ == "__main__":
    start_scheduler()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
