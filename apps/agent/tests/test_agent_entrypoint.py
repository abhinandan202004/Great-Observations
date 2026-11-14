import json

import pytest

from infrawatch_agent import __version__
from infrawatch_agent.__main__ import main


def test_main_emits_structured_record(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    record = json.loads(capsys.readouterr().out)
    assert record["service"] == "agent"
    assert record["version"] == __version__
