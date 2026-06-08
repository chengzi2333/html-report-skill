#!/usr/bin/env python3
"""Regression tests for validate.py."""

import importlib.util
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


BASE_HTML = """<!doctype html>
<html>
<head>
<style>
:root { --accent: #ccff33; }
html { scroll-snap-type: y mandatory; }
.slide { height: 100vh; height: 100dvh; overflow: hidden; scroll-snap-align: start; }
.slide-content { display: flex; flex-direction: column; justify-content: flex-start; }
.slide-content.center-v { justify-content: center; }
.section-head {}
.section-kicker {}
@media print { .slide { page-break-after: always; } }
@media (hover: hover) { .card:hover { transform: translateY(-2px); } }
@media (prefers-reduced-motion: reduce) { * { animation: none; } }
th { text-align: left; border-bottom: 2px solid var(--accent); }
body::before { background-image: linear-gradient(#000, #111); }
.lightbox-overlay {}
</style>
</head>
<body>
<section class="slide"><div class="slide-content center-v"><div class="section-head"><div class="section-kicker">01</div><h2>Intro</h2></div><p class="reveal">Text</p></div></section>
<section class="slide"><div class="slide-content"><div class="section-head"><div class="section-kicker">02</div><h2>Body</h2></div><table><thead><tr><th>A</th></tr></thead></table></div></section>
<script>
const font = "Noto Sans SC";
function setupBreadcrumbs() {}
function updateBreadcrumbs() {}
new IntersectionObserver(() => {});
function setupLightbox() { document.querySelectorAll('img').forEach(img => img.style.cursor = 'zoom-in'); }
function setupEditMode() { localStorage.setItem('x', 'y'); if (event.key === 'E') {} }
</script>
</body>
</html>
"""


def validate_snippet(html: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "deck.html"
        path.write_text(html, encoding="utf-8")
        return validate.validate_html(str(path))


def check(result: dict, name: str) -> dict:
    for item in result["checks"]:
        if item["name"] == name:
            return item
    raise AssertionError(f"missing check: {name}")


def test_declared_interactions_without_real_implementation_fail():
    html = BASE_HTML.replace(
        "<p class=\"reveal\">Text</p>",
        "<p class=\"reveal\">包含弹窗、tooltip、轮播交互能力。</p>",
    )
    result = validate_snippet(html)

    assert not check(result, "Modal 真实交互")["pass"]
    assert not check(result, "Tooltip 真实交互")["pass"]
    assert not check(result, "轮播/证据切换真实交互")["pass"]
    assert not check(result, "交互声明实现一致性")["pass"]


def test_declared_interactions_with_real_implementation_pass():
    html = BASE_HTML.replace(
        "</style>",
        """
.modal { display: none; }
.tooltip-trigger::after { content: attr(data-tooltip); }
.carousel { display: grid; }
</style>""",
    ).replace(
        "</body>",
        """
<button data-modal-target="#m1">详情</button>
<div class="modal" id="m1" role="dialog" aria-modal="true"><button data-modal-close>关闭</button></div>
<span class="tooltip-trigger" data-tooltip="说明">指标</span>
<div class="carousel"><button class="carousel-prev">Prev</button><button class="carousel-next">Next</button></div>
<script>
document.querySelector('[data-modal-target]').addEventListener('click', () => {});
document.querySelector('[data-modal-close]').addEventListener('click', () => {});
document.querySelector('.carousel-next').addEventListener('click', () => {});
</script>
</body>""",
    )
    result = validate_snippet(html)

    assert check(result, "Modal 真实交互")["pass"]
    assert check(result, "Tooltip 真实交互")["pass"]
    assert check(result, "轮播/证据切换真实交互")["pass"]
    assert check(result, "交互声明实现一致性")["pass"]


def test_paged_mode_requires_scroll_snap_and_center_usage():
    html = BASE_HTML.replace("scroll-snap-type: y mandatory;", "")
    result = validate_snippet(html)

    assert not check(result, "翻页模式结构")["pass"]


def test_sparse_card_slide_requires_center_v():
    sparse_slide = """
<section class="slide"><div class="slide-content">
<div class="section-head"><div class="section-kicker">03</div><h2>Data Guard</h2></div>
<div class="card-grid">
<article class="card">A</article><article class="card">B</article>
<article class="card">C</article><article class="card">D</article>
</div>
</div></section>
"""
    html = BASE_HTML.replace("</script>", f"</script>{sparse_slide}")
    result = validate_snippet(html)

    assert not check(result, "稀疏页 center-v 覆盖")["pass"]


def test_large_dark_carousel_block_in_slide_fails_visual_balance():
    bloated_slide = """
<section class="slide" id="slide-interaction"><div class="slide-content center-v">
<div class="section-head"><div class="section-kicker">04</div><h2>Interaction</h2></div>
<div class="card-grid">
<article class="card">A</article><article class="card">B</article><article class="card">C</article>
<article class="card">D</article><article class="card">E</article>
</div>
<div class="evidence-bubble" style="width:100%;display:block;">
<div class="evidence-frame" style="aspect-ratio:3/1;background:#111;border-radius:12px;overflow:hidden;">轮播演示</div>
<button data-evidence-prev>Prev</button><button data-evidence-next>Next</button>
</div>
</div></section>
<script>
document.querySelector('[data-evidence-next]').addEventListener('click', () => {});
</script>
"""
    html = BASE_HTML.replace("</body>", f"{bloated_slide}</body>")
    result = validate_snippet(html)

    assert not check(result, "交互示例视觉占比")["pass"]


if __name__ == "__main__":
    tests = [
        test_declared_interactions_without_real_implementation_fail,
        test_declared_interactions_with_real_implementation_pass,
        test_paged_mode_requires_scroll_snap_and_center_usage,
        test_sparse_card_slide_requires_center_v,
        test_large_dark_carousel_block_in_slide_fails_visual_balance,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")
