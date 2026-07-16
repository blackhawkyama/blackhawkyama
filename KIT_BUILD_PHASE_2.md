# Kit Building Phase 2: New Attack Classes

## Status
Breadth-building phase initiated. Starting with XXE (XML External Entity).

## Phase Overview
Building out kit to cover 6-8 new attack classes before specializing. Goal: wide attack surface for bug bounties + pentest portfolio.

## Current Focus: XXE (XML External Entity)

### Why XXE
- Real-world, high severity
- Less saturated than OWASP Top 10 basics (15-25% less common)
- Better chance of actually finding + claiming bounties
- Foundation for chaining (XXE → SSRF → internal service abuse)

### XXE Exploitation Angles
1. **Basic XXE Injection** → read `/etc/passwd`, file:// protocol access
2. **Blind XXE** → out-of-band exfiltration (DNS/HTTP callbacks)
3. **XXE Billion Laughs** → DoS via entity expansion

### PortSwigger Labs to Complete
- [ ] "Exploiting XXE to retrieve files" (basic)
- [ ] "Blind XXE with out-of-band interaction"
- [ ] "Blind XXE with time-based detection"
- [ ] "XXE via file upload"

### Lab Findings Template
When completing each lab, capture:
- **Input vector** — where XML is accepted (form param, file upload, API endpoint)
- **Parser behavior** — what confirms XXE works
- **Payload used** — exact XXE payload that worked
- **Output/Data exfiltrated** — what was readable
- **Severity** — impact to application

### Writeup Format (post to blog after labs complete)
1. **Recon** — identify XML input, parser behavior
2. **Exploitation** — craft payload, exfiltrate data
3. **Impact** — what data was accessed, why it matters
4. **Root Cause** — why XXE works (entity expansion enabled)
5. **Remediation** — disable DTD, disable entity expansion, whitelist

### Next Steps After XXE
1. **Business Logic Flaws** (highest bounty ROI, every program has them)
2. **Authentication Bypass** (constant, good payouts, very common)
3. **Insecure Deserialization** (Java/Python, high severity when present)
4. **CORS Misconfigurations** (API bypass, growing class)
5. **Web Cache Poisoning** (CDN/proxy abuse, underrated)

## ROI Notes
- XXE payout range: $500-5000+ depending on program
- Business Logic > XXE for consistent bounty $
- XXE value: less competition, higher success rate on found vulns
- Portfolio angle: rounds out attack surface, helps with pentest hiring

## Branch
Working on: `claude/four-horsemen-23z5qt`
Tracking: This file + blog writeups

---
Last updated: 2026-07-16
