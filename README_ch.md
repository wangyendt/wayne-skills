# wayne-skills

[🇺🇸 English](README.md) | [🇨🇳 简体中文](README_ch.md)

> 让 AI 编程助手在真实工程中更稳、更准、更可复用。

`wayne-skills` 是一个面向 Codex/Claude 类助手的技能仓库，围绕 `pywayne` 生态构建。  
它把实际模块能力沉淀为可复用的 `SKILL.md` 工作流，让模型在更少提示下也能选择更合适的 API、约束与执行路径。

## ✨ 这个仓库有什么不一样

- 🧭 **强映射**：技能与源码模块一一对应
- 🧱 **强规范**：命名和结构稳定一致
- 🛡️ **低风险**：减少模型临场“拍脑袋”决策
- 🚀 **覆盖广**：CV、VIO、DSP、LLM、统计、自动化、集成能力

## 📌 快速概览

| 指标 | 数值 |
| --- | --- |
| 技能总数 | `39` |
| `pywayne` 技能 | `34` |
| 通用技能 | `5`（`deep-think`、`send-email`、`shell-shortcuts`、`tutor`、`proactive-agent`） |
| 规范主文档 | `CLAUDE.md` |
| Agent 入口文档 | `AGENTS.md` |

## 🗂️ 仓库结构

- `pywayne/` - 与 `pywayne` 源码模块对齐的技能目录
- `send-email/` - SMTP 邮件发送技能（模板+附件）
- `deep-think/` - 深度分析与问题拆解流程
- `shell-shortcuts/` - 跨平台终端快捷指令（`proxy_on`、`goto`、`gpu`）
- `tutor/` - 数学辅导技能（生成 Manim 教学视频）
- `proactive-agent/` - 主动式 Agent 架构（WAL、Working Buffer 等）
- `CLAUDE.md` - 命名、结构、文档规则
- `AGENTS.md` - 给其他模型/代理的简明协作说明

## 🔗 映射规则

`源码模块路径 -> skill 目录路径 -> skill name`

示例：

- `pywayne/llm/chat_bot.py` -> `pywayne/llm/chat-bot/` -> `pywayne-llm-chat-bot`
- `pywayne/vio/SE3.py` -> `pywayne/vio/se3/` -> `pywayne-vio-se3`
- `pywayne/cv/apriltag_detector.py` -> `pywayne/cv/apriltag-detector/` -> `pywayne-cv-apriltag-detector`

## 🧠 技能领域

### 通用技能

- `deep-think`：结构化深度思考流程
- `send-email`：支持 HTML 模板与附件的 SMTP 邮件发送
- `shell-shortcuts`：配置 `proxy_on/proxy_off/goto/gpu` 与可选 Conda 自动激活
- `tutor`：数学辅导技能（Manim 视频生成）
- `proactive-agent`：主动式 Agent 架构（WAL、Working Buffer 等）

### pywayne 技能领域

- 🛠️ 开发工具：`tools`、`helper`、`bin/*`、`crypto`
- 📊 数据与数学：`dsp`、`maths`、`statistics`、`data-structure`、`plot`
- 🤖 视觉与机器人：`cv/*`、`vio/*`、`calibration/*`、`ahrs/*`、`visualization/*`
- 🔌 平台与集成：`adb/*`、`cross-comm`、`aliyun-oss`
- 💬 产品交互：`llm/*`、`lark-*`、`tts`、`gui`

详细说明请直接查看各目录下 `SKILL.md`。

## ✅ 更新检查清单

新增或更新技能时：

1. 遵循 `CLAUDE.md` 命名规范
2. 目录统一使用 hyphen-case
3. 保持双语 README 链接有效（`README.md` <-> `README_ch.md`）
4. 统计数字与领域描述和实际 `SKILL.md` 保持一致

## 📄 许可证

MIT，见 `LICENSE`。
