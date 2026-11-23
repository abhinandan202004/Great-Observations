"""Which uploaded files are accepted, judged by their bytes rather than their declared type."""

MAX_BYTES = 10 * 1024 * 1024
TEXT_SUFFIXES = (".txt", ".log")


def sniff(name: str, data: bytes) -> str | None:
    """The Content-Type to store and serve ``data`` with, or None if it is not allowed.

    Images and PDFs are recognised by their signature. Text needs a .txt or .log name and must
    be UTF-8 without NUL bytes; it is always served as text/plain, so HTML or SVG uploaded as text
    can never run as a page.
    """
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    if name.lower().endswith(TEXT_SUFFIXES) and data and b"\x00" not in data:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return None
        return "text/plain; charset=utf-8"
    return None
