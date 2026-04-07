import requests
import schedule
import time
from datetime import datetime, timezone
from flask import Flask
from threading import Thread

# 1. WEB SERVER TO PREVENT SLEEPING
app = Flask(__name__)

@app.route('/')
def home():
    return "Forex Bot is Operational"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. CONFIGURATION
DAILY_WEBHOOK = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"
ALERT_WEBHOOK = "https://discord.com/api/webhooks/1491010195801899129/0RTe-_si-spHQtope5NMRUDqq5r7-7ViD-I4HVrZRNxzVsF0B5uTsLbNy6WiPftfv6yD"

TARGET_CURRENCIES = ["EUR", "USD", "NZD", "CAD", "AUD","GBP"]
CACHE_DURATION = 240
sent_alerts = set()
cached_news_data = []
last_fetch_time = 0

FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "NZD": "🇳🇿"
}

# 3. CORE LOGIC
def get_news():
    global cached_news_data, last_fetch_time
    current_time = time.time()
    
    if current_time - last_fetch_time < CACHE_DURATION and cached_news_data:
        return cached_news_data

    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return cached_news_data 

    news_list = []
    for item in data:
        currency = item.get("country", "")
        if currency not in TARGET_CURRENCIES:
            continue

        impact = item.get("impact", "")
        if impact not in ["High", "Medium", "Holiday"]:
            continue

        try:
            dt = datetime.fromisoformat(item.get("date", ""))
            timestamp = int(dt.timestamp())
            news_list.append((timestamp, currency, item.get("title", ""), impact))
        except Exception:
            continue

    cached_news_data = news_list
    last_fetch_time = current_time
    return news_list

def send_daily_calendar():
    all_news = get_news()
    now = datetime.now(timezone.utc)
    day_name = now.strftime("%A").upper()
    
    news = [n for n in all_news if datetime.fromtimestamp(n[0], timezone.utc).date() == now.date()]
    if not news: return

    description = ""
    for n in news:
        ts, curr, title, imp = n
        flag = FLAGS.get(curr, "🏳️")
        icon = "🔴" if imp == "High" else "🟠" if imp == "Medium" else "🏖️"
        description += f"**<t:{ts}:t>** | {flag} **{curr}** | {icon} {imp}\n└ {title}\n\n"

    embed = {
        "title": f"📊 {day_name}'S FOREX CALENDAR",
        "color": 3447003,
        "description": description.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    requests.post(DAILY_WEBHOOK, json={"embeds": [embed]})

def send_weekly_calendar():
    all_news = get_news()
    weekly_news = [n for n in all_news if n[3] in ["High", "Holiday"]]
    if not weekly_news: return

    description = "**MACRO-ECONOMIC OUTLOOK:** Critical zones for the upcoming week.\n"
    current_day = ""

    for n in weekly_news:
        ts, curr, title, imp = n
        day_str = datetime.fromtimestamp(ts, timezone.utc).strftime("%A, %b %d")
        
        if day_str != current_day:
            description += f"\n📅 **__{day_str}__**\n"
            current_day = day_str
            
        flag = FLAGS.get(curr, "🏳️")
        note = ""
        if imp == "Holiday":
            note = "\n   *⚠️ Market Condition: Institutional Bank Closure.*"
        elif "Non-Farm" in title or "NFP" in title:
            note = "\n   *⚠️ Market Condition: High Volatility / Wide Spreads Expected.*"

        description += f"<t:{ts}:t> | {flag} **{curr}** | {'🔴' if imp=='High' else '🛑'} {imp}\n└ {title}{note}\n"

    embed = {
        "title": "🗓️ NEXT WEEK'S CRITICAL WATCHLIST",
        "color": 10181046,
        "description": description.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    requests.post(DAILY_WEBHOOK, json={"embeds": [embed]})

def check_alerts():
    news = get_news()
    now_ts = time.time()
    for n in news:
        ts, curr, title, imp = n
        time_diff = ts - now_ts
        key = f"{curr}_{title}_{ts}"
        if 0 < time_diff <= 3600 and key not in sent_alerts:
            color = 15548997 if imp == "High" else 15105570 if imp == "Medium" else 3447003
            embed = {
                "title": f"{FLAGS.get(curr, '🏳️')} {curr} - {title}",
                "color": color,
                "fields": [
                    {"name": "Impact", "value": f"**{imp}**", "inline": True},
                    {"name": "Time", "value": f"<t:{ts}:F>\n**<t:{ts}:R>**", "inline": False}
                ]
            }
            requests.post(ALERT_WEBHOOK, json={"embeds": [embed]})
            sent_alerts.add(key)

# 4. EXECUTION
keep_alive()
schedule.every().day.at("00:00").do(send_daily_calendar)
schedule.every().sunday.at("08:00").do(send_weekly_calendar)
schedule.every(5).minutes.do(check_alerts)

send_daily_calendar()

while True:
    schedule.run_pending()
    time.sleep(60)
