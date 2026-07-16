#!/usr/bin/env python3
"""将 HTML 中的图片资源转换为 Base64 Data URI。

用法：python inline_images.py <html-file> [--base-dir DIR] [--allow-large]
"""

from __future__ import annotations

import argparse
import base64
import html
import ipaddress
import json
import mimetypes
import os
import re
import socket
import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_HTML_BYTES = 50 * 1024 * 1024
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".avif"}


def validate_remote_url(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False, "只允许 HTTP/HTTPS 图片地址"
    if parsed.username or parsed.password:
        return False, "图片地址不得携带认证信息"
    if not parsed.hostname:
        return False, "图片地址缺少主机名"
    try:
        default_port = 443 if parsed.scheme == "https" else 80
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or default_port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return False, f"域名解析失败：{exc}"
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            label = "回环" if ip.is_loopback else "私网或本地"
            return False, f"禁止访问{label}地址：{ip}"
    return True, ""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _sniff_mime(data: bytes, fallback: str | None = None) -> str | None:
    if fallback:
        declared = fallback.split(";", 1)[0].strip().lower()
        if not declared.startswith("image/"):
            return None
    signatures = [
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (b"\xff\xd8\xff", "image/jpeg"),
        (b"GIF87a", "image/gif"),
        (b"GIF89a", "image/gif"),
        (b"BM", "image/bmp"),
        (b"II*\x00", "image/tiff"),
        (b"MM\x00*", "image/tiff"),
        (b"\x00\x00\x01\x00", "image/x-icon"),
    ]
    for signature, mime in signatures:
        if data.startswith(signature):
            return mime
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    if len(data) >= 12 and data[4:8] == b"ftyp" and data[8:12] in {b"avif", b"avis"}:
        return "image/avif"
    prefix = data[:512].lstrip().lower()
    if prefix.startswith(b"<svg") or (prefix.startswith(b"<?xml") and b"<svg" in prefix):
        return "image/svg+xml"
    return None


def _read_remote(url: str, max_bytes: int, redirects: int = 3) -> tuple[bytes, str]:
    opener = build_opener(_NoRedirect)
    current = url
    for _ in range(redirects + 1):
        allowed, reason = validate_remote_url(current)
        if not allowed:
            raise ValueError(reason)
        request = Request(
            current,
            headers={"Accept": "image/*", "User-Agent": "html-report-skill/1.1"},
        )
        try:
            response = opener.open(request, timeout=15)
        except HTTPError as exc:
            if exc.code in {301, 302, 303, 307, 308} and exc.headers.get("Location"):
                current = urljoin(current, exc.headers["Location"])
                continue
            raise ValueError(f"远程图片下载失败：HTTP {exc.code}") from exc
        except URLError as exc:
            raise ValueError(f"远程图片下载失败：{exc.reason}") from exc
        with response:
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise ValueError(f"单图超过 {max_bytes // 1024 // 1024}MB")
            mime = _sniff_mime(data, response.headers.get_content_type())
            if not mime:
                raise ValueError("远程资源不是可识别图片")
            return data, mime
    raise ValueError("远程图片重定向次数超过 3 次")


def _read_local(reference: str, base_dir: Path, max_bytes: int) -> tuple[bytes, str]:
    parsed = urlparse(reference)
    if parsed.scheme == "file":
        path = Path(unquote(parsed.path))
    else:
        clean = unquote(reference.split("#", 1)[0].split("?", 1)[0])
        path = Path(clean)
        if not path.is_absolute():
            path = base_dir / path
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"本地图片不存在：{reference}")
    if path.stat().st_size > max_bytes:
        raise ValueError(f"单图超过 {max_bytes // 1024 // 1024}MB：{reference}")
    data = path.read_bytes()
    guessed, _ = mimetypes.guess_type(path.name)
    mime = _sniff_mime(data, guessed)
    if not mime:
        raise ValueError(f"本地资源不是可识别图片：{reference}")
    return data, mime


def _to_data_uri(reference: str, base_dir: Path, max_bytes: int) -> str:
    if reference.startswith("data:image/"):
        return reference
    if reference.startswith(("http://", "https://")):
        data, mime = _read_remote(reference, max_bytes)
    else:
        data, mime = _read_local(reference, base_dir, max_bytes)
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _looks_like_css_image(reference: str) -> bool:
    if reference.startswith(("data:image/", "http://", "https://", "file://")):
        suffix = Path(urlparse(reference).path).suffix.lower()
        return not suffix or suffix in IMAGE_EXTENSIONS
    return Path(reference.split("?", 1)[0].split("#", 1)[0]).suffix.lower() in IMAGE_EXTENSIONS


