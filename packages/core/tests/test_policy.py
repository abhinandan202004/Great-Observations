from infrawatch_core.policy import Capability, Relation, Scope, allows, permits, scopes
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


def test_developer_updates_status_only_on_their_teams_incidents() -> None:
    assert permits([Role.DEVELOPER], Capability.UPDATE_STATUS, Relation(team_member=True))
    assert not permits([Role.DEVELOPER], Capability.UPDATE_STATUS, Relation(caller=True))


def test_production_support_updates_status_only_on_incidents_they_raised() -> None:
    assert permits([Role.PRODUCTION_SUPPORT], Capability.UPDATE_STATUS, Relation(caller=True))
    assert not permits(
        [Role.PRODUCTION_SUPPORT], Capability.UPDATE_STATUS, Relation(team_member=True)
    )


def test_incident_commander_updates_any_incident() -> None:
    assert permits([Role.INCIDENT_COMMANDER], Capability.UPDATE_STATUS, Relation())


def test_only_the_caller_may_close_whatever_their_role() -> None:
    everyone_else = Relation(team_member=True, lead=True, resolver=True)

    assert all(permits([r], Capability.CLOSE_INCIDENT, Relation(caller=True)) for r in Role)
    assert not any(permits([r], Capability.CLOSE_INCIDENT, everyone_else) for r in Role)


def test_assignment_needs_a_lead_unless_incident_commander() -> None:
    assert permits([Role.SRE], Capability.ASSIGN, Relation(lead=True))
    assert not permits([Role.SRE], Capability.ASSIGN, Relation(team_member=True))
    assert permits([Role.INCIDENT_COMMANDER], Capability.ASSIGN, Relation())


def test_runbook_writing_needs_the_resolver() -> None:
    assert permits([Role.DEVELOPER], Capability.WRITE_RUNBOOK, Relation(resolver=True))
    assert not permits([Role.DEVELOPER], Capability.WRITE_RUNBOOK, Relation(team_member=True))
