# wayne-skills

[English](README.md) | [简体中文](README_ch.md)

> Reusable playbooks, traceable workflows, practical helpers.

## ✨ Project Goal

`wayne-skills` maintains skills and their supporting scripts for AI agents such as Codex, Claude Code, and OpenClaw. It includes general workflows and skills mapped to the `pywayne` ecosystem; it does not maintain the `pywayne` library implementation. Installing a skill does not automatically install dependencies, enable host hooks, or verify every runtime.

## 📌 At a Glance

| Metric | Value |
| --- | --- |
| Total skills | `47` |
| `pywayne` skills | `35` |
| General skills | `12` |
| Canonical rules | [CLAUDE.md](CLAUDE.md) |
| Agent entry point | [AGENTS.md](AGENTS.md) |

Counts cover source `**/SKILL.md` files, excluding ignored agent-installation mirrors such as `.agents/`, `.claude/`, and `.cursor/`.

## 🗂️ Repository Layout

- `pywayne/`: source-aligned library skills, grouped by domain below.
- Top-level skill folders: general workflows, each with `SKILL.md` and optional scripts/references/assets.
- `learning-tutor/`: interactive teaching plus local capture, outbox, and synchronization helpers.
- `CLAUDE.md` / `AGENTS.md`: repository conventions and agent entry instructions.

## 🔗 Naming and Directory Rules

Map `source module path → skill directory → skill name`; use lowercase hyphen-case for new skill names and directories.

- `pywayne/llm/chat_bot.py` → `pywayne/llm/chat-bot/` → `pywayne-llm-chat-bot`
- `pywayne/vio/SE3.py` → `pywayne/vio/se3/` → `pywayne-vio-se3`
- General skills live in their own top-level folders; they do not require a pywayne prefix.

The catalog links to actual paths, including the existing `pywayne/vio/SO3/` path. No legacy directory was renamed in this update.

## 🧠 Skill Catalog

### General

| Skill Name | Path | Purpose |
| --- | --- | --- |
| `alapi` | [alapi/](alapi/SKILL.md) | Route ALAPI requests using the bundled API catalog. |
| `android-app-publisher` | [android-app-publisher/](android-app-publisher/SKILL.md) | Lightweight client for APK publication, latest releases, and QR codes; the Docker API lives in a separate server repository. |
| `awesome-docs` | [awesome-docs/](awesome-docs/SKILL.md) | Organize architecture, books, references, plans, roadmaps, todos, and technical records. |
| `deep-think` | [deep-think/](deep-think/SKILL.md) | Structure deep analysis and problem decomposition. |
| `learning-tutor` | [learning-tutor/](learning-tutor/SKILL.md) | Teach interactively with evidence, local capture, and resumable records. |
| `proactive-agent` | [proactive-agent/](proactive-agent/SKILL.md) | Design proactive agents with WAL and working buffers. |
| `research-paper-deep-dive` | [research-paper-deep-dive/](research-paper-deep-dive/SKILL.md) | Explain papers, evidence, context, and reproducible methods. |
| `send-email` | [send-email/](send-email/SKILL.md) | Send SMTP email with templates and attachments. |
| `shell-shortcuts` | [shell-shortcuts/](shell-shortcuts/SKILL.md) | Configure cross-platform terminal shortcuts. |
| `tutor-general` | [tutor-general/](tutor-general/SKILL.md) | Produce narrated educational videos with Motion Canvas. |
| `tutor-math-geometry` | [tutor-math-geometry/](tutor-math-geometry/SKILL.md) | Explain math with HTML, geometry animation, and narration. |
| `week-report-system` | [week-report-system/](week-report-system/SKILL.md) | Organize work materials and produce weekly reports. |

### Developer tools

