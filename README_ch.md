# wayne-skills

[English](README.md) | [简体中文](README_ch.md)

> 可复用的工作流、可追溯的过程、实用的配套工具。

## ✨ 项目目标

`wayne-skills` 为 Codex、Claude Code、OpenClaw 等 AI Agent 维护技能与配套脚本，包括通用工作流和映射到 `pywayne` 生态的技能；不维护 `pywayne` 库源码实现。安装 skill 不等于已安装依赖、开启宿主 hooks 或验证所有运行环境。

## 📌 快速概览

| 指标 | 数值 |
| --- | --- |
| 技能总数 | `48` |
| `pywayne` 技能 | `35` |
| 通用技能 | `13` |
| 规范主文档 | [CLAUDE.md](CLAUDE.md) |
| Agent 入口 | [AGENTS.md](AGENTS.md) |

统计源码中的 `**/SKILL.md`，排除 `.agents/`、`.claude/`、`.cursor/` 等被忽略的 Agent 安装镜像。

## 🗂️ 仓库结构

- `pywayne/`：与库源码对应的技能，按下方领域分组。
- 顶层技能目录：通用工作流，包含 `SKILL.md` 及按需提供的 scripts/references/assets。
- `learning-tutor/`：交互教学、本地采集、待同步队列与同步辅助程序。
- `CLAUDE.md` / `AGENTS.md`：仓库约定与 Agent 入口说明。

## 🔗 命名与目录规范

映射关系为 `源码模块路径 → skill 目录 → skill name`；新增技能名称和目录采用小写连字符形式。

- `pywayne/llm/chat_bot.py` → `pywayne/llm/chat-bot/` → `pywayne-llm-chat-bot`
- `pywayne/vio/SE3.py` → `pywayne/vio/se3/` → `pywayne-vio-se3`
- 通用技能位于独立顶层目录，不要求 pywayne 前缀。

清单链接指向真实路径，包括已有的 `pywayne/vio/SO3/`。本次未重命名历史目录。

## 🧠 技能清单

### 通用技能

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `alapi` | [alapi/](alapi/SKILL.md) | 依据内置 API 清单调用 ALAPI。 |
| `android-app-publisher` | [android-app-publisher/](android-app-publisher/SKILL.md) | 轻量客户端：发布 APK、管理最新版并生成二维码；Docker API 位于独立服务端仓库。 |
| `awesome-docs` | [awesome-docs/](awesome-docs/SKILL.md) | 维护技术文档；强调读者需求、逻辑顺序、准确表达及交互图解。 |
| `deep-think` | [deep-think/](deep-think/SKILL.md) | 组织深入分析与问题拆解。 |
| `learning-tutor` | [learning-tutor/](learning-tutor/SKILL.md) | 逐题教学、证据评估、本地采集与跨会话续学。 |
| `proactive-agent` | [proactive-agent/](proactive-agent/SKILL.md) | 设计带 WAL 和工作缓冲的主动式 Agent。 |
| `research-paper-deep-dive` | [research-paper-deep-dive/](research-paper-deep-dive/SKILL.md) | 深入理解论文、证据、背景与可复现方法。 |
| `send-email` | [send-email/](send-email/SKILL.md) | 通过 SMTP 发送带模板与附件的邮件。 |
| `shell-shortcuts` | [shell-shortcuts/](shell-shortcuts/SKILL.md) | 配置跨平台终端快捷命令。 |
| `technical-explainer-video` | [technical-explainer-video/](technical-explainer-video/SKILL.md) | 制作真实 3D、LaTeX 公式与画内同步字幕的技术教学视频，附可运行渲染及检查模板。 |
| `tutor-general` | [tutor-general/](tutor-general/SKILL.md) | 使用 Motion Canvas 制作带配音的教学视频。 |
| `tutor-math-geometry` | [tutor-math-geometry/](tutor-math-geometry/SKILL.md) | 用 HTML、几何动画与配音讲解数学。 |
| `week-report-system` | [week-report-system/](week-report-system/SKILL.md) | 整理工作素材并生成周报。 |

