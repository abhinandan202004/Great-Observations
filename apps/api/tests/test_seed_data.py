from infrawatch_api.seed import RULES, SERVICES, TEAMS, USERS
from infrawatch_core.roles import Role


def test_every_role_has_a_demo_user() -> None:
    assert {u.role for u in USERS} == set(Role)


def test_each_team_has_someone_besides_its_lead() -> None:
    for team in TEAMS:
        assert len([u for u in USERS if u.team == team]) >= 2


def test_every_team_has_a_lead() -> None:
    assert {u.team for u in USERS if u.is_lead} == set(TEAMS)


def test_users_and_services_reference_known_teams() -> None:
    assert {u.team for u in USERS if u.team} <= set(TEAMS)
    assert {s.team for s in SERVICES} <= set(TEAMS)


def test_alert_rules_reference_known_services() -> None:
    assert {r.service for r in RULES} <= {s.name for s in SERVICES}
