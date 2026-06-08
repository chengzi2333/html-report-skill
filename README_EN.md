[简体中文](README.md) | [English](README_EN.md)

# HTML Report Skill

> Turn Markdown or PowerPoint content into Chinese HTML presentations that are ready to present, share, and edit.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub Release](https://img.shields.io/github/v/release/chengzi2333/html-report-skill)

![HTML Report Skill demo](assets/hero.png)

Many document-to-presentation tools stop at generating pages. A real work presentation needs more: Chinese typography must remain readable, tables must stay aligned, images should be inspectable, source content must not disappear, and the result needs a quality gate before it is shared or exported.

HTML Report Skill addresses that workflow. Built on the excellent open-source project [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides), it adds the reliability, interaction, and delivery rules needed for Chinese work reports, project presentations, technical talks, and document visualization.

Current version: **1.0.0 MVP public preview**.

## Why use it

- **Preview before generation**: see three real HTML style previews before the final report is built. Rejecting all three starts a new direction instead of forcing a choice.
- **Chinese-first layout rules**: font fallbacks, table alignment, section headings, content density, sparse-page centering, and dense-reading layouts.
- **Content reliability**: re-read the source before generation and check coverage for headings, images, tables, code blocks, and lists at delivery time.
- **Real interactions**: modal dialogs, tooltips, image lightbox, evidence carousel, and in-browser editing.
- **A quality gate**: `validate.py` checks viewport behavior, layout, interactions, print styles, typography, responsiveness, and whether interaction claims are actually implemented.
- **A complete delivery path**: open the report in the user's local browser, confirm it, then continue to sharing, deployment, or PDF export.

## What this adds to frontend-slides

This is not an official upstream release. It preserves the HTML slide approach, phase-based workflow, style-preset foundation, PPT conversion basics, and Vercel/PDF delivery ideas from frontend-slides, while addressing common gaps in Chinese work presentations.

| Common gap | Enhancement in this project |
|---|---|
| Architecture diagrams and screenshots are hard to inspect | Image-specific presentation rules, click-to-zoom lightbox, and source captions |
| Three style choices can still look too similar | A deliberate mix of safe preset, bold hybrid, and creative direction |
| Chinese tables are hard to scan | Left-aligned content, stronger headers, and density rules for large tables |
| Chinese text falls back to unsuitable system fonts | Chinese font fallback chains, line-height rules, and no first-line indentation |
| Interactions are described but not implemented | Declared modals, tooltips, and carousels must have working CSS and JavaScript |
| Images, tables, or code blocks may disappear between analysis and generation | Re-read the original source before generation and report content coverage at delivery |
| Generated output has no objective quality gate | `validate.py` blocks delivery below 80 and reports remaining issues above the threshold |
| Export starts before the user has checked the result | Phase 5 confirms the demo first; Phase 6 handles sharing and export afterward |

## 30-second quick start

Install with the universal Agent Skills installer:

```bash
npx skills@latest add chengzi2333/html-report-skill -g
```

To check discovery without installing:

```bash
npx skills@latest add chengzi2333/html-report-skill --list
```

Start a new agent session and ask:

```text
Use HTML Report Skill to turn this Markdown document into a Chinese HTML presentation.
```

The workflow will ask about purpose, length, content density, browsing mode, and visual style. You do not need to decide everything in the first prompt.

## Installation

### Option A: npx, recommended

```bash
npx skills@latest add chengzi2333/html-report-skill -g
```

Target a specific agent:

```bash
npx skills@latest add chengzi2333/html-report-skill -g -a codex
npx skills@latest add chengzi2333/html-report-skill -g -a antigravity
npx skills@latest add chengzi2333/html-report-skill -g -a claude-code
npx skills@latest add chengzi2333/html-report-skill -g -a cursor
```

Install into the current project:

```bash
npx skills@latest add chengzi2333/html-report-skill
```

`npx skills` is the universal installer maintained by `vercel-labs/skills`; this repository does not publish its own npm package. The installer detects supported agent runtimes and installs the complete skill directory containing `SKILL.md`.

### Option B: manual clone

Use this option if you do not want to use npx or want full control over the installation path.

Codex:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.codex/skills/html-report-skill
```

Antigravity:

```bash
mkdir -p .agents/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  .agents/skills/html-report-skill
```

Claude Code:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.claude/skills/html-report-skill
```

Cursor:

```bash
mkdir -p ~/.cursor/skills
git clone https://github.com/chengzi2333/html-report-skill.git \
  ~/.cursor/skills/html-report-skill
```

The final structure must be:

```text
<skills-directory>/html-report-skill/SKILL.md
```

Do not copy only `SKILL.md`. The workflow also needs `references/` and `scripts/`.

## Platform status

“Agent Skills support” means the platform can discover `SKILL.md`. “Project verification” means this project has completed the full install, trigger, generation, validation, and delivery workflow on that platform.

| Platform | Agent Skills support | Project verification | Notes |
|---|---|---|---|
| Codex CLI / App | Supported | End-to-end verified | One of the primary test platforms |
| Antigravity | Supported | End-to-end verified | One of the primary test platforms |
| Claude Code | Supported | Full regression pending | Installable; project-specific regression is still needed |
| Cursor | Supported | Full regression pending | Installable; project-specific regression is still needed |

Platform updates may affect skill discovery, context injection, or native question tools. Include the platform name and version when reporting an issue.

## Usage

Give the agent a Markdown file, README, proposal, or PPT and ask for an HTML presentation:

```text
Use HTML Report Skill to turn README.md into a project presentation in HTML.
```

Typical workflow:

1. Detect the source type and runtime environment.
2. Confirm purpose, length, content density, and browsing mode.
3. Generate and open three style previews.
4. Select a style, mix approved elements, or request a new direction.
5. Generate the final HTML.
6. Run content coverage and static quality validation.
7. Confirm the result, then choose sharing, deployment, or PDF export.

## Installation verification

Run inside the installed skill directory:

```bash
test -f SKILL.md
test -f references/style-presets/index.json
test -f scripts/validate.py
test -f scripts/content_coverage.py
```

The `scripts/` directory contains runtime scripts only. Development regression tests are not included in the installable skill.

## Updating and uninstalling

For a manual Git installation:

```bash
cd <skills-directory>/html-report-skill
git pull
```

For an installation managed by `npx skills`, run the install command again and follow the installer prompts.

To uninstall, remove the `html-report-skill` directory from the relevant skills location.

## Known limitations

- Automated content coverage currently focuses on the Markdown path; PPT still requires extracted summaries and manual review.
- `validate.py` is primarily a static validator and does not replace complete multi-viewport visual testing.
- PDF export requires Playwright; Vercel deployment requires the corresponding CLI and account environment.
- Claude Code and Cursor support Agent Skills, but this project has not completed full end-to-end regression on those platforms.
- Typography and layout rules currently prioritize Chinese presentations.

## Feedback

Use [GitHub Issues](https://github.com/chengzi2333/html-report-skill/issues) for reproducible bugs and feature requests.

Please include the platform and version, input type, sanitized source fragment, generated HTML or screenshot, reproduction steps, and validation output.

Do not report security vulnerabilities through a public issue. See [SECURITY.md](SECURITY.md).

## License and attribution

This project is based on [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides), created by Zara Zhang and released under the MIT License. The original copyright notice is preserved:

```text
Copyright (c) 2025 Zara Zhang
```

This is not an official upstream release. See [LICENSE](LICENSE).
