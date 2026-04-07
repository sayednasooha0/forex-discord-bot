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
# !!! PASTE YOUR BRAND NEW WEBHOOKS HERE !!!
DAILY_WEBHOOK = "https://discord.com/api/webhooks/1491066404466851892/PMowcOx14n5LG8Hs_pm5m2ZY5rsVb4lK9ZqGEQYoRN7wU-d5SOZlGe-9neeGyyhNayfZ"
ALERT_WEBHOOK = "https://discord.com/api/webhooks/1491066482077995008/OlaelimR1NnfQ8WM5i21cgE6rvz4J3Hgatu-L44Eu471uYQ3IdlDOc-vJvkBEIc4c2vD"

TARGET_CURRENCIES = ["EUR", "USD", "NZD", "CAD", "AUD", "GBP"]
FLAGS = {"USD": "🇺🇸", "EUR": "🇪🇺", "NZD": "🇳🇿", "CAD": "🇨🇦", "AUD": "🇦🇺", "GBP": "🇬🇧"}

# FIX: Memory to prevent duplicate alerts
sent_alerts = set()

# 3. HELPER FUNCTIONS
def send_webhook(url, payload):
    """Fix 1: Real Debugging + Fix 3: Anti-Spam Delay"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"DISCORD STATUS: {r.status_code}", flush=True)
        if r.status_code >= 400:
            print(f"DISCORD ERROR: {r.text[:200]}", flush=True)
        time.sleep(2) # Fix 3: Small delay between posts
        return r
    except Exception as e:
        print(f"WEBHOOK ERROR: {e}", flush=True)

def get_news():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        return r.json()
    except: return []

# 4. CORE FEATURES
def send_boot_notification():
    payload = {
        "embeds": [{
            "title": "🚀 System Online",
            "description": "Forex News Bot is monitoring: **EUR, USD, NZD, CAD, AUD, GBP**",
            "color": 65280,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
    }
    send_webhook(DAILY_WEBHOOK, payload)

def send_daily_calendar():
    all_data = get_news()
    now_utc = datetime.now(timezone.utc).date()
    news = [n for n in all_data if n.get("country") in TARGET_CURRENCIES and 
            datetime.fromisoformat(n.get("date").replace('Z', '+00:00')).date() == now_utc and 
            n.get("impact") in ["High", "Medium", "Holiday"]]
    
    if not news: return

    description = ""
    for n in news:
        flag = FLAGS.get(n['country'], "🏳️")
        ts = int(datetime.fromisoformat(n['date'].replace('Z', '+00:00')).timestamp())
        description += f"**<t:{ts}:t>** | {flag} **{n['country']}** | {'🔴' if n['impact']=='High' else '🟠'}\n└ {n['title']}\n\n"

    send_webhook(DAILY_WEBHOOK, {"embeds": [{"title": "📊 TODAY'S CALENDAR", "description": description.strip(), "color": 3447003}]})

def check_alerts():
    global sent_alerts
    all_data = get_news()
    now_ts = time.time()
    
    for n in all_data:
        try:
            ts = int(datetime.fromisoformat(n['date'].replace('Z', '+00:00')).timestamp())
            time_diff = ts - now_ts
            # Unique key to prevent double-pings
            alert_key = f"{n['country']}_{n['title']}_{ts}"

            if 0 < time_diff <= 3600 and n['country'] in TARGET_CURRENCIES and \
               n['impact'] in ["High", "Medium"] and alert_key not in sent_alerts:
                
                flag = FLAGS.get(n['country'], "🏳️")
                payload = {"embeds": [{
                    "title": f"{flag} {n['country']} - {n['title']}",
                    "color": 15548997 if n['impact'] == "High" else 15105570,
                    "fields": [
                        {"name": "Impact", "value": f"**{n['impact']}**", "inline": True},
                        {"name": "Time", "value": f"<t:{ts}:F>\n**<t:{ts}:R>**", "inline": False}
                    ]
                }]}
                
                send_webhook(ALERT_WEBHOOK, payload)
                sent_alerts.add(alert_key)
                print(f"DEBUG: Alert Sent for {n['title']}", flush=True)
        except: continue

# 5. EXECUTION
print("Forex News Bot is booting up...", flush=True)

# Fix: Daemonized Thread
server = Thread(target=run)
server.daemon = True
server.start()

time.sleep(15) 
send_boot_notification()
send_daily_calendar()

schedule.every().day.at("00:00").do(send_daily_calendar)
schedule.every(5).minutes.do(check_alerts)

while True:
    schedule.run_pending()
    time.sleep(60)
