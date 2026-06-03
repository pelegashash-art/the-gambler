#!/usr/bin/env python3
"""
The Gambler — Web Management Server
Runs as always-on web server with internal daily scheduler.
"""
import os
import json
import threading
from datetime import datetime, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

from flask import Flask, request, redirect, url_for, session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from main import run

app = Flask(__name__)
app.secret_key = os.getenv("ADMIN_SECRET", "changeme123")

RECIPIENTS_FILE = Path("data/recipients.json")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "gambler2026")
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")


# ── Recipients storage ──────────────────────────────────────────────────

def load_recipients() -> list[str]:
    if RECIPIENTS_FILE.exists():
        return json.loads(RECIPIENTS_FILE.read_text())
    # Default: the main recipient from env
    default = os.getenv("WHATSAPP_RECIPIENT", "")
    return [default] if default else []

def save_recipients(numbers: list[str]):
    RECIPIENTS_FILE.parent.mkdir(exist_ok=True)
    RECIPIENTS_FILE.write_text(json.dumps(numbers, ensure_ascii=False, indent=2))


# ── HTML ────────────────────────────────────────────────────────────────

def render_page(recipients, message=""):
    items = "".join(
        f"""<li class="recipient">
              <span>{r}</span>
              <form method="POST" action="/remove" style="display:inline">
                <input type="hidden" name="number" value="{r}">
                <button type="submit" class="btn-remove">הסר ✕</button>
              </form>
            </li>"""
        for r in recipients
    )
    msg_html = f'<div class="msg">{message}</div>' if message else ""

    return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>🎲 The Gambler — ניהול נמענים</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f1f5f9;
            max-width: 600px; margin: 40px auto; padding: 20px; }}
    h1 {{ color: #10b981; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 20px; margin: 20px 0; }}
    input[type=text] {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #334155;
                        background: #0f172a; color: white; font-size: 16px; box-sizing: border-box; }}
    .btn {{ background: #10b981; color: white; border: none; padding: 10px 20px;
             border-radius: 8px; cursor: pointer; font-size: 15px; margin-top: 10px; }}
    .btn:hover {{ background: #059669; }}
    .btn-remove {{ background: #ef4444; color: white; border: none; padding: 4px 10px;
                   border-radius: 6px; cursor: pointer; }}
    .btn-test {{ background: #3b82f6; }}
    .btn-test:hover {{ background: #2563eb; }}
    ul {{ list-style: none; padding: 0; }}
    .recipient {{ display: flex; justify-content: space-between; align-items: center;
                  padding: 10px; border-bottom: 1px solid #334155; }}
    .msg {{ background: #065f46; color: #6ee7b7; padding: 10px 16px; border-radius: 8px; margin: 10px 0; }}
    .hint {{ color: #64748b; font-size: 13px; margin-top: 6px; }}
    .logout {{ float: left; color: #64748b; text-decoration: none; font-size: 13px; }}
  </style>
</head>
<body>
  <h1>🎲 The Gambler</h1>
  <a class="logout" href="/logout">יציאה</a>

  {msg_html}

  <div class="card">
    <h3>📱 נמענים ({len(recipients)})</h3>
    <ul>{items if items else '<li style="color:#64748b">אין נמענים עדיין</li>'}</ul>
  </div>

  <div class="card">
    <h3>➕ הוסף מספר</h3>
    <form method="POST" action="/add">
      <input type="text" name="number" placeholder="+972501234567" required>
      <p class="hint">⚠️ המספר חייב להיות מאומת ב-Meta Business Dashboard קודם</p>
      <button type="submit" class="btn">הוסף</button>
    </form>
  </div>

  <div class="card">
    <h3>🧪 שלח הודעת בדיקה</h3>
    <form method="POST" action="/test">
      <button type="submit" class="btn btn-test">שלח עכשיו (14/06/2026)</button>
    </form>
  </div>

  <div class="card" style="color:#64748b; font-size:13px;">
    ⏰ ההודעה היומית נשלחת אוטומטית כל יום ב-<strong style="color:#94a3b8">20:00 שעון ישראל</strong>
  </div>
</body>
</html>"""


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
    return render_page(load_recipients())


@app.route("/add", methods=["POST"])
def add():
    if not session.get("auth"):
        return redirect("/login")
    number = request.form.get("number", "").strip()
    recipients = load_recipients()
    if number and number not in recipients:
        recipients.append(number)
        save_recipients(recipients)
        return render_page(recipients, f"✓ {number} נוסף בהצלחה")
    return render_page(recipients, "המספר כבר קיים או לא תקין")


@app.route("/remove", methods=["POST"])
def remove():
    if not session.get("auth"):
        return redirect("/login")
    number = request.form.get("number", "")
    recipients = load_recipients()
    recipients = [r for r in recipients if r != number]
    save_recipients(recipients)
    return render_page(recipients, f"✓ {number} הוסר")


@app.route("/test", methods=["POST"])
def test():
    if not session.get("auth"):
        return redirect("/login")
    from datetime import date
    threading.Thread(target=run, args=(date(2026, 6, 14),), daemon=True).start()
    return render_page(load_recipients(), "✓ הודעת בדיקה נשלחת ברקע...")


@app.route("/health")
def health():
    return {"status": "ok"}


# ── Scheduler ────────────────────────────────────────────────────────────

def scheduled_job():
    print("[Scheduler] Running daily job...")
    run()

scheduler = BackgroundScheduler(timezone=ISRAEL_TZ)
scheduler.add_job(scheduled_job, CronTrigger(hour=20, minute=0, timezone=ISRAEL_TZ))
scheduler.start()
print("[Scheduler] Started — daily job at 20:00 Israel time")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
