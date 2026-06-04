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
    odds_bar = min(100, int(s['odds_calls'] / 500 * 100))
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
            <div class="flow-desc">הבוט קורא את <strong>wc2026_fixtures.xlsx</strong> המקומי (72 משחקים) ומסנן את משחקי היום לפי שעון ישראל.</div>
            <span class="flow-tag">📁 קובץ מקומי</span>
            <span class="flow-tag">ללא API</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">📈</div>
          <div class="flow-body">
            <div class="flow-title">שלב 2 — יחסי הימורים</div>
            <div class="flow-desc">קריאה אחת ל-<strong>The Odds API</strong> לשליפת כל יחסי ה-1X2. התאמה לכל משחק לפי שם הקבוצה.</div>
            <span class="flow-tag">🌐 api.the-odds-api.com</span>
            <span class="flow-tag">500/חודש (חינם)</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">🤖</div>
          <div class="flow-body">
            <div class="flow-title">שלב 3 — ניתוח עם GPT-4.5</div>
            <div class="flow-desc">לכל משחק — קריאה נפרדת ל-<strong>OpenAI GPT-4.5</strong> עם שמות הקבוצות, שעה ויחסי הימורים. מחזיר ניתוח בעברית, המלצה, ניחוש תוצאה וביטחון בכוכבים.</div>
            <span class="flow-tag">🌐 api.openai.com</span>
            <span class="flow-tag">gpt-4.5-preview</span>
            <span class="flow-tag">~600 טוקנים/קריאה</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">📨</div>
          <div class="flow-body">
            <div class="flow-title">שלב 4 — שליחה לטלגרם</div>
            <div class="flow-desc">כל הניתוחים מחוברים להודעה אחת ונשלחים לערוץ. הודעות ארוכות מפוצלות ל-4,000 תווים אוטומטית.</div>
            <span class="flow-tag">🌐 api.telegram.org</span>
            <span class="flow-tag">ללא מגבלה</span>
          </div>
        </div>

        <div class="flow-step">
          <div class="flow-icon">⏰</div>
          <div class="flow-body">
            <div class="flow-title">תזמון אוטומטי</div>
            <div class="flow-desc">כל יום ב-<strong>20:00 שעון ישראל</strong> (17:00 UTC) — APScheduler המובנה בשרת מפעיל את כל התהליך.</div>
            <span class="flow-tag">APScheduler</span>
            <span class="flow-tag">Asia/Jerusalem</span>
          </div>
        </div>

      </div>
    </div>
  </div>

  <h1>🎲 The Gambler</h1>
  <a class="logout" href="/logout">יציאה</a>

  <div class="card">
    <h3 style="margin-top:0">📊 שימוש ב-APIs</h3>
    <div class="stat"><span>🤖 GPT-4.5 — קריאות</span><span class="val">{s['ai_calls']}</span></div>
    <div class="stat"><span>🤖 GPT-4.5 — עלות</span><span class="val">${s['ai_cost']}</span></div>
    <div class="stat"><span>🤖 GPT-4.5 — טוקנים</span><span class="val">{s['ai_input']:,} in / {s['ai_output']:,} out</span></div>
    <div class="stat"><span>📈 Odds API — {s['odds_calls']}/500 החודש</span><span class="val">{s['odds_remaining']} נותרו</span></div>
    <div class="bar-bg"><div class="bar-fill" style="width:{odds_bar}%"></div></div>
    <div class="stat"><span>📨 Telegram</span><span class="val">∞</span></div>
  </div>

  <div class="card">
    <h3 style="margin-top:0">📅 לוח משחקים — שלח ניתוח</h3>
    <p style="color:#64748b;font-size:13px;margin-top:0">כפתור "שלח ניתוח" ישלח לטלגרם את ניתוח המשחקים של אותו יום</p>
    {schedule_html}
  </div>

  <div style="color:#64748b;font-size:12px;text-align:center;margin-top:16px">
    ⏰ שליחה אוטומטית כל יום ב-20:00 שעון ישראל
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
