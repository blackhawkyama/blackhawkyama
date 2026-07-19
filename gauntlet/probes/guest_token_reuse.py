"""Guest Token Reuse Probe: Discover legacy routes and test token escalation."""

import logging
from typing import Dict, List, Optional
import requests

from .base import Probe, ProbeAttempt, Finding, Severity

logger = logging.getLogger(__name__)


class GuestTokenReuseProbe(Probe):
    """Discover and exploit guest token escalation paths."""

    name = "GuestTokenReuseProbe"
    description = "Discover legacy routes that mint guest/partial-auth tokens and test reuse"
    bom = ["requests"]

    def execute(self, target_url: str, **kwargs) -> ProbeAttempt:
        """Execute guest token reuse test against target."""
        attempt = ProbeAttempt(target_url=target_url)

        # Phase 1: Discover legacy routes via static patterns
        legacy_routes = self._discover_legacy_routes(target_url)
        if not legacy_routes:
            logger.info(f"No legacy routes discovered for {target_url}")
            return attempt

        findings = []

        # Phase 2: Test each legacy route for guest token minting
        guest_tokens = {}
        for route in legacy_routes:
            try:
                response = requests.get(route, allow_redirects=True, timeout=5)
                cookies = self._extract_cookies(response.headers)

                # Check for guest/token indicators
                if any("guest" in k.lower() or "token" in k.lower() or "session" in k.lower()
                       for k in cookies.keys()):
                    guest_tokens[route] = cookies
                    findings.append(Finding(
                        title=f"Guest token minted at legacy route",
                        description=f"Legacy route {route} mints guest/session token",
                        severity=Severity.MEDIUM,
                        endpoint=route,
                        category="guest_token_minting",
                        evidence={"route": route, "cookies": list(cookies.keys())}
                    ))
            except Exception as e:
                logger.debug(f"Error testing {route}: {e}")

        # Phase 3: Test each guest token against restricted endpoints
        admin_endpoints = [
            "/api/admin/users",
            "/api/admin/settings",
            "/api/v2/admin/dashboard",
            "/admin",
            "/dashboard",
        ]

        for legacy_route, cookies in guest_tokens.items():
            for admin_endpoint in admin_endpoints:
                full_url = target_url.rstrip("/") + admin_endpoint
                try:
                    r = requests.get(full_url, cookies=cookies, allow_redirects=False, timeout=5)

                    if r.status_code == 200:
                        findings.append(Finding(
                            title="Guest token escalation to admin endpoint",
                            description=f"Guest token from {legacy_route} accesses {admin_endpoint}",
                            severity=Severity.CRITICAL,
                            endpoint=admin_endpoint,
                            category="guest_token_escalation",
                            evidence={
                                "legacy_route": legacy_route,
                                "admin_endpoint": admin_endpoint,
                                "status_code": r.status_code
                            }
                        ))
                except Exception as e:
                    logger.debug(f"Error testing escalation: {e}")

        if findings:
            attempt.metrics["vulnerable"] = True
            attempt.findings = self._sort_findings(findings)
            attempt.metrics["findings_count"] = len(findings)

        return attempt

    def _discover_legacy_routes(self, target: str) -> List[str]:
        """Discover legacy routes via static patterns."""
        patterns = [
            "/api/v1/auth/login",
            "/api/v1/auth/token",
            "/api/v1/users",
            "/api/v1/users/{id}",
            "/api/guest/access",
            "/api/v1/public",
            "/api/v2/auth/callback",
            "/old-api/login",
            "/legacy/auth",
        ]

        discovered = []
        for pattern in patterns:
            url = target.rstrip("/") + pattern
            try:
                r = requests.head(url, timeout=3, allow_redirects=False)
                if r.status_code < 500:
                    discovered.append(url)
                    logger.debug(f"Found legacy route: {url}")
            except Exception:
                pass

        return discovered

    def _extract_cookies(self, headers) -> Dict[str, str]:
        """Extract cookies from Set-Cookie headers."""
        cookies = {}
        for header in headers.getlist("Set-Cookie") if hasattr(headers, "getlist") else []:
            if "=" in header:
                cookie_pair = header.split(";")[0]
                if "=" in cookie_pair:
                    name, value = cookie_pair.split("=", 1)
                    cookies[name.strip()] = value.strip()
        return cookies
