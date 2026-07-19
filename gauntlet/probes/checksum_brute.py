"""Checksum Brute Probe: Detect and exploit fixed-offset checksum validation."""

import logging
from typing import List, Optional
import requests
import re

from .base import Probe, ProbeAttempt, Finding, Severity

logger = logging.getLogger(__name__)


class ChecksumBruteProbe(Probe):
    """Detect and exploit fixed-offset checksum validation."""

    name = "ChecksumBruteProbe"
    description = "Detect fixed-offset validation and attempt alignment attacks"
    bom = ["requests"]

    def execute(self, target_url: str, **kwargs) -> ProbeAttempt:
        """Execute checksum brute probe against target."""
        attempt = ProbeAttempt(target_url=target_url)

        # Find endpoints that accept user input
        checksum_endpoints = self._find_input_endpoints(target_url)
        if not checksum_endpoints:
            logger.info(f"No input endpoints found for {target_url}")
            return attempt

        findings = []

        for endpoint in checksum_endpoints:
            # Test 1: Detect fixed-offset validation pattern
            is_fixed_offset = self._test_fixed_offset_pattern(endpoint)

            if is_fixed_offset:
                logger.debug(f"Fixed-offset validation detected at {endpoint}")

                # Test 2: Generate and test alignment payloads
                payloads = self._generate_alignment_payloads()

                for payload in payloads:
                    try:
                        r = requests.get(f"{endpoint}", params={"input": payload}, timeout=5)

                        if r.status_code == 200 and self._has_xss_signal(r.text):
                            findings.append(Finding(
                                title="Checksum alignment bypass with XSS potential",
                                description=f"Fixed-offset checksum validation bypassed via payload alignment",
                                severity=Severity.HIGH,
                                endpoint=endpoint,
                                category="checksum_alignment_bypass",
                                evidence={
                                    "endpoint": endpoint,
                                    "payload": payload[:100],
                                    "xss_signal_found": True
                                }
                            ))
                            break
                    except Exception as e:
                        logger.debug(f"Error testing payload: {e}")

        if findings:
            attempt.metrics["vulnerable"] = True
            attempt.findings = self._sort_findings(findings)
            attempt.metrics["findings_count"] = len(findings)

        return attempt

    def _find_input_endpoints(self, base_url: str) -> List[str]:
        """Find endpoints that accept input parameters."""
        endpoints = []
        patterns = [
            "/search",
            "/api/search",
            "/query",
            "/api/query",
            "/validate",
            "/api/validate",
            "/check",
            "/process",
        ]

        for pattern in patterns:
            url = base_url.rstrip("/") + pattern
            try:
                r = requests.head(url, timeout=3)
                if r.status_code < 500:
                    endpoints.append(url)
            except Exception:
                pass

        return endpoints

    def _test_fixed_offset_pattern(self, endpoint: str) -> bool:
        """Test if validation keys on fixed character positions."""
        base = "A" * 100

        try:
            r_base = requests.get(endpoint, params={"input": base}, timeout=5)
            base_status = r_base.status_code
            base_response = r_base.text
        except Exception:
            return False

        # Modify character at position 10
        modified_pos10 = base[:10] + "X" + base[11:]

        try:
            r_mod = requests.get(endpoint, params={"input": modified_pos10}, timeout=5)
            mod_status = r_mod.status_code
            mod_response = r_mod.text
        except Exception:
            return False

        # If modifying position 10 consistently changes validation, likely fixed-offset
        return (base_status == 200 and mod_status >= 400) or (base_response != mod_response and len(base_response) != len(mod_response))

    def _generate_alignment_payloads(self) -> List[str]:
        """Generate payloads aligned for fixed-offset validation."""
        payloads = []

        # Strategy: place key characters at common offset positions
        for offset in [10, 20, 30, 50, 90]:
            payload = ["A"] * 100
            payload[offset] = "W"
            payload[offset + 5] = "P"
            payload[offset + 10] = "M"
            payloads.append("".join(payload))

        # Code-golf style: short domain + payload
        short_payloads = [
            "A" * 10 + "x.co" + "A" * 85,
            "A" * 20 + "z.io" + "A" * 75,
            "A" * 30 + "t.me" + "A" * 65,
        ]
        payloads.extend(short_payloads)

        return payloads

    def _has_xss_signal(self, response_text: str) -> bool:
        """Check for XSS signal in response."""
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"alert\(",
            r"eval\(",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True

        return False
