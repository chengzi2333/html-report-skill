#!/usr/bin/env python3
"""Markdown to HTML content coverage report.

Usage:
    python content_coverage.py <source.md> <generated.html>

Exit code:
    0 = pass or manual review required
    1 = missing content or input error
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path


def normalize_text(value: str) -> str:
    """Normalize text for resilient containment checks."""
    unescaped = html.unescape(value)
    return re.sub(r"\s+", " ", unescaped).strip().lower()


def strip_html_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value)


def extract_markdown_elements(markdown: str) -> dict:
    fenced_blocks = re.findall(r"```[^\n]*\n(.*?)```", markdown, re.DOTALL)
    without_code = re.sub(r"```[^\n]*\n.*?```", "", markdown, flags=re.DOTALL)

    headings = [
        match.group(2).strip()
        for match in re.finditer(r"^(#{1,3})\s+(.+?)\s*$", without_code, re.MULTILINE)
        if match.group(2).strip()
    ]
    images = [
        {"alt": alt.strip(), "path": path.strip()}
        for alt, path in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", without_code)
    ]
    tables = extract_pipe_tables(without_code)
    list_items = [
        match.group(1).strip()
        for match in re.finditer(r"^\s*(?:[-*+]\s+|\d+\.\s+)(.+?)\s*$", without_code, re.MULTILINE)
        if match.group(1).strip()
    ]

    return {
        "headings": headings,
        "images": images,
        "tables": tables,
        "code_blocks": [block.strip() for block in fenced_blocks if block.strip()],
        "list_items": list_items,
    }


def extract_pipe_tables(markdown: str) -> list[str]:
    tables = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines) - 1:
        header = lines[i]
        separator = lines[i + 1]
        if is_table_row(header) and is_table_separator(separator):
            table_lines = [header, separator]
            i += 2
            while i < len(lines) and is_table_row(lines[i]):
                table_lines.append(lines[i])
                i += 1
            tables.append("\n".join(table_lines))
            continue
        i += 1
    return tables


def is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not is_table_row(stripped):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def html_text_and_raw(html_content: str) -> tuple[str, str]:
    raw = html.unescape(html_content)
    text = normalize_text(strip_html_tags(raw))
    return text, raw


def count_covered_strings(values: list[str], html_text: str) -> tuple[int, list[str]]:
    covered = 0
    missing = []
    for value in values:
        normalized = normalize_text(value)
        if normalized and normalized in html_text:
            covered += 1
        else:
            missing.append(value)
    return covered, missing


def check_coverage(source_path: str, html_path: str) -> dict:
    source = Path(source_path)
    generated = Path(html_path)

    if source.suffix.lower() != ".md":
        return {
            "source": str(source),
            "generated": str(generated),
            "status": "review",
            "summary": empty_summary(),
            "missing": [],
            "notes": ["PPT/非 MD 路径需人工复核或后续增强。"],
        }

    if not source.exists() or not generated.exists():
        missing_files = [str(path) for path in [source, generated] if not path.exists()]
        return {
            "source": str(source),
            "generated": str(generated),
            "status": "missing",
            "summary": empty_summary(),
            "missing": [{"type": "file", "value": path} for path in missing_files],
            "notes": ["源文件或生成文件不存在。"],
        }

    markdown = source.read_text(encoding="utf-8")
    generated_html = generated.read_text(encoding="utf-8")
    html_text, raw_html = html_text_and_raw(generated_html)
    elements = extract_markdown_elements(markdown)

    missing = []
    summary = {}

    covered, missing_values = count_covered_strings(elements["headings"], html_text)
    summary["headings"] = {"source": len(elements["headings"]), "covered": covered}
    missing.extend({"type": "heading", "value": value} for value in missing_values)

    covered_images = 0
    for image in elements["images"]:
        if image["path"] and image["path"] in raw_html:
            covered_images += 1
        else:
            missing.append({"type": "image", "value": image["path"], "alt": image["alt"]})
    summary["images"] = {"source": len(elements["images"]), "covered": covered_images}

    table_count = len(re.findall(r"<table[\s>]", generated_html, re.IGNORECASE))
    covered_tables = min(len(elements["tables"]), table_count)
    summary["tables"] = {"source": len(elements["tables"]), "covered": covered_tables}
    if table_count < len(elements["tables"]):
        for index in range(table_count + 1, len(elements["tables"]) + 1):
            missing.append({"type": "table", "value": f"Markdown table #{index}"})

    code_count = len(re.findall(r"<(?:pre|code)[\s>]", generated_html, re.IGNORECASE))
    code_covered = 0
    missing_code_blocks = []
    for block in elements["code_blocks"]:
        first_line = normalize_text(block.splitlines()[0] if block.splitlines() else block)
        if first_line and first_line in html_text:
            code_covered += 1
        else:
            missing_code_blocks.append(block)
    code_covered = max(code_covered, min(len(elements["code_blocks"]), code_count))
    summary["code_blocks"] = {"source": len(elements["code_blocks"]), "covered": code_covered}
    if code_covered < len(elements["code_blocks"]):
        for index, block in enumerate(missing_code_blocks, start=1):
            missing.append({"type": "code_block", "value": first_nonempty_line(block) or f"code block #{index}"})

    covered, missing_values = count_covered_strings(elements["list_items"], html_text)
    summary["list_items"] = {"source": len(elements["list_items"]), "covered": covered}
    missing.extend({"type": "list_item", "value": value} for value in missing_values)

    status = "missing" if missing else "pass"
    notes = []
    if any(item["source"] != item["covered"] for item in summary.values()):
        notes.append("发现疑似缺失项，请修复或人工复核后再交付。")
    else:
        notes.append("未发现关键内容缺失。")

    return {
        "source": str(source),
        "generated": str(generated),
        "status": status,
        "summary": summary,
        "missing": missing,
        "notes": notes,
    }


def first_nonempty_line(value: str) -> str:
    for line in value.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def empty_summary() -> dict:
    return {
        "headings": {"source": 0, "covered": 0},
        "images": {"source": 0, "covered": 0},
        "tables": {"source": 0, "covered": 0},
        "code_blocks": {"source": 0, "covered": 0},
        "list_items": {"source": 0, "covered": 0},
    }


def render_markdown_report(report: dict) -> str:
    labels = {
        "headings": "标题",
        "images": "图片",
        "tables": "表格",
        "code_blocks": "代码块",
        "list_items": "列表项",
    }
    status_label = {
        "pass": "通过",
        "review": "需复核",
        "missing": "有缺失",
    }.get(report["status"], report["status"])

    lines = [
        "内容覆盖检查：",
        f"- 原始来源：{report['source']}",
        f"- 生成结果：{report['generated']}",
    ]
    for key, label in labels.items():
        item = report["summary"][key]
        lines.append(f"- {label}：{item['covered']}/{item['source']}")
    lines.append(f"- 结论：{status_label}")

    if report["missing"]:
        lines.append("")
        lines.append("缺失项：")
        for item in report["missing"]:
            value = item.get("value", "")
            lines.append(f"- {item['type']}：{value}")

    if report["notes"]:
        lines.append("")
        lines.append("复核说明：")
        lines.extend(f"- {note}" for note in report["notes"])

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("用法: python content_coverage.py <source.md> <generated.html>", file=sys.stderr)
        return 1

    report = check_coverage(args[0], args[1])
    print(render_markdown_report(report))
    print("\nJSON:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "missing" else 0


if __name__ == "__main__":
    raise SystemExit(main())
