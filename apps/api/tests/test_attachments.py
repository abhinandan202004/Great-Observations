import pytest

from infrawatch_api.attachments import _safe_name


@pytest.mark.parametrize(
    ("given", "kept"),
    [
        ("report.pdf", "report.pdf"),
        ("../../etc/passwd", "passwd"),
        (r"C:\Users\me\shot.png", "shot.png"),
        ("evil\r\nSet-Cookie: x=1.txt", "evilSet-Cookie: x=1.txt"),  # no header injection
        ("café menu.txt", "café menu.txt"),
        ("/", "file"),
    ],
)
def test_only_a_clean_base_name_is_kept(given: str, kept: str) -> None:
    assert _safe_name(given) == kept
