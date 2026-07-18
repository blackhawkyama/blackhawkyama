from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Platform(str, Enum):
    HACKERONE = "hackerone"
    BUGCROWD = "bugcrowd"
    IMMUNEFI = "immunefi"


class BountyProgram(BaseModel):
    """Represents a bug bounty program."""
    id: str = Field(..., description="Unique program ID")
    name: str = Field(..., description="Program name")
    platform: Platform
    url: str = Field(..., description="Link to program")
    min_bounty: Optional[int] = Field(None, description="Minimum bounty in USD")
    max_bounty: Optional[int] = Field(None, description="Maximum bounty in USD")
    avg_bounty: Optional[int] = Field(None, description="Average bounty estimate")
    scope_count: Optional[int] = Field(None, description="Number of in-scope targets")
    active_hunters: Optional[int] = Field(None, description="Approximate active hunters")
    vulnerability_types: List[str] = Field(default_factory=list, description="Accepted vuln types")
    requires_nda: bool = Field(default=False)
    launched_date: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    description: str = Field(default="")


class ScoringFactors(BaseModel):
    """Scoring inputs for a program."""
    program: BountyProgram
    user_skill_match: float = Field(..., ge=0, le=1, description="0-1 match to user skills (OWASP Top 10, web app, API)")
    saturation_factor: float = Field(..., ge=0, le=1, description="0-1 saturation (1=saturated, 0=new)")
    target_interest: float = Field(default=0.5, ge=0, le=1, description="0-1 interest in target type")


class ProgramScore(BaseModel):
    """Scored bounty program with recommendation."""
    program: BountyProgram
    raw_score: float = Field(..., description="(avg_bounty × skill_match) / (1 + saturation)")
    weighted_score: float = Field(..., description="Final score for ranking")
    skill_match: float = Field(description="Skill match percentage")
    saturation: float = Field(description="Saturation level (0-1)")
    recommendation: str = Field(description="Brief recommendation or caution")
    priority: int = Field(default=0, description="Rank priority (1=top)")


class DailyDigest(BaseModel):
    """Daily/weekly digest of top programs."""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    period: str = Field(description="'daily' or 'weekly'")
    top_programs: List[ProgramScore] = Field(description="Top N programs by score")
    summary: str = Field(description="Brief summary of findings")
    total_programs_scanned: int = Field(description="Total programs analyzed")
    new_programs: int = Field(description="New programs this period")
