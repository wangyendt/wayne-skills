# wayne-skills

[🇺🇸 English](README.md) | [🇨🇳 简体中文](README_ch.md)

> Build better AI coding behavior with production-oriented skills.

`wayne-skills` is a curated skill pack for AI coding agents (Codex/Claude style), centered on the `pywayne` ecosystem.  
It converts practical modules into reusable `SKILL.md` playbooks so agents can pick better APIs, workflows, and constraints with less prompting.

## ✨ Why It Stands Out

- 🧭 **Source-aligned**: skills map directly to real module paths
- 🧱 **Stable conventions**: naming and structure stay predictable
- 🛡️ **Lower-risk outputs**: fewer ad-hoc decisions in code generation
- 🚀 **Broad coverage**: CV, VIO, DSP, LLM, statistics, automation, integrations

## 📌 At A Glance

| Metric | Value |
| --- | --- |
| Total skills | `41` |
| `pywayne` skills | `34` |
| General skills | `7` (`deep-think`, `send-email`, `shell-shortcuts`, `tutor-general`, `tutor-math-geometry`, `proactive-agent`, `week-report-system`) |
| Canonical rules | `CLAUDE.md` |
| Agent handoff doc | `AGENTS.md` |

## 🗂️ Repository Layout

- `pywayne/` - skills aligned with `pywayne` source modules
- `send-email/` - SMTP email skill with templates and attachments
- `deep-think/` - deep analysis and decomposition workflow
- `shell-shortcuts/` - cross-platform terminal shortcut commands (`proxy_on`, `goto`, `gpu`)
- `tutor-general/` - general tutoring skill for generating educational videos with Manim
- `tutor-math-geometry/` - math geometry tutoring skill with interactive animations
- `proactive-agent/` - proactive agent architecture (WAL, Working Buffer, etc.)
- `week-report-system/` - AI-powered weekly work report system with Git-based conversation logging
- `CLAUDE.md` - naming, structure, and documentation rules
- `AGENTS.md` - concise instructions for external models/agents

## 🔗 Mapping Rule

`source module path -> skill directory -> skill name`

Examples:

- `pywayne/llm/chat_bot.py` -> `pywayne/llm/chat-bot/` -> `pywayne-llm-chat-bot`
- `pywayne/vio/SE3.py` -> `pywayne/vio/se3/` -> `pywayne-vio-se3`
- `pywayne/cv/apriltag_detector.py` -> `pywayne/cv/apriltag-detector/` -> `pywayne-cv-apriltag-detector`

## 🧠 Skill Domains

### General

- `deep-think`: structured deep reasoning workflow
- `send-email`: SMTP sending with HTML templates and attachments
- `shell-shortcuts`: set up `proxy_on/proxy_off/goto/gpu` and optional Conda autostart
- `tutor-general`: general tutoring skill with Manim video generation
- `tutor-math-geometry`: math geometry tutoring skill with interactive animations
- `proactive-agent`: proactive agent architecture (WAL, Working Buffer, etc.)
- `week-report-system`: AI weekly work report system — auto-records every conversation to GitHub and generates structured weekly reports on demand

## ⭐ Featured: Week Report System

> Automatically turn your daily AI conversations into polished weekly reports.

`week-report-system` silently logs every user–AI exchange (compressed + summarized) to a private GitHub repository, organized by year and week. At any point, ask it to generate a full weekly report — it reads the conversation logs, categorizes work by project, extracts key metrics, and outputs a structured markdown report.

**Repository structure:**
```
week-reports/
├── 2026/
│   └── week12/
│       ├── 20260318-a1b2c3d4.txt      # brief conversation log
│       ├── 20260319-e5f6g7h8.txt
│       └── report-20260320-143022.md  # generated weekly report
```

**How to use:**
- Just chat normally — conversations are recorded in the background
- Say `写周报` / `generate week report` to get a full report
- Say `总结2026年第12周的工作` to report on a specific week

**Install across all AI agents on your machine** with [Skill Manager](https://github.com/wangyendt/skillmanager):
```bash
npm -g install @wang121ye/skillmanager
skillmanager install --global   # select week-report-system from the list
```
One install, works for Claude, ChatGPT, and any other agent that supports skills.

### pywayne Domains

- 🛠️ Developer Tools: `tools`, `helper`, `bin/*`, `crypto`
- 📊 Data & Math: `dsp`, `maths`, `statistics`, `data-structure`, `plot`
- 🤖 Vision & Robotics: `cv/*`, `vio/*`, `calibration/*`, `ahrs/*`, `visualization/*`
- 🔌 Platform & Integration: `adb/*`, `cross-comm`, `aliyun-oss`
- 💬 Product Interfaces: `llm/*`, `lark-*`, `tts`, `gui`

For full details, browse all `**/SKILL.md` files.

## ✅ Update Checklist

When adding/updating skills:

1. Follow naming rules in `CLAUDE.md`
2. Keep directory names in hyphen-case
3. Keep language links valid (`README.md` <-> `README_ch.md`)
4. Sync counts and domain text with actual `SKILL.md` files

## 📄 License

MIT. See `LICENSE`.
