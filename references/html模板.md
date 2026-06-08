# HTML 汇报模板

生成 HTML 幻灯片汇报的参考架构。每个汇报文件都遵循此结构。

## 基础 HTML 结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>汇报标题</title>
  <!-- 字体：使用 Fontshare 或 Google Fonts — 禁止使用系统默认字体 -->
  <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=..." />
  <style>
    /* ===========================================
       CSS 自定义属性（主题）
       修改这些变量即可改变整个外观
       =========================================== */
    :root {
      --bg-primary: #0a0f1c;
      --bg-secondary: #111827;
      --text-primary: #ffffff;
      --text-secondary: #9ca3af;
      --accent: #00ffcc;
      --accent-glow: rgba(0, 255, 204, 0.3);
      --font-display: "Clash Display", sans-serif;
      --font-body: "Satoshi", sans-serif;
      --title-size: clamp(2rem, 6vw, 5rem);
      --subtitle-size: clamp(0.875rem, 2vw, 1.25rem);
      --body-size: clamp(0.75rem, 1.2vw, 1rem);
      --font-cn-sans: "Noto Sans SC", "Source Han Sans SC", "Microsoft YaHei", sans-serif;
      --font-cn-serif: "Noto Serif SC", "Source Han Serif SC", "SimSun", serif;
      --slide-padding: clamp(1.5rem, 4vw, 4rem);
      --content-gap: clamp(1rem, 2vw, 2rem);
      --line-height-base: 1.7;
      --line-height-heading: 1.3;
      --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
      --duration-normal: 0.6s;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    /*
      ---
      在此处粘贴 视口适配.css 的完整内容
      ---
    */

    .reveal {
      opacity: 0;
      transform: translateY(30px);
      transition:
        opacity var(--duration-normal) var(--ease-out-expo),
        transform var(--duration-normal) var(--ease-out-expo);
    }

    .slide.visible .reveal {
      opacity: 1;
      transform: translateY(0);
    }

    .reveal:nth-child(1) { transition-delay: 0.1s; }
    .reveal:nth-child(2) { transition-delay: 0.2s; }
    .reveal:nth-child(3) { transition-delay: 0.3s; }
    .reveal:nth-child(4) { transition-delay: 0.4s; }

    .breadcrumb {
      position: fixed;
      top: clamp(12px, 2vh, 20px);
      left: var(--slide-padding);
      z-index: 50;
      display: flex;
      gap: clamp(8px, 1.5vw, 18px);
      font-family: var(--font-body);
      font-size: var(--small-size);
      font-weight: 500;
      letter-spacing: 0.02em;
    }

    .breadcrumb span {
      color: var(--text-secondary);
      opacity: 0.5;
      cursor: pointer;
      transition: opacity 0.3s ease, color 0.3s ease;
      padding: 2px 6px;
      border-radius: 4px;
    }

    .breadcrumb span.active {
      opacity: 1;
      color: var(--accent);
      font-weight: 700;
    }

    .breadcrumb span:hover {
      opacity: 0.8;
      color: var(--text-primary);
    }

    @media print {
      .breadcrumb { display: none; }
    }
  </style>
</head>
<body>
  <div class="progress-bar"></div>
  <nav class="nav-dots"><!-- 由 JS 生成 --></nav>
  <!-- Breadcrumb 全局章节导航由 setupBreadcrumbs() 动态创建，不要手写 <div class="breadcrumb"> -->

  <section class="slide title-slide">
    <h1 class="reveal">汇报标题</h1>
    <p class="reveal">副标题 / 汇报人</p>
  </section>

  <section class="slide">
    <div class="slide-content">
      <h2 class="reveal">章节标题</h2>
      <p class="reveal">内容...</p>
    </div>
  </section>

  <script>
    class SlidePresentation {
      constructor() {
        this.slides = document.querySelectorAll(".slide");
        this.currentSlide = 0;
        this.setupIntersectionObserver();
        this.setupKeyboardNav();
        this.setupTouchNav();
        this.setupProgressBar();
        this.setupNavDots();
        this.setupBreadcrumbs();
      }

      setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("visible");
              this.currentSlide = Array.from(this.slides).indexOf(entry.target);
              this.updateProgressBar();
              this.updateNavDots();
              this.updateBreadcrumbs();
            }
          });
        }, { threshold: 0.5 });
        this.slides.forEach(slide => observer.observe(slide));
      }

      setupKeyboardNav() {
        document.addEventListener("keydown", (e) => {
          const key = e.key;
          if (key === "ArrowDown" || key === "ArrowRight" || key === " " || key === "PageDown") {
            e.preventDefault();
            this.goToSlide(Math.min(this.currentSlide + 1, this.slides.length - 1));
          } else if (key === "ArrowUp" || key === "ArrowLeft" || key === "PageUp") {
            e.preventDefault();
            this.goToSlide(Math.max(this.currentSlide - 1, 0));
          } else if (key === "Home") {
            e.preventDefault();
            this.goToSlide(0);
          } else if (key === "End") {
            e.preventDefault();
            this.goToSlide(this.slides.length - 1);
          }
        });
      }

      setupTouchNav() {
        let touchStartY = 0;
        document.addEventListener("touchstart", (e) => {
          touchStartY = e.touches[0].clientY;
        });
        document.addEventListener("touchend", (e) => {
          const diff = touchStartY - e.changedTouches[0].clientY;
          if (Math.abs(diff) > 50) {
            const next = diff > 0 ? this.currentSlide + 1 : this.currentSlide - 1;
            this.goToSlide(Math.max(0, Math.min(next, this.slides.length - 1)));
          }
        });
      }

      setupProgressBar() {
        this.progressBar = document.querySelector(".progress-bar");
      }

      updateProgressBar() {
        if (!this.progressBar) return;
        this.progressBar.style.width = `${((this.currentSlide + 1) / this.slides.length) * 100}%`;
      }

      setupNavDots() {
        this.navDotsContainer = document.querySelector(".nav-dots");
        if (!this.navDotsContainer) return;
        this.slides.forEach((_, i) => {
          const dot = document.createElement("button");
          dot.className = "nav-dot";
          dot.addEventListener("click", () => this.goToSlide(i));
          this.navDotsContainer.appendChild(dot);
        });
      }

      updateNavDots() {
        if (!this.navDotsContainer) return;
        this.navDotsContainer.querySelectorAll(".nav-dot").forEach((dot, i) => {
          dot.classList.toggle("active", i === this.currentSlide);
        });
      }

      setupBreadcrumbs() {
        const nav = document.createElement("nav");
        nav.className = "breadcrumb";
        document.body.prepend(nav);
        this.breadcrumbMap = [];
        this.slides.forEach((slide, slideIndex) => {
          const kicker = slide.querySelector(".section-kicker");
          if (!kicker) return;
          const label = kicker.textContent.replace(/^\d+\s*·\s*/, "").trim();
          if (!this.breadcrumbMap.some(b => b.label === label)) {
            this.breadcrumbMap.push({ label, slideIndex });
            const span = document.createElement("span");
            span.textContent = label;
            span.addEventListener("click", () => this.goToSlide(slideIndex));
            nav.appendChild(span);
          }
        });
        this.breadcrumbNav = nav;
        this.updateBreadcrumbs();
      }

      updateBreadcrumbs() {
        if (!this.breadcrumbNav || this.breadcrumbMap.length === 0) return;
        this.breadcrumbNav.querySelectorAll("span").forEach((span, i) => {
          const start = this.breadcrumbMap[i].slideIndex;
          const end = i + 1 < this.breadcrumbMap.length ? this.breadcrumbMap[i + 1].slideIndex : this.slides.length;
          const isActive = this.currentSlide >= start && this.currentSlide < end;
          span.classList.toggle("active", isActive);
          span.style.opacity = isActive ? "1" : "0.5";
        });
      }

      goToSlide(index) {
        this.currentSlide = index;
        this.slides[index].scrollIntoView({ behavior: "smooth" });
      }
    }

    new SlidePresentation();
  </script>
