import logging
from typing import List, Optional, Dict
from .scraper import BountyPlatformScraper
from .scoring import ProgramScorer
from .report import ReportGenerator
from .schemas import BountyProgram, ProgramScore, DailyDigest

logger = logging.getLogger(__name__)


class BountyScout:
    """Main orchestrator for autonomous bug bounty program discovery."""

    def __init__(
        self,
        h1_api_key: Optional[str] = None,
        bc_api_key: Optional[str] = None,
        user_skills: Optional[Dict[str, float]] = None,
    ):
        self.scraper = BountyPlatformScraper(h1_api_key, bc_api_key)
        self.scorer = ProgramScorer(user_skills)
        self.reporter = ReportGenerator()

    def scan_all_platforms(self) -> List[BountyProgram]:
        """Fetch programs from all platforms."""
        logger.info("Starting platform scan...")
        programs = self.scraper.fetch_all_programs()
        logger.info(f"Scan complete: {len(programs)} programs fetched")
        return programs

    def score_programs(self, programs: List[BountyProgram]) -> List[ProgramScore]:
        """Score all programs."""
        logger.info(f"Scoring {len(programs)} programs...")
        scored = self.scorer.score_all(programs)
        logger.info(f"Scoring complete: {len(scored)} programs ranked")
        return scored

    def generate_digest(
        self,
        scored_programs: List[ProgramScore],
        period: str = "daily",
        top_n: int = 5,
        min_skill_match: float = 0.5,
        max_saturation: float = 0.8,
    ) -> DailyDigest:
        """Generate digest from scored programs."""
        digest = self.reporter.create_digest(
            scored_programs,
            period=period,
            top_n=top_n,
            min_skill_match=min_skill_match,
            max_saturation=max_saturation,
        )
        return digest

    def run_full_scan(
        self,
        period: str = "daily",
        top_n: int = 5,
        output_format: str = "markdown",  # or 'json'
    ) -> str:
        """
        Run full scan: fetch → score → generate report.
        Returns formatted output (markdown or JSON).
        """
        logger.info("=== BountyScout Full Scan ===")

        # Fetch
        programs = self.scan_all_platforms()
        if not programs:
            logger.warning("No programs found. Check API keys and network.")
            return "Error: No programs found."

        # Score
        scored = self.score_programs(programs)

        # Digest
        digest = self.generate_digest(scored, period=period, top_n=top_n)

        # Format output
        if output_format == "json":
            output = self.reporter.generate_json_digest(digest)
        else:
            output = self.reporter.generate_markdown_digest(digest)

        logger.info("Scan complete. Digest ready.")
        return output

    def top_programs(self, count: int = 5) -> List[ProgramScore]:
        """Quick fetch of top programs (no full scan, cached if available)."""
        programs = self.scan_all_platforms()
        scored = self.score_programs(programs)
        return scored[:count]
