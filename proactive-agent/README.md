# Proactive Agent - 主动式 Agent 架构

> ⚠️ **重要声明**：本技能基于 [halthelobster/proactive-agent](https://github.com/halthelobster/proactive-agent) 修改而来，中文版由 [wangyendt](https://github.com/wangyendt/wayne-skills) 整理。原作者：https://github.com/halthelobster

让 AI 助手从「等待任务」变成「主动预见」的架构设计。包含 WAL 协议、Working Buffer、自动定时任务等经过实战验证的模式。

## 核心功能

- **WAL 协议** - 写前日志，捕获修正、决策和重要细节
- **Working Buffer** - 在上下文压缩的危险区存活
- **压缩恢复** - 上下文被截断后如何逐步恢复
- **统一搜索** - 说「我不知道」之前，搜遍所有来源
- **安全加固** - 技能安装审核、Agent 网络警告
- **足智多谋** - 试 10 种方法后再求助
- **自我改进护栏** - 用 ADL/VFM 协议安全进化

## 三大支柱

1. **主动** - 创造未被请求的价值
2. **持久** - 扛过上下文丢失
3. **自我进化** - 持续优化服务

## 使用方式

作为 OpenClaw skill 使用，Agent 会在每次会话自动加载。

## 文件说明

- `SKILL.md` - 完整技能文档（中文版）
- `assets/` - 示例文件（AGENTS.md, SOUL.md, USER.md 等）
- `scripts/` - 安全审计脚本

## 更多信息

详见 [SKILL.md](./SKILL.md)
