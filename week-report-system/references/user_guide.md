# Week Report System 完整使用指南

欢迎使用 AI 智能周报系统！本系统可以自动追踪你与 AI 的对话，并在需要时生成结构化的工作周报。

## 🎯 系统功能概览

| 功能 | 说明 | 自动化程度 |
|------|------|-----------|
| 对话追踪 | 自动记录每次对话的问题和回答 | ⭐⭐⭐⭐⭐ 全自动 |
| 智能压缩 | 长对话自动提取要点 | ⭐⭐⭐⭐⭐ 全自动 |
| 云端同步 | 多设备数据自动同步 | ⭐⭐⭐⭐⭐ 全自动 |
| 周报生成 | 一键生成专业周报 | ⭐⭐⭐⭐ 半自动 |
| 隐私保护 | 敏感内容自动跳过 | ⭐⭐⭐⭐⭐ 全自动 |

---

## 📦 安装方式

### 方式一：Skill Manager（推荐）

**优势**：一次安装，所有 AI 智能体（Claude、ChatGPT 等）都能使用

```bash
# 第一步：安装 Skill Manager
npm -g install @wang121ye/skillmanager/latest

# 第二步：安装本技能
skillmanager install --global
```

执行第二步后会出现技能列表，找到并勾选 `week-report-system` 即可。

### 方式二：手动安装

将 skill 文件放置到对应 AI 客户端的 skills 目录下。

---

## 🔧 环境配置（首次使用必做）

### 第一步：创建 GitHub 仓库

1. 打开浏览器，访问 **https://github.com/new**
2. 填写仓库信息：
   - **Repository name**: `week-reports`（或其他你喜欢的名字）
   - **Description**: `我的工作周报记录`
   - **Visibility**: 选择 **Private**（推荐，保护隐私）
   - **❌ 不要**勾选 "Add a README file"
   - **❌ 不要**勾选 ".gitignore" 或 "license"
3. 点击 **Create repository**
4. 记下你的仓库名：`你的用户名/week-reports`

### 第二步：创建 Personal Access Token

1. 访问 **https://github.com/settings/tokens**
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 填写信息：
   - **Note**: `Week Report System Token`
   - **Expiration**: 建议 90 天
   - **Select scopes**: 勾选 ✅ **repo**（完整仓库权限）
4. 点击 **Generate token**
5. **⚠️ 立即复制 Token！**（格式：`ghp_xxxxxxxxxxxx`，只显示一次）

### 第三步：配置环境变量

#### macOS / Linux（Zsh）

```bash
# 打开配置文件
nano ~/.zshrc

# 在文件末尾添加以下内容
export WEEK_REPORT_GIT_USERNAME="你的GitHub用户名"
export WEEK_REPORT_GIT_PERSONAL_TOKEN="ghp_你的token"
export WEEK_REPORT_GIT_REPO="你的用户名/week-reports"

# 保存后执行
source ~/.zshrc
```

#### Windows（PowerShell）

```powershell
# 在 PowerShell 中执行
[Environment]::SetEnvironmentVariable("WEEK_REPORT_GIT_USERNAME", "你的用户名", "User")
[Environment]::SetEnvironmentVariable("WEEK_REPORT_GIT_PERSONAL_TOKEN", "ghp_你的token", "User")
[Environment]::SetEnvironmentVariable("WEEK_REPORT_GIT_REPO", "你的用户名/week-reports", "User")

# 重启终端生效
```

### 第四步：验证配置

```bash
echo "Username: $WEEK_REPORT_GIT_USERNAME"
echo "Token: ✅ (已配置)"
echo "Repo: $WEEK_REPORT_GIT_REPO"
```

如果三个变量都正确显示，配置成功！

---

## 🚀 快速开始

### 场景一：日常对话（自动记录）

直接开始你的工作对话，系统会自动记录：

```
你: 帮我写一个 Python 脚本处理 Excel 数据
AI: [提供解决方案...]
# 系统自动在后台记录这次对话
```

### 场景二：生成周报

当你需要写周报时，只需说：

```
你: 总结2024年第12周的工作
# 或
你: 本周工作总结
# 或
你: 写周报
# 或
你: 生成周报
```

系统会：
1. 从 Git 仓库拉取最新数据
2. 读取该周所有对话记录
3. 分析并生成结构化周报

### 场景三：查看特定周

```
你: 总结2024年第51周的工作
你: 上周周报
```

---

## 📊 周报格式示例

生成的周报包含以下结构：

```markdown
# 周工作汇报 - 2024年第51周

## 📋 本周工作概览
[总体描述本周主要工作内容和成果]

## 📊 分项目工作详情

### 项目一: XXX系统开发
**关键成果:**
- 完成用户认证模块开发
- 优化数据库查询性能 40%

**数据指标:**
- 对话次数: 8次
- 耗时估算: ~12小时

## 📈 本周数据统计
[统计数据表格]

## 🎯 重点工作与贡献
[突出3个核心成就]

## 📝 本周总结与下周计划
[总结 + 下周计划]
```

---

## 🔐 隐私保护

系统会自动跳过包含以下关键词的对话：

- `password`, `secret`, `api key`, `token`, `credential`
- `personal`, `private`, `confidential`
- `不要记录`, `skip logging`, `off record`

你也可以在对话中说：
- "这个问题不要记录"
- "这是私密的，跳过日志"

---

## 📁 数据存储结构

你的 GitHub 仓库会按以下结构组织：

```
week-reports/
├── 2024/
│   ├── week01/
│   │   ├── 20240101-a1b2c3d4.txt    # 1月1日开始的会话
│   │   └── 20240103-e5f6g7h8.txt    # 1月3日开始的会话
│   ├── week02/
│   └── ...
├── 2025/
│   └── ...
└── reports/                          # 生成的周报（可选）
    └── 2024_week12.md
```

文件名格式：`{日期}-{会话ID}.txt`，例如 `20241220-a1b2c3d4.txt`，方便按时间排序。

---

## ❓ 常见问题

### Q: 多个设备同时使用会冲突吗？

A: 不会。系统有自动重试机制，遇到冲突会自动合并。先提交的内容会保留，后提交的会追加。

### Q: 换电脑需要重新配置吗？

A: 是的，需要在新电脑上配置环境变量。但历史数据都在 Git 仓库中，可以完整同步。

### Q: Token 过期了怎么办？

A: 重新生成一个新 Token，更新环境变量即可。历史数据不会丢失。

### Q: 可以只记录特定对话吗？

A: 可以，在不想记录的对话中说 "不要记录" 即可跳过。

### Q: 周报数据安全吗？

A: 建议使用 **Private 仓库**，只有你能看到。Token 只存储在你的本地环境变量中。

---

## 🎓 使用建议

1. **每天正常使用 AI 辅助工作** - 系统会自动记录
2. **周五生成周报** - 说 "生成本周周报"
3. **检查并补充** - AI 生成的周报可能需要你微调
4. **定期备份** - 虽然 Git 仓库已经是备份，建议偶尔本地也保存一份

---

## 🆘 需要帮助？

如果遇到问题，可以问我：
- "周报系统怎么配置环境变量？"
- "如何创建 GitHub Token？"
- "周报格式可以自定义吗？"

---

*祝你工作愉快！让 AI 帮你轻松写周报 📝*
