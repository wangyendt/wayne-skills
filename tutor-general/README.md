# Tutor General - 通用知识教学视频制作

> ⚠️ **重要声明**：本技能受 tutor-math-geometry 启发，用 Motion Canvas 替代 Manim，适配更广泛的知识点讲解。

通用知识教学视频制作技能，用于生成带配音的 Motion Canvas 动画视频。支持任何主题的知识讲解，不限于数学几何。

## 与 tutor-math-geometry 的区别

| 维度 | tutor-math-geometry | tutor-general |
|------|---------------------|--------------|
| 主题 | 数学几何 | 任何知识点 |
| 渲染引擎 | Manim | Motion Canvas (TypeScript) |
| 代码风格 | Python | TypeScript |
| 动画类型 | 数学公式/图形 | 流程图/示意图/动画 |

## 核心工作流

1. **内容分析** → 提炼核心概念，规划可视化
2. **分镜脚本** → 定义幕结构，设计画面/字幕/读白
3. **TTS 音频** → 生成配音文件
4. **验证更新** → 填充音频时长
5. **脚手架** → 生成 Motion Canvas 代码框架
6. **实现代码** → 根据分镜实现动画
7. **渲染验证** → 生成最终视频

## 输出目录

每次任务生成的文件保存在 `tutor_output/{日期}_{主题}/` 目录下。

## 目录说明

- `scripts/` - TTS 生成、音频验证等脚本
- `templates/` - Motion Canvas 项目模板
- `references/` - 分镜脚本示例
- `assets/` - 静态资源

## 使用方式

```bash
# 安装依赖
npm install

# 生成 TTS 音频
python scripts/generate_tts.py audio_list.csv ./audio

# 验证音频并更新分镜
python scripts/validate_audio.py 分镜.md ./audio

# 开发预览
npm run serve

# 导出视频
npm run export
```

## 依赖

- Node.js 16+
- npm
- @motion-canvas/core
- @motion-canvas/2d
- edge-tts
- ffmpeg
