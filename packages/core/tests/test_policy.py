from infrawatch_core.policy import Capability, Scope, allows, scopes
from infrawatch_core.roles import Role


def test_viewer_sees_telemetry_and_status_but_not_incident_detail_or_logs() -> None:
    assert allows([Role.VIEWER], Capability.VIEW_TELEMETRY)
    assert allows([Role.VIEWER], Capability.VIEW_INCIDENT_STATUS)
    assert not allows([Role.VIEWER], Capability.VIEW_INCIDENT_DETAIL)


def test_stakeholder_sees_only_incident_status() -> None:
    assert allows([Role.STAKEHOLDER], Capability.VIEW_INCIDENT_STATUS)
    assert not allows([Role.STAKEHOLDER], Capability.VIEW_TELEMETRY)


def test_only_production_support_raises_incidents() -> None:
    raisers = [role for role in Role if allows([role], Capability.RAISE_INCIDENT)]

    assert raisers == [Role.PRODUCTION_SUPPORT]


def test_only_admin_manages_users_teams_and_rules() -> None:
    managers = [role for role in Role if allows([role], Capability.MANAGE_USERS_TEAMS_RULES)]

    assert managers == [Role.ADMIN]


def test_closing_is_caller_only_for_every_role() -> None:
    assert all(scopes([role], Capability.CLOSE_INCIDENT) == {Scope.CALLER} for role in Role)


def test_team_scope_is_recorded_for_developers() -> None:
    assert scopes([Role.DEVELOPER], Capability.UPDATE_STATUS) == {Scope.OWN_TEAM}


def test_roles_combine_their_scopes() -> None:
    assert scopes([Role.DEVELOPER, Role.INCIDENT_COMMANDER], Capability.UPDATE_STATUS) == {
        Scope.OWN_TEAM,
        Scope.ANY,
    }


def test_no_roles_means_no_capability() -> None:
    assert not allows([], Capability.VIEW_TELEMETRY)
