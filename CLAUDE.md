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

创建 skill 并打包后，**必须删除以下文件/目录**：

1. **`.skill` 文件** - 打包后的文件不需要保留
2. **空的 skill 目录** - 如果 skill 没有 scripts/references/assets，只包含 SKILL.md，则删除其中空的目录

**原因：**
- `.skill` 文件只是用于分发，源码仓库中不需要保留
- 只有 SKILL.md 的 skill 可以直接放在父目录，减少目录层级

**示例：**
```
# 创建后（需要清理）
pywayne/
├── pywayne-plot/          # 只包含 SKILL.md，删除
│   └── SKILL.md
└── pywayne-plot.skill      # 打包文件，删除

# 清理后
pywayne/
└── SKILL.md               # pywayne-plot/SKILL.md 移到这里
```
