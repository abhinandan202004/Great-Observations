"""Runbooks: the six required fields, the root-cause taxonomy, and the closure gate."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RootCause(StrEnum):
    """The controlled taxonomy (context.md section 7): clean labels for later training."""

    CODE_OR_DEPLOY = "code_or_deploy"
    CONFIGURATION = "configuration"
    CAPACITY_OR_INFRASTRUCTURE = "capacity_or_infrastructure"
    DEPENDENCY_OR_THIRD_PARTY = "dependency_or_third_party"
    DATA = "data"
    SECURITY = "security"
    PROCESS_OR_HUMAN = "process_or_human"


@dataclass(frozen=True)
class Runbook:
    timeline: str
    root_cause: str
    contributing_factors: str
    remediation: str
    workaround: str
    similar_incidents: Sequence[str]  # earlier incidents this one resembles
    none_similar: str  # what was searched, when no similar incident was found


def missing(runbook: Runbook) -> list[str]:
    """The required fields left empty; whitespace alone counts as empty."""
    gaps = [
        name
        for name in ("timeline", "root_cause", "contributing_factors", "remediation", "workaround")
        if not getattr(runbook, name).strip()
    ]
    # Similar incidents is answered by naming some, or by saying none were found.
    if not runbook.similar_incidents and not runbook.none_similar.strip():
        gaps.append("similar_incidents")
    return gaps


def may_close(last_resolved_at: datetime | None, approved_versions: Sequence[datetime]) -> bool:
    """True if a runbook version written since the latest resolution has been approved.

    ``approved_versions`` are the creation times of approved versions. A reopen followed by a
    new resolution therefore needs a fresh, approved runbook before the caller can close.
    """
    if last_resolved_at is None:
        return False
    return any(written > last_resolved_at for written in approved_versions)
