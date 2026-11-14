import json

import pytest

from infrawatch_worker import __version__
from infrawatch_worker.__main__ import main


def test_main_emits_structured_record(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    record = json.loads(capsys.readouterr().out)
    assert record["service"] == "worker"
    assert record["version"] == __version__
