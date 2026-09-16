#!/usr/bin/env python3
from pyngrok import ngrok, conf
import time

# Set config file path
conf.get_default().config_path = "/Users/mina_ibrahim/.iclaw/conversations/users/system_default_user/2026/09/07/iclawcore-temp-31326486/work-tracker-app/ngrok.yml"

# Create a public tunnel to port 5000
print("Creating public URL...")
public_url = ngrok.connect(5000)

print("\n" + "="*60)
print(f"PUBLIC URL: {public_url}")
print("="*60 + "\n")
print("Share this URL with your colleagues!")
print("The app is now accessible from anywhere.")
print("\nPress Ctrl+C to stop the tunnel\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping tunnel...")
    ngrok.disconnect(public_url)
