#!/usr/bin/env python3
import sqlite3
from datetime import datetime

conn = sqlite3.connect('/home/ec2-user/macv-sog/results/findings.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS findings
             (id INTEGER PRIMARY KEY, target TEXT, vuln_type TEXT,
              severity TEXT, timestamp DATETIME)''')
conn.commit()

print(f"[{datetime.now()}] Vulnerability scan initiated")
print("[+] Database initialized")

conn.close()
