# Pywayne Skill 命名规范

## Skill 命名规则

在创建 pywayne 库的 skill 时，**必须按照源码和文档的目录结构对 skill 进行命名（name）和目录结构**。

**目录结构：**
- 所有 pywayne skill 都应放在 `pywayne/` 目录下
- 子目录名使用连字符（`-`），Python 模块的下划线 `_` 转连字符 `-`
- SKILL.md 的 `name` 字段使用完整路径（连字符分隔，符合 hyphen-case 规范）

**示例：**

| 源码目录 | Skill 目录结构 | SKILL.md name |
|---------|---------------|---------------|
| `pywayne/lark_custom_bot.py` | `pywayne/lark-custom-bot/` | `pywayne-lark-custom-bot` |
| `pywayne/bin/cmdlogger` | `pywayne/bin/cmdlogger/` | `pywayne-bin-cmdlogger` |
| `pywayne/tts` | `pywayne/tts/` | `pywayne-tts` |
| `pywayne/bin/gettool` | `pywayne/bin/gettool/` | `pywayne-bin-gettool` |
| `pywayne/bin/gitstats` | `pywayne/bin/gitstats/` | `pywayne-bin-gitstats` |
| `pywayne/calibration/magnetometer_calibration.py` | `pywayne/calibration/magnetometer-calibration/` | `pywayne-calibration-magnetometer-calibration` |
| `pywayne/vio/tools.py` | `pywayne/vio/tools/` | `pywayne-vio-tools` |
| `pywayne/vio/SE3.py` | `pywayne/vio/se3/` | `pywayne-vio-se3` |
| `pywayne/vio/SO3.py` | `pywayne/vio/so3/` | `pywayne-vio-so3` |
| `pywayne/llm/chat_bot.py` | `pywayne/llm/chat-bot/` | `pywayne-llm-chat-bot` |

**命名原则：**
1. 源码使用下划线：Python 模块名遵循 PEP8 规范使用下划线（如 `chat_bot.py`）
2. Skill 目录使用连字符：下划线 `_` 转连字符 `-`（如 `chat-bot/`）
3. Skill name 使用连字符：将路径 `/` 替换为 `-`，全部使用小写（如 `pywayne-llm-chat-bot`）
4. 符合 hyphen-case 规范：只允许小写字母、数字和连字符（打包脚本验证要求）

**目的：**
- 使 skill 目录结构与 pywayne 库的代码组织保持一致
- 便于用户理解 skill 对应的源码位置
- 简化技能管理和查找

## Skill 创建后清理

创建 skill 并打包后，**必须执行以下清理**：

1. **删除 `.skill` 文件** - 打包文件不需要保留在源码仓库中
2. **删除 `scripts/references/assets` 中的空文件夹** - 保留非空的文件夹

**原因：**
- `.skill` 文件只用于分发，源码仓库不需要
- 避免空目录占用仓库空间

**示例：**
```
# 创建后（需要清理）
./
├── pywayne/
│   └── plot/
│       ├── SKILL.md
│       ├── scripts/           # 空，删除
│       ├── references/        # 空，删除
│       └── assets/            # 空，删除
└── plot.skill                 # 打包文件，删除

# 清理后
./
└── pywayne/
    └── plot/
        └── SKILL.md
```

## README 编写规范（经验总结）

在为本仓库编写或重写 `README.md` 时，遵循以下规则，确保文档可维护、可检索、可扩展：

1. 先定义定位：开头必须说明仓库目标、适用对象、与 `pywayne` 源仓库的关系（本仓库维护 skill，不维护源码实现）。
2. 明确映射关系：写清楚“源码模块路径 -> skill 目录路径 -> skill name”的映射原则，并给出真实示例。
3. 结构优先：README 至少包含以下板块：
   - 项目目标
   - 仓库结构
   - 命名与目录规范
   - 技能清单（按领域分组）
   - 维护建议
4. 技能清单必须基于仓库真实文件生成，不靠人工记忆；以 `**/SKILL.md` 为准，避免遗漏和过期信息。
5. 分组展示而非平铺：pywayne 技能按领域归类（如 CV、LLM、VIO、工具链等），每项至少包含：
   - `Skill Name`
   - `路径`
   - `作用`（一句话）
6. 与规范保持一致：README 内容必须与当前 `CLAUDE.md` 的命名规则一致；若规则更新，README 需同步更新。
7. 控制信息密度：描述尽量一行一句，减少冗余背景；优先“怎么用/在哪里/做什么”。
8. 可维护性优先：统计数字（如技能总数）应在更新时复核，避免“写死后失真”。

### README 更新流程（建议执行）

1. 读取 `CLAUDE.md` 与当前 `README.md`，确认最新规范。
2. 扫描仓库 `SKILL.md` 列表并提取 `name`、`description`。
3. 先搭好 README 骨架，再填充技能分组表。
4. 自检三项：
   - 路径是否存在
   - 技能数量是否匹配
   - 命名是否符合 hyphen-case 规则
