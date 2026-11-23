import pytest

from infrawatch_core.files import sniff


@pytest.mark.parametrize(
    ("name", "data", "expected"),
    [
        ("shot.png", b"\x89PNG\r\n\x1a\n rest", "image/png"),
        ("photo.jpg", b"\xff\xd8\xff\xe0 rest", "image/jpeg"),
        ("anim.gif", b"GIF89a rest", "image/gif"),
        ("pic.webp", b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/webp"),
        ("report.pdf", b"%PDF-1.7 rest", "application/pdf"),
        ("app.log", b"2026-11-24 ERROR checkout failed\n", "text/plain; charset=utf-8"),
        ("notes.TXT", "café\n".encode(), "text/plain; charset=utf-8"),
    ],
)
def test_allowed_files_are_recognised_by_their_bytes(name: str, data: bytes, expected: str) -> None:
    assert sniff(name, data) == expected


@pytest.mark.parametrize(
    ("name", "data"),
    [
        ("page.html", b"<!doctype html><script>alert(1)</script>"),  # text, but not a text name
        ("logo.svg", b"<svg xmlns='http://www.w3.org/2000/svg'/>"),
        ("fake.png", b"<script>alert(1)</script>"),  # the name says image, the bytes do not
        ("tool.exe", b"MZ\x90\x00"),
        ("archive.log", b"PK\x03\x04\x00\x00"),  # binary with a text name
        ("bad.txt", b"\xff\xfe not utf-8"),
        ("empty.txt", b""),
    ],
)
def test_everything_else_is_refused(name: str, data: bytes) -> None:
    assert sniff(name, data) is None
