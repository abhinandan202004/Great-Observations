import json

import pytest

from infrawatch_demo_app import __version__
from infrawatch_demo_app.__main__ import main


def test_main_emits_structured_record(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    record = json.loads(capsys.readouterr().out)
    assert record["service"] == "demo-app"
    assert record["version"] == __version__
