#!/usr/bin/env python3
"""
The Gambler — Web Server with daily scheduler.
"""
import os
import threading
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


@app.route("/")
def index():
    if not session.get("auth"):
        return redirect("/login")
    from usage_tracker import get_stats
    s = get_stats()
    odds_bar = min(100, int(s['odds_calls'] / 500 * 100))
    return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>🎲 The Gambler</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f1f5f9;
           max-width: 500px; margin: 60px auto; padding: 20px; }}
    h1 {{ color: #10b981; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 24px; margin: 20px 0; }}
    .btn {{ background: #3b82f6; color: white; border: none; padding: 12px 24px;
           border-radius: 8px; cursor: pointer; font-size: 15px; width: 100%; }}
    .btn:hover {{ background: #2563eb; }}
    .msg {{ background: #065f46; color: #6ee7b7; padding: 10px 16px; border-radius: 8px; margin: 10px 0; }}
    .logout {{ float: left; color: #64748b; text-decoration: none; font-size: 13px; }}
    .stat {{ display: flex; justify-content: space-between; padding: 8px 0;
             border-bottom: 1px solid #334155; font-size: 14px; }}
    .stat:last-child {{ border-bottom: none; }}
    .val {{ color: #10b981; font-weight: bold; }}
    .bar-bg {{ background: #334155; border-radius: 4px; height: 8px; margin-top: 6px; }}
    .bar-fill {{ background: #10b981; border-radius: 4px; height: 8px; }}
  </style>
</head>
<body>
  <h1>🎲 The Gambler</h1>
  <a class="logout" href="/logout">יציאה</a>

  <div class="card">
    <h3>📤 שלח הודעת בדיקה</h3>
    <p style="color:#94a3b8;font-size:14px">ריק = היום | או בחר תאריך ספציפי</p>
    <form method="POST" action="/test">
      <input type="date" name="date" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:white;box-sizing:border-box;font-size:15px;margin-bottom:10px">
      <button type="submit" class="btn">שלח עכשיו 🚀</button>
    </form>
  </div>

  <div class="card">
    <h3>📊 שימוש ב-APIs</h3>
    <div class="stat"><span>🤖 Anthropic — קריאות</span><span class="val">{s['anthropic_calls']}</span></div>
    <div class="stat"><span>🤖 Anthropic — עלות</span><span class="val">${s['anthropic_cost']}</span></div>
    <div class="stat"><span>🤖 Anthropic — טוקנים</span><span class="val">{s['anthropic_input']:,} in / {s['anthropic_output']:,} out</span></div>
    <div class="stat">
      <span>📈 Odds API — {s['odds_calls']}/500 החודש</span>
      <span class="val">{s['odds_remaining']} נותרו</span>
    </div>
    <div class="bar-bg"><div class="bar-fill" style="width:{odds_bar}%"></div></div>
    <div class="stat"><span>📨 Telegram</span><span class="val">∞ ללא הגבלה</span></div>
  </div>

  <div class="card" style="color:#64748b; font-size:13px;">
    ⏰ ההודעה היומית נשלחת אוטומטית כל יום ב-<strong style="color:#94a3b8">20:00 שעון ישראל</strong>
    <br><br>
    📨 נשלח לערוץ <strong style="color:#94a3b8">TheGambler</strong> בטלגרם
  </div>
</body>
</html>"""


@app.route("/test", methods=["POST"])
def test():
    if not session.get("auth"):
        return redirect("/login")
    from datetime import date
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
