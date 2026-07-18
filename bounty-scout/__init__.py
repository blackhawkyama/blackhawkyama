"""
BountyScout: Autonomous bug bounty program scanner.
Monitors HackerOne, Bugcrowd, Immunefi. Scores programs. Sends daily digests.
"""

from .bounty_scout import BountyScout
from .schemas import BountyProgram, ProgramScore, DailyDigest, Platform
from .scoring import ProgramScorer
from .scraper import BountyPlatformScraper
from .report import ReportGenerator

__version__ = "0.1.0"
__all__ = [
    "BountyScout",
    "BountyProgram",
    "ProgramScore",
    "DailyDigest",
    "Platform",
    "ProgramScorer",
    "BountyPlatformScraper",
    "ReportGenerator",
]
