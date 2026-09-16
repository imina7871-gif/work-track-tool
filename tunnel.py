#!/usr/bin/env python3
import subprocess
import sys
import time
import re

# Start cloudflared tunnel
cmd = ["/tmp/cloudflared", "tunnel", "--url", "http://localhost:5000"]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

print("Starting tunnel...")
print("Waiting for public URL...")

# Read output and find the URL
for line in process.stdout:
    print(line, end='')
    # Look for the URL in cloudflared output
    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
    if match:
        url = match.group(0)
        print(f"\n{'='*60}")
        print(f"PUBLIC URL: {url}")
        print(f"{'='*60}\n")
        print("Share this URL with your colleagues!")
        print("Press Ctrl+C to stop the tunnel\n")
        
        # Keep the process running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping tunnel...")
            process.terminate()
            sys.exit(0)
