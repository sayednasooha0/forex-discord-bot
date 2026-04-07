import requests
import sys
import time
from flask import Flask
from threading import Thread

def log(msg):
    print(f"DEBUG: {msg}", flush=True)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Active"

def send_final_test():
    # PASTE YOUR BRAND NEW WEBHOOK URL HERE
    url = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"
    
    # Adding a Header makes Discord think we are a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    
    payload = {"content": "📢 **FINAL CONNECTION TEST: SUCCESS**"}
    
    try:
        log("Sending Request...")
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        log(f"Status: {r.status_code}")
        log(f"Discord Response: {r.text}")
    except Exception as e:
        log(f"Connection Error: {e}")

# Startup
log("--- STARTING FINAL ATTEMPT ---")
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

time.sleep(5)
send_final_test()
log("--- BOOT FINISHED ---")

while True:
    time.sleep(60)
