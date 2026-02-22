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
| Total skills | `39` |
| `pywayne` skills | `34` |
| General skills | `5` (`deep-think`, `send-email`, `shell-shortcuts`, `tutor`, `proactive-agent`) |
| Canonical rules | `CLAUDE.md` |
| Agent handoff doc | `AGENTS.md` |

## 🗂️ Repository Layout

- `pywayne/` - skills aligned with `pywayne` source modules
- `send-email/` - SMTP email skill with templates and attachments
- `deep-think/` - deep analysis and decomposition workflow
- `shell-shortcuts/` - cross-platform terminal shortcut commands (`proxy_on`, `goto`, `gpu`)
- `tutor/` - math tutoring skill for generating educational videos with Manim
- `proactive-agent/` - proactive agent architecture (WAL, Working Buffer, etc.)
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
- `tutor`: math tutoring skill with Manim video generation
- `proactive-agent`: proactive agent architecture (WAL, Working Buffer, etc.)

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
