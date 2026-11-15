from infrawatch_api.seed import SERVICES, TEAMS, USERS
from infrawatch_core.roles import Role


def test_every_role_has_exactly_one_demo_user() -> None:
    assert sorted(u.role for u in USERS) == sorted(Role)


def test_every_team_has_a_lead() -> None:
    assert {u.team for u in USERS if u.is_lead} == set(TEAMS)


def test_users_and_services_reference_known_teams() -> None:
    assert {u.team for u in USERS if u.team} <= set(TEAMS)
    assert {s.team for s in SERVICES} <= set(TEAMS)
