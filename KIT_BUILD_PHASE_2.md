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

### Real-World XXE Patterns (from field research)
- **Wayback Machine legacy APIs** — Old XML endpoints still exist on archived routes; often mint guest/partial-auth tokens on POST
- **SOAP endpoints** — Underutilized attack surface; older APIs still accept XML
- **File upload parsers** — E-commerce sites parsing XML from uploaded docs (receipts, invoices, shipping manifests)

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

#### 1. **Authentication Bypass** (constant, good payouts, very common)
   - **AWS Cognito privilege escalation** — custom user attributes are writable even with clean bearer token; self-promote to admin by hitting pool directly
   - **Wayback token leakage** — legacy API routes still mint guest or partial-auth tokens; test each route for escalation
   - **Response header side-channels** — stray Set-Cookie headers on random endpoints grant unintended access

#### 2. **Business Logic Flaws** (highest bounty ROI, every program has them)
   - Harder to systematize but highest bounty range ($1k-25k+)
   - Every pentest report includes logic flaws
   - Requires manual testing + lateral thinking

#### 3. **Insecure Deserialization** (Java/Python, high severity when present)
   - Gadget chain exploitation (Java, Python pickle)
   - Object injection leading to RCE

#### 4. **Reflected XSS + Checksum Bypass** (code golf exploitation)
   - E-commerce platforms with form checksums at fixed string offsets
   - Wayback Machine often has versions without validation
   - Alignment puzzle: match exact characters at fixed offsets

#### 5. **Response Header / Cookie Enumeration** (underappreciated surface)
   - Stray Set-Cookie on random API calls
   - Agents catch this; humans skim past
   - Often grants unintended access or info disclosure

#### 6. **CORS Misconfigurations** (API bypass, growing class)
   - Overly permissive origins
   - Credential-included cross-origin requests

#### 7. **Web Cache Poisoning** (CDN/proxy abuse, underrated)
   - Cache key confusion
   - Response splitting via newlines in headers

## ROI Notes
- XXE payout range: $500-5000+ depending on program
- Business Logic > XXE for consistent bounty $
- XXE value: less competition, higher success rate on found vulns
- Portfolio angle: rounds out attack surface, helps with pentest hiring

## Tooling Enhancements

### Gauntlet Probes (AI Security)
- **Wayback token leakage** — detect if legacy routes mint unintended tokens
- **Cognito attribute injection** — test custom attribute escalation
- **Response header enumeration** — flag stray Set-Cookie, Auth headers

### Recce Phases (Autonomous Recon)
- **Phase 1 (new):** Query Wayback Machine for legacy API routes
- **Phase 2 (enhanced):** Feed Wayback URLs into testing pipeline
- **Phase 3 (new):** Prioritize by auth token likelihood

---

## Branch
Working on: `claude/four-horsemen-23z5qt`
Tracking: This file + blog writeups + gauntlet/recce enhancements

---
Last updated: 2026-07-19
