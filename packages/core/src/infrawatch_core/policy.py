"""Permission matrix from context.md section 4, as pure functions.

Each role grants a capability in one scope. ``allows`` asks whether a role holds a capability
at all; ``permits`` asks whether it holds it for one incident, given how the user relates to it.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from infrawatch_core.roles import Role


class Capability(StrEnum):
    VIEW_TELEMETRY = "view_telemetry"
    VIEW_INCIDENT_STATUS = "view_incident_status"
    VIEW_INCIDENT_DETAIL = "view_incident_detail"
    RAISE_INCIDENT = "raise_incident"
    CHANGE_SEVERITY = "change_severity"
    UPDATE_STATUS = "update_status"
    ASSIGN = "assign"
    WRITE_RUNBOOK = "write_runbook"
    APPROVE_RUNBOOK = "approve_runbook"
    CLOSE_INCIDENT = "close_incident"
    MANAGE_ONCALL = "manage_oncall"
    DRAFT_COMMS = "draft_comms"
    APPROVE_COMMS = "approve_comms"
    GIVE_AI_FEEDBACK = "give_ai_feedback"
    MANAGE_USERS_TEAMS_RULES = "manage_users_teams_rules"


class Scope(StrEnum):
    ANY = "any"
    OWN_TEAM = "own_team"
    OWN_INCIDENTS = "own_incidents"
    LEAD = "lead"  # team lead of the incident's team (a membership attribute)
    RESOLVER = "resolver"  # an engineer on a team working the incident (writes its runbook)
    CALLER = "caller"  # the incident's caller, as the spec defines it


_ANY = Scope.ANY
_CLOSE = {role: Scope.CALLER for role in Role}  # "caller only, regardless of role"

_GRANTS: dict[Role, dict[Capability, Scope]] = {
    Role.PRODUCTION_SUPPORT: {
        Capability.VIEW_TELEMETRY: _ANY,
        Capability.VIEW_INCIDENT_STATUS: _ANY,
        Capability.VIEW_INCIDENT_DETAIL: _ANY,
        Capability.RAISE_INCIDENT: _ANY,
        Capability.CHANGE_SEVERITY: _ANY,
        Capability.UPDATE_STATUS: Scope.OWN_INCIDENTS,
        Capability.ASSIGN: Scope.LEAD,
        Capability.GIVE_AI_FEEDBACK: _ANY,
    },
    Role.DEVELOPER: {
        Capability.VIEW_TELEMETRY: _ANY,
        Capability.VIEW_INCIDENT_STATUS: _ANY,
        Capability.VIEW_INCIDENT_DETAIL: _ANY,
        Capability.UPDATE_STATUS: Scope.OWN_TEAM,
        Capability.ASSIGN: Scope.LEAD,
        Capability.WRITE_RUNBOOK: Scope.RESOLVER,
        Capability.APPROVE_RUNBOOK: Scope.LEAD,
        Capability.MANAGE_ONCALL: Scope.OWN_TEAM,
        Capability.GIVE_AI_FEEDBACK: _ANY,
    },
    Role.SRE: {
        Capability.VIEW_TELEMETRY: _ANY,
        Capability.VIEW_INCIDENT_STATUS: _ANY,
        Capability.VIEW_INCIDENT_DETAIL: _ANY,
        Capability.CHANGE_SEVERITY: _ANY,
        Capability.UPDATE_STATUS: Scope.OWN_TEAM,
        Capability.ASSIGN: Scope.LEAD,
        Capability.WRITE_RUNBOOK: Scope.RESOLVER,
        Capability.APPROVE_RUNBOOK: Scope.LEAD,
        Capability.MANAGE_ONCALL: Scope.OWN_TEAM,
        Capability.GIVE_AI_FEEDBACK: _ANY,
    },
    Role.ADMIN: {
        Capability.VIEW_TELEMETRY: _ANY,
        Capability.VIEW_INCIDENT_STATUS: _ANY,
        Capability.VIEW_INCIDENT_DETAIL: _ANY,
        Capability.MANAGE_ONCALL: _ANY,
        Capability.MANAGE_USERS_TEAMS_RULES: _ANY,
    },
    Role.INCIDENT_COMMANDER: {
        Capability.VIEW_TELEMETRY: _ANY,
        Capability.VIEW_INCIDENT_STATUS: _ANY,
        Capability.VIEW_INCIDENT_DETAIL: _ANY,
        Capability.CHANGE_SEVERITY: _ANY,
        Capability.UPDATE_STATUS: _ANY,
        Capability.ASSIGN: _ANY,
        Capability.APPROVE_RUNBOOK: _ANY,
        Capability.APPROVE_COMMS: _ANY,
        Capability.GIVE_AI_FEEDBACK: _ANY,
    },
    Role.COMMS: {
        Capability.VIEW_TELEMETRY: _ANY,
        Capability.VIEW_INCIDENT_STATUS: _ANY,
        Capability.VIEW_INCIDENT_DETAIL: _ANY,
        Capability.DRAFT_COMMS: _ANY,
        Capability.GIVE_AI_FEEDBACK: _ANY,
    },
    Role.VIEWER: {
        Capability.VIEW_TELEMETRY: _ANY,
        Capability.VIEW_INCIDENT_STATUS: _ANY,
    },
    Role.STAKEHOLDER: {
        Capability.VIEW_INCIDENT_STATUS: _ANY,
    },
}
for _role, _close in _CLOSE.items():
    _GRANTS[_role][Capability.CLOSE_INCIDENT] = _close


def scopes(roles: Iterable[Role], capability: Capability) -> frozenset[Scope]:
    """Every scope in which any of the roles holds the capability (empty if none)."""
    return frozenset(_GRANTS[role][capability] for role in roles if capability in _GRANTS[role])


def allows(roles: Iterable[Role], capability: Capability) -> bool:
    """True if any of the roles holds the capability in some scope."""
    return bool(scopes(roles, capability))


@dataclass(frozen=True)
class Relation:
    """How one user relates to one incident."""

    caller: bool = False  # raised it
    team_member: bool = False  # belongs to a team with a task on it
    lead: bool = False  # leads a team with a task on it
    resolver: bool = False  # moved it to Resolved


def permits(roles: Iterable[Role], capability: Capability, relation: Relation) -> bool:
    """True if any of the roles holds the capability in a scope this relation satisfies."""
    held = {
        Scope.ANY: True,
        Scope.OWN_TEAM: relation.team_member,
        Scope.OWN_INCIDENTS: relation.caller,
        Scope.LEAD: relation.lead,
        Scope.RESOLVER: relation.resolver,
        Scope.CALLER: relation.caller,
    }
    return any(held[scope] for scope in scopes(roles, capability))
