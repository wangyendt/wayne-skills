# wayne-skills

`wayne-skills` 是一个面向 Codex/Claude 类 AI 编程助手的技能仓库，目标是把 `pywayne` 工具库能力沉淀为可复用的 `SKILL.md` 指令集，让助手在对应任务中自动调用正确的方法、参数和工作流。

## 项目目标

- 把 `pywayne` 源码能力映射为结构化技能，降低 AI 使用门槛
- 统一技能命名、目录布局和描述风格，便于检索与维护
- 覆盖从数值计算、视觉、VIO、统计到 LLM/自动化等常见研发场景

## 与 pywayne 的关系

- 源项目：`pywayne`（`wayne_algorithm_lib`）
- 本仓库：仅维护技能定义，不包含 `pywayne` 源码实现
- 技能目录与源码模块保持一一对应，便于“看到技能名就能定位源码模块”

## 仓库结构

- `pywayne/`：与 `pywayne` 源码模块对应的技能（当前 34 个）
- `send-email/`：通用邮件发送技能（独立于 pywayne）
- `deep-think/`：深度思考与问题拆解技能（通用）
- `CLAUDE.md`：本仓库技能命名规范与维护约束

## 命名与目录规范

遵循 `CLAUDE.md` 中规则：

1. 源码模块名使用下划线（PEP8），技能目录使用连字符（hyphen-case）
2. `SKILL.md` 的 `name` 使用完整路径语义并全小写连字符
3. 路径映射保持稳定：源码路径 -> skill 目录路径 -> skill name

示例：

- `pywayne/llm/chat_bot.py` -> `pywayne/llm/chat-bot/` -> `pywayne-llm-chat-bot`
- `pywayne/vio/SE3.py` -> `pywayne/vio/se3/` -> `pywayne-vio-se3`

## 技能清单

### 通用技能（2）

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `deep-think` | `deep-think/SKILL.md` | 深入分析、系统化拆解复杂问题 |
| `send-email` | `send-email/SKILL.md` | 通过 SMTP 发送 HTML 邮件/附件/模板邮件 |

### pywayne 技能（34）

#### ADB / 设备

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-adb-logcat-reader` | `pywayne/adb/adb-logcat-reader/SKILL.md` | 实时读取 Android `adb logcat` 日志（C++/Python 后端） |

#### AHRS / 姿态

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-ahrs-tools` | `pywayne/ahrs/ahrs-tools/SKILL.md` | 四元数分解、姿态补偿（roll/pitch） |

#### 对象存储

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-aliyun-oss` | `pywayne/aliyun-oss/SKILL.md` | Aliyun OSS 上传/下载/列举/复制/移动/删除 |

#### 命令行工具

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-bin-cmdlogger` | `pywayne/bin/cmdlogger/SKILL.md` | 记录命令 stdin/stdout/stderr 并实时输出 |
| `pywayne-bin-gettool` | `pywayne/bin/gettool/SKILL.md` | 拉取/编译/安装 C++ 第三方工具库 |
| `pywayne-bin-gitstats` | `pywayne/bin/gitstats/SKILL.md` | Git 提交时段统计与可视化 |

#### 标定 / 通信 / 加密

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-calibration-magnetometer-calibration` | `pywayne/calibration/magnetometer-calibration/SKILL.md` | 磁力计软硬铁标定 |
| `pywayne-cross-comm` | `pywayne/cross-comm/SKILL.md` | WebSocket 跨语言消息通信与文件传输 |
| `pywayne-crypto` | `pywayne/crypto/SKILL.md` | 字符串/字节加解密、混淆与批处理 |

#### 计算机视觉（CV）

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-cv-apriltag-detector` | `pywayne/cv/apriltag-detector/SKILL.md` | AprilTag 检测与结果绘制 |
| `pywayne-cv-camera-model` | `pywayne/cv/camera-model/SKILL.md` | 相机模型加载与投影计算 |
| `pywayne-cv-geometric-hull-calculator` | `pywayne/cv/geometric-hull-calculator/SKILL.md` | 凸包/凹包/最小外接矩形计算 |
| `pywayne-cv-stereo-tag-matcher` | `pywayne/cv/stereo-tag-matcher/SKILL.md` | 双目 AprilTag 匹配与可视化 |
| `pywayne-cv-tools` | `pywayne/cv/tools/SKILL.md` | OpenCV YAML 读写与节点解析 |

#### 数据结构 / 信号 / GUI / 配置

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-data-structure` | `pywayne/data-structure/SKILL.md` | 条件树、并查集、XML I/O |
| `pywayne-dsp` | `pywayne/dsp/SKILL.md` | 滤波、峰值检测、去趋势、DTW |
| `pywayne-gui` | `pywayne/gui/SKILL.md` | Windows GUI 自动化、热键、窗口控制 |
| `pywayne-helper` | `pywayne/helper/SKILL.md` | YAML 项目配置共享与等待机制 |

#### 飞书生态

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-lark-bot` | `pywayne/lark-bot/SKILL.md` | 飞书机器人 API 全功能封装 |
| `pywayne-lark-bot-listener` | `pywayne/lark-bot-listener/SKILL.md` | 飞书消息监听（文本/图片/文件） |
| `pywayne-lark-custom-bot` | `pywayne/lark-custom-bot/SKILL.md` | 飞书自定义机器人 webhook 发送 |

#### LLM 交互

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-llm-chat-bot` | `pywayne/llm/chat-bot/SKILL.md` | OpenAI 兼容聊天接口与会话管理 |
| `pywayne-llm-chat-ollama-gradio` | `pywayne/llm/chat-ollama-gradio/SKILL.md` | Ollama + Gradio 多会话聊天 UI |
| `pywayne-llm-chat-window` | `pywayne/llm/chat-window/SKILL.md` | PyQt5 桌面聊天窗口与流式输出 |

#### 数学 / 绘图 / 统计 / 通用工具

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-maths` | `pywayne/maths/SKILL.md` | 因数分解、数字统计、Karatsuba 乘法 |
| `pywayne-plot` | `pywayne/plot/SKILL.md` | 频谱图与时频分析可视化 |
| `pywayne-statistics` | `pywayne/statistics/SKILL.md` | 37+ 统计检验与统一结果接口 |
| `pywayne-tools` | `pywayne/tools/SKILL.md` | 常用工具函数（日志/计时/YAML 等） |
| `pywayne-tts` | `pywayne/tts/SKILL.md` | 文本转语音（say/gTTS） |

#### VIO / 3D 可视化

| Skill Name | 路径 | 作用 |
| --- | --- | --- |
| `pywayne-vio-se3` | `pywayne/vio/se3/SKILL.md` | SE(3) 变换、李群李代数映射 |
| `pywayne-vio-so3` | `pywayne/vio/so3/SKILL.md` | SO(3) 旋转表示转换与运算 |
| `pywayne-vio-tools` | `pywayne/vio/tools/SKILL.md` | VIO 位姿格式转换与轨迹可视化 |
| `pywayne-visualization-pangolin-utils` | `pywayne/visualization/pangolin-utils/SKILL.md` | Pangolin 实时 3D 可视化 |
| `pywayne-visualization-rerun-utils` | `pywayne/visualization/rerun-utils/SKILL.md` | Rerun 静态 3D 可视化工具 |

## 维护建议

- 新增/更新技能时，优先与 `pywayne` 源码目录保持对齐
- 完成打包后清理 `.skill` 文件和空目录（见 `CLAUDE.md`）
- 更新 README 的技能清单，保证仓库文档与实际内容一致

## 许可证

本仓库使用 `MIT License`，见 `LICENSE`。
