import requests
import schedule
import time
from datetime import datetime, timezone
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Forex Bot is Operational"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

DAILY_WEBHOOK = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"

TARGET_CURRENCIES = ["EUR", "USD", "NZD", "CAD", "AUD", "GBP"]
FLAGS = {"USD": "🇺🇸", "EUR": "🇪🇺", "NZD": "🇳🇿", "CAD": "🇨🇦", "AUD": "🇦🇺", "GBP": "🇬🇧"}

def get_news():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        news_list = []
        for item in data:
            if item.get("country") in TARGET_CURRENCIES and item.get("impact") in ["High", "Medium"]:
                dt = datetime.fromisoformat(item.get("date", "").replace('Z', '+00:00'))
                news_list.append((int(dt.timestamp()), item.get("country"), item.get("title"), item.get("impact")))
        return news_list
    except:
        return []

def force_test_post():
    all_news = get_news()
    if not all_news:
        print("No news found to post.")
        return

    # This pulls EVERY news item from the whole week to force a message
    description = "🚀 **FORCE TEST: ALL WEEKLY NEWS**\n\n"
    for n in all_news[:15]: # Show first 15 items
        ts, curr, title, imp = n
        flag = FLAGS.get(curr, "🏳️")
        icon = "🔴" if imp == "High" else "🟠"
        description += f"<t:{ts}:d> | {flag} **{curr}** | {icon}\n└ {title}\n\n"

    embed = {
        "title": "✅ CONNECTION VERIFIED: LIVE FEED ACTIVE",
        "color": 65280, # Green
        "description": description.strip(),
        "footer": {"text": "Render Cloud Deployment Successful"}
    }
    requests.post(DAILY_WEBHOOK, json={"embeds": [embed]})
    print("Force Test message sent to Discord!")

# EXECUTION
keep_alive()
force_test_post() # Runs immediately on startup!

while True:
    time.sleep(60)