</body>
</html>
```

---

## 强制性的 JavaScript 功能

每个汇报文件必须包含：
1. **SlidePresentation 类** — 主控制器，包含：
- 键盘导航（方向键、空格、Page Up/Down）
- 触摸/滑动手势
- 鼠标滚轮导航
- 进度条更新
- 导航圆点
- **Breadcrumb 章节导航**（`setupBreadcrumbs()` + `updateBreadcrumbs()`）：从每张 slide 的 `.section-kicker` 自动提取章节名，在 `<body>` 顶部动态生成**唯一一个全局导航条**并绑定点击跳转。**禁止在 HTML 源码中手写 `<div class="breadcrumb">`**，否则会每张 slide 各渲染一个导致导航栏重复显示。
2. **Intersection Observer** — 滚动触发动效：
- 幻灯片进入视口时添加 `.visible` class
- 高效触发 CSS transition
3. **可选增强效果**（匹配选择的风格）：
- 自定义光标轨迹
- 粒子系统背景 (canvas)
- 视差效果
- 3D 悬停倾斜
- 磁吸按钮
- 数字递增动画
4. **浏览器内编辑**（默认包含，仅当用户明确要求锁定时跳过）：
- 编辑切换按钮（默认隐藏，通过悬停热区或按 `E` 键显示）
- 自动保存到 localStorage
- 导出/保存文件功能

---

## 图片处理流程

### 图片分类呈现策略

根据图片类型采用不同的展示方式（详见 [排版规范.md](排版规范.md)）：
```css
/* 架构图 — 全宽居中，可放大 */
.slide-image.architecture {
    display: block;
    margin: 0 auto;
    max-width: min(90vw, 1100px);
    max-height: min(55vh, 550px);
    cursor: zoom-in;
}
/* 流程图 — 撑满空间为主角 */
.slide-image.flowchart {
    display: block;
    margin: 0 auto;
    max-width: min(92vw, 1200px);
    max-height: min(60vh, 600px);
    cursor: zoom-in;
}
/* 截图/界面图 — 可选侧边展示或带边框卡片 */
.slide-image.screenshot {
    max-width: min(50vw, 600px);
    max-height: min(45vh, 400px);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
/* 数据图表 — 居中，下方配数据来源 */
.slide-image.chart {
    display: block;
    margin: 0 auto;
    max-width: min(85vw, 900px);
    max-height: min(50vh, 450px);
}
/* 引用说明/数据来源文字 */
.image-caption {
    font-size: var(--small-size);
    color: var(--text-secondary, #888);
    text-align: center;
    margin-top: clamp(0.3rem, 0.5vh, 0.5rem);
}
```
### Markdown 图片处理

从 Markdown 文档转换时，识别 `![描述](路径)` 语法：
1. **路径处理**：优先使用相对路径。如果路径中的文件不存在，搜索当前目录及子目录
2. **图片类型识别**：根据文件名和上下文自动分类（架构图、流程图、截图等），应用对应的展示策略
3. **缺失图片处理**：如果图片文件不存在，用占位元素替代，并标注缺失信息

### 图片点击放大（Lightbox）

所有图片默认添加点击放大功能（零外部依赖，纯 JS 实现）：
```javascript
class ImageLightbox {
    constructor() {
        this.setupLightbox();
    }
    setupLightbox() {
        // 为所有图片添加点击放大     document.querySelectorAll('.slide img').forEach(img => {
            img.style.cursor = 'zoom-in';
            img.addEventListener('click', (e) => {
                e.stopPropagation();
                this.open(img.src, img.alt);
            }
            );
        }
        );
        // 点击遮罩层关闭     this.overlay = document.createElement('div');
        this.overlay.className = 'lightbox-overlay';
        this.overlay.innerHTML = '<div class="lightbox-content"><img src="" alt="" /><p class="lightbox-caption"></p><button class="lightbox-close">✕</button></div>';
        this.overlay.addEventListener('click', () => this.close());
        document.body.appendChild(this.overlay);
    }
    open(src, alt) {
        const img = this.overlay.querySelector('img');
        const caption = this.overlay.querySelector('.lightbox-caption');
        img.src = src;
        img.alt = alt;
        caption.textContent = alt || '';
        this.overlay.classList.add('active');
    }
    close() {
        this.overlay.classList.remove('active');
    }
}
// Lightbox 样式（内联在 <style> 中）
/* .lightbox-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.9);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
}
.lightbox-overlay.active {
    opacity: 1;
    pointer-events: auto;
}
.lightbox-overlay img {
    max-width: 90vw;
    max-height: 85vh;
    object-fit: contain;
}
.lightbox-caption {
    color: #ccc;
    text-align: center;
    margin-top: 0.5rem;
    font-size: clamp(0.75rem, 1vw, 0.9rem);
}
.lightbox-close {
    position: absolute;
    top: 2rem;
    right: 2rem;
    color: #fff;
    font-size: clamp(1.5rem, 3vw, 2rem);
    background: none;
    border: none;
    cursor: pointer;
}
*/
```
### 图片处理命令
**依赖：** `pip install Pillow`
```python
from PIL import Image, ImageDraw

