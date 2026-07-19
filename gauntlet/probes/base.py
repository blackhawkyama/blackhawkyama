"""Base Probe class for security testing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class Severity(str, Enum):
    """Finding severity levels."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Finding:
    """Security finding from a probe."""
    title: str
    description: str
    severity: Severity
    endpoint: Optional[str] = None
    category: Optional[str] = None
    remediation: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


@dataclass
class ProbeAttempt:
    """Probe execution attempt context."""
    target_url: str
    endpoints: Optional[List[str]] = None
    bearer_token: Optional[str] = None
    user_token: Optional[str] = None
    guest_token: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    findings: List[Finding] = field(default_factory=list)


class Probe(ABC):
    """Base class for security probes."""

    name: str = "BaseProbe"
    description: str = "Base probe class"
    bom: List[str] = []  # Bill of Materials (dependencies)

    @abstractmethod
    def execute(self, target_url: str, **kwargs) -> ProbeAttempt:
        """Execute probe against target. Override in subclasses."""
        pass

    def _severity_to_rank(self, severity: Severity) -> int:
        """Convert severity to numeric rank for sorting."""
        ranks = {
            Severity.INFO: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }
        return ranks.get(severity, 0)

    def _sort_findings(self, findings: List[Finding]) -> List[Finding]:
        """Sort findings by severity (descending)."""
        return sorted(findings, key=lambda f: self._severity_to_rank(f.severity), reverse=True)
