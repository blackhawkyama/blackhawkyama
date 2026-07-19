# Advanced Hacking Patterns & Kit Enhancements

Real-world techniques from recent bug bounty work. Integrate into gauntlet, recce, and methodology.

---

## Pattern 1: Guest-Token Bug Class

**What it is:** Legacy API routes that mint guest or partial-auth tokens, bypassing modern auth checks.

**Root cause:** Hard-coded access grants on deprecated endpoints.

**Discovery:** Query Wayback Machine for legacy URLs → test each for token minting → reuse token on other endpoints.

**Example flow:**
1. Find legacy route via Wayback (e.g., `/api/v1/document/{id}`)
2. Load page → server mints `guest_token=xxx`
3. Reuse token to read/update adjacent data API never authorized
4. Result: Escalation from guest → authenticated user scope

**Agent exploit pattern:**
```
1. Wayback query → discover legacy routes
2. Test each route with GET/POST → capture Set-Cookie
3. Reuse cookie on admin endpoints
4. Report any 200 responses on endpoints that should 403
```

**Defense perspective:** Modern auth checks bypass if you hit legacy routes. Audit all routes, not just current API versions.

---

## Pattern 2: Cookie Enumeration (Underrated Surface)

**What it is:** Audit every cookie across every endpoint, understand what each does, how flipping one changes response.

**Why agents are good at this:** Spot stray Set-Cookie, test each in isolation, build dependency map.

**Discovery method:**
1. Crawl target (all endpoints)
2. Log every Set-Cookie response
3. For each cookie, test:
   - Remove it → does request fail?
   - Modify it → does response change?
   - Escalate value (if numeric) → does it grant higher access?
   - Rotate to another user's cookie → IDOR test
4. Build cookie dependency matrix

**Real-world signal:** A random Set-Cookie on `/api/search` that you've never seen → dig there.

**Probe approach:**
```python
# For each endpoint:
for endpoint in endpoints:
    response = requests.get(endpoint)
    
    # Capture all cookies
    cookies = extract_cookies(response)
    
    # Test each cookie's impact
    for cookie in cookies:
        # Test 1: Remove cookie
        r1 = requests.get(endpoint, cookies={k:v for k,v in cookies.items() if k != cookie})
        
        # Test 2: Flip/escalate cookie
        r2 = requests.get(endpoint, cookies={**cookies, cookie: flip_value(cookies[cookie])})
        
        # Test 3: Use another user's cookie
        r3 = requests.get(endpoint, cookies={**cookies, cookie: other_user_cookie})
        
        # Compare responses
        if r1.status_code != response.status_code or r2.text != response.text:
            # Cookie is meaningful → potential escalation/IDOR
```

---

## Pattern 3: GraphQL Coverage & Validator Pitfalls

**Discovery:**
- Hit GraphQL endpoint
- Introspection query → list all operations
- Test each mutation/query with different auth levels

**Key insight:** Different queries can have different middleware + auth schemes.

**Signal to watch:** `403 → 401` flip (middleware auth bypass, but no data access).

**Validator tuning problem:**
- Too loose: Reports null-byte bypass as "critical" when it only bypasses middleware (no impact)
- Too tight: Eats real findings, flags escalations as dupes

**Solution:** Impact-focused validator, not bypass-focused.
- Middleware bypass alone = medium (not crit)
- Middleware bypass + data access = high/crit
- Escalation path (guest→user, user→admin) = separate workflow

**Real-world example:** Apollo-based server flagged authorization at "this layer, not that one" → told us to dig at next layer → found real escalation.

---

## Pattern 4: JS Extraction → Endpoint Inventory → Coverage Tracking

**Primary mission:** Pull all JS (source, maps, lazy chunks) → extract every API endpoint → systematically test.

**Workflow:**
1. **Extract:** All JS files (main bundle, chunks, maps)
2. **Parse:** Build endpoint inventory (from fetch/axios/$.ajax calls)
3. **Track:** Queue endpoints, mark as tested/untested
4. **Coverage:** Measure → identify gaps → double down

**Example coverage system:**
```python
class CoverageTracker:
    endpoints = {
        '/api/users': {'tested': False, 'bugs': 0},
        '/api/admin': {'tested': False, 'bugs': 0},
        '/api/profile': {'tested': True, 'bugs': 2},
    }
    
    def test_endpoint(self, path):
        self.endpoints[path]['tested'] = True
        # Run exploit tests
        bugs = run_tests(path)
        self.endpoints[path]['bugs'] = len(bugs)
        return bugs
    
    def coverage_report(self):
        untested = [k for k,v in self.endpoints.items() if not v['tested']]
        return f"Tested: {len([x for x in self.endpoints.values() if x['tested']])}/{len(self.endpoints)}, Gap: {untested}"
```

