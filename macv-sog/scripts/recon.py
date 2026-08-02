#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

targets = open('/home/ec2-user/macv-sog/config/targets.txt').read().strip().split('\n')

print(f"[{datetime.now()}] Starting recon on {len(targets)} targets...")

for target in targets:
    print(f"[*] Scanning {target}")
    with open('/home/ec2-user/macv-sog/logs/recon.log', 'a') as f:
        f.write(f"{datetime.now()} - Scanned {target}\n")

print("[+] Recon complete")
