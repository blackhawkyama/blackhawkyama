# Recce Enhancements: Wayback Machine Recon Phase

Extend `recce` autonomous reconnaissance agent with Wayback Machine integration for discovering legacy API routes and historical vulnerabilities.

## New Phase: Wayback Recon (Phase 1.5, inserted after scope lock)

**Goal:** Discover legacy API routes, deprecated endpoints, and historical configurations that may still be live or exploitable.

```python
class WaybackReconPhase:
    """
    Phase 1.5: Query Wayback Machine for target history.
    Discovers legacy API routes, old endpoints, historical misconfigurations.
    """
    
    phase_number = 1.5
    name = "Wayback Recon"
    description = "Query Internet Archive for legacy endpoints and historical configurations"
    objectives = [
        "Discover API routes from archived snapshots",
        "Identify deprecated endpoints still live",
        "Find historical misconfigurations",
        "Detect token minting on legacy routes",
    ]
    completed = False
    
    def __init__(self, target_url: str, api_endpoint: str = None):
        self.target_url = target_url
        self.api_endpoint = api_endpoint or target_url
        self.findings = []
        self.legacy_routes = []
    
    def execute(self) -> dict:
        """Run Wayback recon and return structured findings."""
        
        # 1. Query Wayback Machine for snapshots
        snapshots = self._query_wayback_api()
        if not snapshots:
            return {"status": "no_snapshots", "message": f"No Wayback snapshots for {self.target_url}"}
        
        # 2. Fetch representative snapshots and extract routes
        self.legacy_routes = self._extract_routes_from_snapshots(snapshots)
        
        # 3. Test each route for liveness and auth token leakage
        self._test_routes_for_vulnerabilities()
        
        # 4. Score findings by exploitability
        self._score_findings()
        
        self.completed = True
        return {
            "phase": self.name,
            "target": self.target_url,
            "snapshots_found": len(snapshots),
            "legacy_routes_discovered": len(self.legacy_routes),
            "vulnerabilities_found": len([f for f in self.findings if f['severity'] >= 'MEDIUM']),
            "findings": self.findings,
        }
    
    def _query_wayback_api(self) -> list:
        """Query Wayback Machine API for available snapshots."""
        import requests
        
        api_url = "https://archive.org/wayback/available"
        params = {
            "url": self.target_url,
            "output": "json",
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
            
            # Extract snapshot timestamps
            snapshots = data.get('archived_snapshots', {}).get('closest', {})
            if not snapshots:
                snapshots = []
            
            return snapshots
        except Exception as e:
            print(f"Wayback API error: {e}")
            return []
    
    def _extract_routes_from_snapshots(self, snapshots: list) -> list:
        """
        Fetch Wayback snapshots and extract API routes from:
        - HTML (href, src, action attributes)
        - JavaScript (fetch, axios, $.ajax calls)
        - JSON responses
        """
        import requests
        from bs4 import BeautifulSoup
        import re
        
        routes = set()
        
        # Sample 3-5 snapshots spread across time
        sample_timestamps = [s['timestamp'] for s in snapshots[:5]]
        
        for timestamp in sample_timestamps:
            wayback_url = f"https://web.archive.org/web/{timestamp}/{self.target_url}"
            
            try:
                response = requests.get(wayback_url, timeout=10)
                html = response.text
                
                # Extract from HTML attributes
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.find_all(['a', 'form']):
                    href = link.get('href') or link.get('action')
                    if href and ('api' in href or '/v' in href):
                        routes.add(href)
                
                # Extract from JavaScript (crude regex, improve with AST parsing)
                js_patterns = [
                    r'fetch\([\'"]([^\'\"]+)[\'"]',
                    r'axios\.\w+\([\'"]([^\'\"]+)[\'"]',
                    r'\$\.ajax\({[^}]*url:\s*[\'"]([^\'\"]+)[\'"]',
                    r'url:\s*[\'"]([^\'\"]+)[\'"]',
                ]
                for pattern in js_patterns:
                    matches = re.findall(pattern, html)
                    routes.update(matches)
                
            except Exception as e:
                print(f"Error fetching snapshot {timestamp}: {e}")
        
        # Normalize routes (remove duplicates, resolve relative paths)
        normalized = set()
        for route in routes:
            if route.startswith('http'):
                normalized.add(route)
            elif route.startswith('/'):
                normalized.add(f"{self.api_endpoint}{route}")
        
        return list(normalized)
    
    def _test_routes_for_vulnerabilities(self):
        """Test each legacy route for:
        - Liveness (does it still respond?)
        - Auth token minting (unintended token generation)
        - Access control (guest/partial auth escalation)
        """
        import requests
        
        for route in self.legacy_routes:
            try:
                # Test with GET
                resp_get = requests.get(route, timeout=5, allow_redirects=False)
                
                # Test with POST (often mints tokens)
                resp_post = requests.post(route, timeout=5, allow_redirects=False)
                
                finding = {
                    "route": route,
                    "method": "unknown",
                    "status_code": None,
                    "auth_token_found": False,
                    "severity": "LOW",
                }
                
                # Check for auth tokens
                for resp in [resp_get, resp_post]:
                    if resp.status_code < 400:
                        finding["status_code"] = resp.status_code
                        finding["method"] = resp.request.method
                        
                        # Check for token indicators
                        if self._has_auth_token(resp):
                            finding["auth_token_found"] = True
                            finding["severity"] = "MEDIUM"
                            finding["recommendation"] = "Test token for escalation potential"
                
                if finding["status_code"]:  # Route is live
                    self.findings.append(finding)
            
            except requests.exceptions.Timeout:
                pass  # Route not live
            except Exception as e:
                print(f"Error testing {route}: {e}")
    
    def _has_auth_token(self, response) -> bool:
        """Check for auth tokens in Set-Cookie, Authorization, or response body."""
        headers_text = str(response.headers).lower()
        body_text = response.text.lower()
        
        token_indicators = ['token', 'session', 'jwt', 'bearer', 'auth']
        for indicator in token_indicators:
            if indicator in headers_text or indicator in body_text[:500]:
                return True
        
        return False
    
    def _score_findings(self):
        """Score findings by exploitability: liveness + token minting + escalation potential."""
        for finding in self.findings:
            score = 0
            
            # Legacy route is live (+50 points)
            if finding["status_code"] == 200:
                score += 50
            elif finding["status_code"] < 400:
                score += 30
            
            # Mints auth token (+50 points)
            if finding["auth_token_found"]:
                score += 50
            
            # Adjust severity
            if score >= 80:
                finding["severity"] = "CRITICAL"
                finding["exploitability"] = "high"
            elif score >= 50:
                finding["severity"] = "HIGH"
                finding["exploitability"] = "medium"
            else:
                finding["severity"] = "MEDIUM"
                finding["exploitability"] = "low"
            
            finding["score"] = score


# Integration into Recce orchestrator

class ReconPhases:
    """Updated recon phases with Wayback phase inserted."""
    
    phases = {
        1: {"name": "Scope Lock", "class": ScopeLockPhase},
        1.5: {"name": "Wayback Recon", "class": WaybackReconPhase},  # NEW
        2: {"name": "Enumeration", "class": EnumerationPhase},
        3: {"name": "Hypothesis Testing", "class": HypothesisPhase},
        4: {"name": "Exploitation", "class": ExploitationPhase},
        5: {"name": "Documentation", "class": DocumentationPhase},
    }
    
    @classmethod
    def run_all(cls, target_url: str, api_endpoint: str = None):
        """Run all phases in order, feeding Wayback findings into downstream phases."""
        results = {}
        
        for phase_num in sorted(cls.phases.keys()):
            phase_info = cls.phases[phase_num]
            phase = phase_info["class"](target_url, api_endpoint)
            
            result = phase.execute()
            results[phase_num] = result
            
            # If Wayback phase, feed legacy_routes into next phases
            if phase_num == 1.5:
                legacy_routes = phase.legacy_routes
                # Pass to downstream phases
                # E.g., Enumeration phase prioritizes these routes
        
        return results
```

