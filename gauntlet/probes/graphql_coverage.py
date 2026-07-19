"""GraphQL Coverage Probe: Test every query/mutation with different auth levels."""

import logging
from typing import Dict, List, Optional, Any
import requests
import json
import re

from .base import Probe, ProbeAttempt, Finding, Severity

logger = logging.getLogger(__name__)


class GraphQLCoverageProbe(Probe):
    """Comprehensive GraphQL attack surface mapper."""

    name = "GraphQLCoverageProbe"
    description = "Introspect GraphQL endpoint and test each operation with different auth levels"
    bom = ["requests"]

    def execute(self, target_url: str, bearer_token: Optional[str] = None, **kwargs) -> ProbeAttempt:
        """Execute GraphQL coverage against target."""
        attempt = ProbeAttempt(target_url=target_url, bearer_token=bearer_token)

        # Find GraphQL endpoint
        graphql_endpoint = self._find_graphql_endpoint(target_url)
        if not graphql_endpoint:
            logger.info(f"No GraphQL endpoint found for {target_url}")
            return attempt

        # Introspect schema
        introspection = self._introspect(graphql_endpoint)
        if not introspection or "data" not in introspection:
            logger.info(f"GraphQL introspection failed for {graphql_endpoint}")
            return attempt

        operations = self._extract_operations(introspection)
        if not operations:
            logger.info("No operations found in introspection")
            return attempt

        findings = []

        # Test each operation
        for op_name, op_info in operations.items():
            op_type = op_info.get("type", "query")

            # Test with different auth levels
            r_noauth = self._test_operation(graphql_endpoint, op_name, op_type, auth=None)
            r_auth = self._test_operation(graphql_endpoint, op_name, op_type, auth=bearer_token) if bearer_token else None

            # Analyze responses
            if r_noauth and r_noauth.status_code == 200 and "data" in (r_noauth.json() or {}):
                findings.append(Finding(
                    title=f"Unauthenticated {op_type}: {op_name}",
                    description=f"GraphQL {op_type} '{op_name}' accessible without authentication",
                    severity=Severity.HIGH,
                    category="graphql_unauthenticated",
                    evidence={"operation": op_name, "type": op_type}
                ))
            elif r_noauth and r_noauth.status_code == 403 and r_auth and r_auth.status_code == 200:
                findings.append(Finding(
                    title=f"Middleware bypass on {op_type}: {op_name}",
                    description=f"Middleware auth blocks unauthenticated access but authenticated user can access",
                    severity=Severity.MEDIUM,
                    category="graphql_middleware_bypass",
                    evidence={"operation": op_name, "type": op_type}
                ))
            elif r_noauth and r_noauth.status_code == 401:
                if r_auth and r_auth.status_code == 403:
                    findings.append(Finding(
                        title=f"Deeper auth gap in {op_type}: {op_name}",
                        description=f"Middleware auth required but object-level auth fails",
                        severity=Severity.MEDIUM,
                        category="graphql_deeper_auth_gap",
                        evidence={"operation": op_name, "type": op_type}
                    ))

        if findings:
            attempt.metrics["vulnerable"] = True
            attempt.findings = self._sort_findings(findings)
            attempt.metrics["findings_count"] = len(findings)

        return attempt

    def _find_graphql_endpoint(self, base_url: str) -> Optional[str]:
        """Find GraphQL endpoint by testing common paths."""
        candidates = [
            "/graphql",
            "/api/graphql",
            "/v1/graphql",
            "/gql",
            "/api/gql",
        ]

        for path in candidates:
            url = base_url.rstrip("/") + path
            try:
                r = requests.post(url, json={"query": "{__typename}"}, timeout=3)
                if r.status_code < 500:
                    return url
            except Exception:
                pass

        return None

    def _introspect(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Run introspection query."""
        query = """
        {
          __schema {
            types {
              name
              kind
              fields {
                name
              }
            }
            queryType { name }
            mutationType { name }
          }
        }
        """
        try:
            response = requests.post(endpoint, json={"query": query}, timeout=5)
            return response.json()
        except Exception as e:
            logger.debug(f"Introspection error: {e}")
            return None

    def _extract_operations(self, introspection: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Extract query and mutation names from introspection."""
        operations = {}
        data = introspection.get("data", {})
        schema = data.get("__schema", {})

        # Query operations
        query_type = schema.get("queryType", {})
        if query_type and query_type.get("name"):
            for type_info in schema.get("types", []):
                if type_info.get("name") == query_type.get("name"):
                    for field in type_info.get("fields", []):
                        operations[field["name"]] = {"type": "query"}

        # Mutation operations
        mutation_type = schema.get("mutationType", {})
        if mutation_type and mutation_type.get("name"):
            for type_info in schema.get("types", []):
                if type_info.get("name") == mutation_type.get("name"):
                    for field in type_info.get("fields", []):
                        operations[field["name"]] = {"type": "mutation"}

        return operations

    def _test_operation(self, endpoint: str, op_name: str, op_type: str, auth: Optional[str] = None) -> Optional[requests.Response]:
        """Test a single operation."""
        query = f"{{ {op_name} {{ __typename }} }}"
        headers = {}
        if auth:
            headers["Authorization"] = f"Bearer {auth}"

        try:
            return requests.post(endpoint, json={"query": query}, headers=headers, timeout=5)
        except Exception as e:
            logger.debug(f"Error testing {op_name}: {e}")
            return None
