from itertools import product

import pytest

from infrawatch_core.lifecycle import Move, Status, TransitionError, classify

S = Status
# Every transition context.md section 5 lists; anything else must be refused.
LISTED = {
    (S.RAISED, S.ACKNOWLEDGED): Move.FORWARD,
    (S.ACKNOWLEDGED, S.INVESTIGATING): Move.FORWARD,
    (S.INVESTIGATING, S.MITIGATING): Move.FORWARD,
    (S.MITIGATING, S.MONITORING): Move.FORWARD,
    (S.MONITORING, S.RESOLVED): Move.FORWARD,
    (S.ACKNOWLEDGED, S.RAISED): Move.REGRESSION,
    (S.INVESTIGATING, S.RAISED): Move.REGRESSION,
    (S.INVESTIGATING, S.ACKNOWLEDGED): Move.REGRESSION,
    (S.MITIGATING, S.RAISED): Move.REGRESSION,
    (S.MITIGATING, S.ACKNOWLEDGED): Move.REGRESSION,
    (S.MITIGATING, S.INVESTIGATING): Move.REGRESSION,
    (S.MONITORING, S.RAISED): Move.REGRESSION,
    (S.MONITORING, S.ACKNOWLEDGED): Move.REGRESSION,
    (S.MONITORING, S.INVESTIGATING): Move.REGRESSION,
    (S.MONITORING, S.MITIGATING): Move.REGRESSION,
    (S.RESOLVED, S.INVESTIGATING): Move.REOPEN,
    (S.RESOLVED, S.CLOSED): Move.CLOSE,
}


@pytest.mark.parametrize(("current", "target"), list(product(Status, Status)))
def test_every_pair_matches_the_lifecycle_table(current: Status, target: Status) -> None:
    expected = LISTED.get((current, target))
    if expected is None:
        with pytest.raises(TransitionError):
            classify(current, target)
    else:
        assert classify(current, target) is expected


def test_closed_is_terminal() -> None:
    assert not [target for (current, target) in LISTED if current is S.CLOSED]
