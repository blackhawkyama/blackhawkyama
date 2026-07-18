import requests
import json
import logging
from typing import List, Optional
from datetime import datetime
from .schemas import BountyProgram, Platform

logger = logging.getLogger(__name__)


class BountyPlatformScraper:
    """Scraper for bug bounty platforms."""

    def __init__(self, hackerone_api_key: Optional[str] = None, bugcrowd_api_key: Optional[str] = None):
        self.h1_key = hackerone_api_key
        self.bc_key = bugcrowd_api_key
        self.session = requests.Session()
        self.session.timeout = 10
        self.programs_cache = {}

    def scrape_hackerone(self) -> List[BountyProgram]:
        """Fetch programs from HackerOne API or public listing."""
        programs = []

        # If API key available, use official API
        if self.h1_key:
            return self._scrape_h1_api()

        # Fallback: public scraping (limited data)
        logger.info("HackerOne: Using public fallback (no API key)")
        try:
            url = "https://hackerone.com/bug-bounty-programs?page=1"
            headers = {
                "User-Agent": "Mozilla/5.0 (Authorized Security Testing)",
                "Accept": "application/json"
            }
            resp = self.session.get(url, headers=headers)
            resp.raise_for_status()

            # Parse response for program links
            # This is a simplified scrape; full implementation needs BeautifulSoup
            # For now, return empty to show structure
            logger.warning("HackerOne public scraping requires JS rendering. Use API key for full data.")
        except Exception as e:
            logger.error(f"HackerOne scrape failed: {e}")

        return programs

    def _scrape_h1_api(self) -> List[BountyProgram]:
        """HackerOne GraphQL API with authentication."""
        programs = []

        query = """
        {
          me {
            programs(first: 100, where: { state: "open" }) {
              edges {
                node {
                  id
                  name
                  url
                  bounty {
                    minAmount
                    maxAmount
                    averageAmount
                  }
                  createdAt
                  launchedAt
                }
              }
            }
          }
        }
        """

        headers = {
            "Authorization": f"Bearer {self.h1_key}",
            "Content-Type": "application/json"
        }

        try:
            resp = self.session.post(
                "https://api.hackerone.com/graphql",
                json={"query": query},
                headers=headers
            )
            resp.raise_for_status()
            data = resp.json()

            if "data" in data and "me" in data["data"]:
                for edge in data["data"]["me"]["programs"]["edges"]:
                    node = edge["node"]
                    program = BountyProgram(
                        id=node["id"],
                        name=node["name"],
                        platform=Platform.HACKERONE,
                        url=node["url"],
                        min_bounty=node.get("bounty", {}).get("minAmount"),
                        max_bounty=node.get("bounty", {}).get("maxAmount"),
                        avg_bounty=node.get("bounty", {}).get("averageAmount"),
                        launched_date=node.get("launchedAt"),
                    )
                    programs.append(program)
                logger.info(f"HackerOne: Fetched {len(programs)} programs")
        except Exception as e:
            logger.error(f"HackerOne API failed: {e}")

        return programs

    def scrape_bugcrowd(self) -> List[BountyProgram]:
        """Fetch programs from Bugcrowd."""
        programs = []
        logger.info("Bugcrowd: Fetching programs...")

        try:
            # Bugcrowd public API endpoint
            url = "https://api.bugcrowd.com/programs"
            headers = {
                "User-Agent": "Mozilla/5.0 (Authorized Security Testing)",
                "Accept": "application/json"
            }

            if self.bc_key:
                headers["Authorization"] = f"Token token={self.bc_key}"

            resp = self.session.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for program_data in data.get("programs", []):
                if program_data.get("state") == "active":
                    program = BountyProgram(
                        id=program_data["id"],
                        name=program_data["name"],
                        platform=Platform.BUGCROWD,
                        url=program_data.get("url", ""),
                        max_bounty=program_data.get("bounty_max"),
                        description=program_data.get("description", ""),
                        requires_nda=program_data.get("requires_nda", False),
                    )
                    programs.append(program)

            logger.info(f"Bugcrowd: Fetched {len(programs)} programs")
        except Exception as e:
            logger.error(f"Bugcrowd scrape failed: {e}")

        return programs

    def scrape_immunefi(self) -> List[BountyProgram]:
        """Fetch programs from Immunefi (web3/crypto focused)."""
        programs = []
        logger.info("Immunefi: Fetching programs...")

        try:
            url = "https://api.immunefi.com/programs"
            headers = {
                "User-Agent": "Mozilla/5.0 (Authorized Security Testing)",
                "Accept": "application/json"
            }

            resp = self.session.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for program_data in data.get("programs", []):
                if program_data.get("status") == "active":
                    program = BountyProgram(
                        id=program_data["id"],
                        name=program_data["name"],
                        platform=Platform.IMMUNEFI,
                        url=program_data.get("website", ""),
                        max_bounty=program_data.get("maxBounty"),
                        description=program_data.get("description", ""),
                    )
                    programs.append(program)

            logger.info(f"Immunefi: Fetched {len(programs)} programs")
        except Exception as e:
            logger.error(f"Immunefi scrape failed: {e}")

        return programs

    def fetch_all_programs(self) -> List[BountyProgram]:
        """Fetch from all platforms and combine."""
        all_programs = []

        h1_programs = self.scrape_hackerone()
        bc_programs = self.scrape_bugcrowd()
        immunefi_programs = self.scrape_immunefi()

        all_programs.extend(h1_programs)
        all_programs.extend(bc_programs)
        all_programs.extend(immunefi_programs)

        logger.info(f"Total programs fetched: {len(all_programs)}")
        return all_programs