### 开发工具

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-bin-cmdlogger` | [pywayne/bin/cmdlogger/](pywayne/bin/cmdlogger/SKILL.md) | 记录命令输入与输出。 |
| `pywayne-bin-gettool` | [pywayne/bin/gettool/](pywayne/bin/gettool/SKILL.md) | 获取 C++ 工具与库。 |
| `pywayne-bin-gitstats` | [pywayne/bin/gitstats/](pywayne/bin/gitstats/SKILL.md) | 分析 Git 提交活动。 |
| `pywayne-bin-toolsetup` | [pywayne/bin/toolsetup/](pywayne/bin/toolsetup/SKILL.md) | 配置开发命令与工具环境。 |
| `pywayne-crypto` | [pywayne/crypto/](pywayne/crypto/SKILL.md) | 使用字符串和字节加解密工具。 |
| `pywayne-helper` | [pywayne/helper/](pywayne/helper/SKILL.md) | 管理共享项目配置。 |
| `pywayne-tools` | [pywayne/tools/](pywayne/tools/SKILL.md) | 使用控制台、计时、配置与通用工具。 |

### 数据与数学

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-data-structure` | [pywayne/data-structure/](pywayne/data-structure/SKILL.md) | 使用逻辑树、并查集和 XML 工具。 |
| `pywayne-dsp` | [pywayne/dsp/](pywayne/dsp/SKILL.md) | 滤波并分析采样信号。 |
| `pywayne-maths` | [pywayne/maths/](pywayne/maths/SKILL.md) | 使用数论与算术工具。 |
| `pywayne-plot` | [pywayne/plot/](pywayne/plot/SKILL.md) | 绘制频谱与时频数据。 |
| `pywayne-statistics` | [pywayne/statistics/](pywayne/statistics/SKILL.md) | 执行统计检验与诊断。 |

### 视觉与传感器

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-ahrs-tools` | [pywayne/ahrs/ahrs-tools/](pywayne/ahrs/ahrs-tools/SKILL.md) | 分解姿态并补偿横滚与俯仰。 |
| `pywayne-calibration-magnetometer-calibration` | [pywayne/calibration/magnetometer-calibration/](pywayne/calibration/magnetometer-calibration/SKILL.md) | 标定磁力计与传感器误差。 |
| `pywayne-cv-apriltag-detector` | [pywayne/cv/apriltag-detector/](pywayne/cv/apriltag-detector/SKILL.md) | 检测 AprilTag，用于标定与位姿估计。 |
| `pywayne-cv-camera-model` | [pywayne/cv/camera-model/](pywayne/cv/camera-model/SKILL.md) | 使用相机模型与标定文件。 |
| `pywayne-cv-geometric-hull-calculator` | [pywayne/cv/geometric-hull-calculator/](pywayne/cv/geometric-hull-calculator/SKILL.md) | 计算凸包、凹包和包围矩形。 |
| `pywayne-cv-stereo-tag-matcher` | [pywayne/cv/stereo-tag-matcher/](pywayne/cv/stereo-tag-matcher/SKILL.md) | 匹配双目相机中的 AprilTag。 |
| `pywayne-cv-tools` | [pywayne/cv/tools/](pywayne/cv/tools/SKILL.md) | 读写 OpenCV YAML 数据。 |

### VIO 与可视化

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-vio-so3` | [pywayne/vio/SO3/](pywayne/vio/SO3/SKILL.md) | 计算 SO(3) 旋转与李群运算。 |
| `pywayne-vio-se3` | [pywayne/vio/se3/](pywayne/vio/se3/SKILL.md) | 计算 SE(3) 刚体变换。 |
| `pywayne-vio-tools` | [pywayne/vio/tools/](pywayne/vio/tools/SKILL.md) | 处理视觉惯性位姿与轨迹。 |
| `pywayne-visualization-pangolin-utils` | [pywayne/visualization/pangolin-utils/](pywayne/visualization/pangolin-utils/SKILL.md) | 使用 Pangolin 显示几何与轨迹。 |
| `pywayne-visualization-rerun-utils` | [pywayne/visualization/rerun-utils/](pywayne/visualization/rerun-utils/SKILL.md) | 使用 Rerun 显示几何与传感器数据。 |

