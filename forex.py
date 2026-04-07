import requests
import sys
import time
from flask import Flask
from threading import Thread

# Force Python to show logs immediately
def log(msg):
    print(f"DEBUG: {msg}", flush=True)
    sys.stdout.flush()

app = Flask(__name__)
@app.route('/')
def home(): return "Debug Live"

log("--- SCRIPT STARTING ---")

def send_now():
    url = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"
    log(f"Targeting Webhook: {url[:20]}...")
    
    payload = {"content": "🚀 **MANUAL OVERRIDE: TESTING CONNECTION**"}
    
    try:
        log("Sending POST request...")
        r = requests.post(url, json=payload, timeout=15)
        log(f"STATUS CODE: {r.status_code}")
        log(f"RESPONSE: {r.text}")
    except Exception as e:
        log(f"ERROR: {str(e)}")

# Start Flask in background
log("Starting Web Server...")
Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)).start()

# Wait 5 seconds for network to stabilize
time.sleep(5)

# Trigger the message
send_now()

log("--- BOOT SEQUENCE COMPLETE ---")

while True:
    time.sleep(60)