**Real impact:** One target went quiet after early wave → added coverage tracking → second wave of bugs from untested endpoints.

---

## Pattern 5: Third-Party Auth Misconfigurations

### AWS Cognito Privilege Escalation
**Pattern:** Custom user attributes writable by default.
```
1. App hands you clean bearer token (via normal login)
2. You bypass normal flow, hit Cognito API directly
3. Update custom:role = "admin" via AdminUpdateUserAttributes
4. Get new token → admin access
```

**Why it works:** Cognito allows custom attributes writable unless explicitly marked read-only.

**Signal:** Any Cognito pool in use (check for cognito-idp API calls).

### Firebase RLS Mistakes
**Pattern:** Row-level security `.eq()` operator confusion.
```sql
-- Wrong: assumes user_id in JWT is trustworthy
select * from posts where user_id = auth.uid()  -- but auth.uid() can be spoofed

-- Right: verify token signature first, use claim not user input
```

### Supabase Custom Domains
**Pattern:** Supabase stood up by user, RLS not configured.
- Check supabase.co domain on target
- Test if auth is enforced
- Try unauthenticated queries

**Detection:** Look for supabase.co API calls in JS.

---

## Pattern 6: Checksum Gating & Code Golf Exploitation

**The weird XSS:** Reflected XSS gated by checksum that required exact characters at fixed offsets.

**Constraints stacked:**
1. Keep string length constant (length counted before rendering)
2. Keep W, P, M at specific indices (component named WPM)
3. Escape double-quote using %22 (costs 3 chars vs 1)
4. Code-golf payload into remaining bytes

**Exploitation:** Assign short domain to variable, align M inside import → trigger import → RCE.

**Lesson:** Checksums at fixed offsets create puzzles, not security. Agents good at code golf; humans slow.

**Pattern detection:** If validation key on character positions, try:
- Sliding payloads along offset
- Using shorter encodings (%22 vs ")
- Aligning payload boundaries with validation points

---

## Gauntlet Probe Ideas

### 1. Cookie Auditor Probe
Test impact of each cookie in isolation + combinations.

### 2. GraphQL Coverage Probe
Introspect → test every mutation/query → map auth levels per operation.

### 3. Third-Party Auth Detector
Scan for Cognito, Firebase, Supabase APIs → test for misconfig.

### 4. Checksum Brute Probe
If fixed-offset validation detected, try alignment attacks.

### 5. Guest-Token Reuse Probe
Capture partial-auth tokens → test against restricted endpoints.

---

## Recce Phase Ideas

### Phase 2.5: JS Coverage Mapping
Extract all JS → build endpoint inventory → track coverage.

### Phase 3.5: Third-Party Auth Enumeration
Detect auth service (Cognito/Firebase/Supabase) → test for misconfiguration.

---

## Methodology: Double Down

When agent finds one bug pointing at systemic pattern:
1. **Identify pattern:** JWT validation flaw? Auth bypass? Cookie misuse?
2. **Find all instances:** Where else does this pattern appear?
3. **Test systematically:** Each instance with same exploit
4. **Report cluster:** One finding → five findings if pattern repeats

**Example:** Agent finds JWT validation flaw in `/api/auth/refresh` → you ask "find every JWT validation in the app" → agent finds same flaw in 4 other endpoints → report as cluster.

---

## Event: HackerOne US South Summer Sessions

Post-auth on major HackerOne customer, July 2026, remote-only, limited slots.

Historically brutal post-auth scope → good signal for smaller field.

---

## Bonus: Agent Jailbreaking (Defensive Perspective)

**How it works (so you can defend):**
```
1. Ask agent to debug tool
2. Provide curl | bash install line
3. Agent balks at piping
4. "OK, read the script first"
5. Script rotates: first request = benign, second = reverse shell
6. Agent reads benign, thinks OK, pipes to bash → shell
```

**Defense:** Agents should refuse curl | bash even after reading. Code review then execute in isolated sandbox.

**From pentest side:** If you're testing agent security, this is the pattern.

---

## Summary: Kit Improvements

1. **Gauntlet:** Add cookie auditor, GraphQL introspector, auth service detector, guest-token tester
2. **Recce:** Add JS coverage phase, third-party auth phase
3. **Methodology:** Integrate guest-token hunting, cookie enumeration, checksum code-golf, double-down clustering
4. **BountyScout:** Score programs higher if they use Cognito/Firebase/Supabase (high-risk auth services)

These patterns feed directly into pentest reports and bug bounty payouts.
