"""The eight user roles. Team lead is a membership attribute, not a role."""

from enum import StrEnum


class Role(StrEnum):
    PRODUCTION_SUPPORT = "production_support"
    DEVELOPER = "developer"
    SRE = "sre"
    ADMIN = "admin"
    INCIDENT_COMMANDER = "incident_commander"
    COMMS = "comms"
    VIEWER = "viewer"
    STAKEHOLDER = "stakeholder"