| Skill Name | Path | Purpose |
| --- | --- | --- |
| `pywayne-bin-cmdlogger` | [pywayne/bin/cmdlogger/](pywayne/bin/cmdlogger/SKILL.md) | Record a command’s input and output. |
| `pywayne-bin-gettool` | [pywayne/bin/gettool/](pywayne/bin/gettool/SKILL.md) | Fetch C++ tools and libraries. |
| `pywayne-bin-gitstats` | [pywayne/bin/gitstats/](pywayne/bin/gitstats/SKILL.md) | Analyze Git commit activity. |
| `pywayne-bin-toolsetup` | [pywayne/bin/toolsetup/](pywayne/bin/toolsetup/SKILL.md) | Configure development commands and tool environments. |
| `pywayne-crypto` | [pywayne/crypto/](pywayne/crypto/SKILL.md) | Use string and byte encryption helpers. |
| `pywayne-helper` | [pywayne/helper/](pywayne/helper/SKILL.md) | Manage shared project configuration. |
| `pywayne-tools` | [pywayne/tools/](pywayne/tools/SKILL.md) | Use console, timing, configuration, and utility helpers. |

### Data and mathematics

| Skill Name | Path | Purpose |
| --- | --- | --- |
| `pywayne-data-structure` | [pywayne/data-structure/](pywayne/data-structure/SKILL.md) | Use logical trees, union-find, and XML helpers. |
| `pywayne-dsp` | [pywayne/dsp/](pywayne/dsp/SKILL.md) | Filter and analyze sampled signals. |
| `pywayne-maths` | [pywayne/maths/](pywayne/maths/SKILL.md) | Use number-theory and arithmetic helpers. |
| `pywayne-plot` | [pywayne/plot/](pywayne/plot/SKILL.md) | Visualize spectrograms and time-frequency data. |
| `pywayne-statistics` | [pywayne/statistics/](pywayne/statistics/SKILL.md) | Run statistical tests and diagnostics. |

### Vision and sensors

| Skill Name | Path | Purpose |
| --- | --- | --- |
| `pywayne-ahrs-tools` | [pywayne/ahrs/ahrs-tools/](pywayne/ahrs/ahrs-tools/SKILL.md) | Decompose attitude and compensate roll/pitch. |
| `pywayne-calibration-magnetometer-calibration` | [pywayne/calibration/magnetometer-calibration/](pywayne/calibration/magnetometer-calibration/SKILL.md) | Calibrate magnetometers and sensor errors. |
| `pywayne-cv-apriltag-detector` | [pywayne/cv/apriltag-detector/](pywayne/cv/apriltag-detector/SKILL.md) | Detect AprilTags for calibration and pose estimation. |
| `pywayne-cv-camera-model` | [pywayne/cv/camera-model/](pywayne/cv/camera-model/SKILL.md) | Work with camera models and calibration files. |
| `pywayne-cv-geometric-hull-calculator` | [pywayne/cv/geometric-hull-calculator/](pywayne/cv/geometric-hull-calculator/SKILL.md) | Compute convex/concave hulls and bounding rectangles. |
| `pywayne-cv-stereo-tag-matcher` | [pywayne/cv/stereo-tag-matcher/](pywayne/cv/stereo-tag-matcher/SKILL.md) | Match AprilTags across stereo camera views. |
| `pywayne-cv-tools` | [pywayne/cv/tools/](pywayne/cv/tools/SKILL.md) | Read and write OpenCV YAML data. |

### VIO and visualization

| Skill Name | Path | Purpose |
| --- | --- | --- |
| `pywayne-vio-so3` | [pywayne/vio/SO3/](pywayne/vio/SO3/SKILL.md) | Compute SO(3) rotations and Lie operations. |
| `pywayne-vio-se3` | [pywayne/vio/se3/](pywayne/vio/se3/SKILL.md) | Compute SE(3) rigid transformations. |
| `pywayne-vio-tools` | [pywayne/vio/tools/](pywayne/vio/tools/SKILL.md) | Process visual-inertial poses and trajectories. |
| `pywayne-visualization-pangolin-utils` | [pywayne/visualization/pangolin-utils/](pywayne/visualization/pangolin-utils/SKILL.md) | Visualize geometry and trajectories with Pangolin. |
| `pywayne-visualization-rerun-utils` | [pywayne/visualization/rerun-utils/](pywayne/visualization/rerun-utils/SKILL.md) | Visualize geometry and sensor data with Rerun. |

