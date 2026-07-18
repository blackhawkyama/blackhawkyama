import json
import logging
from typing import List
from datetime import datetime
from .schemas import ProgramScore, DailyDigest

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate digests and reports in JSON/Markdown."""

    @staticmethod
    def generate_markdown_digest(digest: DailyDigest) -> str:
        """Generate markdown digest for email/GitHub."""
        lines = []

        lines.append("# 🐺 BountyScout Digest")
        lines.append(f"\n**Generated:** {digest.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append(f"**Period:** {digest.period.title()}")
        lines.append(f"**Programs Scanned:** {digest.total_programs_scanned}")
        lines.append(f"**New This Period:** {digest.new_programs}")

        lines.append("\n---\n")
        lines.append("## Top Targets for You\n")

        if not digest.top_programs:
            lines.append("No programs found matching your filters.\n")
        else:
            for idx, score in enumerate(digest.top_programs, 1):
                p = score.program
                lines.append(f"### {idx}. {p.name}")
                lines.append(f"**Platform:** {p.platform.value.title()}")
                lines.append(f"**Score:** {score.weighted_score:.0f} | Skill Match: {score.skill_match:.0f}% | Saturation: {score.saturation:.0f}%")
                lines.append(f"**Bounty:** ${score.program.avg_bounty or 'TBD':,}")
                lines.append(f"**Link:** [Open Program]({p.url})")
                lines.append(f"**Recommendation:** {score.recommendation}")

                if p.scope_count:
                    lines.append(f"**Scope:** {p.scope_count} targets")
                if p.requires_nda:
                    lines.append("⚠️ **Requires NDA**")

                lines.append("")

        lines.append("---\n")
        lines.append("## Summary\n")
        lines.append(digest.summary)
        lines.append("\n")
        lines.append("**Next Steps:**")
        lines.append("1. Review top programs above")
        lines.append("2. Check current scope and in-scope techs")
        lines.append("3. Update your BountyScout skills if you find a gap")
        lines.append("4. Start with #1 if skill match > 80%")

        return "\n".join(lines)

    @staticmethod
    def generate_json_digest(digest: DailyDigest) -> str:
        """Generate JSON digest for programmatic use."""
        data = {
            "generated_at": digest.generated_at.isoformat(),
            "period": digest.period,
            "total_programs_scanned": digest.total_programs_scanned,
            "new_programs": digest.new_programs,
            "summary": digest.summary,
            "top_programs": [
                {
                    "rank": score.priority,
                    "name": score.program.name,
                    "platform": score.program.platform.value,
                    "url": score.program.url,
                    "score": score.weighted_score,
                    "skill_match": score.skill_match,
                    "saturation": score.saturation,
                    "avg_bounty": score.program.avg_bounty,
                    "recommendation": score.recommendation,
                }
                for score in digest.top_programs
            ]
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def create_digest(
        scored_programs: List[ProgramScore],
        period: str = "daily",
        top_n: int = 5,
        min_skill_match: float = 0.5,
        max_saturation: float = 0.8
    ) -> DailyDigest:
        """
        Create a digest from scored programs.
        Filters: min skill match, max saturation, rank top N.
        """
        # Filter by criteria
        filtered = [
            s for s in scored_programs
            if s.skill_match >= (min_skill_match * 100) and s.saturation <= (max_saturation * 100)
        ]

        # Get top N
        top = filtered[:top_n]

        # Count new programs (launched in last 7 days)
        now = datetime.utcnow()
        new_count = sum(
            1 for s in filtered
            if s.program.launched_date and (now - s.program.launched_date).days <= 7
        )

        # Generate summary
        if top:
            avg_score = sum(s.weighted_score for s in top) / len(top)
            summary = (
                f"Found {len(filtered)} qualified programs this {period}. "
                f"Top {len(top)} averaging {avg_score:.0f} points. "
                f"{new_count} launched in the last 7 days. "
                f"Skill match and saturation filtered for high-ROI targets."
            )
        else:
            summary = f"No programs found matching your criteria this {period}. Broaden filters or wait for new launches."

        return DailyDigest(
            period=period,
            top_programs=top,
            summary=summary,
            total_programs_scanned=len(scored_programs),
            new_programs=new_count,
        )
