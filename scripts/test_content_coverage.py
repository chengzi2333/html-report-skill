#!/usr/bin/env python3
"""Regression tests for content_coverage.py."""

import importlib.util
import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("content_coverage", ROOT / "scripts" / "content_coverage.py")
content_coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(content_coverage)


def write_files(source: str, html: str):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    md_path = root / "source.md"
    html_path = root / "deck.html"
    md_path.write_text(source, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")
    return tmp, md_path, html_path


def test_reports_pass_when_markdown_elements_are_covered():
    tmp, md_path, html_path = write_files(
        """# 项目复盘

## 关键结论

![架构图](assets/arch.png)

| 模块 | 状态 |
|---|---|
| 生成 | 完成 |

```python
print("ok")
```

- 安装路径清楚
- 示例可验证
""",
        """<html><body>
<h1>项目复盘</h1>
<h2>关键结论</h2>
<img src="assets/arch.png" alt="架构图">
<table><tr><th>模块</th><th>状态</th></tr><tr><td>生成</td><td>完成</td></tr></table>
<pre><code>print("ok")</code></pre>
<ul><li>安装路径清楚</li><li>示例可验证</li></ul>
</body></html>""",
    )
    with tmp:
        report = content_coverage.check_coverage(str(md_path), str(html_path))

    assert report["status"] == "pass"
    assert report["summary"]["headings"] == {"source": 2, "covered": 2}
    assert report["summary"]["images"] == {"source": 1, "covered": 1}
    assert report["summary"]["tables"] == {"source": 1, "covered": 1}
    assert report["summary"]["code_blocks"] == {"source": 1, "covered": 1}
    assert report["summary"]["list_items"] == {"source": 2, "covered": 2}
    assert report["missing"] == []


def test_reports_missing_items_and_nonzero_cli_exit():
    tmp, md_path, html_path = write_files(
        """# 项目复盘

## 风险

![流程图](assets/flow.png)

| 风险 | 应对 |
|---|---|
| 图片缺失 | 补回 |

```bash
python validate.py demo.html
```

1. 保留标题
2. 保留表格
""",
        """<html><body><h1>项目复盘</h1><p>保留标题</p></body></html>""",
    )
    with tmp:
        report = content_coverage.check_coverage(str(md_path), str(html_path))
        with redirect_stdout(io.StringIO()):
            exit_code = content_coverage.main([str(md_path), str(html_path)])

    assert report["status"] == "missing"
    missing_types = {item["type"] for item in report["missing"]}
    assert {"heading", "image", "table", "code_block", "list_item"}.issubset(missing_types)
    assert exit_code == 1


def test_non_markdown_input_requires_manual_review():
    tmp, md_path, html_path = write_files("not markdown", "<html></html>")
    ppt_path = Path(tmp.name) / "slides.pptx"
    ppt_path.write_text("fake", encoding="utf-8")
    with tmp:
        report = content_coverage.check_coverage(str(ppt_path), str(html_path))

    assert report["status"] == "review"
    assert "PPT/非 MD 路径需人工复核或后续增强" in report["notes"][0]


if __name__ == "__main__":
    tests = [
        test_reports_pass_when_markdown_elements_are_covered,
        test_reports_missing_items_and_nonzero_cli_exit,
        test_non_markdown_input_requires_manual_review,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")
