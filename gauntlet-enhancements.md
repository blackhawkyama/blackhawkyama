# Gauntlet Enhancements: Real-World Probes

Add these probes to gauntlet for field-ready vulnerability detection.

## 1. Wayback Token Leakage Probe

**What it does:** Query Wayback Machine for legacy API routes of a target, test each for unintended token minting.

```python
class WaybackTokenLeakageProbe(Probe):
    """Detect legacy API routes that mint unintended auth tokens."""
    
    bom = ['wayback-token-leakage']
    
    def _execute_attempt(self, attempt, seq):
        target = attempt.prompt.target_url
        
        # Query Wayback for snapshots
        wayback_snapshots = self._query_wayback(target)
        
        # Extract unique API routes
        legacy_routes = self._extract_routes(wayback_snapshots)
        
        # Test each route for token minting
        for route in legacy_routes:
            response = requests.post(route, data={})
            
            # Check for auth tokens in response
            if self._has_auth_token(response):
                attempt.metrics['vulnerable'] = True
                attempt.metrics['severity'] = 'HIGH'
                attempt.metrics['finding'] = f"Legacy route {route} mints unintended token"
                attempt.metrics['token_header'] = self._extract_token(response)
        
        return attempt
    
    def _query_wayback(self, url):
        """Query Wayback Machine API for snapshots."""
        api_url = f"https://archive.org/wayback/available?url={url}"
        return requests.get(api_url).json()
    
    def _extract_routes(self, snapshots):
        """Extract unique API routes from archived HTML/JS."""
        # Parse JavaScript and HTML for API endpoints
        # Return list of unique routes
        pass
    
    def _has_auth_token(self, response):
        """Check for auth tokens in Set-Cookie or response body."""
        return 'Set-Cookie' in response.headers or 'token' in response.text.lower()
```

**Usage:**
```python
probe = WaybackTokenLeakageProbe()
attempt = probe.attempt("https://target-ecommerce.com")
probe.execute(attempt)
if attempt.metrics['vulnerable']:
    print(f"Found: {attempt.metrics['finding']}")
```

---

## 2. AWS Cognito Attribute Injection Probe

**What it does:** Test if custom user attributes in AWS Cognito are writable, enabling self-promotion to admin.

```python
class CognitoPrivilegeEscalationProbe(Probe):
    """Detect writable custom attributes in Cognito pools."""
    
    bom = ['cognito-attribute-injection']
    
    def _execute_attempt(self, attempt, seq):
        target = attempt.prompt.target_url
        bearer_token = attempt.prompt.bearer_token  # Clean user token
        
        # Discover Cognito pool ID from app
        pool_id = self._discover_cognito_pool(target)
        if not pool_id:
            return attempt
        
        # Test custom attribute writability
        test_attributes = {
            'custom:role': 'admin',
            'custom:admin': 'true',
            'custom:is_admin': 'true',
        }
        
        for attr, value in test_attributes.items():
            response = self._test_attribute_write(pool_id, bearer_token, attr, value)
            
            if response.status_code == 200:
                # Verify escalation
                new_token = self._get_new_token(pool_id, bearer_token)
                if self._is_admin(new_token):
                    attempt.metrics['vulnerable'] = True
                    attempt.metrics['severity'] = 'CRITICAL'
                    attempt.metrics['finding'] = f"Writable custom attribute '{attr}' enables admin escalation"
                    attempt.metrics['methodology'] = 'AWS Cognito misconfiguration'
        
        return attempt
    
    def _discover_cognito_pool(self, url):
        """Extract Cognito pool ID from app JS/API responses."""
        # Look for pool IDs in HTML, API responses
        pass
    
    def _test_attribute_write(self, pool_id, token, attr, value):
        """Test if custom attribute is writable via AdminUpdateUserAttributes."""
        # Call Cognito API to update attribute
        pass
    
    def _is_admin(self, token):
        """Decode JWT and check for admin role."""
        decoded = jwt.decode(token, options={"verify_signature": False})
        return 'admin' in str(decoded).lower()
```

**Usage:**
```python
probe = CognitoPrivilegeEscalationProbe()
attempt = probe.attempt("https://target-app.com", bearer_token=user_token)
probe.execute(attempt)
```

---

## 3. Response Header Enumeration Probe

**What it does:** Crawl target and flag stray Set-Cookie, Authorization headers, or auth tokens on unexpected endpoints.

```python
class ResponseHeaderSideChannelProbe(Probe):
    """Detect auth tokens and credentials leaked in response headers."""
    
    bom = ['response-header-sidechannel']
    
    def _execute_attempt(self, attempt, seq):
        target = attempt.prompt.target_url
        
        # Crawl target endpoints
        endpoints = self._crawl_endpoints(target)
        
        findings = []
        for endpoint in endpoints:
            response = requests.get(endpoint, allow_redirects=True)
            
            # Check for suspicious headers
            suspicious = self._check_headers(response.headers, endpoint)
            if suspicious:
                findings.extend(suspicious)
        
        if findings:
            attempt.metrics['vulnerable'] = True
            attempt.metrics['severity'] = 'MEDIUM'
            attempt.metrics['findings'] = findings
            attempt.metrics['count'] = len(findings)
        
        return attempt
    
    def _crawl_endpoints(self, url):
        """Crawl target for all endpoints."""
        # Use Burp/ffuf wordlist or app JS
        pass
    
    def _check_headers(self, headers, endpoint):
        """Check for auth tokens, cookies, or sensitive data."""
        suspicious = []
        
        # Flag Set-Cookie on non-standard endpoints
        if 'Set-Cookie' in headers:
            cookie_value = headers['Set-Cookie']
            if 'token' in cookie_value.lower() or 'session' in cookie_value.lower():
                suspicious.append({
                    'endpoint': endpoint,
                    'header': 'Set-Cookie',
                    'value': cookie_value[:50] + '...',
                    'risk': 'Unintended auth token on unexpected endpoint'
                })
        
        # Flag Authorization headers
        if 'Authorization' in headers:
            suspicious.append({
                'endpoint': endpoint,
                'header': 'Authorization',
                'risk': 'Leaked auth header in response'
            })
        
        return suspicious
```

**Usage:**
```python
probe = ResponseHeaderSideChannelProbe()
attempt = probe.attempt("https://target-api.com")
probe.execute(attempt)
for finding in attempt.metrics.get('findings', []):
    print(f"{finding['endpoint']}: {finding['risk']}")
```

---

## Integration

Add these to `gauntlet/probes/` directory:
- `wayback_token_leakage.py`
- `cognito_privilege_escalation.py`
- `response_header_sidechannel.py`

Register in `gauntlet/__init__.py`:
```python
from .probes.wayback_token_leakage import WaybackTokenLeakageProbe
from .probes.cognito_privilege_escalation import CognitoPrivilegeEscalationProbe
from .probes.response_header_sidechannel import ResponseHeaderSideChannelProbe

PROBES = [
    WaybackTokenLeakageProbe,
    CognitoPrivilegeEscalationProbe,
    ResponseHeaderSideChannelProbe,
    # ... existing probes
]
```

Then in CI/test:
```python
suite = gauntlet.GauntletSuite(probes=PROBES)
results = suite.run(target="https://target.com")
```

---

## Priority for Implementation

1. **Response Header Enumeration** (easiest, highest signal-to-noise)
2. **Cognito Attribute Injection** (high severity, AWS-focused apps)
3. **Wayback Token Leakage** (requires Wayback API + parsing, but real-world impact)

All three feed into bounty hunting and pentest reports.
