[简体中文](README.md) | [English](README_EN.md)

# HTML Report Skill

> 将 Markdown 文档或 PowerPoint 内容转换为精美、可交互、可直接投屏的中文 HTML 汇报。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub Release](https://img.shields.io/github/v/release/chengzi2333/html-report-skill)

![HTML Report Skill 示例](assets/hero.png)

本仓库根目录就是可安装的 Agent Skill。它面向中文工作汇报、项目演示、技术分享和文档可视化场景，生成零构建、浏览器直接打开的单文件 HTML 演示文稿。

当前版本为 **1.0.0 MVP 公开试用版**。

## 支持平台

“官方 Skills 支持”表示平台能够发现 `SKILL.md`；“本项目验证状态”表示本项目是否已经完成安装、触发、生成、验证和交付的完整流程。

| 平台 | 官方 Skills 支持 | 本项目验证状态 | 推荐安装位置 |
|---|---|---|---|
| Codex CLI / App | 支持 | 已完成端到端验证 | `~/.codex/skills/html-report-skill` |
| Antigravity | 支持 | 已完成端到端验证 | `.agents/skills/html-report-skill` 或 `~/.gemini/config/skills/html-report-skill` |
| Claude Code | 支持 | 待完成端到端回归 | `~/.claude/skills/html-report-skill` |
| Cursor | 支持 | 待完成端到端回归 | `~/.cursor/skills/html-report-skill` |

平台更新可能影响 skill 发现、上下文注入或原生提问能力。遇到问题时，请同时提供平台名称和版本。

## 30 秒快速开始

### Codex

```bash
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.codex/skills/html-report-skill
```

新开一个 Codex 会话，然后输入：

```text
请使用 HTML Report Skill，把这份 Markdown 转成 10 页左右的中文汇报 HTML。
```

### 其他平台

克隆仓库到对应平台的 skills 目录，保证最终结构为：

```text
<skills-directory>/html-report-skill/SKILL.md
```

必须保留整个仓库目录，不要只复制 `SKILL.md`，因为生成流程还会读取 `references/` 并调用 `scripts/`。

## 安装

### Codex CLI / App

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.codex/skills/html-report-skill
```

验证：

```bash
test -f ~/.codex/skills/html-report-skill/SKILL.md && echo "安装成功"
```

### Antigravity

工作区级：

```bash
mkdir -p .agents/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  .agents/skills/html-report-skill
```

用户级：

```bash
mkdir -p ~/.gemini/config/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.gemini/config/skills/html-report-skill
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.claude/skills/html-report-skill
```

Claude Code 支持 Agent Skills，但本项目尚未完成该平台的完整端到端回归。

### Cursor

```bash
mkdir -p ~/.cursor/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.cursor/skills/html-report-skill
```

Cursor 支持 Agent Skills，但本项目尚未完成该平台的完整端到端回归。如果 Settings 中可见但会话没有加载，请重启 Cursor 并新建 Agent 会话。

### 更新

进入已安装目录后执行：

```bash
git pull
```

更新后建议新开会话。

### 卸载

删除对应平台 skills 目录中的 `html-report-skill` 文件夹即可。

## 核心能力

- **先预览再生成**：生成 3 套差异化风格预览，用户确认后才进入正式生成。
- **中文排版优化**：提供中文字体回退、表格对齐、内容密度和章节标题规范。
- **内容可靠性**：生成前回读原文，交付时检查标题、图片、表格、代码块和列表覆盖情况。
- **质量门禁**：使用 `validate.py` 检查视口、布局、交互、打印、字体和响应式规则。
- **真实交互**：支持 modal、tooltip、图片 lightbox、证据轮播和浏览器内编辑。
- **双浏览模式**：支持投屏翻页和连续滚动阅读。
- **多平台提问适配**：按平台使用原生选项能力，不可用时安全降级为普通短问。
- **交付闭环**：HTML 验收后再进入分享、部署或 PDF 导出选择。

## 使用方式

提供 Markdown 文件或 PPT，并描述用途、篇幅和阅读密度。例如：

```text
请使用 HTML Report Skill，把 README.md 转成项目演示汇报。
控制在 12-15 页，使用翻页模式，内容适合高密度阅读。
```

流程包括：

1. 检测输入类型和运行环境。
2. 确认用途、篇幅、内容密度和浏览方式。
3. 生成并打开 3 套风格预览。
4. 用户选择风格或要求重新生成。
5. 生成正式 HTML。
6. 执行内容覆盖率和静态质量验证。
7. 用户确认后选择分享、部署或 PDF 导出。

## 本地验证

```bash
python3 scripts/test_validate.py
python3 scripts/test_content_coverage.py
python3 scripts/test_export_pdf_security.py

for f in scripts/*.py; do
  python3 -m py_compile "$f"
done

bash -n scripts/*.sh
```

## 已知限制

- 自动内容覆盖率当前主要服务 Markdown 主路径；PPT 仍需结合提取摘要和人工复核。
- `validate.py` 以静态规则检查为主，不能替代完整的多视口视觉验收。
- PDF 导出需要 Playwright；Vercel 部署需要对应 CLI 和账号环境。
- Claude Code 和 Cursor 已支持 Agent Skills 格式，但本项目尚未完成这两个平台的完整回归。
- 当前主要针对中文汇报排版优化，英文长文档效果仍需更多反馈。

## 反馈

请通过 [GitHub Issues](https://github.com/chengzi2333/html-report-skill/issues) 提交问题或建议。

为了便于复现，请尽量提供：

- 使用平台和版本。
- 输入类型：Markdown 或 PPT。
- 可脱敏的输入片段。
- 生成的 HTML、截图或问题页面。
- 完整复现步骤。
- `validate.py` 和内容覆盖率输出。

安全漏洞不要提交公开 Issue，请阅读 [SECURITY.md](SECURITY.md)。

## License 与致谢

本项目基于 [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) 改造，保留原作者 Zara Zhang 的 MIT License 和版权声明：

```text
Copyright (c) 2025 Zara Zhang
```

本项目不是上游官方版本。详见 [LICENSE](LICENSE)。

