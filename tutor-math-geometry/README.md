# Tutor Math Geometry - 数学几何教学视频制作

> ⚠️ **重要声明**：本技能基于 [xiaotianfotos/skills](https://github.com/xiaotianfotos/skills) 的 tutor 项目修改而来，保留了核心工作流和功能。原作者：https://github.com/xiaotianfotos

**本版本修改**：每次任务输出到独立文件夹 `tutor_output/{日期}_{题目}/`，避免文件混乱。专注数学几何教学视频。

## 核心工作流（与原版一致）

1. **数学分析** → 推导数学事实，建立几何模型
2. **HTML 可视化** → SVG 画图形，展示画图过程
3. **分镜脚本** → 定义幕结构，设计画面/字幕/读白
4. **TTS 音频** → 生成配音文件
5. **验证更新** → 填充音频时长
6. **脚手架** → 生成 Manim 代码框架
7. **实现代码** → 根据分镜实现动画
8. **渲染验证** → 生成最终视频

## 输出目录

每次任务生成的文件保存在 `tutor_output/{日期}_{题目}/` 目录下：
- `math_analysis.md` - 数学分析
- `数学_{日期}_{题目}.html` - HTML 可视化
- `{日期}_{题目}_分镜.md` - 分镜脚本
- `audio/` - TTS 音频文件
- `script.py` - Manim 动画代码
- `media/` - 渲染输出（视频）

## 目录说明

- `scripts/` - TTS 生成、音频验证、代码检查、渲染等脚本
- `templates/` - Manim 脚手架模板
- `references/` - 分镜脚本示例
- `sample/` - **早期探索时找到的一种风格，可以作为参考**

## 使用方式

```bash
# 初始化项目（会自动创建 tutor_output/{日期}_{题目}/ 目录）
python init.py [项目目录]

# 生成 TTS 音频
python scripts/generate_tts.py audio_list.csv ./audio

# 验证音频并更新分镜
python scripts/validate_audio.py 分镜.md ./audio

# 检查代码结构
python scripts/check.py

# 渲染视频
python scripts/render.py
```

## 依赖

- uv
- manim
- edge-tts