### Platform integrations

| Skill Name | Path | Purpose |
| --- | --- | --- |
| `pywayne-adb-logcat-reader` | [pywayne/adb/adb-logcat-reader/](pywayne/adb/adb-logcat-reader/SKILL.md) | Read Android logcat streams. |
| `pywayne-aliyun-oss` | [pywayne/aliyun-oss/](pywayne/aliyun-oss/SKILL.md) | Manage files in Aliyun OSS. |
| `pywayne-cross-comm` | [pywayne/cross-comm/](pywayne/cross-comm/SKILL.md) | Exchange messages over cross-language WebSockets. |
| `pywayne-lark-bot` | [pywayne/lark-bot/](pywayne/lark-bot/SKILL.md) | Use the Feishu bot API. |
| `pywayne-lark-bot-listener` | [pywayne/lark-bot-listener/](pywayne/lark-bot-listener/SKILL.md) | Receive real-time Feishu bot events. |
| `pywayne-lark-custom-bot` | [pywayne/lark-custom-bot/](pywayne/lark-custom-bot/SKILL.md) | Send Feishu webhook messages. |

### Interfaces and speech

| Skill Name | Path | Purpose |
| --- | --- | --- |
| `pywayne-gui` | [pywayne/gui/](pywayne/gui/SKILL.md) | Automate Windows windows and hotkeys. |
| `pywayne-llm-chat-bot` | [pywayne/llm/chat-bot/](pywayne/llm/chat-bot/SKILL.md) | Use OpenAI-compatible chat APIs. |
| `pywayne-llm-chat-ollama-gradio` | [pywayne/llm/chat-ollama-gradio/](pywayne/llm/chat-ollama-gradio/SKILL.md) | Build a Gradio interface for Ollama chat. |
| `pywayne-llm-chat-window` | [pywayne/llm/chat-window/](pywayne/llm/chat-window/SKILL.md) | Use a streaming PyQt chat window. |
| `pywayne-tts` | [pywayne/tts/](pywayne/tts/SKILL.md) | Convert text to audio. |

## ⭐ Learning Tutor: Local First

Use `learning-tutor` for one-question-at-a-time teaching, Feynman explanations, evidence-linked assessments, and resumable learning. It includes opt-in transcript adapters, a local SQLite outbox, and an SSH/HTTPS sync client. Repeated uploads are deduplicated by event identity; parallel learning branches retain their evidence.

A PostgreSQL [record backend](learning-tutor/references/record-backend.md) and separate [image-storage service](learning-tutor/references/assets.md) are deployed on hx470 over SSH. Records, evidence-linked assessments, and checkpoints sync with commit receipts; private OSS images retain PostgreSQL metadata. One local Codex learning trial and fresh-state restoration have been checked. Other host/OS coverage and a public HTTPS gateway remain separate work. Embeddings, personal-memory writes, scheduled review, and reminders are not enabled.

See the skill's [setup guide](learning-tutor/references/setup.md) and [validation status](learning-tutor/references/validation.md). No real learning records or credentials belong in this repository.

## ✅ Maintenance

1. Read `CLAUDE.md` before editing; follow actual module paths and skill names.
2. Regenerate/check the catalog against source `**/SKILL.md`, excluding ignored installation mirrors.
3. Keep both READMEs aligned in counts, paths, and capabilities.
4. Remove generated `.skill` archives and empty resource directories after packaging.
5. Run changed helper tests; distinguish tested behavior from planned integrations.

## 📄 License

MIT. See [LICENSE](LICENSE).