def inline_html(
    html_path: str | Path,
    *,
    base_dir: str | Path | None = None,
    allow_large: bool = False,
) -> dict:
    path = Path(html_path)
    root = Path(base_dir).resolve() if base_dir else path.parent.resolve()
    original = path.read_text(encoding="utf-8")
    unresolved: list[dict[str, str]] = []
    cache: dict[str, str] = {}
    inlined = 0
    max_image = sys.maxsize if allow_large else MAX_IMAGE_BYTES

    def convert(reference: str) -> str:
        nonlocal inlined
        value = html.unescape(reference.strip())
        if value.startswith("data:image/"):
            return value
        if value in cache:
            return cache[value]
        try:
            result = _to_data_uri(value, root, max_image)
        except (OSError, ValueError) as exc:
            unresolved.append({"reference": value, "error": str(exc)})
            return reference
        cache[value] = result
        inlined += 1
        return result

    tag_pattern = re.compile(r"<(?:img|source|input|video)\b[^>]*>", re.IGNORECASE | re.DOTALL)
    attr_pattern = re.compile(r"\b(src|poster)\s*=\s*([\"'])(.*?)\2", re.IGNORECASE | re.DOTALL)
    srcset_pattern = re.compile(r"\bsrcset\s*=\s*([\"'])(.*?)\1", re.IGNORECASE | re.DOTALL)

    def split_srcset(value: str) -> list[str]:
        """Split candidates without treating the Data URI payload comma as a separator."""
        candidates: list[str] = []
        start = 0
        candidate_is_data = value.lstrip().lower().startswith("data:image/")
        data_payload_started = False
        saw_whitespace_after_payload = False
        for index, character in enumerate(value):
            if candidate_is_data:
                if character == "," and not data_payload_started:
                    data_payload_started = True
                    continue
                if data_payload_started and character.isspace():
                    saw_whitespace_after_payload = True
                if character == "," and saw_whitespace_after_payload:
                    candidates.append(value[start:index].strip())
                    start = index + 1
                    remainder = value[start:].lstrip().lower()
                    candidate_is_data = remainder.startswith("data:image/")
                    data_payload_started = False
                    saw_whitespace_after_payload = False
            elif character == ",":
                candidates.append(value[start:index].strip())
                start = index + 1
                candidate_is_data = value[start:].lstrip().lower().startswith("data:image/")
        tail = value[start:].strip()
        if tail:
            candidates.append(tail)
        return candidates

    def replace_tag(match: re.Match) -> str:
        tag = match.group(0)
        originals: list[str] = []

        def replace_attr(attr: re.Match) -> str:
            name, quote, reference = attr.groups()
            if not html.unescape(reference.strip()).lower().startswith("data:image/"):
                originals.append(reference)
            return f"{name}={quote}{convert(reference)}{quote}"

        def replace_srcset(attr: re.Match) -> str:
            quote, value = attr.groups()
            candidates = []
            for item in split_srcset(value):
                parts = item.strip().split()
                if not parts:
                    continue
                if not html.unescape(parts[0].strip()).lower().startswith("data:image/"):
                    originals.append(parts[0])
                candidates.append(" ".join([convert(parts[0]), *parts[1:]]))
            return f"srcset={quote}{', '.join(candidates)}{quote}"

        replaced = attr_pattern.sub(replace_attr, tag)
        replaced = srcset_pattern.sub(replace_srcset, replaced)
        if originals and re.match(r"<img\b", tag, re.IGNORECASE) and "data-source-path=" not in replaced:
            marker = html.escape(originals[0], quote=True)
            replaced = replaced[:-1].rstrip() + f' data-source-path="{marker}">'
        return replaced

    converted = tag_pattern.sub(replace_tag, original)

    css_pattern = re.compile(r"url\(\s*([\"']?)(?!data:image/)([^\"')]+)\1\s*\)", re.IGNORECASE)

    def replace_css(match: re.Match) -> str:
        reference = match.group(2).strip()
        if not _looks_like_css_image(reference):
            return match.group(0)
        return f'url("{convert(reference)}")'

    converted = css_pattern.sub(replace_css, converted)
    final_bytes = len(converted.encode("utf-8"))
    if not allow_large and final_bytes > MAX_HTML_BYTES:
        unresolved.append({"reference": str(path), "error": "最终 HTML 超过 50MB"})

    success = not unresolved
    if success:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(converted)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    return {
        "success": success,
        "file": str(path),
        "inlined": inlined,
        "final_bytes": final_bytes,
        "unresolved": unresolved,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="将 HTML 图片转换为 Base64 Data URI")
    parser.add_argument("html_file")
    parser.add_argument("--base-dir")
    parser.add_argument("--allow-large", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = inline_html(args.html_file, base_dir=args.base_dir, allow_large=args.allow_large)
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
