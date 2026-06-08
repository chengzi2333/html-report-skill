[简体中文](README.md) | [English](README_EN.md)

# HTML Report Skill

> Turn Markdown documents and PowerPoint content into polished, interactive, presentation-ready HTML reports.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub Release](https://img.shields.io/github/v/release/chengzi2333/html-report-skill)

![HTML Report Skill demo](assets/hero.png)

The repository root is an installable Agent Skill. It is optimized for Chinese work reports, project presentations, technical talks, and document visualization. Generated presentations are self-contained HTML files that open directly in a browser.

Version **1.0.0** is an MVP public preview.

## Platform support

“Agent Skills support” means the platform can discover `SKILL.md`. “Project verification” means this project has completed the full install, trigger, generation, validation, and delivery workflow on that platform.

| Platform | Agent Skills support | Project verification | Recommended location |
|---|---|---|---|
| Codex CLI / App | Supported | End-to-end verified | `~/.codex/skills/html-report-skill` |
| Antigravity | Supported | End-to-end verified | `.agents/skills/html-report-skill` or `~/.gemini/config/skills/html-report-skill` |
| Claude Code | Supported | Full regression pending | `~/.claude/skills/html-report-skill` |
| Cursor | Supported | Full regression pending | `~/.cursor/skills/html-report-skill` |

## Quick start

### Codex

```bash
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.codex/skills/html-report-skill
```

Start a new Codex session and ask:

```text
Use HTML Report Skill to turn this Markdown document into
a Chinese HTML presentation of about 10 slides.
```

## Installation

Clone the complete repository into the skills directory for your platform. Do not copy only `SKILL.md`; the workflow also reads `references/` and calls scripts in `scripts/`.

### Codex CLI / App

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.codex/skills/html-report-skill
```

### Antigravity

Workspace:

```bash
mkdir -p .agents/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  .agents/skills/html-report-skill
```

User-level:

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

Claude Code supports Agent Skills, but this project has not completed a full end-to-end regression on Claude Code yet.

### Cursor

```bash
mkdir -p ~/.cursor/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.cursor/skills/html-report-skill
```

Cursor supports Agent Skills, but this project has not completed a full end-to-end regression on Cursor yet.

### Update

Run `git pull` inside the installed skill directory, then start a new agent session.

## Key capabilities

- **Preview before generation**: generate three distinct visual previews before building the final report.
- **Chinese typography**: font fallbacks, table alignment, content-density rules, and section-heading patterns.
- **Content reliability**: re-read the source and report coverage for headings, images, tables, code blocks, and lists.
- **Quality gate**: validate viewport, layout, interactions, print styles, typography, and responsive rules.
- **Real interactions**: modal dialogs, tooltips, image lightbox, evidence carousel, and in-browser editing.
- **Two browsing modes**: presentation paging and continuous reading.
- **Multi-platform prompts**: use native structured questions where available and fall back safely.
- **Delivery workflow**: confirm the HTML before deployment, sharing, or PDF export.

## Example request

```text
Use HTML Report Skill to turn README.md into a project presentation.
Use 12-15 slides, presentation paging, and high-density reading.
```

## Installation verification

```bash
test -f SKILL.md
test -f references/style-presets/index.json
test -f scripts/validate.py
test -f scripts/content_coverage.py
```

The `scripts/` directory contains runtime scripts required by the skill. Project regression tests are development assets and are not included in the installable package.

## Known limitations

- Automated content coverage currently focuses on the Markdown path.
- `validate.py` is primarily static validation and does not replace full multi-viewport visual testing.
- PDF export requires Playwright; Vercel deployment requires the corresponding CLI and account environment.
- Claude Code and Cursor support Agent Skills, but full project regression is still pending.
- The current typography rules primarily target Chinese presentations.

## Feedback

Use [GitHub Issues](https://github.com/chengzi2333/html-report-skill/issues) for reproducible bugs and feature requests.

Include the platform and version, input type, sanitized source fragment, generated HTML or screenshot, reproduction steps, and validation output.

Do not report security vulnerabilities through a public issue. See [SECURITY.md](SECURITY.md).

## License and attribution

This project is based on [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides), created by Zara Zhang and released under the MIT License. The original copyright notice is preserved:

```text
Copyright (c) 2025 Zara Zhang
```

This is not an official upstream release. See [LICENSE](LICENSE).
