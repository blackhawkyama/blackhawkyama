import logging
from typing import List
from datetime import datetime, timedelta
from .schemas import BountyProgram, ScoringFactors, ProgramScore

logger = logging.getLogger(__name__)


class ProgramScorer:
    """Scores bug bounty programs based on ROI + skill match + saturation."""

    # Your skill tags (can be customized)
    DEFAULT_SKILLS = {
        "web_app": 0.9,           # Excellent (OWASP Top 10, PortSwigger training)
        "api_testing": 0.85,      # Strong (GraphQL, REST, BOLA testing)
        "access_control": 0.9,    # Excellent (IDOR, broken AC, cross-tenant testing)
        "ssrf": 0.8,              # Strong
        "xss": 0.85,              # Strong
        "sqli": 0.85,             # Strong
        "xxe": 0.6,               # Starting (currently learning)
        "deserialization": 0.4,   # Beginner
        "business_logic": 0.5,    # Beginner
        "auth_bypass": 0.6,       # Beginner
    }

    def __init__(self, user_skills: dict = None):
        self.skills = user_skills or self.DEFAULT_SKILLS

    def calculate_skill_match(self, program: BountyProgram) -> float:
        """
        Calculate how well program's vuln types match user's skills (0-1).
        """
        if not program.vulnerability_types:
            # Default to 0.6 if types unknown
            return 0.6

        matches = []
        for vuln_type in program.vulnerability_types:
            normalized = vuln_type.lower().strip()
            for skill_name, skill_level in self.skills.items():
                if skill_name.replace("_", " ") in normalized or normalized in skill_name:
                    matches.append(skill_level)
                    break

        if not matches:
            return 0.5  # Unknown vuln type

        return sum(matches) / len(matches)

    def estimate_saturation(self, program: BountyProgram, historical_data: dict = None) -> float:
        """
        Estimate saturation (0-1) based on:
        - Program age (older = more saturated)
        - Platform (HackerOne > Bugcrowd > Immunefi in saturation)
        - Active hunter count if available
        Returns: 0 = new/unsaturated, 1 = fully saturated
        """
        saturation = 0.5  # Default baseline

        # Age penalty: programs older than 1 year are more saturated
        if program.launched_date:
            age_days = (datetime.utcnow() - program.launched_date).days
            if age_days < 30:
                saturation = 0.2  # Very new
            elif age_days < 90:
                saturation = 0.35  # Recently launched
            elif age_days < 365:
                saturation = 0.6  # Established
            else:
                saturation = 0.8  # Mature, likely saturated

        # Platform saturation adjustment
        platform_saturation = {
            "hackerone": 0.05,     # Add 5% (most saturated)
            "bugcrowd": -0.05,     # Subtract 5%
            "immunefi": -0.1,      # Subtract 10% (less saturated)
        }
        saturation += platform_saturation.get(program.platform.value, 0)

        # Hunter count penalty
        if program.active_hunters and program.active_hunters > 100:
            saturation += 0.15

        return min(max(saturation, 0), 1)  # Clamp 0-1

    def score_program(self, program: BountyProgram) -> ProgramScore:
        """
        Calculate comprehensive score for a program.
        Formula: (avg_bounty × skill_match) / (1 + saturation)
        """
        # Baseline bounty (use avg if available, else midpoint)
        if program.avg_bounty:
            bounty = program.avg_bounty
        elif program.min_bounty and program.max_bounty:
            bounty = (program.min_bounty + program.max_bounty) / 2
        elif program.max_bounty:
            bounty = program.max_bounty * 0.7  # Estimate
        else:
            bounty = 1000  # Conservative default

        skill_match = self.calculate_skill_match(program)
        saturation = self.estimate_saturation(program)

        # Raw score: bounty weighted by skill match, reduced by saturation
        raw_score = (bounty * skill_match) / (1 + saturation)

        # Weighted score: apply additional modifiers
        # Boost for new programs, penalize over-saturated
        weighted_score = raw_score
        if saturation < 0.3:
            weighted_score *= 1.5  # Boost new programs
        if saturation > 0.8:
            weighted_score *= 0.5  # Penalize saturated

        # Generate recommendation
        recommendation = self._generate_recommendation(program, skill_match, saturation, bounty)

        return ProgramScore(
            program=program,
            raw_score=raw_score,
            weighted_score=weighted_score,
            skill_match=skill_match * 100,
            saturation=saturation * 100,
            recommendation=recommendation,
        )

    def _generate_recommendation(self, program: BountyProgram, skill_match: float, saturation: float, bounty: float) -> str:
        """Generate human-readable recommendation."""
        parts = []

        if skill_match > 0.8:
            parts.append("Strong skill match")
        elif skill_match > 0.6:
            parts.append("Decent skill match")
        else:
            parts.append("Learning opportunity")

        if saturation < 0.3:
            parts.append("low saturation")
        elif saturation < 0.6:
            parts.append("moderate saturation")
        else:
            parts.append("HIGH saturation")

        if bounty > 5000:
            parts.append(f"${bounty:,.0f} avg payout")
        elif bounty > 1000:
            parts.append(f"${bounty:,.0f} avg bounty")

        return " · ".join(parts)

    def score_all(self, programs: List[BountyProgram]) -> List[ProgramScore]:
        """Score all programs and return ranked by weighted score."""
        scores = [self.score_program(p) for p in programs]
        scores.sort(key=lambda s: s.weighted_score, reverse=True)

        # Assign priority rankings
        for idx, score in enumerate(scores, 1):
            score.priority = idx

        return scores
