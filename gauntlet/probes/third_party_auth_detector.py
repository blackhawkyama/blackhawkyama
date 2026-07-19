"""Third-Party Auth Detector: Test Cognito, Firebase, Supabase for misconfigurations."""

import logging
import re
from typing import Dict, List, Optional
import requests
import json

from .base import Probe, ProbeAttempt, Finding, Severity

logger = logging.getLogger(__name__)


class ThirdPartyAuthDetectorProbe(Probe):
    """Detect and test third-party auth services for misconfiguration."""

    name = "ThirdPartyAuthDetectorProbe"
    description = "Detect Cognito, Firebase, Supabase usage and test for misconfigurations"
    bom = ["requests"]

    AUTH_SERVICES = {
        "cognito": {
            "pattern": r"cognito-idp.*amazonaws|identityPoolId|userPoolId",
            "test": "_test_cognito_misconfiguration",
        },
        "firebase": {
            "pattern": r"firebaseapp\.com|firebase\.google|firestore",
            "test": "_test_firebase_rls",
        },
        "supabase": {
            "pattern": r"supabase\.co|supabase\.io",
            "test": "_test_supabase_rls",
        },
    }

    def execute(self, target_url: str, bearer_token: Optional[str] = None, **kwargs) -> ProbeAttempt:
        """Execute third-party auth detection against target."""
        attempt = ProbeAttempt(target_url=target_url, bearer_token=bearer_token)

        # Fetch JS content from target
        js_content = self._fetch_js_content(target_url)
        if not js_content:
            logger.info(f"No JS content found for {target_url}")
            return attempt

        findings = []

        # Detect auth services
        for service, config in self.AUTH_SERVICES.items():
            if re.search(config["pattern"], js_content, re.IGNORECASE):
                logger.info(f"Detected {service} usage")
                test_method = getattr(self, config["test"], None)
                if test_method:
                    result = test_method(target_url, js_content, bearer_token)
                    if result:
                        findings.extend(result)

        if findings:
            attempt.metrics["vulnerable"] = True
            attempt.findings = self._sort_findings(findings)
            attempt.metrics["findings_count"] = len(findings)

        return attempt

    def _fetch_js_content(self, target_url: str) -> Optional[str]:
        """Fetch main JS bundles from target."""
        try:
            r = requests.get(target_url, timeout=10)
            content = r.text
            # Extract script tags with src attributes
            js_urls = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content)
            combined_js = content  # Include HTML for inline scripts

            # Fetch bundled JS files
            for js_url in js_urls[:5]:  # Limit to first 5 to avoid bloat
                if not js_url.startswith("http"):
                    js_url = target_url.rstrip("/") + "/" + js_url.lstrip("/")
                try:
                    js_r = requests.get(js_url, timeout=5)
                    combined_js += js_r.text[:50000]  # Limit per file
                except Exception:
                    pass

            return combined_js
        except Exception as e:
            logger.debug(f"Error fetching JS: {e}")
            return None

    def _test_cognito_misconfiguration(self, target_url: str, js_content: str, bearer_token: Optional[str]) -> List[Finding]:
        """Test Cognito for common misconfigurations."""
        findings = []

        # Extract Cognito identifiers
        identity_pool = re.search(r"identityPoolId['\"]?\s*:\s*['\"]([^'\"]+)['\"]", js_content)
        user_pool = re.search(r"userPoolId['\"]?\s*:\s*['\"]([^'\"]+)['\"]", js_content)
        client_id = re.search(r"userPoolWebClientId['\"]?\s*:\s*['\"]([^'\"]+)['\"]", js_content)
        region = re.search(r"region['\"]?\s*:\s*['\"]?(us-[a-z]+-\d+)['\"]?", js_content)

        if identity_pool:
            findings.append(Finding(
                title="Cognito Identity Pool ID exposed",
                description="Identity Pool ID found in client-side code - test for unauthenticated access",
                severity=Severity.MEDIUM,
                category="cognito_exposure",
                evidence={"identity_pool_id": identity_pool.group(1)[:20] + "..."}
            ))

        if user_pool and client_id and region:
            findings.append(Finding(
                title="Cognito User Pool configuration exposed",
                description="User Pool ID and Client ID exposed - test for Signup API bypass",
                severity=Severity.MEDIUM,
                category="cognito_exposure",
                evidence={
                    "user_pool_id": user_pool.group(1)[:20] + "...",
                    "client_id": client_id.group(1)[:20] + "...",
                }
            ))

        return findings

    def _test_firebase_rls(self, target_url: str, js_content: str, bearer_token: Optional[str]) -> List[Finding]:
        """Test Firebase Firestore for RLS gaps."""
        findings = []

        # Look for Firebase API key
        api_key = re.search(r"apiKey['\"]?\s*:\s*['\"]([^'\"]+)['\"]", js_content)
        if not api_key:
            return findings

        project_id = re.search(r"projectId['\"]?\s*:\s*['\"]([^'\"]+)['\"]", js_content)
        if not project_id:
            return findings

        # Test unauthenticated Firestore access
        try:
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id.group(1)}/databases/_(default)/documents/users"
            r = requests.get(
                firestore_url,
                headers={"X-Goog-Api-Key": api_key.group(1)},
                timeout=5
            )

            if r.status_code == 200:
                findings.append(Finding(
                    title="Firebase Firestore unauthenticated access",
                    description="Firestore accessible without authentication - RLS not enforced",
                    severity=Severity.CRITICAL,
                    category="firebase_rls_bypass",
                    evidence={"project_id": project_id.group(1)[:20] + "..."}
                ))
        except Exception as e:
            logger.debug(f"Firebase test error: {e}")

        return findings

    def _test_supabase_rls(self, target_url: str, js_content: str, bearer_token: Optional[str]) -> List[Finding]:
        """Test Supabase for RLS gaps."""
        findings = []

        # Look for Supabase configuration
        supabase_url = re.search(r"https://[a-z0-9]+\.supabase\.co", js_content)
        api_key = re.search(r"anonKey['\"]?\s*:\s*['\"]([^'\"]+)['\"]", js_content)

        if not supabase_url or not api_key:
            return findings

        # Test unauthenticated query
        try:
            r = requests.get(
                f"{supabase_url.group(0)}/rest/v1/users?select=*",
                headers={
                    "apikey": api_key.group(1),
                    "Authorization": f"Bearer {api_key.group(1)}",
                },
                timeout=5
            )

            if r.status_code == 200:
                findings.append(Finding(
                    title="Supabase unauthenticated RLS bypass",
                    description="Supabase tables accessible with anon key - RLS not enforced",
                    severity=Severity.CRITICAL,
                    category="supabase_rls_bypass",
                    evidence={"url": supabase_url.group(0)[:30] + "..."}
                ))
        except Exception as e:
            logger.debug(f"Supabase test error: {e}")

        return findings
