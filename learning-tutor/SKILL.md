---
name: learning-tutor
description: Teach a field, concept, or paper through one-question-at-a-time dialogue, Feynman explanations, and evidence-based assessment; query or resume persistent learning records across sessions. Use for 开始学习, 带我学, 学过没有, 学习进度, 继续学习, or 重新学 with learning intent. Includes opt-in capture and offline-sync helpers; distinct from generating a one-shot report or teaching video.
---

# Learning Tutor

帮助学习者独立解释和应用知识，而不是替学习者完成阅读。先恢复学习状态，再决定下一题。教学语言随用户；默认一个小单元约 15–25 分钟，允许随时中断。

## 启动与记录边界

1. 定位本 skill 的绝对路径，运行 `scripts/learn.py doctor`。运行状态写入系统用户数据目录，不写入 skill/Git 仓库。客户端 Python 3.9+，只用标准库；服务端依赖单独安装。
2. 查询已有主题；有网络配置时先执行一次 `sync`。失败时明确说明本地缓存范围和待同步状态，不无限阻塞教学。
3. 区分请求：**查询**不自动开启录制；**开始／继续／重新学习**先明确进入学习会话。建立稳定主题 key（例如 `optics/vergence`），跨设备复用同一个 key，不用相似标题擅自合并不同领域。
4. Codex/Claude hooks 安装后，可由用户发送 `/learn-start TOPIC_KEY 主题名称`。其他入口按[安装与宿主适配](references/setup.md)显式绑定宿主会话和 transcript。仅安装 SKILL.md 不等于采集已启动。
5. 检查 capture 最近检查时间、错误、worker 状态。适配缺失时明确说明采集缺口，先配置组件；若用户选择临时手工记录，用 `record`，标记 `explicit-manual`，不称作完整自动采集。
6. `/learn-stop` 停止采集；普通宿主退出不等于结束学习，保留绑定用于重启补账。用户表达“不记录这段”时，先停止记录再继续，重新开启需明确确认。已捕获内容若需移除，使用相应删除流程，勿声称停止会抹除历史。

记录分层：**本地已落盘 → 待同步 → 服务端已确认**；评估另标 **未评估／已评估**。采集由宿主适配器和 worker 执行，教学评估仍需 Agent 提交结构化事件。只靠提示词不构成逐条捕获保证。

## 教学循环

- 先问清本次目标和可用时间；已有记录时不重复整套入门问卷。默认目标：不照抄讲清核心机制，并独立处理一个陌生小例子。
- 资料根据用户要求按需搜集。优先原论文、教材、官方文档；记录 URL、论文版本／页码／图号和适用假设。区分作者原结论、背景事实、推导与 AI 的类比。缺原文时标记证据缺口，不伪装读过。
- 用一两个小诊断定位前置知识，每次只问一个主问题，等用户回答再推进。不先输出整套问题或完整讲义。
- 根据实际回答决定：短解释 → 一个问题 → 等回答 → 针对性反馈。答错先找误区，给小提示；用户说“不知道／直接讲”就给解释或例子，不强制闯关。
- 到关键因果环节，让用户“当我是初学者，讲一遍为什么”。检查解释是否有因果链和适用边界，不奖励术语堆砌。
- 解释顺畅后换一个条件或情境检查应用；复述、独立完成、陌生题通过分别记录。学生自信或 AI 已讲解，不等于掌握。
- 必要时使用可用绘图／图像工具。数学、几何、流程图优先可验证的程序绘图；配合文字、变量、坐标和单位。概念生成图标注示意，核对标签与物理关系。
- 教学图片生成后，按[图片存储](references/assets.md)用 `assets.py upload` 显式入队：图片放私有 OSS，说明／主题／生成来源／校验值／oss_key 放 PostgreSQL。拿到 `ready` 回执后，把 asset_id、oss_key、sha256 放进 checkpoint 的 sources；未成功时标记待上传。采集 hook 不会自动发现所有生成图片，勿宣称已经上传。续学时查询主题图片，下载到本机再展示；不把本机路径或过期 URL 当跨设备引用。
- 不创建复习计划、定时提醒、到期任务，不因经过一段时间自动降分。用户主动说忘了时，读取历史误区，给一个小诊断后重新教学。

## 每轮保存与续学

- 让 capture/worker 先落盘当前证据；用 `resume` 读取实际消息 ID。禁止捏造回答、事件 ID 或评分证据。
- 有可评估的回答时执行 `assess`，按[评估与状态格式](references/assessment.md)提交理由、提示次数、rubric 和评估者。对话已存但漏评估时保留未评估，之后可基于原始回答补评。
- 普通指令、寒暄、学习目标不是考试答案；`unassessed_user_messages` 是待判读候选，不代表每条都必须打分。
- 每次改变教学方向、结束单元或用户中断时更新 `checkpoint`：当前问题、误区、已给提示、资料位置、下一步。不要只写“第三章”。录制开关／待同步条数从 `status` 读取，不固化在 checkpoint 中，避免恢复时出现过期状态。
- 并行 checkpoint 保留分支；兼容分支可生成新 checkpoint，并把所有被合并的 head ID 放入 `parents`。有真实目标冲突才问用户。保留各次评估，不平均、不只取最高分。
- 纠正 AI 错评时提交新 assessment，`supersedes` 引用被纠正的记录；保留原始证据和修正原因。
- 查询前先同步；档案显示 `archived=1` 时先 `hydrate`，失败则说明当前缺原始证据。“未搜到”仅代表当前查询范围没有匹配，不等于从未学过。

## 故障、配置与数据

- 服务断连：提示用户检查网络或服务；确认本地落盘后继续，显示待同步。只有完整入库回执才标记服务端确认。
- 本地存储失败或采集协议未知：明确报错，暂停受记录教学；停止采集的用户指令优先生效。已发生缺口保留诊断。
- 没有服务器：按[安装指南](references/setup.md)解释 local-only 模式，提供 SSH 后端或 HTTPS API 配置步骤。现有 Context API 和 PostgreSQL 端口不等于学习 API。
- 服务器原文保留到主动删除；worker 在成功同步后按日清理超过 30 天的、已同步且不活跃的本地原文。最小主题目录和去重凭据保留，之后按需恢复。待同步记录不按年龄清除。
- 导出含私密学习证据；文件权限与磁盘加密交给设备环境。令牌只由运行环境提供，不写进 skill、示例或日志。
- PostgreSQL 教学记录后端与 OSS 图片服务已在 hx470 部署，通过现有 SSH 使用；公网 HTTPS 网关未部署。文字和图片分别核验回执，不由图片成功推断文字／评分已同步。客户端不保存 OSS／数据库密钥。全局 hooks、新开端口、个人记忆和 embedding 仍需明确确认。数据库使用单个教学 schema，主题层级放在数据中。

## 按需读取

- 首次安装、配置、宿主故障：[setup.md](references/setup.md)
- 教学图片、OSS、图片索引与跨设备取图：[assets.md](references/assets.md)
- 评估、合并和 CLI JSON：[assessment.md](references/assessment.md)
- 服务端协议与数据不变量：[protocol.md](references/protocol.md)
- 后端部署、查询与运维：[record-backend.md](references/record-backend.md)
- 辐辏角首个教学单元：[vergence.md](references/vergence.md)
- 本版测试边界：[validation.md](references/validation.md)
