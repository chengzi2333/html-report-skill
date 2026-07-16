#!/usr/bin/env python3
"""HTML 汇报质量自动验证脚本。

用法: python validate.py <html文件路径>
输出: JSON 格式验证结果 + exit code (0=通过, 1=不通过)
"""

import json
import re
import sys
from pathlib import Path


def validate_html(html_path: str) -> dict:
    """验证 HTML 文件质量，返回结构化结果。"""
    path = Path(html_path)
    if not path.exists():
        return {"success": False, "score": 0, "checks": [], "error": f"文件不存在: {html_path}"}

    content = path.read_text(encoding="utf-8")
    lower_content = content.lower()
    checks = []

    def strip_tags(fragment: str) -> str:
        return re.sub(r"<[^>]+>", " ", fragment)

    file_size = path.stat().st_size
    checks.append({
        "name": "文件大小",
        "pass": file_size > 10240,
        "detail": f"{file_size} bytes {'✓' if file_size > 10240 else '✗ (应 > 10KB)'}",
    })

    has_100vh = "100vh" in content
    has_100dvh = "100dvh" in content
    checks.append({
        "name": "视口适配",
        "pass": has_100vh and has_100dvh,
        "detail": f"100vh: {'✓' if has_100vh else '✗'}, 100dvh: {'✓' if has_100dvh else '✗'}",
    })

    has_lightbox = "lightbox" in content.lower() or "zoom-in" in content
    checks.append({
        "name": "图片放大",
        "pass": has_lightbox,
        "detail": "✓" if has_lightbox else "✗ 缺少 lightbox 或 zoom-in",
    })

    image_references = []
    for tag in re.findall(r"<(?:img|source|input|video)\b[^>]*>", content, re.IGNORECASE | re.DOTALL):
        image_references.extend(
            match[2].strip()
            for match in re.findall(r"\b(src|poster)\s*=\s*([\"'])(.*?)\2", tag, re.IGNORECASE | re.DOTALL)
        )
        for value in re.findall(r"\bsrcset\s*=\s*[\"'](.*?)[\"']", tag, re.IGNORECASE | re.DOTALL):
            data_uri_pattern = r"data:image/[^,\s]+,[A-Za-z0-9+/=]+"
            image_references.extend(re.findall(data_uri_pattern, value, re.IGNORECASE))
            remainder = re.sub(data_uri_pattern, "", value, flags=re.IGNORECASE)
            for item in remainder.split(","):
                parts = item.strip().split()
                if parts and not re.fullmatch(r"\d+(?:\.\d+)?[wx]", parts[0]):
                    image_references.append(parts[0])
    css_image_references = [
        ref.strip()
        for ref in re.findall(
            r"(?:background(?:-image)?|content)\s*:[^;{}]*url\(\s*[\"']?([^\"')]+)",
            content,
            re.IGNORECASE,
        )
    ]
    image_references.extend(css_image_references)
    non_portable_images = [
        ref for ref in image_references if ref and not ref.lower().startswith("data:image/") and not ref.startswith("#")
    ]
    checks.append({
        "name": "图片可移植性",
        "pass": not non_portable_images,
        "detail": "✓" if not non_portable_images else f"✗ 发现未内联图片: {non_portable_images[:4]}",
    })

    table_count = len(re.findall(r"<table[\s>]", content, re.IGNORECASE))
    th_center = re.findall(r"<th[^>]*text-align:\s*center", content, re.IGNORECASE)
    tables_pass = table_count == 0 or len(th_center) == 0
    checks.append({
        "name": "表格规范",
        "pass": tables_pass,
        "detail": f"表格数: {table_count}, 表头居中: {len(th_center)} {'✓' if tables_pass else '✗ (不应有居中表头)'}",
    })

    has_chinese_font = any(
        font in content
        for font in ["Noto Sans SC", "Noto Serif SC", "Source Han Sans", "Source Han Serif", "Microsoft YaHei"]
    )
    checks.append({
        "name": "中文字体",
        "pass": has_chinese_font,
        "detail": "✓" if has_chinese_font else "✗ 缺少中文字体回退",
    })

    banned_fonts = []
    font_families = re.findall(r"font-family\s*:[^;]+", content, re.IGNORECASE)
    for family in font_families:
        for font in ["Inter", "Roboto"]:
            if re.search(rf"['\"]?\b{font}\b['\"]?", family, re.IGNORECASE):
                banned_fonts.append(font)
    banned_fonts = sorted(set(banned_fonts))
    checks.append({
        "name": "禁用字体检查",
        "pass": len(banned_fonts) == 0,
        "detail": "✓" if not banned_fonts else f"✗ 发现禁用字体: {banned_fonts}",
    })

    has_observer = "IntersectionObserver" in content
    has_reveal = "reveal" in content
    checks.append({
        "name": "交互动画",
        "pass": has_observer and has_reveal,
        "detail": f"IntersectionObserver: {'✓' if has_observer else '✗'}, reveal: {'✓' if has_reveal else '✗'}",
    })

    has_clamp = "clamp(" in content
    checks.append({
        "name": "响应式 clamp",
        "pass": has_clamp,
        "detail": "✓" if has_clamp else "✗ 缺少 clamp() 响应式变量",
    })

    has_center_v = "center-v" in content
    checks.append({
        "name": "垂直居中补偿",
        "pass": has_center_v,
        "detail": "✓" if has_center_v else "✗ 缺少 center-v 规则或用法",
    })

    has_section_head = "section-head" in content and "section-kicker" in content
    checks.append({
        "name": "section-head 模式",
        "pass": has_section_head,
        "detail": "✓" if has_section_head else "✗ 缺少 section-head / section-kicker",
    })

    has_breadcrumb_js = "setupBreadcrumbs" in content and "updateBreadcrumbs" in content
    duplicate_breadcrumb_html = len(re.findall(r'<div[^>]+class=["\'][^"\']*breadcrumb', content, re.IGNORECASE)) > 0
    checks.append({
        "name": "Breadcrumb 动态导航",
        "pass": has_breadcrumb_js and not duplicate_breadcrumb_html,
        "detail": "✓" if has_breadcrumb_js and not duplicate_breadcrumb_html else "✗ Breadcrumb 应由 JS 动态生成，禁止手写重复 HTML",
    })

    has_print = "@media print" in content
    checks.append({
        "name": "打印样式",
        "pass": has_print,
        "detail": "✓" if has_print else "✗ 缺少 @media print",
    })

    has_reduced_motion = "prefers-reduced-motion" in content
    checks.append({
        "name": "减少动效支持",
        "pass": has_reduced_motion,
        "detail": "✓" if has_reduced_motion else "✗ 缺少 prefers-reduced-motion",
    })

    has_edit_storage = "contenteditable" in content.lower() or "localStorage" in content
    has_edit_trigger = (
        "edit-toggle" in content
        or re.search(r"\.key\s*={2,3}\s*['\"]e['\"]", content, re.IGNORECASE)
        or re.search(r"\.key\s*={2,3}\s*['\"]E['\"]", content)
        or "KeyE" in content
        or "按 E 键" in content
    )
    checks.append({
        "name": "浏览器内编辑",
        "pass": has_edit_storage and has_edit_trigger,
        "detail": (
            "✓"
            if has_edit_storage and has_edit_trigger
            else f"编辑存储: {'✓' if has_edit_storage else '✗'}, E键/按钮触发: {'✓' if has_edit_trigger else '✗'}"
        ),
    })

    has_css_vars = ":root" in content and "var(" in content
    checks.append({
        "name": "CSS 变量",
        "pass": has_css_vars,
        "detail": "✓" if has_css_vars else "✗ 缺少 :root 或 var() CSS 变量",
    })

    has_texture_or_gradient = any(
        token in content
        for token in ["linear-gradient", "radial-gradient", "body::before", "background-image"]
    )
    checks.append({
        "name": "渐变/纹理背景",
        "pass": has_texture_or_gradient,
        "detail": "✓" if has_texture_or_gradient else "✗ 缺少渐变或纹理背景",
    })

    has_hover_media = "@media (hover: hover)" in content or "@media(hover:hover)" in content.replace(" ", "")
    has_hover_rule = ":hover" in content
    checks.append({
        "name": "hover 增强",
        "pass": has_hover_media and has_hover_rule,
        "detail": f"hover媒体查询: {'✓' if has_hover_media else '✗'}, :hover规则: {'✓' if has_hover_rule else '✗'}",
    })

    th_styles = re.findall(r"th\s*\{[^}]*\}", content, re.IGNORECASE | re.DOTALL)
    thead_styles = re.findall(r"thead[^{}]*\{[^}]*\}", content, re.IGNORECASE | re.DOTALL)
    inline_th_border = re.findall(r"<th[^>]*border-bottom", content, re.IGNORECASE)
    has_th_border = any("border-bottom" in style.lower() for style in th_styles + thead_styles) or bool(inline_th_border)
    checks.append({
        "name": "表头强调底边",
        "pass": has_th_border,
        "detail": "✓" if has_th_border else "✗ 缺少 th/thead 的 border-bottom 强调线",
    })

    modal_declared = any(token in lower_content for token in ["弹窗", "模态", "modal"])
    has_modal_structure = bool(
        re.search(r'class=["\'][^"\']*\bmodal\b', content, re.IGNORECASE)
        or re.search(r'role=["\']dialog["\']', content, re.IGNORECASE)
    )
    has_modal_trigger = bool(
        re.search(r"data-modal-(target|open)", content, re.IGNORECASE)
        or "openModal" in content
        or re.search(r"\.hidden\s*=\s*false", content)
        or re.search(r"\.classList\.add\(['\"](?:active|open|is-open)", content)
    )
    has_modal_close = bool(
        "data-modal-close" in content
        or "closeModal" in content
        or "Escape" in content
        or "Esc" in content
    )
    modal_pass = (not modal_declared) or (has_modal_structure and has_modal_trigger and has_modal_close)
    checks.append({
        "name": "Modal 真实交互",
        "pass": modal_pass,
        "detail": (
            "未声明 modal/弹窗，跳过"
            if not modal_declared
            else f"结构: {'✓' if has_modal_structure else '✗'}, 触发: {'✓' if has_modal_trigger else '✗'}, 关闭: {'✓' if has_modal_close else '✗'}"
        ),
    })

    tooltip_declared = any(token in lower_content for token in ["tooltip", "提示", "数据标注"])
    has_tooltip_target = bool(
        re.search(r"data-tooltip", content, re.IGNORECASE)
        or re.search(r'class=["\'][^"\']*(?:tooltip|tip-trigger)', content, re.IGNORECASE)
        or re.search(r"aria-describedby=", content, re.IGNORECASE)
    )
    has_tooltip_rendering = bool(
        re.search(r"(?:tooltip|data-tooltip)[^{}]*(?:::before|::after)", content, re.IGNORECASE | re.DOTALL)
        or re.search(r"\.tooltip[^{}]*\{", content, re.IGNORECASE)
    )
    tooltip_pass = (not tooltip_declared) or (has_tooltip_target and has_tooltip_rendering)
    checks.append({
        "name": "Tooltip 真实交互",
        "pass": tooltip_pass,
        "detail": (
            "未声明 tooltip/提示，跳过"
            if not tooltip_declared
            else f"目标元素: {'✓' if has_tooltip_target else '✗'}, 展示样式: {'✓' if has_tooltip_rendering else '✗'}"
        ),
    })

    carousel_declared = any(token in lower_content for token in ["轮播", "carousel", "证据切换", "截图证据"])
    has_carousel_structure = bool(
        re.search(r'class=["\'][^"\']*(?:carousel|evidence)', content, re.IGNORECASE)
        or re.search(r"data-carousel", content, re.IGNORECASE)
    )
    has_carousel_controls = bool(
        re.search(r'(?:prev|next|上一|下一|carousel-prev|carousel-next|evidencePrev|evidenceNext)', content, re.IGNORECASE)
    )
    has_carousel_binding = bool(
        has_carousel_controls and re.search(r"addEventListener\(['\"]click", content)
    )
    carousel_pass = (not carousel_declared) or (has_carousel_structure and has_carousel_controls and has_carousel_binding)
    checks.append({
        "name": "轮播/证据切换真实交互",
        "pass": carousel_pass,
        "detail": (
            "未声明轮播/证据切换，跳过"
            if not carousel_declared
            else f"结构: {'✓' if has_carousel_structure else '✗'}, 控件: {'✓' if has_carousel_controls else '✗'}, 点击绑定: {'✓' if has_carousel_binding else '✗'}"
        ),
    })

    visual_issues = []
    interaction_tags = re.findall(
        r"<(?:div|section|article)\b[^>]*(?:evidence|carousel)[^>]*>",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    for index, tag in enumerate(interaction_tags, start=1):
        style_match = re.search(r'style=["\']([^"\']+)["\']', tag, re.IGNORECASE | re.DOTALL)
        style = style_match.group(1).lower() if style_match else ""
        tag_lower = tag.lower()
        has_large_aspect = bool(re.search(r"aspect-ratio\s*:\s*(?:3\s*/\s*1|[2-9](?:\.\d+)?\s*/\s*1)", style))
        has_full_width = bool(re.search(r"width\s*:\s*(?:100%|100vw)", style))
        has_dark_bg = bool(re.search(r"background(?:-color)?\s*:\s*(?:#0{3,6}|#111|#000|rgba?\(\s*0\s*,\s*0\s*,\s*0|rgba?\(\s*17\s*,\s*23\s*,\s*29)", style))
        has_height_cap = bool(re.search(r"(?:max-)?height\s*:\s*(?:min\(\s*22vh\s*,\s*180px\s*\)|1[0-8]\dpx|[1-9]\dpx)", style))
        is_inline_frame = "evidence-frame" in tag_lower or "carousel" in tag_lower
        if is_inline_frame and has_dark_bg and (has_large_aspect or has_full_width) and not has_height_cap:
            visual_issues.append(f"交互演示块#{index} 过大或缺少高度上限")
    checks.append({
        "name": "交互示例视觉占比",
        "pass": not visual_issues,
        "detail": "✓" if not visual_issues else f"✗ {', '.join(visual_issues[:4])}",
    })

    body_match = re.search(r"<body([^>]*)>", content, re.IGNORECASE)
    body_attrs = body_match.group(1) if body_match else ""
    uses_scroll_mode = bool(re.search(r'class=["\'][^"\']*\bscroll-mode\b', body_attrs, re.IGNORECASE))
    uses_paged_mode = not uses_scroll_mode
    has_scroll_snap = "scroll-snap-type" in content and "scroll-snap-align" in content
    slide_height_rule = bool(
        re.search(r"\.slide\s*\{[^}]*height\s*:\s*100vh[^}]*height\s*:\s*100dvh", content, re.IGNORECASE | re.DOTALL)
        or (has_100vh and has_100dvh and "scroll-snap-align" in content)
    )
    slide_count = len(re.findall(r'<section[^>]+class=["\'][^"\']*\bslide\b', content, re.IGNORECASE))
    center_v_count = len(re.findall(r'class=["\'][^"\']*\bcenter-v\b', content, re.IGNORECASE))
    enough_center_v = slide_count < 4 or center_v_count >= max(1, round(slide_count * 0.2))
    paged_pass = (not uses_paged_mode) or (has_scroll_snap and slide_height_rule and enough_center_v)
    checks.append({
        "name": "翻页模式结构",
        "pass": paged_pass,
        "detail": (
            "连续滚动模式，跳过"
            if not uses_paged_mode
            else f"scroll-snap: {'✓' if has_scroll_snap else '✗'}, slide高度: {'✓' if slide_height_rule else '✗'}, center-v: {center_v_count}/{slide_count} {'✓' if enough_center_v else '✗'}"
        ),
    })

    sparse_missing = []
    slide_fragments = re.findall(
        r"<section\b[^>]*class=[\"'][^\"']*\bslide\b[^\"']*[\"'][^>]*>.*?</section>",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    for index, slide in enumerate(slide_fragments, start=1):
        if "center-v" in slide:
            continue
        if re.search(r"<(?:table|pre|code)\b", slide, re.IGNORECASE):
            continue
        card_count = len(re.findall(
            r'class=["\'][^"\']*(?<![\w-])(?:card|insight|risk-card|phase)(?![\w-])',
            slide,
            re.IGNORECASE,
        ))
        has_section_head = "section-head" in slide and "section-kicker" in slide
        text_len = len(strip_tags(slide).strip())
        image_count = len(re.findall(r"<img\b", slide, re.IGNORECASE))
        short_list_count = len(re.findall(r"<li\b", slide, re.IGNORECASE))
        sparse_by_cards = has_section_head and 1 <= card_count <= 4 and text_len < 1400
        sparse_by_image = has_section_head and 1 <= image_count <= 2 and short_list_count <= 5 and text_len < 1000
        sparse_by_short_text = has_section_head and card_count == 0 and image_count == 0 and short_list_count <= 5 and text_len < 700
        if sparse_by_cards or sparse_by_image or sparse_by_short_text:
            slide_id = re.search(r'id=["\']([^"\']+)["\']', slide, re.IGNORECASE)
            sparse_missing.append(slide_id.group(1) if slide_id else f"slide-{index}")
    sparse_center_pass = (not uses_paged_mode) or not sparse_missing
    checks.append({
        "name": "稀疏页 center-v 覆盖",
        "pass": sparse_center_pass,
        "detail": (
            "连续滚动模式，跳过"
            if not uses_paged_mode
            else ("✓" if not sparse_missing else f"✗ 疑似稀疏但未加 center-v: {', '.join(sparse_missing[:6])}")
        ),
    })

    declared_mismatches = []
    if modal_declared and not modal_pass:
        declared_mismatches.append("弹窗")
    if tooltip_declared and not tooltip_pass:
        declared_mismatches.append("tooltip/提示")
    if carousel_declared and not carousel_pass:
        declared_mismatches.append("轮播/证据切换")
    checks.append({
        "name": "交互声明实现一致性",
        "pass": not declared_mismatches,
        "detail": "✓" if not declared_mismatches else f"✗ 声明但缺少真实实现: {', '.join(declared_mismatches)}",
    })

    passed = sum(1 for check in checks if check["pass"])
    score = round(passed / len(checks) * 100) if checks else 0
    blocking_names = {"图片可移植性"}
    blocking_failures = [
        check["name"] for check in checks if check["name"] in blocking_names and not check["pass"]
    ]
    return {
        "success": score >= 80 and not blocking_failures,
        "score": score,
        "passed": passed,
        "total": len(checks),
        "blocking_failures": blocking_failures,
        "checks": checks,
    }


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print("用法: python scripts/validate.py <html文件路径>")
        print("通过标准: 综合得分 >= 80")
        sys.exit(0 if len(sys.argv) >= 2 else 2)

    result = validate_html(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
