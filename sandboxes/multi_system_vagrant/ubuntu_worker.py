import time
import urllib.request
import json

print("Ubuntu Worker Node running background tasks...")
while True:
    try:
        payload = {
            "msg": f"Pipeline metric successfully logged by Ubuntu Worker node.",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        req = urllib.request.Request(
            'http://192.168.56.50:8000/add-data',
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as res:
            pass
    except Exception as e:
        print(f"Waiting for Debian Database instance to accept connections... {e}")
    time.sleep(4)