### 平台集成

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-adb-logcat-reader` | [pywayne/adb/adb-logcat-reader/](pywayne/adb/adb-logcat-reader/SKILL.md) | 读取 Android logcat 日志流。 |
| `pywayne-aliyun-oss` | [pywayne/aliyun-oss/](pywayne/aliyun-oss/SKILL.md) | 管理阿里云 OSS 文件。 |
| `pywayne-cross-comm` | [pywayne/cross-comm/](pywayne/cross-comm/SKILL.md) | 通过跨语言 WebSocket 交换消息。 |
| `pywayne-lark-bot` | [pywayne/lark-bot/](pywayne/lark-bot/SKILL.md) | 使用飞书机器人 API。 |
| `pywayne-lark-bot-listener` | [pywayne/lark-bot-listener/](pywayne/lark-bot-listener/SKILL.md) | 接收飞书机器人实时事件。 |
| `pywayne-lark-custom-bot` | [pywayne/lark-custom-bot/](pywayne/lark-custom-bot/SKILL.md) | 发送飞书 webhook 消息。 |

### 界面与语音

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-gui` | [pywayne/gui/](pywayne/gui/SKILL.md) | 自动化 Windows 窗口与快捷键。 |
| `pywayne-llm-chat-bot` | [pywayne/llm/chat-bot/](pywayne/llm/chat-bot/SKILL.md) | 使用 OpenAI 兼容聊天 API。 |
| `pywayne-llm-chat-ollama-gradio` | [pywayne/llm/chat-ollama-gradio/](pywayne/llm/chat-ollama-gradio/SKILL.md) | 为 Ollama 聊天构建 Gradio 界面。 |
| `pywayne-llm-chat-window` | [pywayne/llm/chat-window/](pywayne/llm/chat-window/SKILL.md) | 使用流式 PyQt 聊天窗口。 |
| `pywayne-tts` | [pywayne/tts/](pywayne/tts/SKILL.md) | 把文字转换为音频。 |

## ⭐ Learning Tutor：本地优先

`learning-tutor` 支持逐题教学、费曼解释、带证据的评估与中断后续学，配有显式开启的 transcript 适配器、本地 SQLite 待同步队列和 SSH／HTTPS 同步客户端。重复上传按事件身份去重；并行学习保留各分支证据。

PostgreSQL [记录后端](learning-tutor/references/record-backend.md)及独立[图片服务](learning-tutor/references/assets.md)已在 hx470 部署，通过 SSH 使用。文字、证据评估和进度 checkpoint 按提交回执同步；私有 OSS 图片保留 PostgreSQL 元数据。本机 Codex 一次学习试用及全新状态恢复已核对；其他宿主／系统覆盖和公网 HTTPS 网关仍待分别验收。尚未启用 Embedding、个人记忆写入、计划复习或提醒。

参见 skill 的[安装说明](learning-tutor/references/setup.md)与[验证状态](learning-tutor/references/validation.md)。真实学习记录和凭据不纳入本仓库。

## ✅ 维护建议

1. 修改前阅读 `CLAUDE.md`，按真实模块路径和 skill 名称维护。
2. 根据源码 `**/SKILL.md` 生成／核对清单，排除被忽略的安装镜像。
3. 中英文 README 的数量、路径与能力描述保持一致。
4. 打包后清理生成的 `.skill` 文件和空资源目录。
5. 执行变更脚本的测试，区分已验证行为与计划接入能力。

## 📄 许可证

MIT，见 [LICENSE](LICENSE)。
