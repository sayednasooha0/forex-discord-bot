import requests
import time
from flask import Flask
from threading import Thread

# 1. SIMPLEST WEB SERVER
app = Flask(__name__)
@app.route('/')
def home(): return "Test Server Live"

def run(): app.run(host='0.0.0.0', port=8080)

# 2. THE TEST FUNCTION
def send_test():
    # YOUR WEBHOOK
    url = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"
    
    payload = {
        "content": "🚀 **RENDER IS TALKING TO DISCORD!**",
        "embeds": [{
            "title": "✅ Connection Success",
            "description": "If you see this, your bot is officially online and the Webhook is working perfectly.",
            "color": 65280
        }]
    }
    
    try:
        print("Attempting to send Discord message...")
        r = requests.post(url, json=payload)
        print(f"Response Code: {r.status_code}")
        if r.status_code == 204 or r.status_code == 200:
            print("SUCCESS: Check your Discord channel!")
        else:
            print(f"FAILED: Discord rejected the message. Code: {r.status_code}")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

# 3. STARTUP
Thread(target=run).start()
time.sleep(2) # Wait for server to breath
send_test()

while True:
    time.sleep(60)