# 圆形裁剪（用于现代/简洁风格的 logo）
def crop_circle(input_path, output_path):
    img = Image.open(input_path).convert('RGBA')
    w, h = img.size
    size = min(w, h)
    left, top = (w - size) // 2, (h - size) // 2
    img = img.crop((left, top, left + size, top + size))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    img.putalpha(mask)
    img.save(output_path, 'PNG')

# 缩小（用于过大图片，避免 HTML 体积膨胀）
def resize_max(input_path, output_path, max_dim=1200):
    img = Image.open(input_path)
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    img.save(output_path, quality=85)
```
| 场景 | 操作 |
|------|------|
| 方形 logo 配圆角风格 | `crop_circle()` |
| 图片 > 1MB | `resize_max(max_dim=1200)` |
| 宽高比不对 | 手动 `img.crop()` 裁剪 |  处理后的图片保存时加 `_processed` 后缀，永远不覆盖原始文件。

---

## 表格处理规范

### MD 表格自动转换

从 Markdown 的表格语法自动转换为 HTML 表格时，遵循以下规范：
1. **表头自动左对齐**（非居中），因为中文表格左对齐阅读效率更高
2. **自适应宽度** — `width: 100%`，不通列由内容决定宽度
3. **表头有底部分隔线**，用强调色增强视觉层次
4. **正文行之间有极淡分隔线**，减轻视觉疲劳
5. **小字号表格** — 当表格列数 ≥ 5 或总行数 ≥ 10 时，字号适当缩小 `font-size: clamp(0.65rem, 1vw, 0.85rem)`

### 表格嵌入幻灯片的排版规则

表格必须放在 `.slide-content` 内部，且遵循：
- 表格前后各留至少 `--content-gap` 的间距
- 表格的 `max-height` 受限于幻灯片剩余空间
- 如果表格内容过多导致溢出，必须拆分到多张幻灯片
- 中文字段名如需换行，使用 `white-space: nowrap` 确保表头不折行

---

## 卡片 hover 增强规范

所有卡片、面板、表格行等可交互元素必须统一应用以下 hover 效果。**使用 `@media (hover: hover) and (pointer: fine)` 包裹，避免触屏设备误触发。**

### 分级 hover 规范
| 元素类型 | hover 效果 | 说明 |
|----------|-----------|------|
| 卡片/面板 | `translateY(-5px)` + inset 发光边框 + 复合阴影增强 | 上浮感，"被选中"信号 |
| 表格行 | 背景色微变（主题色 5-10% 透明度）+ 首列文字变强调色加粗 + 可选左侧出现色条 | 视觉追踪引导 |
| 节点/标签 | `scale(1.05)` + 阴影扩散 | 轻量反馈 |
| 按钮/操作 | `translateY(-2px)` + 背景色加深 | 可点击暗示 |

### 通用卡片 hover CSS
```css
/* 基础卡片样式 */
.card {
    border-radius: 12px;
    background: var(--bg-card);
    border: 1px solid var(--border-card, var(--line));
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    transition: transform 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
}
/* 增强悬停 — inset发光 + 复合阴影 */
@media (hover: hover) and (pointer: fine) {
    .card:hover {
        transform: translateY(-5px);
        border-color: rgba(var(--accent-rgb, 183, 25, 43), 0.3);
        box-shadow:       0 20px 50px rgba(0, 0, 0, 0.12),
        /* 外阴影 */
        0 0 0 3px rgba(var(--accent-rgb, 183, 25, 43), 0.06),
        /* 扩散光晕 */
        inset 0 0 0 1px rgba(var(--accent-rgb, 183, 25, 43), 0.08);
        /* 内部发光边框 */
    }
}
```
### 表格行 hover CSS
```css
@media (hover: hover) and (pointer: fine) {
    table tbody tr:hover {
        background: rgba(var(--accent-rgb), 0.06);
        box-shadow: inset 4px 0 0 var(--accent);
        /* 左侧强调色条 */
    }
    table tbody tr:hover td:first-child {
        color: var(--accent);
        font-weight: 900;
    }
}
```
---

## 背景纹理增强

根据汇报风格和场景，自动选用以下背景纹理方案。所有纹理通过 `body::before` 伪元素实现，不影响内容层级。

### 网格纹理（推荐作为默认基准）
```css
body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:     linear-gradient(rgba(24, 32, 40, 0.035) 1px, transparent 1px),     linear-gradient(90deg, rgba(24, 32, 40, 0.035) 1px, transparent 1px);
    background-size: 42px 42px;
    mask-image: linear-gradient(to bottom, transparent 0%, black 16%, black 72%, transparent 100%);
    z-index: 0;
}
```
### 渐变光晕（适合商务汇报）
```css
body {
    background:     radial-gradient(circle at 80% 8%, rgba(var(--accent-rgb), 0.08), transparent 30rem),     linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 48%, var(--bg-primary) 100%);
}
```
### 使用规则
1. 纹理叠加使用 `body::before` 伪元素，配合 `pointer-events: none`
2. 纹理透明度控制在 0.03-0.08，微妙而不突兀
3. 深色背景时纹理透明度可适当提高
4. 不同风格自动适配：技术风→网格纹理，商务风→渐变光晕，编辑风→噪点纹理

---

## 打印样式基准

所有生成 HTML 文件必须包含基础 `@media print` 规则：
```css
@media print {
    /* 隐藏交互元素 */
    .nav, .progress-bar, .nav-dots, .keyboard-hint,   .edit-toggle, .edit-toast, .edit-panel {
        display: none !important;
    }
    /* 移除背景效果（省墨）*/
    body {
        background: #fff !important;
    }
    body::before {
        display: none;
    }
    .hero, .finale {
        color: #111 !important;
        background: #fff !important;
    }
    .hero::before, .hero::after, .finale::before, .finale::after {
        display: none;
    }
    /* 展开隐藏内容 */
    .finale-detail, .expandable-content, [hidden].print-show {
        max-height: none !important;
        opacity: 1 !important;
        overflow: visible !important;
        transform: none !important;
    }
    /* 移除动画 */
    .reveal {
        opacity: 1 !important;
        transform: none !important;
    }
    /* 分页控制 */
    section {
        page-break-inside: avoid;
    }
    h2, h3 {
        page-break-after: avoid;
    }
}
```
---

## 排版规范引用

在生成每一张幻灯片的内容时，必须参考 [排版规范.md](排版规范.md)，按照内容类型选择对应的排版策略。核心原则：
| 内容类型 | 排版策略 |
|----------|----------|
| 表格页面 | h2 左锚点 + 表格自然填充 |
| 图文混排 | h2 左锚点 + 左右双栏 |
| 稀疏内容（一句描述+一张图） | h2 左锚点 + 图片撑满为主角 |
| 卡片网格 | h2 左锚点 + 卡片均匀填满 |
| 强调块 | 使用 Statement 组件 |
| 数据洞察 | 使用 Insight 组件组 |
| 阶段回顾 | 使用 Timeline 组件 |
| 进度清单 | 使用 Check List 组件 |
| 风险说明 | 使用 Risk Card 组件 |

---

## 代码质量
**注释：** 每个区块都需要清晰的注释，说明其作用及如何修改。
**无障碍：**
- 语义化 HTML（`<section>`, `<nav>`, `<main>`）
- 完整的键盘导航支持
- 必要时添加 ARIA 标签
- `prefers-reduced-motion` 支持（已在视口适配.css 中包含）

## 文件结构

单个汇报：
```
汇报文件名.html        # 自包含，所有 CSS/JS 内联
assets/                 # 仅图片，如有
```
同一项目多次汇报：
```
[名称].html
[名称]-assets/
```
