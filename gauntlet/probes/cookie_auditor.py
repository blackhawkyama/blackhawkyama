"""Cookie Auditor Probe: Test cookie impact across endpoints."""

import logging
from typing import Dict, List, Optional
import requests

from .base import Probe, ProbeAttempt, Finding, Severity

logger = logging.getLogger(__name__)


class CookieAuditorProbe(Probe):
    """Audit cookies across endpoints for escalation, IDOR, and dependency."""

    name = "CookieAuditorProbe"
    description = "Test every cookie's impact in isolation and combinations"
    bom = ["requests"]

    def execute(self, target_url: str, endpoints: Optional[List[str]] = None, **kwargs) -> ProbeAttempt:
        """Execute cookie audit against target."""
        attempt = ProbeAttempt(target_url=target_url, endpoints=endpoints)

        if not endpoints:
            endpoints = self._crawl_target(target_url)
            if not endpoints:
                logger.info(f"No endpoints found for {target_url}")
                return attempt

        attempt.endpoints = endpoints
        findings = []

        # Phase 1: Collect all cookies from all endpoints
        cookie_map = {}
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, allow_redirects=True, timeout=5)
                cookies = self._extract_cookies(response)
                if cookies:
                    cookie_map[endpoint] = cookies
            except Exception as e:
                logger.debug(f"Error fetching {endpoint}: {e}")

        if not cookie_map:
            logger.info("No cookies found")
            return attempt

        # Phase 2: Test each cookie's impact
        for endpoint, cookies in cookie_map.items():
            for cookie_name, cookie_value in cookies.items():
                # Test 1: Remove cookie
                cookies_without = {k: v for k, v in cookies.items() if k != cookie_name}
                try:
                    r_without = requests.get(endpoint, cookies=cookies_without, timeout=5, allow_redirects=False)
                except Exception:
                    continue

                # Test 2: Escalate cookie if numeric
                if cookie_value.isdigit():
                    cookies_escalated = cookies.copy()
                    cookies_escalated[cookie_name] = str(int(cookie_value) + 1)
                    try:
                        r_escalated = requests.get(endpoint, cookies=cookies_escalated, timeout=5, allow_redirects=False)
                        if r_escalated.status_code == 200 and r_escalated.text != r_without.text:
                            findings.append(Finding(
                                title=f"Numeric cookie escalation: {cookie_name}",
                                description=f"Escalating {cookie_name} from {cookie_value} grants access to different data",
                                severity=Severity.HIGH,
                                endpoint=endpoint,
                                category="cookie_escalation",
                                evidence={"cookie": cookie_name, "original_value": cookie_value}
                            ))
                    except Exception:
                        pass

                # Test 3: Cookie necessity
                try:
                    r_base = requests.get(endpoint, cookies=cookies, timeout=5, allow_redirects=False)
                    if r_base.status_code == 200 and r_without.status_code != 200:
                        findings.append(Finding(
                            title=f"Required cookie: {cookie_name}",
                            description=f"Cookie {cookie_name} is necessary for endpoint access",
                            severity=Severity.LOW,
                            endpoint=endpoint,
                            category="cookie_necessity",
                            evidence={"cookie": cookie_name}
                        ))
                except Exception:
                    pass

        # Phase 3: Cross-endpoint cookie reuse (IDOR)
        endpoint_list = list(cookie_map.keys())
        for i, endpoint1 in enumerate(endpoint_list):
            for endpoint2 in endpoint_list[i+1:]:
                cookies_e2 = cookie_map.get(endpoint2, {})
                if not cookies_e2:
                    continue

                try:
                    r = requests.get(endpoint1, cookies=cookies_e2, timeout=5, allow_redirects=False)
                    if r.status_code == 200:
                        findings.append(Finding(
                            title="IDOR via cookie transfer",
                            description=f"Cookies from {endpoint2} work on {endpoint1}",
                            severity=Severity.CRITICAL,
                            endpoint=endpoint1,
                            category="idor_cookie_transfer",
                            evidence={"source": endpoint2, "target": endpoint1}
                        ))
                except Exception:
                    pass

        if findings:
            attempt.metrics["vulnerable"] = True
            attempt.metrics["severity"] = "HIGH"
            attempt.findings = self._sort_findings(findings)
            attempt.metrics["findings_count"] = len(findings)

        return attempt

    def _extract_cookies(self, response) -> Dict[str, str]:
        """Extract cookies from Set-Cookie headers."""
        cookies = {}
        for header in response.headers.getlist("Set-Cookie"):
            if "=" in header:
                cookie_pair = header.split(";")[0]
                if "=" in cookie_pair:
                    name, value = cookie_pair.split("=", 1)
                    cookies[name.strip()] = value.strip()
        return cookies

    def _crawl_target(self, url: str) -> List[str]:
        """Crawl target for endpoints (simplified)."""
        endpoints = []
        base_patterns = [
            "/api/users",
            "/api/profile",
            "/api/admin",
            "/api/settings",
            "/dashboard",
            "/account",
        ]

        for pattern in base_patterns:
            test_url = url.rstrip("/") + pattern
            try:
                r = requests.head(test_url, timeout=3)
                if r.status_code < 500:
                    endpoints.append(test_url)
            except Exception:
                pass

        return endpoints
