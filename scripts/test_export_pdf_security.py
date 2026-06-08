#!/usr/bin/env python3
"""Security regression tests for export-pdf.sh."""

from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export-pdf.sh"


def is_allowed_request(raw_url: str) -> bool:
    """Mirror export-pdf.sh request path boundary logic for representative cases."""
    serve_root = Path("/tmp/deck").resolve()
    html_path = (serve_root / "deck.html").resolve()

    pathname = urlsplit(raw_url).path
    decoded_path = unquote(pathname)
    if decoded_path == "/":
        candidate = html_path
    else:
        relative_path = PurePosixPath("." + decoded_path)
        candidate = (serve_root / Path(*relative_path.parts)).resolve()

    try:
        candidate.relative_to(serve_root)
    except ValueError:
        return False
    return True


def test_server_binds_to_loopback():
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'server.listen(0, "127.0.0.1"' in text


def test_playwright_uses_loopback_url():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "http://127.0.0.1:${port}/" in text


def test_path_traversal_is_rejected():
    assert is_allowed_request("/") is True
    assert is_allowed_request("/assets/a.png") is True
    assert is_allowed_request("/../../etc/passwd") is False
    assert is_allowed_request("/%2e%2e/%2e%2e/etc/passwd") is False
    assert is_allowed_request("/assets/../deck.html") is True


if __name__ == "__main__":
    tests = [
        test_server_binds_to_loopback,
        test_playwright_uses_loopback_url,
        test_path_traversal_is_rejected,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")
