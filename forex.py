import requests
import schedule
import time
from datetime import datetime, timezone
from flask import Flask
from threading import Thread

# ==========================================
# 1. THE "FAKE WEBSITE" (KEEPS THE BOT AWAKE)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Forex Bot is awake and running!"

def run():
    # Render.com will look for this web server to keep the app alive
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 2. YOUR FOREX BOT CONFIGURATION
# ==========================================
DAILY_WEBHOOK = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"
ALERT_WEBHOOK = "https://discord.com/api/webhooks/1491010195801899129/0RTe-_si-spHQtope5NMRUDqq5r7-7ViD-I4HVrZRNxzVsF0B5uTsLbNy6WiPftfv6yD"

TARGET_CURRENCIES = ["EUR", "USD", "NZD"]
CACHE_DURATION = 240 # 4 minutes
sent_alerts = set()
cached_news_data = []
last_fetch_time = 0

FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
    "CAD": "🇨🇦", "AUD": "🇦🇺", "NZD": "🇳🇿", "CHF": "🇨🇭",
    "CNY": "🇨🇳", "INR": "🇮🇳"
}

# ==========================================
# 3. THE BOT ENGINE
# ==========================================
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
    except Exception as e:
        print(f"Error fetching data: {e}")
        return cached_news_data 

    news_list = []
    for item in data:
        currency = item.get("country", "")
        if currency not in TARGET_CURRENCIES:
            continue

        impact = item.get("impact", "")
        if impact not in ["High", "Medium", "Holiday"]:
            continue

        title = item.get("title", "")
        date_str = item.get("date", "")

        try:
            dt = datetime.fromisoformat(date_str)
            timestamp = int(dt.timestamp())
            news_list.append((timestamp, currency, title, impact))
        except Exception:
            continue

    cached_news_data = news_list
    last_fetch_time = current_time
    return news_list

def send_daily_calendar():
    all_news = get_news()
    today_dt = datetime.now()
    today_date = today_dt.date()
    day_name = today_dt.strftime("%A").upper() 
    
    news = [n for n in all_news if datetime.fromtimestamp(n[0]).date() == today_date]
    if not news:
        return

    description = ""
    for n in news:
        timestamp, currency, title, impact = n
        discord_time = f"<t:{timestamp}:t>"
        flag = FLAGS.get(currency, "🏳️")
        
        if impact == "High": icon = "🔴"
        elif impact == "Medium": icon = "🟠"
        else: icon = "🏖️" 

        description += f"**{discord_time}** | {flag} **{currency}** | {icon} {impact}\n└ {title}\n\n"

    embed = {
        "title": f"📊 {day_name}'S FOREX CALENDAR",
        "color": 3447003, 
        "description": description.strip(),
        "footer": {"text": "Forex News Bot • High & Medium Impact + Holidays"},
        "timestamp": datetime.now(timezone.utc).isoformat() 
    }
    try:
        requests.post(DAILY_WEBHOOK, json={"embeds": [embed]})
    except Exception as e:
        print(f"Error: {e}")

def send_weekly_calendar():
    all_news = get_news()
    weekly_news = [n for n in all_news if n[3] in ["High", "Holiday"]]
    if not weekly_news:
        return

    description = "**MACRO-ECONOMIC OUTLOOK:** Please review the critical volatility zones and liquidity constraints for the upcoming trading week.\n"
    current_day_str = ""

    for n in weekly_news:
        timestamp, currency, title, impact = n
        dt = datetime.fromtimestamp(timestamp)
        day_str = dt.strftime("%A, %b %d")
        
        if day_str != current_day_str:
            description += f"\n📅 **__{day_str}__**\n"
            current_day_str = day_str
            
        discord_time = f"<t:{timestamp}:t>"
        flag = FLAGS.get(currency, "🏳️")
        note = "" 
        
        if impact == "Holiday":
            icon = "🛑"
            note = "\n   *⚠️ Market Condition: Institutional Bank Closure / Extreme Low Liquidity Expected.*"
        elif impact == "High":
            icon = "🔴"
            if "Non-Farm" in title or "NFP" in title or "Employment Change" in title:
                note = "\n   *⚠️ Market Condition: High Volatility Event / Wide Spreads Expected. Strict Risk Management Advised.*"

        description += f"{discord_time} | {flag} **{currency}** | {icon} {impact}\n└ {title}{note}\n"

    embed = {
        "title": "🗓️ NEXT WEEK'S CRITICAL WATCHLIST",
        "color": 10181046, 
        "description": description.strip(),
        "footer": {"text": "Institutional Weekly Briefing • High Impact & Holidays Only"},
        "timestamp": datetime.now(timezone.utc).isoformat() 
    }
    try:
        requests.post(DAILY_WEBHOOK, json={"embeds": [embed]})
    except Exception as e:
        print(f"Error: {e}")

def check_alerts():
    news = get_news()
    now_ts = datetime.now().timestamp()

    for n in news:
        timestamp, currency, title, impact = n
        time_until_news = timestamp - now_ts
        key = f"{currency}_{title}_{timestamp}"

        if 0 < time_until_news <= 3600 and key not in sent_alerts:
            flag = FLAGS.get(currency, "🏳️")
            if impact == "High":
                color = 15548997 ; icon = "🔴 HIGH IMPACT"
            elif impact == "Medium":
                color = 15105570 ; icon = "🟠 MEDIUM IMPACT"
            else:
                color = 3447003 ; icon = "🛑 BANK HOLIDAY"
            
            embed = {
                "title": f"{flag} {currency} - {title}",
                "color": color,
                "fields": [
                    {"name": "Impact", "value": f"**{icon}**", "inline": True},
                    {"name": "Time", "value": f"<t:{timestamp}:F>\n**<t:{timestamp}:R>**", "inline": False}
                ],
                "footer": {"text": "⚠️ Expect Volatility" if impact in ["High", "Medium"] else "Expect low liquidity"}
            }
            try:
                requests.post(ALERT_WEBHOOK, json={"embeds": [embed]})
                sent_alerts.add(key)
                print(f"Alert sent: {title}")
            except Exception as e:
                print(f"Error: {e}")

# ==========================================
# 4. THE STARTUP SEQUENCE
# ==========================================
print("Starting Cloud Forex Discord News Bot...")

# Start the fake web server to trick Render into keeping us online
keep_alive()

schedule.every().day.at("00:00").do(send_daily_calendar)
schedule.every().sunday.at("08:00").do(send_weekly_calendar)
schedule.every(5).minutes.do(check_alerts)

send_daily_calendar()
check_alerts() 

while True:
    schedule.run_pending()
    time.sleep(60)