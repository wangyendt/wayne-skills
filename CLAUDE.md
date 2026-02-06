# Pywayne Skill 命名规范

## Skill 命名规则

在创建 pywayne 库的 skill 时，**必须按照源码和文档的目录结构对 skill 进行命名（name）和目录结构**。

**目录结构：**
- 所有 pywayne skill 都应放在 `pywayne/` 目录下
- 子目录名使用连字符（`-`），对应源码模块名（下划线转连字符）
- SKILL.md 的 `name` 字段使用完整路径（连字符分隔）

**示例：**

| 源码目录 | Skill 目录结构 | SKILL.md name |
|---------|---------------|---------------|
| `pywayne/lark_custom_bot.py` | `pywayne/lark-custom-bot/` | `pywayne-lark-custom-bot` |
| `pywayne/bin/cmdlogger` | `pywayne/bin/cmdlogger/` | `pywayne-bin-cmdlogger` |
| `pywayne/tts` | `pywayne/tts/` | `pywayne-tts` |
| `pywayne/bin/gettool` | `pywayne/bin/gettool/` | `pywayne-bin-gettool` |
| `pywayne/bin/gitstats` | `pywayne/bin/gitstats/` | `pywayne-bin-gitstats` |

**命名原则：**
1. 目录结构：`pywayne/<module-name>/`，Python 模块的下划线 `_` 转连字符 `-`
2. Skill name：将路径 `/` 替换为 `-`，统一小写
3. 保持与 pywayne 源码目录一致的结构

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
