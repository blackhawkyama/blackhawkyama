"""Example: Using Gauntlet probes."""

from gauntlet import PROBES

# Example 1: Run all probes against a target
def scan_target(target_url: str, bearer_token: str = None):
    """Run all probes against target."""
    print(f"Scanning {target_url}...")

    for probe_class in PROBES:
        probe = probe_class()
        print(f"\n[*] Running {probe.name}...")

        try:
            attempt = probe.execute(target_url, bearer_token=bearer_token)

            if attempt.findings:
                print(f"    Found {len(attempt.findings)} findings:")
                for finding in attempt.findings:
                    print(f"      - [{finding.severity}] {finding.title}")
                    print(f"        {finding.description}")
            else:
                print(f"    No findings")

        except Exception as e:
            print(f"    Error: {e}")


# Example 2: Run individual probe
def run_cookie_auditor(target_url: str):
    """Example: Run CookieAuditorProbe."""
    from gauntlet import CookieAuditorProbe

    probe = CookieAuditorProbe()
    attempt = probe.execute(target_url)

    if attempt.findings:
        for finding in attempt.findings:
            print(f"[{finding.severity}] {finding.title}")
            print(f"  {finding.description}")
            if finding.endpoint:
                print(f"  Endpoint: {finding.endpoint}")
    else:
        print("No cookie issues found")


# Example 3: Run GraphQL probe with auth
def run_graphql_probe(target_url: str, bearer_token: str):
    """Example: Run GraphQLCoverageProbe with authentication."""
    from gauntlet import GraphQLCoverageProbe

    probe = GraphQLCoverageProbe()
    attempt = probe.execute(target_url, bearer_token=bearer_token)

    print(f"Tested GraphQL operations: {attempt.metrics.get('findings_count', 0)} issues found")


if __name__ == "__main__":
    # Example usage
    target = "https://example.com"
    token = "your-bearer-token-here"

    scan_target(target, bearer_token=token)
