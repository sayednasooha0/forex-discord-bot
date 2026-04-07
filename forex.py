import requests
import schedule
import time
from datetime import datetime, timezone
from flask import Flask
from threading import Thread
import sys

# 1. STEALTH WEB SERVER
app = Flask(__name__)
@app.route('/')
def home(): return "Forex Bot: Active & Stealthy"

def run():
    app.run(host='0.0.0.0', port=8080)

# 2. CONFIGURATION
DAILY_WEBHOOK = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"
ALERT_WEBHOOK = "https://discord.com/api/webhooks/1491010195801899129/0RTe-_si-spHQtope5NMRUDqq5r7-7ViD-I4HVrZRNxzVsF0B5uTsLbNy6WiPftfv6yD"

TARGET_CURRENCIES = ["EUR", "USD", "NZD", "CAD", "AUD", "GBP"]
FLAGS = {"USD": "🇺🇸", "EUR": "🇪🇺", "NZD": "🇳🇿", "CAD": "🇨🇦", "AUD": "🇦🇺", "GBP": "🇬🇧"}

# 3. CORE LOGIC
def get_news():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"DEBUG: Data Fetch Error: {e}", flush=True)
        return []

# NEW: BOOT NOTIFICATION FUNCTION
def send_boot_notification():
    payload = {
        "embeds": [{
            "title": "🚀 System Online",
            "description": "Forex News Bot has successfully deployed to Render.\nMonitoring: **EUR, USD, NZD, CAD, AUD, GBP**",
            "color": 65280, # Green
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
    }
    try:
        requests.post(DAILY_WEBHOOK, json=payload, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        print("DEBUG: Boot notification sent to Discord.", flush=True)
    except Exception as e:
        print(f"DEBUG: Boot Notification Failed: {e}", flush=True)

def send_daily_calendar():
    all_data = get_news()
    now_utc = datetime.now(timezone.utc).date()
    
    news = []
    for item in all_data:
        try:
            item_date = datetime.fromisoformat(item['date'].replace('Z', '+00:00')).date()
            if item_date == now_utc and item['country'] in TARGET_CURRENCIES and item['impact'] in ["High", "Medium", "Holiday"]:
                news.append(item)
        except: continue

    print(f"DEBUG: Found {len(news)} events for today.", flush=True)
    if not news: return

    description = ""
    for n in news:
        flag = FLAGS.get(n['country'], "🏳️")
        icon = "🔴" if n['impact'] == "High" else "🟠"
        ts = int(datetime.fromisoformat(n['date'].replace('Z', '+00:00')).timestamp())
        description += f"**<t:{ts}:t>** | {flag} **{n['country']}** | {icon}\n└ {n['title']}\n\n"

    payload = {
        "embeds": [{
            "title": f"📊 {datetime.now().strftime('%A').upper()}'S FOREX CALENDAR",
            "description": description.strip(),
            "color": 3447003,
            "footer": {"text": "Institutional Grade Feed"}
        }]
    }
    try:
        requests.post(DAILY_WEBHOOK, json=payload, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    except: pass

def check_alerts():
    all_data = get_news()
    now_ts = time.time()
    for n in all_data:
        try:
            ts = int(datetime.fromisoformat(n['date'].replace('Z', '+00:00')).timestamp())
            time_diff = ts - now_ts
            if 0 < time_diff <= 3600 and n['country'] in TARGET_CURRENCIES and n['impact'] in ["High", "Medium"]:
                flag = FLAGS.get(n['country'], "🏳️")
                payload = {
                    "embeds": [{
                        "title": f"{flag} {n['country']} - {n['title']}",
                        "color": 15548997 if n['impact'] == "High" else 15105570,
                        "fields": [
                            {"name": "Impact", "value": f"**{n['impact']}**", "inline": True},
                            {"name": "Time", "value": f"<t:{ts}:F>\n**<t:{ts}:R>**", "inline": False}
                        ]
                    }]
                }
                requests.post(ALERT_WEBHOOK, json=payload, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        except: continue

# 4. EXECUTION
print("Forex News Bot is booting up...", flush=True)
Thread(target=run).start()

# Let the network settle to avoid Cloudflare ban
time.sleep(15) 

# --- STARTUP ACTIONS ---
send_boot_notification() # This tells you it worked!
send_daily_calendar()    # This sends today's remaining news

# 5. SCHEDULING
schedule.every().day.at("00:00").do(send_daily_calendar)
schedule.every(5).minutes.do(check_alerts)

while True:
    schedule.run_pending()
    time.sleep(60)
