# Pywayne Skill 命名规范

## Skill 命名规则

在创建 pywayne 库的 skill 时，**必须按照源码和文档的目录结构对 skill 进行命名（name）**。

**命名格式：**
- 使用连字符（`-`）连接目录路径

**示例：**

| 源码目录 | Skill 命名 |
|---------|-----------|
| `pywayne/bin/cmdlogger` | `pywayne-bin-cmdlogger` |
| `pywayne/tts` | `pywayne-tts` |
| `pywayne/bin/gettool` | `pywayne-bin-gettool` |
| `pywayne/bin/gitstats` | `pywayne-bin-gitstats` |
| `pywayne/data/` | `pywayne-data` |
| `pywayne/llm/` | `pywayne-llm` |

**命名原则：**
1. 将源码目录路径中的 `/` 替换为 `-`
2. 统一使用小写字母
3. 保持与 pywayne 源码目录一致的结构

**目的：**
- 使 skill 命名与 pywayne 库的代码组织结构保持一致
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
pywayne/
├── plot/
│   ├── SKILL.md
│   ├── scripts/           # 空，删除
│   ├── references/        # 空，删除
│   └── assets/            # 空，删除
└── pywayne-plot.skill      # 打包文件，删除

# 清理后
pywayne/
├── plot/
│   └── SKILL.md
```
