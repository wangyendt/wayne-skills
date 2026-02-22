# Tutor General - 通用知识教学视频制作

> ⚠️ **重要声明**：本技能受 tutor-math-geometry 启发，用 Motion Canvas 替代 Manim，适配更广泛的知识点讲解。

通用知识教学视频制作技能，用于生成带配音的 Motion Canvas 动画视频。支持任何主题的知识讲解（科普、技术原理、流程演示等），不限于数学几何。

## 与 tutor-math-geometry 的区别

| 维度 | tutor-math-geometry | tutor-general |
|------|---------------------|--------------|
| 主题 | 数学几何 | 任何知识点 |
| 渲染引擎 | Manim (Python) | Motion Canvas (TypeScript) |
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

## 使用场景示例

- 科普讲解（什么是 DIC？什么是量子计算？）
- 技术原理演示（神经网络如何工作？）
- 流程介绍（Kubernetes 架构）
- 概念解析（什么是向量数据库？）

## 目录结构

```
tutor-general/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── scripts/
│   ├── generate_tts.py       # TTS 生成
│   └── validate_audio.py      # 音频验证
├── templates/
│   ├── scene_scaffold.ts    # 代码脚手架
│   └── package.json         # 项目模板
└── references/
    └── storyboard_sample.md # 分镜示例
```

## 快速开始

```bash
# 1. 分析内容（手动或 AI 辅助）
# 创建 content_analysis.md

# 2. 编写分镜脚本
# 创建 {主题}_分镜.md

# 3. 生成 TTS
python scripts/generate_tts.py audio_list.csv ./audio

# 4. 验证音频
python scripts/validate_audio.py 分镜.md ./audio

# 5. 实现动画
# 参考 templates/scene_scaffold.ts 编写 TypeScript 代码

# 6. 开发预览
npm run serve

# 7. 导出视频
npm run export
```

## 依赖

- **运行时**：Node.js 16+
- **动画引擎**：@motion-canvas/core, @motion-canvas/2d, @motion-canvas/ui
- **语音合成**：edge-tts
- **视频处理**：ffmpeg

## 安装

```bash
# 复制模板
cp -r templates/* my-project/
cd my-project

# 安装依赖
npm install

# 开发预览
npm run serve

# 导出视频
npm run export
```

## Motion Canvas 特点

- ✅ 实时预览（边改边看）
- ✅ TypeScript 类型安全
- ✅ 适合流程图/示意图/动画
- ✅ 可交互预览