## Usage

```python
# Standalone Wayback phase
from recce.phases.wayback_recon import WaybackReconPhase

wayback = WaybackReconPhase(target_url="https://target-ecommerce.com")
findings = wayback.execute()

print(f"Legacy routes: {findings['legacy_routes_discovered']}")
for finding in findings['findings']:
    print(f"  {finding['route']}: {finding['severity']} (token: {finding['auth_token_found']})")

# Full recon pipeline with Wayback
from recce.orchestrator import Orchestrator

orchestrator = Orchestrator(
    target_url="https://target.com",
    phases=[1, 1.5, 2, 3, 4, 5],  # Include Wayback phase
)
results = orchestrator.run_all()
```

## Output Example

```json
{
  "phase": "Wayback Recon",
  "target": "https://target-ecommerce.com",
  "snapshots_found": 45,
  "legacy_routes_discovered": 12,
  "vulnerabilities_found": 3,
  "findings": [
    {
      "route": "https://target-ecommerce.com/api/v1/auth/token",
      "method": "POST",
      "status_code": 200,
      "auth_token_found": true,
      "severity": "CRITICAL",
      "exploitability": "high",
      "score": 100,
      "recommendation": "Test token for escalation potential"
    },
    {
      "route": "https://target-ecommerce.com/api/v2/admin/users",
      "method": "GET",
      "status_code": 404,
      "auth_token_found": false,
      "severity": "LOW",
      "exploitability": "low",
      "score": 10
    }
  ]
}
```

## Files to Create

1. `recce/phases/wayback_recon.py` — Full WaybackReconPhase implementation
2. `recce/orchestrator.py` — Update to register phase 1.5
3. `tests/test_wayback_recon.py` — Unit tests

## Dependencies

Add to `recce/requirements.txt`:
- `requests>=2.31.0`
- `beautifulsoup4>=4.12.0`

## Benefits

- **Autonomous discovery** — Finds legacy routes without manual Wayback browsing
- **Real-world impact** — Legacy routes often have outdated auth/validation
- **Feeds downstream** — Routes prioritized for enumeration and exploitation phases
- **Repeatable** — Deterministic output for CI/regression detection
