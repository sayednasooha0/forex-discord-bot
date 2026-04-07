import requests
import sys

# 1. YOUR WEBHOOK URL
url = "https://discord.com/api/webhooks/1491002012119076985/-SpK7iShVnetlkjZXCfrg3gpRDnNvZqlJhy8lf7CWk0SL_HRCsl389QK0ESjiPNK1cCm"

print("--- STEP 1: ATTEMPTING DISCORD CONNECTION ---", flush=True)

try:
    # 2. SEND A PLAIN TEXT MESSAGE (NO EMBEDS)
    payload = {"content": "Hello from Render! Connection is working."}
    r = requests.post(url, json=payload, timeout=10)
    
    print(f"--- STEP 2: STATUS CODE: {r.status_code} ---", flush=True)
    print(f"--- STEP 3: DISCORD SAYS: {r.text} ---", flush=True)

except Exception as e:
    print(f"--- STEP 2: CONNECTION FAILED: {e} ---", flush=True)

# 3. STOP THE SCRIPT SO RENDER LOGS IT
sys.exit(0)
